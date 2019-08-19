import json
import os
from datetime import datetime
import re

# import analyzers
import weirdsort
import tweepy
from flask import Flask, jsonify, redirect, render_template, request, session

app = Flask(__name__)

app.secret_key = os.environ["FLASK_SECRET"]

CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
CALLBACK_URL = "http://localhost:5000/callback"

sorts = [
    {"qs": "chronological", "key": "created_at", "display": "Chronologically"},
    {"qs": "alphabetical", "key": "lower_text", "display": "Alphabetically"},
    {"qs": "favorites", "key": "favorites", "display": "Total Favorites"},
    {"qs": "retweets", "key": "retweets", "display": "Total Retweets"},
    {"qs": "length", "key": "length", "display": "Length"},
    {"qs": "hashtags", "key": "total_hashtags", "display": "Total Hashtags"},
    {"qs": "username", "key": "username", "display": "Alphabetically by Username"},
    {"qs": "userposts", "key": "total_userposts", "display": "Total User Posts"},
    {"qs": "marx", "key": "marx", "display": "Most Marxist"},
    {"qs": "kafka", "key": "kafka", "display": "Most Kafkaesque"},
    {"qs": "shame", "key": "shame", "display": "Shame"},
    {"qs": "ted", "key": "ted", "display": "TEDness"},
    {"qs": "emoji", "key": "total_emoji", "display": "Total Emoji"},
    {"qs": "nouns", "key": "total_noun", "display": "Noun Density"},
    {"qs": "verbs", "key": "total_verb", "display": "Verb Density"},
    {"qs": "adjectives", "key": "total_adj", "display": "Adjective Density"},
    {"qs": "numbers", "key": "total_num", "display": "Number of Numbers"},
    {
        "qs": "stop_words",
        "key": "total_stop",
        "display": "Density of Filler Words/Percentage of Words Which Are Filler Words",
    },
    {"qs": "named_entities", "key": "total_entities", "display": "Proper Noun Density"},
    {"qs": "antisemitism", "key": "antisemitism", "display": "Antisemitism"},
    {"qs": "eroticism", "key": "erotic", "display": "Eroticism"},
    # {
    #     "qs": "word_length",
    #     "key": "word_length",
    #     "display": "Average Word Length",
    # },
    {"qs": "drilism", "key": "__label__dril", "display": "dril-ism"},
    {"qs": "cop", "key": ["__label__CommissBratton"], "display": "Cop-Like"},
    {"qs": "goth", "key": "__label__sosadtoday", "display": "Gothness"},
    {
        "qs": "neoliberal",
        "key": ["__label__ThirdWayTweet", "__label__ChelseaClinton"],
        "display": "Neoliberalism",
    },
    {
        "qs": "advertising",
        "key": ["__label__amazon"],
        "display": "Similarity To Corporate Social Media Accounts",
    },
    {"qs": "gendered", "key": "total_gendered", "display": "Gendered"},
]


@app.route("/")
def home():
    if not authed():
        return redirect("/auth")

    return render_template("index_vue.html")

    # testing = request.args.get("testing", "false")
    # tweets = get_tweets(testing=testing)
    #
    # reverse = request.args.get("reverse", "false") == "true"
    # sorter = request.args.get("sort", "chronological")
    #
    # tweets = sort_tweets(tweets, sorter, reverse)
    #
    # # return jsonify(tweets)
    # return render_template(
    #     "index.html",
    #     tweets=tweets,
    #     reverse=reverse,
    #     sorter=sorter,
    #     testing=testing,
    #     sorts=sorts,
    # )


@app.route("/tweets")
def tweets():
    testing = request.args.get("testing", "false")
    tweets = get_tweets(testing=testing)
    tweets = [serialize_tweet(t) for t in tweets]
    return jsonify(tweets)
    # try:
    #     tweets = get_tweets(testing=testing)
    #     tweets = [t.__dict__ for t in tweets]
    #     return jsonify(tweets)
    # except Exception as e:
    #     return jsonify({"error": "Could not fetch tweets"})


@app.route("/auth")
def auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    url = auth.get_authorization_url()
    session["request_token"] = auth.request_token["oauth_token"]
    return redirect(url)


@app.route("/callback")
def twitter_callback():
    request_token = session["request_token"]
    del session["request_token"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    verifier = request.args.get("oauth_verifier")
    auth.request_token = {"oauth_token": request_token, "oauth_token_secret": verifier}
    auth.get_access_token(verifier)
    session["token"] = (auth.access_token, auth.access_token_secret)

    return redirect("/")

def authed():
    try:
        token, token_secret = session["token"]
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth)
        return api.me()
    except Exception as e:
        return False

def get_tweets(testing=False):
    if testing == "true":
        with open("sample_tweets.json", "r") as infile:
            tweets = json.load(infile)
    else:
        token, token_secret = session["token"]
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth)

        tweets = []

        # for status in tweepy.Cursor(api.home_timeline, tweet_mode="extended", count=200).items(400):
        #     tweets.append(status._json)
        # print("TOTAL", len(tweets))
        tweets = api.home_timeline(count=200, tweet_mode="extended")
        tweets = [t._json for t in tweets]

    tweets = weirdsort.analyze_lines(tweets, textkey="full_text")

    for tweet in tweets:
        dt = datetime.strptime(tweet.original["created_at"], "%a %b %d %H:%M:%S %z %Y")
        tweet.created_at = dt.strftime("%m/%d/%y %H:%M:%S")
        tweet.favorites = tweet.original["favorite_count"]
        tweet.retweets = tweet.original["retweet_count"]
        tweet.username = tweet.original["user"]["name"]
        tweet.total_userposts = tweet.original["user"]["statuses_count"]

    return tweets


def sort_tweets(tweets, sorter, reverse):
    sort_params = next((s for s in sorts if s["qs"] == sorter), sorts[0])

    if isinstance(sort_params["key"], list):
        tweets = sorted(
            tweets,
            key=lambda k: sum([getattr(k, keyname) for keyname in sort_params["key"]]),
            reverse=reverse,
        )
    else:
        tweets = sorted(
            tweets, key=lambda k: getattr(k, sort_params["key"]), reverse=reverse
        )

    return tweets


def serialize_tweet(tweet):
    data = tweet.__dict__
    data["media"] = data["original"].get("extended_entities", {}).get("media", [])
    data["screen_name"] = data["original"]["user"]["screen_name"]
    data["name"] = data["original"]["user"]["name"]
    data["tweet_id"] = data["original"]["id"]
    del data["doc"]
    del data["original"]
    return data

