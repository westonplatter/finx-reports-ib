[![Tests](https://github.com/westonplatter/finx-reports-ib/actions/workflows/ci.yml/badge.svg)](https://github.com/westonplatter/finx-reports-ib/actions/workflows/ci.yml) [![Docs](https://github.com/westonplatter/finx-reports-ib/actions/workflows/docs.yml/badge.svg)](https://github.com/westonplatter/finx-reports-ib/actions/workflows/docs.yml)

# Finx Reports - IB
Python package to generate reports from Interactive Brokers.


## Installing
Install the module from github,
```bash
pip install git+https://https://github.com/westonplatter/finx-reports-ib.git@main
```

Or add it to your `requirements.txt` file,
```bash
finx_reports_ib @ git+https://https://github.com/westonplatter/finx-reports-ib.git@main
```

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


2. Clone the repo and install it with uv

    ```bash
    git clone git@github.com:westonplatter/finx-reports-ib.git
    cd finx-reports-ib

    # Install uv if you haven't already
    # See: https://docs.astral.sh/uv/getting-started/installation/

    # Sync dependencies (creates virtual environment and installs all dependencies)
    uv sync

    # Or sync with optional dev dependencies
    uv sync --extra dev
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
    ```bash
    # note that `report-name` matches up with annual key in the .env file
    uv run python -c "from finx_reports_ib.download_trades import execute_csv_for_accounts; execute_csv_for_accounts('annual', cache=True)"
    ```

5. See files in the `data` directory

## uv Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and Python environment management.

### Essential Commands

- **Install dependencies**
  ```bash
  uv sync                    # Install core dependencies
  uv sync --extra dev        # Install with dev dependencies
  uv sync --extra test       # Install with test dependencies
  uv sync --all-extras       # Install with all optional dependencies
  ```

- **Run Python code**
  ```bash
  uv run python <script>     # Run a Python script
  uv run pytest              # Run tests
  ```

- **Manage dependencies**
  ```bash
  uv add <package>           # Add a package to dependencies
  uv add --dev <package>     # Add a package to dev dependencies
  uv remove <package>        # Remove a package
  ```

- **Build and release**
  ```bash
  uv build                   # Build the package (replaces python setup.py sdist bdist_wheel)
  ```