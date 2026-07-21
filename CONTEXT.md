## Project Overview
[About project](./README.md)

## Facebook Groups
- [Departure City] - each group represents a separate city in Poland (Poz, WWA, WRO, KTW, KRK, GDA)
- Posts published both in the group and on the FB profile page

## Current State
- Working scraper for flights per [Departure City], plus all available running events (including distance, location, and time)
- Ready-to-use CSV files with connections and prices
- Missing: updating only the CSV without re-scraping all running events from scratch - optimization needed (flight data refresh)
- Adding an "already_posted" column with date and price to the CSV file

### CSV Files (in ./results/)
| City | File(s) |
|------|---------|
| GDN | ryanair_GDN_trips.csv |
| KRK | ryanair_KRK_trips.csv |
| KTW | ryanair_KTW_trips.csv |
| POZ | ryanair_POZ_trips.csv |
| WWA | ryanair_WAW_trips.csv & ryanair_WMI_trips.csv |
| WRO | ryanair_WRO_trips.csv |

### CSV Structure
`event_id, event_distance, event_price, event_price_currency, event_date, event_location`

**Example:**
`TCS Lidingöloppet, 30km, 22.55, eur, 2026-09-26T22:00:00, Lidingö:Sweden`

## Project Goal
Maintain up-to-date pricing data.

## Known Issues
- IP blocking during flight scraping (proxy is costly)

## TODO
1. Add starting coordinates to the CSV
2. Build a website based on the CSV (as an HTML table)
3. Build a Home page with a breakdown per departure city
4. Build an accordion with a vertical timeline per event:
    - Departure location (price, date, and time + link)
    - Public transport (Google Maps link?) (date and time)
    - Hotel selection-cheapest and closest to the start location (price + booking.com links)
    - Return flight (price, date and time, link)
5. Daily generated FB post files created by an agent:
    - Agent checks offers on each run and selects X offers per post
    - Agent collects hotel prices ("from X")
    - Agent creates a post-file with X offers, ready to paste directly into the group and onto the running profile's wall
    - Agent generates/selects an image for the post (posts with an image get better reach on FB)
    - Rule: 1 post per day per city containing three offers as a roundup
6. Manually open the file per day/city and create the FB post

## Duplicate Handling Logic
- If an offer was already posted and the price dropped → treat as new "hot content" (post type: "Price dropped by X!") - even better content than a brand-new offer
- If the price increased → don't repost (no one wants to read "more expensive than before"), unless the event date is close, and it's one of the last chances
- If the price is unchanged → cooldown; don't repeat the same offer for at least 14 days

## My Role as Admin
- Run the AI agent, which opens the files, selects three offers for today per city, fills in missing prices and links, and produces a ready-to-use file for me
- I manually paste the ready file onto FB

## Agent Role
Described in the TODO section.
