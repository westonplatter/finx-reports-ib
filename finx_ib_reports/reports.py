"""
Account PnL Report

The goal of this is to role up positions by proudct (eg, /CL) into a
summary PnL.
"""

import pandas as pd


similar_product_mapper = {
    "MCL": "CL",
    "YC": "ZC"
}

class PnlReport:
    def __init__(self, positions, quotes):
        self.positions = positions
        self.quotes = quotes

    def summary_table(self) -> pd.DataFrame:
        rows = []
        for pos in self.positions:
            # print(pos)
            pass
            # row = {"contract.symbol": pos.contract.symbol}
            # rows.append(row)
        return pd.DataFrame(rows)


class OptionGreeksReport:
    def __init__(self, positions, quotes):
        self.positions = positions
        self.quotes = quotes

    def summary_table(self) -> pd.DataFrame:
        rows = []
        for pos in self.positions:
            row = {"delta": 0.0}
            rows.append(row)
        return pd.DataFrame(rows)
