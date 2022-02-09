from decimal import Decimal
import pickle
from pydantic import BaseModel

from finx_ib_reports.input_sources import TwsApiSource
from finx_ib_reports.reports import PnlReport



similar_product_mapping = {
    "MCL": "MCL",
    "YC": "ZC"
}

class ReportContract(BaseModel):
    con_id: int
    symbol: str

    @classmethod
    def gen_from_ibinsync(cls, contract):
        return cls(con_id=contract.condId, symbol=contract.symbol)

class ReportPosition(BaseModel):
    account: str
    contract: ReportContract
    position: Decimal

    @classmethod
    def gen_from_ibinsyc(cls, position):
        rcontract = ReportContract.gen_from_ibinsync(position.contract)

        return ReportPosition(
            account=position.account,
            contract=rcontract,
            position=position.position)
    
    @classmethod
    def gen_from_ibsync_list(cls, positions):
        rpositions = []
        for position in positions:
            rpositions.append(cls.gen_from_ibinsyc(position))
        return rpositions


def api_fetch():
    s = TwsApiSource()
    aids = [x for x in s.get_accounts() if 'U31' in x]

    for aid in aids:
        positions = s.get_positions(aid)

    position = positions[0]

    rpositions = []
    for pos in positions:
        rpositions.append(rposition)


    with open("weston.positions", "wb") as fh:
        pickle.dump(rpositions, fh)
        
    # con_ids = []
    # for px in positions:
        # con_ids.append(px.contract.conId)

    # quotes = s.get_quotes(con_ids)

    # with open("weston.quotes", "wb") as fh:
        # pickle.dump(str(quotes), fh)


def cache_fetch():
    with open("weston.positions", "rb") as fh:
        positions = pickle.load(fh)

    print(positions[0])

    # with open("weston.quotes", "rb") as fh:
        # quotes = pickle.load(fh)

    # report = PnlReport(positions, quotes)
    # df = report.summary_table()
    # print(df)


if __name__ == "__main__":
    # api_fetch()
    cache_fetch()

