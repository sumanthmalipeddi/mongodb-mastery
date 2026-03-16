"""
Advanced Web Scraper — Production-Grade Version
================================================
Enhanced scraper with: logging, rate limiting, retry logic, deduplication,
command-line arguments, data validation, and progress tracking.

Usage:
    python scraper_advanced.py
    python scraper_advanced.py --pages 5 --delay 2 --verbose
    python scraper_advanced.py --help
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pymongo import MongoClient, TEXT
from pymongo.errors import ConnectionFailure, BulkWriteError

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

BASE_URL = "http://quotes.toscrape.com"
DB_NAME = "quotes_db"
COLLECTION_NAME = "quotes"


# =========================================================================
# Logging Setup
# =========================================================================

def setup_logging(verbose=False):
    """Configure logging with appropriate level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


# =========================================================================
# HTTP Session with Retry Logic
# =========================================================================

def create_session(max_retries=3):
    """Create a requests session with automatic retry on failure."""
    session = requests.Session()

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "MongoDB-Learning-Scraper/1.0 (Educational Project)"
    })

    return session


# =========================================================================
# Data Validation
# =========================================================================

def validate_quote(quote_data):
    """Validate a scraped quote document before insertion."""
    errors = []

    if not quote_data.get("text") or len(quote_data["text"].strip()) == 0:
        errors.append("Empty quote text")
    if not quote_data.get("author") or len(quote_data["author"].strip()) == 0:
        errors.append("Empty author")
    if not isinstance(quote_data.get("tags"), list):
        errors.append("Tags must be a list")
    if not isinstance(quote_data.get("page_number"), int) or quote_data["page_number"] < 1:
        errors.append("Invalid page number")
    if not isinstance(quote_data.get("word_count"), int) or quote_data["word_count"] < 1:
        errors.append("Invalid word count")

    return errors


# =========================================================================
# MongoDB Connection
# =========================================================================

def connect_to_mongodb(logger):
    """Connect to MongoDB with error handling."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        logger.error("MONGODB_URI not found in .env file!")
        sys.exit(1)

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info("Connected to MongoDB")
        return client, client[DB_NAME][COLLECTION_NAME]
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        sys.exit(1)


# =========================================================================
# Scraping
# =========================================================================

def scrape_page(session, url, page_number, logger):
    """Scrape a single page and return list of quote documents."""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return [], None

    soup = BeautifulSoup(response.text, "lxml")
    quotes = []

    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").get_text().strip("\u201c\u201d")
        author = quote_div.find("small", class_="author").get_text()
        tags = [tag.get_text() for tag in quote_div.find_all("a", class_="tag")]

        quote_doc = {
            "text": text,
            "author": author,
            "tags": tags,
            "page_number": page_number,
            "source_url": url,
            "scraped_at": datetime.now(timezone.utc),
            "word_count": len(text.split())
        }

        # Validate before adding
        errors = validate_quote(quote_doc)
        if errors:
            logger.warning(f"Invalid quote skipped: {errors}")
            continue

        quotes.append(quote_doc)

    # Find next page URL
    next_button = soup.find("li", class_="next")
    next_url = BASE_URL + next_button.find("a")["href"] if next_button else None

    return quotes, next_url


def scrape_all(session, max_pages, delay, logger):
    """Scrape all pages with rate limiting and progress tracking."""
    all_quotes = []
    url = f"{BASE_URL}/page/1/"
    page_number = 1

    logger.info(f"Starting scrape (max_pages={max_pages}, delay={delay}s)")

    while url and page_number <= max_pages:
        # Progress indicator
        progress = f"[{page_number}/{max_pages}]" if max_pages < 100 else f"[page {page_number}]"
        logger.info(f"{progress} Scraping {url}")

        quotes, next_url = scrape_page(session, url, page_number, logger)
        all_quotes.extend(quotes)

        logger.debug(f"  Got {len(quotes)} quotes from page {page_number}")

        url = next_url
        page_number += 1

        # Rate limiting — be respectful
        if url:
            logger.debug(f"  Waiting {delay}s before next request...")
            time.sleep(delay)

    logger.info(f"Scraping complete: {len(all_quotes)} total quotes from {page_number - 1} pages")
    return all_quotes


# =========================================================================
# Storage with Deduplication
# =========================================================================

def store_quotes(collection, quotes, logger):
    """Store quotes with deduplication (skip existing quotes)."""
    # Create unique index on text + author to prevent duplicates
    collection.create_index([("text", 1), ("author", 1)], unique=True)

    new_count = 0
    skip_count = 0

    for quote in quotes:
        try:
            collection.insert_one(quote)
            new_count += 1
        except Exception:
            # Duplicate — already exists
            skip_count += 1

    logger.info(f"Storage: {new_count} new, {skip_count} duplicates skipped")

    # Create additional indexes
    collection.create_index("author")
    collection.create_index("tags")
    collection.create_index([("text", TEXT)])
    collection.create_index("page_number")
    logger.info("Indexes created")


# =========================================================================
# Main
# =========================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape quotes.toscrape.com and store in MongoDB"
    )
    parser.add_argument(
        "--pages", type=int, default=100,
        help="Maximum number of pages to scrape (default: 100 = all)"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--fresh", action="store_true",
        help="Drop existing collection before scraping"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logging(args.verbose)

    logger.info("=" * 50)
    logger.info("Advanced Web Scraper — Starting")
    logger.info("=" * 50)

    # Connect
    client, collection = connect_to_mongodb(logger)

    # Fresh start if requested
    if args.fresh:
        collection.drop()
        logger.info("Dropped existing collection")

    # Create HTTP session with retries
    session = create_session()

    # Scrape
    quotes = scrape_all(session, args.pages, args.delay, logger)

    if not quotes:
        logger.error("No quotes scraped!")
        client.close()
        sys.exit(1)

    # Store with deduplication
    store_quotes(collection, quotes, logger)

    # Summary
    total = collection.count_documents({})
    unique_authors = len(collection.distinct("author"))
    unique_tags = len(collection.distinct("tags"))

    logger.info("=" * 50)
    logger.info("Summary")
    logger.info(f"  Total quotes: {total}")
    logger.info(f"  Unique authors: {unique_authors}")
    logger.info(f"  Unique tags: {unique_tags}")
    logger.info("=" * 50)

    client.close()


if __name__ == "__main__":
    main()
