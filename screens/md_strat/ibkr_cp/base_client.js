

// market data fields

const mdf = {

    last:           31,
    bid:            84,
    ask_size:       85,
    ask:            86,
    bid_size:       88,
    md_available:   6509,
    last_size:      7059,
    mark:           7635,
    delayed:        "HasDelayed",
    ts_base:        "TimestampBase",
    ts_delta:       "TimestampDelta"

};


class base_client {
 

    constructor(
        host = "localhost", 
        port = 5000
    ) {

        this.rest_uri   = `http://${host}:${port}/v1/api`;
        this.ws_uri     = `ws://${host}:${port}/v1/api/ws`;
        this.ws         = null;

        let def_ws_handler  = async (evt) =>  {

            if (evt.data) {
            
                let msg = JSON.parse(await evt.data.text());

                console.log(JSON.stringify(msg, null, 2));
            
            }

        }

        this.ws_cls_handler = def_ws_handler;
        this.ws_opn_handler = def_ws_handler;
        this.ws_err_handler = def_ws_handler;
        this.ws_msg_handler = def_ws_handler;

    }

    
    async secdef(conids) {

        let res = await fetch(
                    `${this.rest_uri}/trsrv/secdef`,
                    {
                        method:     "POST",
                        body:       JSON.stringify({ conids: conids }),
                        headers:    { "Content-Type": "application/json" }
                    }
                );
        
        res = res.status == 200 ? await res.json() : null;

        return res;

    }

    
    async search(symbol, name, secType) {

        let res = await fetch(
                    `${this.rest_uri}/iserver/secdef/search`,
                    {
                        method:     "POST",
                        body:       JSON.stringify(
                                        {
                                            symbol:     symbol,
                                            name:       name,
                                            secType:    secType
                                        }
                                    ),
                        headers:    { "Content-Type": "application/json" }
                    }
                );
        
        res = res.status == 200 ? await res.json() : null;

        return res;

    }

    
    async secdef_info(
        conid,
        sectype,
        month,
        exchange,
        strike,
        right
    ) {

        let url = `${this.rest_uri}/iserver/secdef/info?conid=${conid}&sectype=${sectype}`;

        if (month)      url += `&month=${month}`;
        if (exchange)   url += `&exchange=${exchange}`;
        if (strike)     url += `&strike=${strike}`;
        if (right)      url += `&right=${right}`;

        let res = await fetch(url);

        res = res.status == 200 ? await res.json() : null;

        return res;

    }


    async strikes(
        conid,
        sectype,
        month,
        exchange
    ) {

        let url = `${this.rest_uri}/iserver/secdef/strikes?conid=${conid}&sectype=${sectype}&month=${month}`;

        if (exchange) url += `&exchange=${exchange}`;

        let res = await fetch(url);

        res = res.status == 200 ? await res.json() : null;

        return res;

    }


    async init_ws() {

        let res = await fetch(`${this.rest_uri}/tickle`);

        if (res.status == 200) {

            let body            = await res.json();
            this.session        = body.session;
            this.ws             = new WebSocket(this.ws_uri);
            
            this.ws.onerror     = this.ws_err_handler;
            this.ws.onopen      = this.ws_opn_handler;
            this.ws.onmessage   = this.ws_msg_handler;
            this.ws.onclose     = this.ws_cls_handler;

            while (true)

                if (!this.ws.readyState)

                    // wait until websocket is ready
                
                    await new Promise(resolve => setTimeout(resolve, 1000));
                
                else

                    break;
            
        } else {

            // error receiving session token

            console.log(res.text);

            this.ws = null;

        }

    }


    async set_ws_handlers(
        msg_handler,
        err_handler,
        opn_handler,
        cls_handler
    ) {

        if (!this.ws) await this.init_ws();

        if (msg_handler) { 
            
            this.ws_msg_handler = msg_handler;
            this.ws.onmessage   = msg_handler;

        }

        if (err_handler) {
        
            this.ws_err_handler = err_handler;
            this.ws.onerror     = err_handler;
        
        }

        if (opn_handler) {
        
            this.ws_opn_handler = opn_handler
            this.ws.onopen      = opn_handler;
        
        }

        if (cls_handler) {
        
            this.ws.onclose     = cls_handler 
            this.ws.onclose     = cls_handler;
        
        }

    }


    async sub_market_data(conid, fields) {

        if (!this.ws) await this.init_ws();
        if (!this.ws) return;

        fields = JSON.stringify(fields.map( i => String(i) ));

        let cmd = `smd+${conid}+{ "fields": ${fields} }`;

        this.ws.send(cmd);

    }


    unsub_market_data(conid) {

        if (!this.ws) return;

        this.ws.send(`umd+${conid}+{}`);

    }


}
