import datetime
import json
import os
from urllib.request import urlopen
from urllib.parse import quote

from dotenv import load_dotenv
import feedparser
from flask import Flask, make_response, render_template, request

# Load environment variables
load_dotenv()

# Constants
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={{}}&units=metric&APPID={WEATHER_API_KEY}"

DEFAULTS = {
  'publication': 'breaking-belize-news',
  'city': 'Belize,bz',
  'currency_from': 'BZD',
  'currency_to': 'USD'
}

RSS_FEEDS = {'breaking-belize-news': 'https://www.breakingbelizenews.com/feed/',
             'channel-7':'http://www.7newsbelize.com/rss.php',
	         'channel-5':'https://edition.channel5belize.com/feed',
             'love-news': 'http://lovefm.com/feed/',
             'amandala': 'http://amandala.com.bz/news/feed/',
             'san-pedro-sun': 'https://www.sanpedrosun.com/feed/',
             'reporter': 'http://www.reporter.bz/feed/',
             'mybelize': 'http://www.mybelize.net/feed/'}
app = Flask(__name__)


def get_news(publication):
  """Fetch news for a specific publication."""
  feed = feedparser.parse(RSS_FEEDS.get(publication, DEFAULTS["publication"]))
  return feed['entries']


def get_weather(city):
  """Fetch weather information for a specific city."""
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
        "country": parsed['sys']['country']
      }
  except Exception as e:
    print(f"Error fetching weather: {e}")
  return {}


@app.route("/")
def home():
  """Home route to display news and weather."""
  publication = get_value_with_fallback("publication")
  city = get_value_with_fallback("city")

  articles = get_news(publication)
  weather = get_weather(city)

  response = make_response(render_template(
    "home.html", articles=articles, weather=weather, options=RSS_FEEDS, publication=publication
  ))
  expires = datetime.datetime.now() + datetime.timedelta(days=365)
  response.set_cookie("publication", publication, expires=expires)
  response.set_cookie("city", city, expires=expires)
  return response


def get_value_with_fallback(key):
  """Get value from request args, cookies or defaults."""
  return request.args.get(key) or request.cookies.get(key) or DEFAULTS[key]


if __name__ == '__main__':
  app.run()
