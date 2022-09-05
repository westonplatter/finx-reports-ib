# Finx Reports - IB
Python package to generate reports from Interactive Brokers.

## Getting Started

1. Create a Flex Report in the Interactive Broker website (see this [link](https://guides.interactivebrokers.com/ap/Content/activityflex.htm))
   1. Query Name = AllAccounts-AnnualReport
   2. Sections to include in the report. In each, select all Options and all Fields/Columns except: `Serial Number`, `Delivery Type`, `Commodity Type`, `Fineness`, `Weight`.
      1. Account Information
      2. Change in NAV
      3. Complex Positions
      4. Mark-to-Market Performance Summary in Base
      5. Month & Year to Date Performance Summary in Base
      6. Open Positions
      7. Option Exercises, Assignments, and Expirations
      8. Realized and Unrealized Performance Summary in Base
   3. Accounts = select all desired accounts (python code is able to handle single or multiple accounts)
   4. Models = Optional
   5. Format = XML
   6. Period = Last 365 Days
   7. Date Format = yyy-MM-dd
   8. Time Format = HH:mm:ss
   9. Date/Time Separator = ;semicolon
   10. ProfitLoss = Default
   11. Include Canceled Trades = No
   12. Include Base Currency = No
   13. Include All Audit Fields = No
   14. Display Account Alias in Place of Account ID = No
   15. Breakout by Day = No


2. Clone the repo + install dependencies
    
    ```
    git clone git@github.com:westonplatter/finx-reports-ib.git
    cd finx-reports-ib
    pip install -r requirements/requirements.txt
    ```

3. Create your own `.env` file
    
    Copy the sample env file,
    ```
    cp .env.example .env
    ```

    Edit it with your own values,
    ```
    IB_JSON='{"accounts": [{"name": "account1", "flex_token": "123", "annual": <ibkr_query_id>}]}'
    ```

4. Run the download command
    ```
    # note that `report-name` matches up with annual key in the .env file
    python cli.py download --report-name=annual --cache

    # see the python import/methods in cli.py
    ```

5. See files in the `data` directory



## License
BSD-3. See LICENSE file.
