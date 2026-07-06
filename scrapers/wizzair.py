import json
import random
import requests
import time
from datetime import datetime, timedelta
from fake_useragent import UserAgent


class WizzairScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.get("https://www.wizzair.com/")

        self.version = "29.5.0"
        self.base_url = f"https://be.wizzair.com/{self.version}/Api/asset/farechart"
        self.session.headers.update({
            'User-Agent': self.ua.random,
            "Content-Type": "application/json",
            "Origin": "https://www.wizzair.com"
        })

    def get_fare_chart(self, origin, destination, date_str):
        clean_date = str(date_str).split('T')[0]
        event_dt = datetime.strptime(clean_date, '%Y-%m-%d')
        return_date = (event_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        token = self.session.cookies.get('RequestVerificationToken')

        headers = {
            "Referer": f"https://www.wizzair.com/en-gb/booking/select-flight/{origin}/{destination}/{clean_date}/{return_date}/1/0/0/null",
            "X-RequestVerificationToken": token if token else ""
        }
        payload = {
            "isRescueFare": False,
            "adultCount": 1,
            "childCount": 0,
            "dayInterval": 9,
            "wdc": False,
            "isFlightChange": False,
            "flightList": [
                {"departureStation": origin, "arrivalStation": destination, "date": clean_date},
                {"departureStation": destination, "arrivalStation": origin, "date": f"{return_date}T00:00:00"}
            ]
        }

        try:
            self.session.headers.update(headers)
            response = self.session.post(self.base_url, json=payload, timeout=10)
            print(f"Status: {response.status_code}, URL: {self.base_url}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"WizzAir FareChart Error: {e}")
            return None

    def find_best_trip(self, event_date_str, origin, dest):
        self.session = requests.Session()
        event_date = datetime.strptime(event_date_str.split('T')[0], '%Y-%m-%d')
        data = self.get_fare_chart(origin, dest, event_date_str)
        time.sleep(random.uniform(0.2, 0.8))

        if not data:
            return None

        out_flights = [f for f in data.get('outboundFlights', []) if f['priceType'] == 'price']
        ret_flights = [f for f in data.get('returnFlights', []) if f['priceType'] == 'price']

        best_total = float('inf')
        best_option = None

        for out in out_flights:
            out_d = datetime.strptime(out['date'][:10], '%Y-%m-%d')

            if not (event_date - timedelta(days=3) <= out_d < event_date):
                continue

            for ret in ret_flights:
                ret_d = datetime.strptime(ret['date'][:10], '%Y-%m-%d')

                if not (event_date <= ret_d <= event_date + timedelta(days=4)):
                    continue

                total = out['price']['amount'] + ret['price']['amount']
                if total < best_total:
                    best_total = total
                    best_option = {
                        'price': total,
                        'out_time': out['date'],
                        'ret_time': ret['date']
                    }

        return best_option