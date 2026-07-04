import json
import os
import pandas as pd
from geopy.distance import geodesic

ORIGIN = 'POZ'
MAX_DISTANCE_KM = 50


def load_data():
    with open('../data/running_events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    with open('../data/ryanair_connections.json', 'r', encoding='utf-8') as f:
        connections = json.load(f)
    return events, connections


def get_nearest_airport_info(event_coords, airports_db):
    nearest_code = None
    min_dist = float('inf')

    for code, data in airports_db.items():
        coords = data.get('coordinates', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            dist = geodesic(event_coords, (lat, lon)).km
            if dist < min_dist:
                min_dist = dist
                nearest_code = code

    return nearest_code, min_dist


def has_route(origin_code, dest_code, airports_db):
    origin_data = airports_db.get(origin_code)
    if not origin_data:
        return False
    return f"airport:{dest_code}" in origin_data.get('routes', [])


def fetch_flight_price(origin, dest, date):
    return 0


def process_trips(events, connections):
    trips = []
    airports = {item['iataCode']: item for item in connections}

    for event in filter(lambda e: e.get('hasTickets') is not False, events):
        coords = event.get('startPoint')
        if not coords or len(coords) < 2:
            continue

        event_coords = (coords[1], coords[0])
        dest, dist = get_nearest_airport_info(event_coords, airports)

        if dest and dist <= MAX_DISTANCE_KM and has_route(ORIGIN, dest, airports):
            price = fetch_flight_price(ORIGIN, dest, event.get('dateNextRaceLocal'))

            trips.append({
                'event_name': event.get('title'),
                'city': event.get('city'),
                'event_date': event.get('dateNextRaceLocal'),
                'airport': dest,
                'distance': round(dist, 2),
                'flight_price': price
            })
    return pd.DataFrame(trips)


def main():
    events, connections = load_data()
    df = process_trips(events, connections)

    output_dir = '../results'
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f'{output_dir}/{ORIGIN}_trips.csv', index=False)
    print(f"Processing complete. Saved {len(df)} entries.")


if __name__ == "__main__":
    main()