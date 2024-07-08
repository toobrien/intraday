
async function init() {

    const root      = "http://localhost:8081";
    const config    = await (await fetch(`${root}/get_config`)).json();

}

init();