from finx_ib_reports.download_trades import get_flex_token


def test_get_flex_token():
    configs = {"IB_FLEX_TOKEN": 123}
    assert get_flex_token(configs) == 123
