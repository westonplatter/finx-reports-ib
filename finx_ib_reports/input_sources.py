from ib_insync import IB, Contract, Option
from ib_insync.ticker import Ticker
from typing import List

class TwsApiSource:
    def __init__(self, ib=None):
        if ib is None:
            self.ib = IB()
            self.ib.connect('127.0.0.1', 8888, clientId=0)
        else:
            self.ib = ib
            
    def get_accounts(self):
        return self.ib.managedAccounts()

    def get_positions(self, aid: str):
        return self.ib.positions(account=aid)
    
    def get_quotes(self, con_ids: List[str]):
        # gen and qualify contract
        contracts = []
        for con_id in con_ids:
            contracts.append(Option(conId=con_id))
        contracts = self.ib.qualifyContracts(*contracts)
        
        # get option quotes
        return self.ib.reqTickers(*contracts)
