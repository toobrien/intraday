const   ROOT            = "http://localhost:8081";
const   CLIENT          = new base_client();
const   L1              = {};
let     TS              = null;
let     DEBUG           = null;
let     x_id            = null;
let     y_id            = null;
let     quote_interval  = null;
let     model_interval  = null;
let     X               = null;
let     Y               = null;
let     residuals       = null;


async function update_chart() {}


async function update_model() {

    let body = {
        x: L1[x_id]["mids"],
        y: L1[y_id]["mids"]
    }

    let res = await (await fetch(
                `${ROOT}/get_model`,
                {
                    method:     "POST",
                    headers:    { "Content-Type": "application/json" },
                    body:       JSON.stringify(body)
                }
            )).json();
        
    X = res.x;
    Y = res.y;

}


function update_data() {

    let quotes = Object.values(L1);

    for (let quote of quotes)
    
        if (!quote[mdf.bid] || !quote[mdf.ask])

            return;

    for ( let quote of quotes)

        quote.mids.append(quote.mid);

    TS.append(/* ... */);

}


function m_handler(evt) {

    if (!evt.data) return;
    
    let msg = JSON.parse(evt.data);

    if (CONFIG.debug)

        console.log(JSON.stringify(msg, null, 2));

    if (msg.topic.includes('smd+')) {

        let conid = msg.conid;

        if (conid in L1) {

            let quote = L1[conid];

            msg[mdf.bid] ? quote[mdf.bid] = parseFloat(msg[mdf.bid]) : null;
            msg[mdf.ask] ? quote[mdf.ask] = parseFloat(msg[mdf.ask]) : null;

            quote["mid"] = (quote[mdf.bid] + quote[mdf.ask]) / 2;

        }

    }

}


async function init() {

    const config    = await (await fetch(`${ROOT}/get_config`)).json();

    x_sym           = config["x_sym"];
    x_id            = config["x_id"];
    x               = config["x"];
    y_sym           = config["y_sym"];
    y_id            = config["y_id"];
    y               = config["y"];
    quote_interval  = config["quote_interval"];
    model_interval  = config["model_interval"];

    for (let cfg of [ [ x_id, x_sym, x ], [ y_id, y_sym, y] ]) {

        let id          = cfg[0];
        let sym         = cfg[1]
        let mids        = cfg[2];
        L1[id]          = {};
        L1[id][sym]     = sym;
        L1[id][mdf.bid] = null;
        L1[id][mdf.ask] = null;
        L1[id]["mid"]   = null;
        L1[id]["mids"]  = mids;

    }

    await CLIENT.set_ws_handlers(msg_handler = m_handler);

}


init();

setInterval(update_data,  quote_interval);
setInterval(update_model, model_interval);