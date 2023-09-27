
const   SERVER      = "localhost";
const   PORT        = 8080;


async function init() {

    const config = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();

}

init();