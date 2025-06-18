#!/usr/bin/env python3
"""
nyt_rss_summarizer.py

Fetches the NYT Home Page RSS feed and prints out short article summaries.
"""

import feedparser
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
SUMMARY_SENTENCES = 3  # adjust for desired brevity

def fetch_feed(url: str):
    return feedparser.parse(url)

def fetch_full_article(url: str):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        # Strip HTML tags crudely—better to use BeautifulSoup if needed
        text = resp.text
        # A crude fallback: split on paragraphs
        return "\n".join(text.split("<p>")[1:6])  # get first few paragraphs
    except Exception as e:
        print(f"⚠️ Could not fetch full text for {url}: {e}")
        return ""

def summarize_text(text: str, num_sentences: int = 3) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

def generate_articles(feed):
    articles = []
    for entry in feed.entries:
        title = entry.get("title", "No title")
        link = entry.get("link", "No link")
        summary = entry.get("summary", "")

        text_source = summary
        if link:
            full_text = fetch_full_article(link)
            if len(full_text) > 200:  # only override if full text seems substantial
                text_source = full_text
        
        succinct = summarize_text(text_source, SUMMARY_SENTENCES)
        articles.append({
            "title": title,
            "link": link,
            "summary": succinct
        })
    return articles

def main():
    feed = fetch_feed(RSS_URL)
    articles = generate_articles(feed)
    for art in articles:
        print("=" * 80)
        print(f"📰 {art['title']}\nLink: {art['link']}\n")
        print(f"{art['summary']}\n")

if __name__ == "__main__":
    main()
