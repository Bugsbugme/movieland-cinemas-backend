from datetime import datetime, timedelta
from time import sleep

import httpx
from decouple import config

# Setting the variable "timestamp" to the current date and time.
timestamp = datetime.now()

# Setting the variable "date_range" to a timedelta object with a value of 100 days.
date_range = timedelta(days=100)

# Converting the timestamp object to a string and then formatting it to the format "YYYY-MM-DD".
today = timestamp.strftime("%Y-%m-%d")

# Subtracting the value of the "date_range" variable from the "timestamp" variable and then formatting
# the result to the format "YYYY-MM-DD".
now_showing_range = (timestamp - date_range).strftime("%Y-%m-%d")

# Adding the value of the "date_range" variable to the "timestamp" variable and then formatting the
# result to the format "YYYY-MM-DD".
coming_soon_range = (timestamp + date_range).strftime("%Y-%m-%d")

# Getting the value of the TMDB_API_KEY environment variable and assigning it to the variable
# "api_key".
api_key = config("TMDB_API_KEY")

# Creating a variable called "base_url" and assigning it a string value. The string value is a url
# that is used to make requests to the TMDB API. The url contains a placeholder for the API key. The
# placeholder is replaced with the value of the "api_key" variable.
base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"

# Creating a list of dictionaries. Each dictionary contains a query string and a boolean value.
# The "released" property is attached to each movie and used by the front end.
query_list = [
    {
        # Query for Now Showing movies
        "query_string": f"&sort_by=popularity.desc&region=AU&include_adult=false&include_video=false&primary_release_date.gte={now_showing_range}&primary_release_date.lte={today}&with_release_type=3%7C2&vote_average.gte=6&vote_count.gte=60&with_original_language=en",
        "released": True,
    },
    {
        # Query for Coming Soon movies
        "query_string": f"&sort_by=popularity.desc&region=AU&include_adult=false&include_video=false&primary_release_date.gte={today}&primary_release_date.lte={coming_soon_range}&with_release_type=3%7C2&with_original_language=en",
        "released": False,
    },
]

movie_list = []

# Creating a client object and assigning it to the variable "client".
with httpx.Client() as client:

    # Getting the total number of pages for each query.
    for query in query_list:
        try:
            response = client.get(f"{base_url}{query['query_string']}")
            response.raise_for_status()
        except:
            # TODO: Add logging function
            raise
        else:
            data = response.json()
            query["total_pages"] = data["total_pages"]

    # A while loop that is iterating through the query list.
    for query in query_list:
        page_key = 0
        # It is then checking if the page key is less than the total pages and less than 3.
        while page_key < query["total_pages"] and page_key < 3:
            page_key = page_key + 1
            sleep(0.2)
            # If it is, it increments the page key by 1, waits 0.2 seconds, and then makes a request to the url.
            try:
                response = client.get(
                    f"{base_url}{query['query_string']}&page={page_key}"
                )
                response.raise_for_status()
            except:
                # TODO: Add logging function
                raise
            # If the request is successful, it parses the response as json and then iterates through the results.
            else:
                data = response.json()
                for movie in data["results"]:
                    # If the movie has a backdrop, poster, and popularity greater than 5, it adds the movie to the movie list and prints the title.
                    if (
                        movie["backdrop_path"] != None
                        and movie["poster_path"] != None
                        and movie["popularity"] >= 5
                    ):
                        movie["released"] = query["released"]
                        movie_list.append(movie)
                        print(f"Adding: {movie['title']}")

print(f"{movie_list} total: {len(movie_list)}")
