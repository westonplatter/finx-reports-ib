from finx_ib_reports.input_sources import TwsApiSource

import pickle


s = TwsApiSource()
aids = [x for x in s.get_accounts() if 'U31' in x]


for aid in aids:
    pxs = s.get_positions(aid)
    pxs = [x for x in pxs if x.contract.symbol in ['CL', 'MCL']]
    
    con_ids = []
    for px in pxs:
        con_ids.append(px.contract.conId)

    quotes = s.get_quotes(con_ids)

    with open("weston.objects", "wb") as fh:
        pickle.dump(str(quotes), fh)
