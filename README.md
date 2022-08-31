# Finx Reports - IB
Python package to fetch reports from IB.

## Example
Example `.env` file,
```
IB_JSON='{"accounts": [{"name": "account1", "flex_token": "123", "weekly": 890}]}'

PORTFOLIOS_DISCORD_WEBHOOK_URL=https://discord_url
```

Example python,
```
from finx_ib_reports.download_trades import execute_discord_for_accounts
execute_discord_for_accounts(report_name="weekly", cache=False, file_name=".env")
```

And checkout the reports in `data`.


## License
BSD-3. See LICENSE file.
