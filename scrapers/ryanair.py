import random
import requests
import time
from datetime import timedelta, datetime
from fake_useragent import UserAgent


class RyanairScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.cache = {}
        self.base_url = "https://www.ryanair.com/api/farfnd/v4/oneWayFares"

    def _get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.ryanair.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_fares(self, origin, dest, month):
        cache_key = f"{origin}_{dest}_{month}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        url = f"{self.base_url}/{origin}/{dest}/cheapestPerDay"
        params = {'outboundMonthOfDate': month, 'currency': 'PLN'}

        try:
            resp = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
            resp.raise_for_status()
            data = resp.json()

            fares = {f['day']: f for f in data['outbound']['fares'] if f.get('price')}
            self.cache[cache_key] = fares
            return fares
        except Exception as e:
            print(f"Error fetching fares for {origin}-{dest}: {e}")
            return {}

    def find_best_trip(self, event_date_str, origin, dest):
        event_date = datetime.strptime(event_date_str.split('T')[0], '%Y-%m-%d')
        month = event_date.strftime('%Y-%m-01')
        out_fares = self.get_fares(origin, dest, month)
        ret_fares = self.get_fares(dest, origin, month)
        time.sleep(random.uniform(0.2, 0.8))

        best_total = float('inf')
        best_option = None

        for i in range(0, 3):
            out_d = (event_date - timedelta(days=i)).strftime('%Y-%m-%d')
            for j in range(1, 4):
                ret_d = (event_date + timedelta(days=j)).strftime('%Y-%m-%d')

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