import os
from datetime import datetime, timedelta
from time import sleep

import httpx

database = {"movie_list": []}

# Creating date strings for today's date, and 100 days from that date into the past and future.
today = datetime.now()
now_showing_range = (today - timedelta(days=100)).strftime("%Y-%m-%d")
coming_soon_range = (today + timedelta(days=100)).strftime("%Y-%m-%d")

api_key = os.environ.get("TMDB_API_KEY")
base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"
query = f"&sort_by=popularity.desc&region=AU&include_adult=false&include_video=false&primary_release_date.gte={now_showing_range}&primary_release_date.lte={coming_soon_range}&with_release_type=3%7C2&with_original_language=en"

with httpx.Client() as client:

    def fetcher(page_key=1):

        try:
            response = client.get(f"{base_url}{query}&page={page_key}")
            response.raise_for_status()
            print(response.url)
        except:
            # TODO: Add logging function
            raise
        else:
            data = response.json()
            total_pages = data["total_pages"]
            print(f"Page {page_key}/{total_pages}")
            for movie in data["results"]:
                # If the movie has a backdrop, poster, and popularity greater than 5, it adds the movie to the movie list and prints the title.
                release_date = datetime.strptime(
                    movie["release_date"], "%Y-%m-%d"
                ).date()
                if movie["backdrop_path"] != None and movie["poster_path"] != None:
                    if (
                        release_date <= today.date()
                        and movie["vote_average"] >= 6
                        and movie["vote_count"] >= 60
                    ):
                        movie["released"] = True
                        database["movie_list"].append(movie)
                        print(
                            f"Adding: {movie['title']} - Release Date: {release_date}"
                        )
                    elif release_date >= today.date() and movie["popularity"] >= 3:
                        movie["released"] = False
                        database["movie_list"].append(movie)
                        print(
                            f"Adding: {movie['title']} - Release Date: {release_date}"
                        )

            if page_key < total_pages:
                page_key += 1
                sleep(0.2)
                fetcher(page_key)

    fetcher()
    database["date_created"] = today.strftime("%d-%m-%Y %H:%M:%S")

print(f"{database} total: {len(database['movie_list'])}")
