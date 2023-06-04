"""
Data fetching function to create a dummy database for the MovieLand Cinemas website.
Fetches data about movies from TMDB API - https://www.themoviedb.org/documentation/api

By default, it fetches data for the AU REGION as the data for releases in NZ is limited.
This can be changed with the "TMDB_REGION" environment variable.

Requires:
    TMDB API key, stored as an environment variable
    HTTPX Python library - https://www.python-httpx.org/
"""

import os
from datetime import datetime, timedelta
from time import sleep

import httpx

from _utils import fetcher, movie_constructor

# Create date object for today's date, and date strings for 100 days before and after that date.
today = datetime.now()
now_showing_range = (today - timedelta(days=100)).strftime("%Y-%m-%d")
coming_soon_range = (today + timedelta(days=100)).strftime("%Y-%m-%d")

# Set the TMDB API key in environment variables
API_KEY = f"?api_key={os.environ.get('TMDB_API_KEY')}"

# Set the TMDB REGION in environment variables
# This parameter is expected to be an ISO 3166-1 code - https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
REGION = os.environ.get("TMDB_REGION")
BASE_URL = "https://api.themoviedb.org/3/"
DISCOVER_URL = f"discover/movie{API_KEY}"
MAIN_QUERY = f"&sort_by=popularity.desc&region={REGION}&include_adult=false&include_video=false&primary_release_date.gte={now_showing_range}&primary_release_date.lte={coming_soon_range}&with_release_type=3%7C2&with_original_language=en"

database = {"movie_list": []}

with httpx.Client() as client:

    def get_movies(page_key=1):
        """
        Fetches the data from the TMDB API for each page of results, checks each movie has a backdrop and poster,
        if the movie has an IMDB ID, fetches more data about the movie, and then adds it to the database.

        :param page_key: The page number of the API call, defaults to 1 (optional)
        """
        data = fetcher(f"{BASE_URL}{DISCOVER_URL}{MAIN_QUERY}&page={page_key}", client)
        total_pages = data["total_pages"]
        print(f"Page {page_key}/{total_pages}")

        for movie in data["results"]:
            movie_id = movie["id"]
            MOVIE_URL = f"movie/{movie_id}{API_KEY}"
            MOVIE_QUERY = (
                "&language=en-US&append_to_response=release_dates,videos,credits"
            )
            if movie["backdrop_path"] != None and movie["poster_path"] != None:
                movie_details = fetcher(
                    f"{BASE_URL}{MOVIE_URL}{MOVIE_QUERY}",
                    client,
                )
                if (
                    movie_details["status"] == "Released"
                    # Checking for an IMDB ID can help with filtering out unwanted movies
                    and movie_details["imdb_id"] != None
                    # Some extra options to filter out movies with low TMDB user ratings
                    and movie_details["vote_average"] >= 5
                    # and movie_details["vote_count"] >= 50
                    and movie["popularity"] >= 5
                ):
                    print(f"Adding: [{movie_details['id']}] - {movie_details['title']}")
                    database["movie_list"].append(movie_constructor(movie_details))
                elif (
                    movie_details["status"] != "Released"
                    and movie_details["imdb_id"] != None
                    and movie["popularity"] >= 5
                ):
                    print(f"Adding: [{movie_details['id']}] - {movie_details['title']}")
                    database["movie_list"].append(movie_constructor(movie_details))
                else:
                    print("Discarding...")
                sleep(0.2)
        # Cycle through all the query result pages
        if page_key < total_pages:
            page_key += 1
            sleep(0.2)
            get_movies(page_key)
        else:
            print("Fetching complete.")

    get_movies()
    # Add timestamp to the database dictionary
    database["date_created"] = today.strftime("%d-%m-%Y %H:%M:%S")

print(f"Movies in Database: {len(database['movie_list'])}")
