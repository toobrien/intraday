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

        /*
        let def_ws_handler = (evt) =>  {

            if (evt.data) {
            
                let msg = JSON.parse(evt.data);

                console.log(JSON.stringify(msg, null, 2));
            
            }

        }
        */

        let def_ws_handler = (evt) => {};

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


    async orders(filters = null, force = null) {

        // query string params not implemented

        let params = new URLSearchParams();

        if (filters)    params.append("filter", filters);
        if (force)      params.append("force", force);
        
        let res = await fetch(
            `${this.rest_uri}/iserver/account/orders` + params,
            {
                method: "GET",
                headers: { "accept": "application/json" }
            }
        );

        res = res.status == 200 ? await res.json() : { error: res.statusText };

        return res;

    }


    async place_order(account_id, args) {

        let res = await fetch(
            `${this.rest_uri}/iserver/account/${account_id}/orders`,
            {
                method:     "POST",
                body:       JSON.stringify(args),
                headers:    { "Content-Type": "application/json" }
            }
        );

        res = res.status == 200 ? await res.json() : { error: res.statusText };

        return res;

    }


    async reply(reply_id) {

        let res = await fetch(
            `${this.rest_uri}/iserver/reply/${reply_id}`,
            {
                method:     "POST",
                body:       JSON.stringify({ "confirmed": true })
            }
        );

        res = res.status == 200 ? await res.json() : { error: res.statusText };

        return res;

    }

    async modify_order(account_id, order_id, args) {

        let res = await fetch(
            `${this.rest_uri}/iserver/account/${account_id}/order/${order_id}`,
            {
                method:     "POST",
                body:       JSON.stringify(args),
                headers:    { "Content-Type": "application/json" }
            }
        )

        res = res.status == 200 ? await res.json() : { error: res.statusText };

        return res;

    }


    async cancel_order(account_id, order_id) {

        let res = await fetch(
            `${this.rest_uri}/iserver/account/${account_id}/order/${order_id}`,
            { method: "DELETE" }
        );

        res = res.status == 200 ? await res.json() : { "error": res.statusText };

        return res;

    }


    async tickle() {

        let res = await fetch(
            `${this.rest_uri}/tickle`,

        );

        res = res.status == 200 ? await res.json() : { "error": res.statusText };

        return res;

    }

    
    async sub_order_updates() {

        if (!this.ws) await this.init_ws();
        if (!this.ws) return;

        this.ws.send("sor+{}");

    }
    

    unsub_order_updates() {

        if (!this.ws) return;

        this.ws.send("uor+{}");

    }


}
