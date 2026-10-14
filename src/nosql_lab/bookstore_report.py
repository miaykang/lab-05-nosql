#!/usr/bin/env python3
"""Print a bookstore inventory report from MongoDB Atlas."""

import logging
import os
import sys

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Read Atlas credentials from the environment (do not hardcode).
MONGODB_ATLAS_URL = os.getenv("MONGODB_ATLAS_URL")
MONGODB_ATLAS_USER = os.getenv("MONGODB_ATLAS_USER")
MONGODB_ATLAS_PWD = os.getenv("MONGODB_ATLAS_PWD")


def main():
    """Connect to Atlas, join authors to books, and print the report."""
    if not all([MONGODB_ATLAS_URL, MONGODB_ATLAS_USER, MONGODB_ATLAS_PWD]):
        logging.error(
            "Set MONGODB_ATLAS_URL, MONGODB_ATLAS_USER, and MONGODB_ATLAS_PWD"
        )
        return 1

    client = None
    try:
        # Username and password must be passed here; they are not in the URL.
        client = MongoClient(
            MONGODB_ATLAS_URL,
            username=MONGODB_ATLAS_USER,
            password=MONGODB_ATLAS_PWD,
            appname="bookstore_report"
        )
        # Test the connection
        client.admin.command("ismaster")
        logging.info("Successfully connected to MongoDB Atlas.")

        db = client["bookstore"]
        authors_col = db["authors"]
        books_col = db["books"]

        # Includes loaded authors and the author added in bookstore.js step 7.
        target_author_ids = ["author_002", "author_003", "author_004"]

        author_count = authors_col.count_documents(
            {"_id": {"$in": target_author_ids}}
        )
        print(f"Authors: {author_count}\n")

        authors_cursor = authors_col.find({"_id": {"$in": target_author_ids}})
        for author in authors_cursor:
            print(author["name"])
            # Books whose author_ids list contains this author's _id.
            books_cursor = books_col.find({"author_ids": author["_id"]})
            for book in books_cursor:
                print(f"  {book['title']} ({book['published_year']})")
            print()

    except ConnectionFailure as e:
        logging.error("Failed to connect to MongoDB Atlas: %s", e)
        return 1
    except OperationFailure as e:
        logging.error("MongoDB operation failed: %s", e)
        return 1
    except Exception as e:
        logging.error("An error occurred: %s", e)
        return 1
    finally:
        if client is not None:
            client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
