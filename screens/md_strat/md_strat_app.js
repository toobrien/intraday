
const   SERVER      = "localhost";
const   PORT        = 8080;
const   CONFIG      = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
const   CLIENT      = new opt_client();


function get_strategy(strat) {

    return  strat == "call"             ? CLIENT.get_call_defs          :
            strat == "call_vertical"    ? CLIENT.get_call_vertical_defs :
            strat == "fly"              ? CLIENT.get_fly_defs           :
            strat == "iron_fly"         ? CLIENT.get_iron_fly_defs      :
            strat == "put"              ? CLIENT.get_put_defs           :
            strat == "put_vertical"     ? CLIENT.get_put_vertical_defs  :
            strat == "straddle"         ? CLIENT.get_straddle_defs      :
            strat == "calendar"         ? CLIENT.get_calendar_defs      :
            null;

}


async function init() {

    const strat         = get_strategy(CONFIG["strat"]);
    const strat_defs    = strat(
                            CONFIG["ul_type"],
                            CONFIG["ul_sym"],
                            CONFIG["ul_exps"],
                            CONFIG["opt_exps"],
                            CONFIG["lo_str"],
                            CONFIG["hi_str"],
                            CONFIG["side"],
                            CONFIG["params"]
                        );

}


init();