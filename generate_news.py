#!/usr/bin/env python3

import feedparser
import requests
import json
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
SUMMARY_SENTENCES = 3
OUTPUT_FILE = "news.json"

def fetch_feed(url):
    return feedparser.parse(url)

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def fetch_article_text(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return clean_html(resp.text)
    except Exception as e:
        print(f"Failed to fetch article: {e}")
        return ""

def summarize(text, n=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, n)
    return " ".join(str(s) for s in summary)

def generate_articles():
    feed = fetch_feed(RSS_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "No Title")
        link = entry.get("link", "")
        fallback_summary = entry.get("summary", "")

        full_text = fetch_article_text(link)
        content_to_summarize = full_text if len(full_text) > 500 else fallback_summary

        try:
            summary = summarize(content_to_summarize, SUMMARY_SENTENCES)
        except:
            summary = fallback_summary

        articles.append({
            "title": title,
            "link": link,
            "summary": summary.strip()
        })

    return articles

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    articles = generate_articles()
    save_to_json(articles, OUTPUT_FILE)
    print(f"✅ Saved {len(articles)} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
