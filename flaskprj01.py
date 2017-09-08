import json
import urllib2
import urllib
import feedparser
from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn':'http://rss.cnn.com/rss/edition.rss',
              'fox':'http://feeds.foxnews.com/foxnews/latest',
                'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
            'city':'Belize,bz'}

@app.route("/")
def home():

    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS['publication']
    articles= get_news(publication)
    #get cust weather based on user input or default
    city = request.args.get('city')
    if not city :
        city = DEFAULTS['city']
    weather = get_weather(city)
    return render_template("home.html",articles=articles,weather=weather)


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=f47aeab3995ca500141e77a82f634ba6"
    query = urllib.quote(query)
    url = api_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"],
                   "temperature":parsed["main"]["temp"],
                   "city":parsed["name"]}
    return weather


if __name__ == '__main__':
    app.run()



##Version 1
# import feedparser
# from flask import Flask
#
# app = Flask(__name__)
#
#
# BBC_FEED = "http://feeds.bbci.co.uk/news/rss.xml"
#
# @app.route('/')
# def get_news():
#     feed = feedparser.parse(BBC_FEED)
#     first_article = feed['entries'][0]
#     return """
#     <html>
#     <body>
#     <h1>BBC Headlines</h1>
#     <b>{0}</b><br/>
#     <i>{1}</i><br/>
#     <p>{2}</p><br/>
#     </body>
#     <html>
#     """.format(first_article.get("title"),first_article.get("published"),first_article.get("summary"))
#
# if __name__ == '__main__':
#     app.run()

#Version2
# @app.route("/")
# @app.route("/<publication>")
# def get_news(publication="bbc"):
#     feed = feedparser.parse(RSS_FEEDS[publication])
#     first_article=feed['entries'][0]
#     return """
#     <html>
#     <body>
#     <h1>Headlines</h1>
#     <b>{0}</b><br/>
#     <i>{1}</i><br/>
#     <p>{2}</p><br/>
#     </body>
#     </html>
#     """.format(first_article.get("title"),first_article.get("published"),first_article.get("summary"))
