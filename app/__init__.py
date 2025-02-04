import datetime
import json
import os
from traceback import print_tb
from urllib.request import urlopen
from urllib.parse import quote

import feedparser
from dotenv import load_dotenv
from flask import Flask, request, render_template, make_response, jsonify

load_dotenv()

app = Flask(__name__)

# Environment / config
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={{}}&units=metric&APPID={WEATHER_API_KEY}"

# RSS feeds dictionary
RSS_FEEDS = {
  'breaking-belize-news': 'https://www.breakingbelizenews.com/feed/',
  'channel-7': 'http://www.7newsbelize.com/rss.php',
  'channel-5': 'https://edition.channel5belize.com/feed',
  'love-news': 'http://lovefm.com/feed/',
  'amandala': 'http://amandala.com.bz/news/feed/',
  'san-pedro-sun': 'https://www.sanpedrosun.com/feed/',
  'reporter': 'http://www.reporter.bz/feed/',
  'mybelize': 'http://www.mybelize.net/feed/',
  'national-perspective': 'https://nationalperspectivebz.com/aggregator/rss/',
}

READABLE_NAMES = {
    'breaking-belize-news': 'Breaking Belize News',
    'channel-7': 'Channel 7 News',
    'channel-5': 'Channel 5 News',
    'love-news': 'Love News',
    'amandala': 'Amandala',
    'san-pedro-sun': 'San Pedro Sun',
    'reporter': 'The Reporter',
    'mybelize': 'MyBelize',
    'national-perspective': 'National Perspective',
}

DEFAULTS = {
  'publication': 'all',  # Use "all" to fetch from all sources by default
  'city': 'Belize,bz',
}


def get_all_news():
  """
  Fetch news from ALL sources. Interleave them into a single list.
  Attempt to handle errors gracefully (logging them), and continue.
  """
  all_articles = []
  for source_name, feed_url in RSS_FEEDS.items():
    try:
      feed = feedparser.parse(feed_url)
      # feedparser sets 'bozo' if there's a parsing error
      if feed.bozo:
        print(f"[ERROR] Problem parsing {source_name}: {feed.bozo_exception}")
      else:
        all_articles.extend(feed.entries)
    except Exception as e:
      print(f"[ERROR] Failed to fetch feed for {source_name}: {e}")
  # Optional: sort the aggregated list by 'published_parsed' if available
  # This ensures the "interleaving" is chronological from all feeds.
  all_articles.sort(key=lambda x: x.get('published_parsed', None), reverse=True)
  return all_articles


def get_news(publication):
  """
  Fetch news for a specific publication.
  Fallback to default publication if missing.
  """
  all_articles = []

  feed_url = RSS_FEEDS.get(publication)
  print(f"Fetching {publication} from {feed_url}")
  if not feed_url:
    # If somehow invalid publication, return all or fallback.
    return get_all_news()

  try:
    feed = feedparser.parse(feed_url)
    if feed.bozo:
      print(f"[ERROR] Problem parsing {publication}: {feed.bozo_exception}")
      return []
    return feed.entries
  except Exception as e:
    print(f"[ERROR] Exception fetching {publication}: {e}")
    return []


def get_weather(city):
  """
  Fetch weather information for a specific city.
  Return a dict with keys: description, temperature, city, country
  If there's an error, returns {}.
  """
  query = quote(city)
  url = WEATHER_URL.format(query)
  try:
    data = urlopen(url).read()
    parsed = json.loads(data)
    if parsed.get("weather"):
      return {
        "description": parsed["weather"][0]["description"],
        "temperature": parsed["main"]["temp"],
        "city": parsed["name"],
        "country": parsed["sys"]["country"]
      }
  except Exception as e:
    print(f"[ERROR] Error fetching weather: {e}")
  return {}


def get_value_with_fallback(key):
  """
  Get a value from request args, cookies, or fallback to DEFAULTS.
  """
  return request.args.get(key) or request.cookies.get(key) or DEFAULTS[key]


@app.route("/")
def home():
  """
  Main route: show the entire page (weather + news).
  By default, fetch all news. If a publication is selected, fetch that feed.
  """
  publication = get_value_with_fallback("publication")
  city = get_value_with_fallback("city")

  # Decide if we fetch ALL or single publication
  if publication == "all":
    articles = get_all_news()
    pub_display = "All Belize Sources"
  else:
    articles = get_news(publication)
    pub_display = publication

  weather = get_weather(city)

  # Prepare response with cookies
  response = make_response(render_template(
    "home.html",
    articles=articles,
    weather=weather,
    options=RSS_FEEDS,
    readable_names=READABLE_NAMES,
    publication=pub_display
  ))
  # Set cookies to remember user selection for a year
  expires = datetime.datetime.now() + datetime.timedelta(days=365)
  response.set_cookie("publication", publication, expires=expires)
  response.set_cookie("city", city, expires=expires)
  return response


@app.route("/articles")
def articles_partial():
  """
  HTMX endpoint that returns only the articles section (HTML snippet).
  This allows the page to update <section> or <div> with new articles
  when user changes dropdown, without a full page refresh.
  """
  publication = request.args.get("publication", "all")
  if publication == "all":
    articles = get_all_news()
    pub_display = "All Belize Sources"
  else:
    print(f"Fetching {publication}")
    articles = get_news(publication)
    pub_display = publication

  return render_template("_articles_partial.html", articles=articles, publication=pub_display)


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0")
