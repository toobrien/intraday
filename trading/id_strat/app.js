

async function demo_opt_client() {

    const client    = new opt_client();
    const opt_defs  = await client.get_defs_ind("SPX", "20230901", 4470, 4530, "C");
    const ul_conid  = opt_defs.ul_conid; 
    const fly_defs  = client.get_butterfly_defs(opt_defs.defs, "-", 1);
    const conids    = fly_defs.map(def => def.conid);
        
    conids.push(ul_conid);

    client.sub_l1(conids);

    // await new Promise(resolve => setTimeout(resolve, 10000));
    
    // client.unsub_l1(conids);

}


demo_opt_client();