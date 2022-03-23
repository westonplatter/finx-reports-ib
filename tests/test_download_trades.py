from finx_ib_reports.config_helpers import get_ib_json


def test_get_ib_json():
    configs = {"IB_JSON": '{"a": 1}'}
    assert get_ib_json(configs) == {"a": 1}
