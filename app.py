import json
import os
import re
from datetime import datetime
import tweepy
from flask import Flask, jsonify, redirect, render_template, request, session
import weirdsort
import secretz

app = Flask(__name__)

app.secret_key = secretz.FLASK_SECRET

CONSUMER_KEY = secretz.TWITTER_CONSUMER_KEY
CONSUMER_SECRET = secretz.TWITTER_CONSUMER_SECRET


@app.route("/")
def index():
    return render_template("about.html")


@app.route("/home")
def home():
    if not authed():
        return redirect("/auth")

    return render_template("index_vue.html")


@app.route("/tweets")
def tweets():
    testing = request.args.get("testing", "false")
    try:
        tweets = get_tweets(testing=testing)
        tweets = [serialize_tweet(t) for t in tweets]
        return jsonify(tweets)
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not fetch tweets"})


@app.route("/auth")
def auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, get_callback_url())
    url = auth.get_authorization_url()
    session["request_token"] = auth.request_token["oauth_token"]
    return redirect(url)


@app.route("/callback")
def twitter_callback():
    request_token = session["request_token"]
    del session["request_token"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, get_callback_url())
    verifier = request.args.get("oauth_verifier")
    auth.request_token = {"oauth_token": request_token, "oauth_token_secret": verifier}
    auth.get_access_token(verifier)
    session["token"] = (auth.access_token, auth.access_token_secret)

    return redirect("/home")


def authed():
    try:
        token, token_secret = session["token"]
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, get_callback_url())
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
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, get_callback_url())
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
        tweet.screen_name = tweet.original["user"]["screen_name"]
        tweet.name = tweet.original["user"]["name"]
        tweet.tweet_id = tweet.original["id_str"]

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
    del data["doc"]
    del data["original"]
    return data


def get_callback_url():
    return request.url_root + "callback"
