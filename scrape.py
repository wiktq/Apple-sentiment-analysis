import asyncio
import csv
import logging
import random
import json
from twikit import Client, TooManyRequests
from datetime import datetime
from typing import List, Tuple, Optional
from credentials import (
    RAW_DIR,
    COOKIES_FILE,
    RESUME_FILE,
    TWITTER_USERNAME,
    TWITTER_EMAIL,
    TWITTER_PASSWORD,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set minimum value of tweets you want to get per query
MINIMUM_TWEETS = 500  

# List of dates with 7-day range before and after
DATES = [
    ("2011-08-17", "2011-08-31", "aug_24_2011.csv", ["Apple"]),
    ("2010-01-20", "2010-02-03", "jan_27_2010.csv", ["Apple"]),
    ("2014-08-24", "2014-09-07", "aug_31_2014.csv", ["Apple"]),
    ("2010-02-26", "2010-03-12", "mar_5_2010.csv", ["Apple"]),
    ("2011-07-27", "2011-08-11", "aug_3_2011.csv", ["Apple"]),
    ("2014-05-05", "2014-05-19", "may_12_2014.csv", ["Apple"]),
]
async def get_tweets(client: Client, query: str, tweets: Optional[object]) -> object:
    if tweets is None:
        logging.info(f"Getting tweets for query: {query}")
        tweets = await client.search_tweet(query, product="Latest")
    else:
        wait_time = random.randint(5, 25)
        logging.info(
            f"Getting next tweets for query: {query} after {wait_time} seconds"
        )
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets


async def scrape_tweets(query: str, filename: str, start_date: str, end_date: str) -> None:
    client = Client(language="en-US")
    await client.login(
        auth_info_1=TWITTER_USERNAME,
        auth_info_2=TWITTER_EMAIL,
        password=TWITTER_PASSWORD,
    )
    client.save_cookies(str(COOKIES_FILE))

    tweet_count = 0
    tweets = None

    full_path = RAW_DIR / filename

    if RESUME_FILE.exists():
        with RESUME_FILE.open("r") as f:
            resume_state = json.load(f)
        if resume_state["query"] == query:
            tweet_count = resume_state["tweet_count"]
            logging.info(f"Resuming scraping for {query} from tweet {tweet_count}")

    with full_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if tweet_count == 0:
            writer.writerow(["Tweet_Count", "Query", "Text", "Created_At"])

        while tweet_count < MINIMUM_TWEETS:
            try:
                query_with_date = f"{query} lang:en since:{start_date} until:{end_date}"
                tweets = await get_tweets(client, query_with_date, tweets)
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                logging.warning(f"Rate limit reached. Waiting until {rate_limit_reset}")
                wait_time = (rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                logging.error(f"Error fetching tweets: {str(e)}")
                await asyncio.sleep(60)
                continue

            if not tweets:
                logging.info(f"No more tweets found for query: {query}")
                break

            for tweet in tweets:
                tweet_text = tweet.text.lower()  # Convert to lowercase for easier comparison

                # Define words to exclude tweets related to fruit, juice, and other possible spam
                exclude_words = ["fruit", "juice", "tree", "pie", "cider", "orchard", "win", "free", "cinnamon", "caramel", "eat", "eating", "meal", "recipe", "dessert", "picking", "giveaway", "jack", "taste", "wood", "shabby", "slice", "bees", "banana", "ate", "cake", "viral", "sour", "flavor"]

                # Only save tweets about the company, excluding tweets with queries included above
                if "apple" in tweet_text and not any(exclude in tweet_text for exclude in exclude_words):
                    tweet_count += 1
                    tweet_data = [
                        tweet_count,
                        query,
                        tweet.text,
                        tweet.created_at,
                    ]
                    writer.writerow(tweet_data)

            logging.info(f"Got {tweet_count} tweets for query: {query}")

            with RESUME_FILE.open("w") as f:
                json.dump({"query": query, "tweet_count": tweet_count}, f)

    logging.info(f"Done for query: {query}. {tweet_count} tweets found")
    RESUME_FILE.unlink(missing_ok=True)

    await asyncio.sleep(15)


async def main():
    for start_date, end_date, filename, queries in DATES:
        for query in queries:
            await scrape_tweets(query, filename, start_date, end_date)


if __name__ == "__main__":
    asyncio.run(main())
