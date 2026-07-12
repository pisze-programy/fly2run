# Fly2Run

Fly2Run is an automated system for finding the cheapest flight connections to running events and marathons in Europe. The system combines data about running events with flight information to provide users with cost-effective travel options.

## Overview

The project consists of several components that work together to gather, process, and present information about running events and affordable flight connections:

1. **Event Data Collection** - Scrapes running events from WorldsMarathons.com
2. **Flight Connection Data** - Loads flight connection data for Ryanair and WizzAir
3. **Flight Price Scraper** - Crawlers for fetching flight prices from Ryanair and WizzAir
4. **Trip Recommendation Engine** - Matches events with affordable flights and generates reports

### Scripts

- `scripts/get_running_events.py` - Collects running events data from WorldsMarathons.com
- `scripts/get_trip_deals.py` - Main engine that matches events with flight connections

### Scrapers

- `scrapers/ryanair.py` - Ryanair flight price scraper
- `scrapers/wizzair.py` - WizzAir flight price scraper

### Data Files

The project uses data stored in the `data/` directory:

- `running_events.json` - List of running events in Europe
- `ryanair_connections.json` - Flight connections for Ryanair
- `wizzair_connections.json` - Flight connections for WizzAir

## Usage

1. Run event collection script:
   ```bash
   python scripts/get_running_events.py
   ```

2. Run trip deal script (this will generate CSV reports in the `results/` directory):
   ```bash
   python scripts/get_trip_deals.py
   ```

## Output

The system generates CSV files in the `results/` directory containing the best flight deals for running events, including:
- Event information (name, location, date)
- Flight details (prices, departure and return dates)
- Popularity score of the event
- Total trip cost breakdown

## Requirements

- Python 3.6+
- Required packages: requests, pandas, geopy, tqdm, fake-useragent

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The system can be configured in `scripts/get_trip_deals.py`:

- `CONFIG['carrier']` - Choose between 'ryanair' and 'wizzair'
- `CONFIG['origin']` - Starting city (POZ, WAW, WMI, WRO, GDN, KRK, KTW)
- `CONFIG['MAX_DISTANCE_KM']` - Maximum distance in kilometers for event-airport matching

## Note

This project uses web scraping techniques to collect data from external sources. Please respect the terms of service of these websites and use this tool responsibly.

## License

This project is available under the MIT license.
