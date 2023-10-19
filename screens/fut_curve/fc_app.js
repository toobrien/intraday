const CONFIG = await (await fetch(`http://localhost:8080/config`)).json();
const CLIENT = new base_client();


async function init() {

    let futs = await CLIENT.futures([ CONFIG["symbol"] ]);

    console.log(json.stringify(futs, null, 2));

}


init();