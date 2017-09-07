import feedparser
from flask import Flask
from flask import render_template

app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn':'http://rss.cnn.com/rss/edition.rss',
              'fox':'http://feeds.foxnews.com/foxnews/latest',
                'iol':'http://www.iol.co.za/cmlink/1.640'}


@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article=feed['entries'][0]
    return render_template("home.html", article=first_article)

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
