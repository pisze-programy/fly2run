import json
import os
import pandas as pd
import requests
import datetime
from geopy.distance import geodesic

ORIGIN = 'POZ'
MAX_DISTANCE_KM = 50
PRICE_CACHE = {}


def load_data():
    with open('../data/running_events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    with open('../data/ryanair_connections.json', 'r', encoding='utf-8') as f:
        connections = json.load(f)
    return events, connections


def calculate_popularity_score(event):
    score = 0

    score += (event.get('reviewsCount', 0) * 5)
    score += int(event.get('rating', 0) * 10)
    score += (event.get('resultsCount', 0) * 0.5)

    if event.get('promoted'):
        score += 20

    return score


def get_fares(origin, dest, month):
    cache_key = f"{origin}_{dest}_{month}"
    if cache_key in PRICE_CACHE:
        return PRICE_CACHE[cache_key]

    url = f"https://www.ryanair.com/api/farfnd/v4/oneWayFares/{origin}/{dest}/cheapestPerDay"
    params = {'outboundMonthOfDate': month, 'currency': 'PLN'}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0'}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5).json()
        fares = {f['day']: f for f in resp['outbound']['fares'] if f.get('price')}
        PRICE_CACHE[cache_key] = fares
        return fares
    except:
        return {}


def find_best_trip(event_date_str, origin, dest):
    try:
        event_date = datetime.datetime.strptime(event_date_str[:10], '%Y-%m-%d')
    except:
        return None

    month = event_date.strftime('%Y-%m-01')
    out_fares = get_fares(origin, dest, month)
    ret_fares = get_fares(dest, origin, month)

    best_total = float('inf')
    best_option = None

    for i in range(0, 3):
        out_d = (event_date - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        for j in range(1, 4):
            ret_d = (event_date + datetime.timedelta(days=j)).strftime('%Y-%m-%d')

            if out_d in out_fares and ret_d in ret_fares:
                price_out = out_fares[out_d]
                price_ret = ret_fares[ret_d]
                total = price_out['price']['value'] + price_ret['price']['value']

                if total < best_total:
                    best_total = total
                    best_option = {
                        'price': total,
                        'out_time': price_out.get('departureDate'),
                        'ret_time': price_ret.get('departureDate')
                    }
    return best_option


def process_trips(events, connections):
    trips = []
    airports_codes = {item['iataCode']: item for item in connections}
    origin_data = airports_codes.get(ORIGIN)

    if not origin_data:
        return pd.DataFrame()

    valid_destinations = {
        route.split(':')[1] for route in origin_data.get('routes', [])
        if route.startswith('airport:')
    }

    print(f"Total events: {len(events)}")
    processed_count = 0

    for event in events:
        coords = event.get('startPoint')
        if not coords or len(coords) < 2:
            continue

        event_coords = (coords[1], coords[0])  # (lat, lon)

        for dest_code in valid_destinations:
            dest_data = airports_codes.get(dest_code)
            if not dest_data: continue

            dest_coords = (dest_data['coordinates']['latitude'], dest_data['coordinates']['longitude'])
            dist = geodesic(event_coords, dest_coords).km

            if dist <= MAX_DISTANCE_KM:
                event_date = event.get('dateNextRace')
                trip = find_best_trip(event_date, ORIGIN, dest_code)

                if trip:
                    flight_price = trip['price']
                    total_trip_price = flight_price # TODO: add hotel prices
                    popularity_score = calculate_popularity_score(event)

                    trips.append({
                        'event_id': event.get('title'),
                        'event_distance': event.get('distance'),
                        'event_price': event.get('minPrice'),
                        'event_price_currency': event.get('searchCurrency'),
                        'event_date': event_date,
                        'event_location': f"{event.get('city')}:{event.get('country')}",
                        'airport': dest_code,

                        "popularity_score": popularity_score,

                        'departure_date': trip['out_time'],
                        'return_date': trip['ret_time'],
                        'flight_price': flight_price,

                        # TODO: Add Booking.com integration

                        'total_trip_price' : total_trip_price,
                    })
                    processed_count += 1

    print(f"Events within {MAX_DISTANCE_KM}km of reachable airports: {processed_count}")
    return pd.DataFrame(trips)


def main():
    events, connections = load_data()
    df = process_trips(events, connections)

    popular_events = df[df['popularity_score'] > 20].sort_values(
        by=['total_trip_price'], ascending=True
    )
    rest_events = df[df['popularity_score'] <= 20].sort_values(
        by='total_trip_price', ascending=True
    )
    df = pd.concat([popular_events, rest_events])

    output_dir = '../results'
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f'{output_dir}/{ORIGIN}_trips.csv', index=False)
    print("Processing complete.")


if __name__ == "__main__":
    main()