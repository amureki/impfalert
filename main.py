import json
import os
import urllib.request
import urllib.parse
from time import sleep
from datetime import date

SLEEP_TIME = os.environ.get('SLEEP_TIME', 20)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_CHAT_ID = os.environ.get('TELEGRAM_BOT_CHAT_ID')

EARLIEST_APPOINTMENT_DATE = str(date.today())

DOCTOLIB_BASE_API_URL = "https://www.doctolib.de/availabilities.json"

# https://impfstoff.link/
URLS = {
    "biontech_arena": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2495719&agenda_ids=397766-397800-402408-397776&practice_ids=158431&destroy_temporary=true&limit=5",
    "biontech_messe": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2495719&agenda_ids=397844-397846-457504-397845-457511-457405-457406-457411-457415-457416-457418-457426-457436-457439-457443-457453-457477-457487-457497-404659-457400-457404-457407-457408-457409-457410-457412-457414-457419-457420-457421-457424-457425-457427-457428-457429-457430-457432-457435-457442-457448-457457-457463-457470-457483-457489-457493&practice_ids=158434&destroy_temporary=true&limit=5",
    "biontech_tegel": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2495719&agenda_ids=397843-457297-397841-397842-457512-457515-457460-457514-457363-457500-404656-457510-457513-457268-457285-457293-457324-457341-457250-457251-457252-457253-457254-457255-457256-457263-457264-457265-457266-457267-457271-457275-457276-457277-457279-457281-457282-457286-457287-457289-457290-457292-457294-457295-457300-457301-457303-457309-457317-457323-457326-457331-457333-457338-457343-457349-457358-457399-457413&practice_ids=158436&destroy_temporary=true&limit=5",
    "biontech_velodrom": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2495719&agenda_ids=457319-404654-457312-457215-397973-457206-457227-457204-457208-457229-457280-457296-397974-397972-457310-457210-457212-457213-457216-457218-457274-457278-457283-457288-457291-457299-457304-457306-457315-457321&practice_ids=158435&destroy_temporary=true&limit=5",
    "erikahess_moderna": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2537716&agenda_ids=457956-457952-457975-457943-457979-457947-457951-457954-457902-457959-457903-457976-457966-457901-457913-457970-457941-457945-457946-457955-457953-457968-457971-457920-457973-457977-457960-457961-457963-457964-457906-457936-457967-457944-457910&practice_ids=158437&destroy_temporary=true&limit=5",
    "tegel_moderna": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2537716&agenda_ids=465584-465619-465575-465527-465534-465598-465601-465651-465543-466146-465630-465532-465526-465609-465615-465653-466127-466144-466128-466129-466130-466131-466132-466133-466134-466135-466136-466137-466138-466139-466140-466141-466143-466145-466147-466148-466149-466150-466151-466152-466153-466154-465678-465550-465553-465594-465701-465555-465558-465580-465582-465592&practice_ids=158436&destroy_temporary=true&limit=5",
    "tempelhof_moderna": f"{DOCTOLIB_BASE_API_URL}?start_date={EARLIEST_APPOINTMENT_DATE}&visit_motive_ids=2537716&agenda_ids=467901-467933-467894-467897-467898-467899-467895-467896-467900-467908-467912-467893-467903-467905-467906-467907-467910-467911-467934-467935-467936-467937-467938-467939-467940&practice_ids=158433&destroy_temporary=true&limit=5",
}

# https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-XXXXX
PRACTICE_MAPPING = {
    "biontech_arena": "158431",
    "biontech_messe": "158434",
    "biontech_tegel": "158436",
    "biontech_velodrom": "158435",
    "erikahess_moderna": "158437",
    "tegel_moderna": "158436",
    "tempelhof_moderna": "158433",
}

DOCTOLIB_API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}


def send_telegram_message(message):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "chat_id": TELEGRAM_BOT_CHAT_ID,
        "parse_mode": "Markdown",
        "text": message,
    }

    request_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    request = urllib.request.Request(request_url, data=json.dumps(data).encode(), headers=headers)
    response = urllib.request.urlopen(request)
    data = response.read().decode('utf-8')
    print(data)


def parse_urls():
    for name, url in URLS.items():
        verbose_name = name.replace("_", " ").title()
        print(f'Checking {verbose_name}...')
        request = urllib.request.Request(
            url,
            headers=DOCTOLIB_API_HEADERS
        )
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        json_data = json.loads(data)
        availabilities = json_data['availabilities']
        total = json_data['total']
        reason = json_data.get('reason')
        message = json_data.get('message')
        if not total and not availabilities:
            print(f'Not available: {reason}. Msg: {message}')
        else:
            practice_url = f"https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-{PRACTICE_MAPPING[name]}"
            alert_message = f'Impf alert in {verbose_name}! Go check at: {practice_url}.'
            print(f'************************ATTENTION!!!************************')
            print(alert_message)
            send_telegram_message(alert_message)


if __name__ == '__main__':
    while True:
        parse_urls()
        print('.....................')
        sleep(SLEEP_TIME)
