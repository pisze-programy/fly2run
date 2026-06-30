import requests
import json
import time


# Get cookies via devtools/network - https://worldsmarathons.com/s/running/europe?search=
cookies = {
    'cf_clearance': 'TRQ7m58HzjD1T04eeP2zYRngCz_o92SIZ_BmmbqCz18-1782827279-1.2.1.1-xjU4BjYYN4tY81UnQ9YqAlQEyiCFM9z0wAMCaWBwQRj_qqyzRfodSD7Orj0gCoUXbiSRt6372Z6H1zwneVaYx3Tvjl8UNk9JJoOR2_6Wzg9taCjgvd6.vxgXaNTvoJU2_zHlqSXG7osE3348eTrGN.PXxRR100kfxTSUh2RHEEm59cxL3Vtxm38EZA.qvGah6HzoxMzhk9rjc5g7u5QclXz8eFnmdq2dm4qNbLy39FH5VrlYothhsDK_4LQY4s5FPdzi7EJf2npsllTwLgls.1DfiQGlSFy0Bm9F6VVXVRgoMQuwDJnfjLApUkDW5Fz2ehftK2u2uehKVSZxxjYS3RYZa4IgHTlAl0cQ3i9pBe2DTJyFAdaLLvlnjtmm.TOkMavyiamM7vaou.etadNKRnSAJkQ6FsiR1QwxM__qwhdH_yxg12Juq0pQonbjJjBav.f3rroea7fCkYjsRcTZY3moxIcnKnWxxBhA0M8Qhx0xYQcf1E_fSdBaqo1OKHrpBwelpHkFFFcJlC3DoXTmAQ',
    'cookieyes-consent': 'consentid:OXM0ZHBZMTZWRUNPZFdDeEgzNmVjZHZ0YWszb2I1ZXg,consent:no,action:yes,necessary:yes,functional:no,analytics:no,performance:no,advertisement:no,other:no',
    'ai_session': 'tLDr5|1782827480348|1782828624691'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0',
    'Accept': 'application/json'
}

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

all_events = []
page = 1

while True:
    print(f"Fetching page {page}...")
    url = f"https://worldsmarathons.com/api/search?sport=running&continent=europe&search=&page={page}&currency=EUR"

    resp = session.get(url)

    if resp.status_code != 200:
        print(f"Error {resp.status_code}")
        break

    data = resp.json()
    results = data.get('results', [])

    if not results:
        print("No results, finished.")
        break

    all_events.extend(results)
    print(f"Fetched {len(results)} items. Total: {len(all_events)}")

    if len(results) < 21:
        break

    page += 1
    time.sleep(0.3)

with open('all_events.json', 'w') as f:
    json.dump(all_events, f)

print(f"Done. Total saved: {len(all_events)}")
