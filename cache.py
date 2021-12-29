import datetime

slots_cache = {
    "biontech_messe": {},
    "moderna_messe":  {},
    "biontech_tegel": {},
    "moderna_tegel":  {},
}


def update_cache(practice, available_dates):
    now = datetime.datetime.now().replace(microsecond=0).isoformat()
    slots_cache[practice].update(
        {available_date: now for available_date in available_dates}
    )
    return slots_cache


def exists_in_cache(practice, available_date):
    return available_date in slots_cache[practice].keys()
