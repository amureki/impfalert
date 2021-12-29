import json
import os
from typing import Optional
from urllib.error import URLError
import urllib.parse
import urllib.request
from time import sleep
from datetime import date

from cache import update_cache, exists_in_cache, slots_cache
from notifications import send_alerts

SLEEP_TIME = os.environ.get("SLEEP_TIME", 60)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_CHAT_ID = os.environ.get("TELEGRAM_BOT_CHAT_ID")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
HEALTHCHECK_TOKEN = os.environ.get("HEALTHCHECK_TOKEN")

EARLIEST_APPOINTMENT_DATE = os.environ.get(
    "EARLIEST_APPOINTMENT_DATE", str(date.today())
)

DOCTOLIB_BASE_API_URL = "https://www.doctolib.de/availabilities.json"

PRACTICE_PARAMS = {
    "biontech_messe": "visit_motive_ids=3091828&agenda_ids=457424-457489-397846-404659-457448-457453-457410-457416-457439-457400-457429-457504-457497-457405-457404-457406-457409-457407-397844-457455-457511-397845-457436-457442-457487-457463-457477-457483-457470-457457-457493-457408&insurance_sector=public&practice_ids=158434",
    "moderna_messe":  "visit_motive_ids=3091829&agenda_ids=493322-493298-493320-493285-493317-493306-493324-493314-493308-493300&insurance_sector=public&practice_ids=195952",
    "biontech_tegel": "visit_motive_ids=3091828&agenda_ids=457399-457317-457323-457301-457500-457252-457285-457295-457324-457341-457460-457413-457250-457251-457292-457290-457331-457277-457333-457265-457309-457293&insurance_sector=public&practice_ids=158436",
    "moderna_tegel":  "visit_motive_ids=3091829&agenda_ids=465532-465550-465555-465553-465527-465543-465558-465575-465534-465526&insurance_sector=public&practice_ids=191612",
}

# https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-XXXXX
PRACTICE_MAPPING = {
    "biontech_messe": "158434",
    "moderna_messe":  "195952",
    "biontech_tegel": "158436",
    "moderna_tegel":  "191612",
}

def send_doctolib_request(params, date) -> Optional[dict]:
    url = f"{DOCTOLIB_BASE_API_URL}?start_date={date}&destroy_temporary=true&limit=5&{params}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    try:
        response = urllib.request.urlopen(request)
    except URLError as e:
        print(f"Error: {e}")
        return
    data = response.read().decode("utf-8")
    return json.loads(data)


def parse_urls():
    print(f'cache: {slots_cache}')
    for practice_name, params in PRACTICE_PARAMS.items():
        practice_verbose_name = practice_name.replace("_", " ").title()
        print(f"Checking {practice_verbose_name}...")
        data = send_doctolib_request(params=params, date=EARLIEST_APPOINTMENT_DATE)
        if data is None:
            print(f"Failed to check {practice_verbose_name}...")
            continue

        availabilities = data["availabilities"]
        total = data["total"]

        # doctolib might return availabilities without any slots, just check for total slot number
        if not total: # and not availabilities:
            reason = data.get("reason")
            message = data.get("message")
            print(f"Not available: {reason}. Msg: {message}")
            continue

        practice_booking_url = f"https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-{PRACTICE_MAPPING[practice_name]}"
        alert_message = (
            f"Impf alert in {practice_verbose_name}!\n\n" f"Book at: {practice_booking_url}."
        )

        proposed_next_slot_date = data.get("next_slot")
        all_available_dates = []
        new_available_dates = []
        if proposed_next_slot_date:
            next_slots_data = send_doctolib_request(
                params=params, date=proposed_next_slot_date
            )
            if next_slots_data is None:
                print(f"Failed to check {practice_verbose_name}...")
                continue

            availabilities = next_slots_data["availabilities"]
            total = next_slots_data["total"]
            for (
                availability
            ) in availabilities:  # dict_keys(['date', 'slots', 'substitution'])
                all_available_dates.append(availability.get("date"))

            for available_date in all_available_dates:
                if not exists_in_cache(practice_name, available_date):
                    new_available_dates.append(available_date)

            if new_available_dates:
                update_cache(practice_name, new_available_dates)
                verbose_dates = ", ".join(new_available_dates)
                alert_message = (
                    f"Impf alert in {practice_verbose_name}!\n"
                    f"Earliest available dates: {verbose_dates}.\n"
                    f"Amount of slots: {total}.\n\n"
                    f"Book at: {practice_booking_url}."
                )

        if all_available_dates and not new_available_dates:
            return

        print(data)
        print(f"************************ATTENTION************************")
        print(alert_message)
        print(f"**********************ATTENTION END**********************")
        send_alerts(alert_message)


if __name__ == "__main__":
    try:
        send_alerts("Bot online...")
        while True:
            parse_urls()
            print(".....................")
            sleep(int(SLEEP_TIME))
            if HEALTHCHECK_TOKEN:
                urllib.request.urlopen("https://hc-ping.com/{}".format(HEALTHCHECK_TOKEN))
    finally:
        send_alerts("Bot offline...")
