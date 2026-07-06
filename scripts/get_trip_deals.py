import json
import os
import pandas as pd
import random
import requests
import sys
import time
from datetime import datetime, timedelta
from fake_useragent import UserAgent
from geopy.distance import geodesic
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.wizzair import WizzairScraper
from scrapers.ryanair import RyanairScraper


# Global Config
ORIGIN = 'POZ' # POZ WAW/WMI WRO GDN KRK KTW
MAX_DISTANCE_KM = 50

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

def process_trips(events, connections, scraper):
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

    for event in tqdm(events, desc="Processing events"):
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
                event_date_str = event.get('dateNextRace')
                trip = scraper.find_best_trip(event_date_str, ORIGIN, dest_code)

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
    carrier = 'ryanair'
    scraper = RyanairScraper()

    df = process_trips(events, connections, scraper)

    popular_events = df[df['popularity_score'] > 20].sort_values(
        by=['total_trip_price'], ascending=True
    )
    rest_events = df[df['popularity_score'] <= 20].sort_values(
        by='total_trip_price', ascending=True
    )
    df = pd.concat([popular_events, rest_events])

    output_dir = '../results'
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f'{output_dir}/{carrier}_{ORIGIN}_trips.csv', index=False)
    print("Processing complete.")


if __name__ == "__main__":
    main()