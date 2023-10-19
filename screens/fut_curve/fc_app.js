

async function init() {

    const config = await ((await fetch("http://localhost:8080/config")).json());
    const client = new base_client();

    let futs = await client.futures([ config["symbol"] ]);

    console.log(JSON.stringify(futs, null, 2));

}


init();