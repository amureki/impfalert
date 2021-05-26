from cache import slots_cache, update_cache, exists_in_cache


def test_update_cache():
    assert slots_cache == {
        "biontech_arena": {},
        "biontech_messe": {},
        "biontech_tegel": {},
        "biontech_velodrom": {},
        "erikahess_moderna": {},
        "tegel_moderna": {},
        "tempelhof_moderna": {},
    }

    update_cache("biontech_arena", ['2021-05-31', '2021-06-01'])
    assert list(slots_cache["biontech_arena"].keys()) == ['2021-05-31', '2021-06-01']


def test_exists_in_cache():
    global slots_cache

    slots_cache = {
        "biontech_arena": {'2021-05-31': '2021-05-10T21:49:42', '2021-06-01': '2021-05-10T21:49:42'},
        "biontech_messe": {},
        "biontech_tegel": {},
        "biontech_velodrom": {},
        "erikahess_moderna": {},
        "tegel_moderna": {},
        "tempelhof_moderna": {},
    }

    assert exists_in_cache("biontech_arena", '2021-05-31') is True
    assert exists_in_cache("biontech_arena", '2021-01-01') is False
    assert exists_in_cache("biontech_messe", '2021-05-31') is False
