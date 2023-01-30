"""
Data fetching function for creating a dummy database for the MovieLand Cinemas website.
Fetches data about movies from TMDB API - https://www.themoviedb.org/documentation/api

By default, it fetches data for the AU region as the data for release dates and certifications in NZ is limited.
This can be changed with the "TMDB_REGION" environment variable.

Requires:
    TMDB API key, stored as an environment variable
    HTTPX Python library - https://www.python-httpx.org/
"""

import os
from datetime import datetime, timedelta
from time import sleep

import httpx

# Create date object for today's date, and date strings for 100 days before and from that date.
today = datetime.now()
now_showing_range = (today - timedelta(days=100)).strftime("%Y-%m-%d")
coming_soon_range = (today + timedelta(days=100)).strftime("%Y-%m-%d")

# Set the TMDB API key in environoment varibles
api_key = os.environ.get("TMDB_API_KEY")

# Set the TMDB region in environoment varibles
# This parameter is expected to be an ISO 3166-1 code - https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
region = os.environ.get("TMDB_REGION")
base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"
query = f"&sort_by=popularity.desc&region={region}&include_adult=false&include_video=false&primary_release_date.gte={now_showing_range}&primary_release_date.lte={coming_soon_range}&with_release_type=3%7C2&with_original_language=en"

database = {"movie_list": []}


def get_release_info(data: list, fallback: str):
    """
    It takes the release dates results from the movie details query, sorts them by region.
    Then it filters out the theatrical release date from the first region that lists one.
    Prioritises the NZ region using the AU region as a fallback for the date and certification
    and US region as a fallback for the certification.
    Returns either the first best result, or an dictionary with fallback properties.

    :param data: list - The list of release dates results.
    :type data: list
    :param fallback: This is the fallback date that will be used if the release date is not found
    :type fallback: str
    :return: A dictionary with the release date and certification of the movie or fallback dictionary.
    """
    priority_order = ["NZ", "AU", "US"]
    filtered_data = list(
        filter(
            lambda i: i["type"] == 3,
            sorted(
                list(
                    filter(
                        lambda i: i["iso_3166_1"] == "NZ"
                        or i["iso_3166_1"] == "AU"
                        or i["iso_3166_1"] == "US",
                        data,
                    )
                ),
                key=lambda i: priority_order.index(i["iso_3166_1"]),
            )[0]["release_dates"],
        )
    )

    if len(filtered_data) != 0:
        release_info = {
            "release_date": filtered_data[0]["release_date"],
            "certification": "TBA"
            if filtered_data[0]["certification"] == ""
            else filtered_data[0]["certification"],
        }
        print(release_info)
        return release_info
    else:
        release_info = {"release_date": fallback, "certification": "TBA"}
        print(release_info)
        return release_info


def get_trailer(data: list):
    """
    Takes the video results from the movie details query and filters and sorts out the ones
    that are official English trailers.
    Returns the first best result, or a None object.

    :param data: The list of video results.
    :type data: list
    :return: A dictionary with the name, key, and link of the trailer or None.
    """
    filtered_data = sorted(
        sorted(
            list(
                filter(
                    lambda i: i["name"].lower() == "official trailer"
                    or i["name"].lower() == "trailer"
                    or "official trailer" in i["name"].lower()
                    or "trailer" in i["name"].lower(),
                    list(
                        filter(
                            lambda i: i["type"] == "Trailer",
                            list(
                                filter(
                                    (lambda i: i["iso_639_1"] == "en"),
                                    data,
                                )
                            ),
                        )
                    ),
                )
            ),
            key=lambda i: i["official"],
            reverse=True,
        ),
        key=lambda i: i["name"],
    )

    if len(filtered_data) != 0:
        trailer_info = {
            "name": filtered_data[0]["name"],
            "key": filtered_data[0]["key"],
            "link": f"https://www.youtube.com/watch?v={filtered_data[0]['key']}",
        }
        print(f"Trailer Info: {trailer_info['name']} - Link: {trailer_info['link']}")
        return trailer_info
    else:
        print("Trailer Info: Not Available")
        return None


def movie_constructor(data: dict, released: bool):
    """
    It takes in a dictionary of movie data and a boolean value, and returns a dictionary of movie data
    with the following keys: tmdb_id, imdb_id, title, tagline, released, release_date, certification,
    runtime, director, actors, overview, genres, backdrop, poster, and trailer

    :param data: The data returned from the movie details query.
    :type data: dict
    :param released: Boolean value to check if the movie is released or not
    :type released: bool
    :return: A dictionary with the following keys:
        tmdb_id,
        imdb_id,
        title,
        tagline,
        released,
        release_date,
        certification,
        runtime,
        director,
        actors,
        overview,
        genres,
        backdrop,
        poster,
        trailer
    """

    release_dates = data["release_dates"]["results"]
    if len(release_dates) != 0:
        release_info = get_release_info(release_dates, data["release_date"])
        release_date = release_info["release_date"]
        certification = release_info["certification"]
    else:
        release_date = data["release_date"]
        certification = "TBA"

    trailers = data["videos"]["results"]
    if len(trailers) != 0:
        trailer_info = get_trailer(trailers)
        trailer = trailer_info["link"] if trailer_info else None
    else:
        print("Trailer Info: Not Available")
        trailer = None

    movie = {
        "tmdb_id": data["id"],
        "imdb_id": data["imdb_id"],
        "title": data["title"],
        "tagline": data["tagline"],
        "released": released,
        "release_date": release_date,
        "certification": certification,
        "runtime": data["runtime"],
        "director": list(
            filter(lambda i: i["job"] == "Director", data["credits"]["crew"])
        ),
        "actors": sorted(
            data["credits"]["cast"], key=lambda i: i["order"], reverse=False
        )[0:5],
        "overview": data["overview"],
        "genres": data["genres"],
        "backdrop": data["backdrop_path"],
        "poster": data["poster_path"],
        "trailer": trailer,
    }
    return movie


with httpx.Client() as client:

    def fetcher(url: str):
        try:
            response = client.get(url)
            response.raise_for_status()
            # print(response.url)
        except:
            # TODO: Add logging function
            raise
        else:
            data = response.json()
            return data

    def get_movies(page_key=1):
        """
        It fetches the data from the TMDB API for each page of results, checks each movie has a backdrop and poster, checks if the movie
        has been released, checks if the movie has an IMDB ID, fetches more data for the movie, and then adds it to the database.

        :param page_key: The page number of the API call, defaults to 1 (optional)
        """
        data = fetcher(f"{base_url}{query}&page={page_key}")
        total_pages = data["total_pages"]
        print(f"Page {page_key}/{total_pages}")

        for movie in data["results"]:
            movie_id = movie["id"]
            release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").date()
            if movie["backdrop_path"] != None and movie["poster_path"] != None:
                if (
                    release_date <= today.date()
                    # and movie["vote_average"] >= 5
                    # and movie["vote_count"] >= 50
                    and movie["popularity"] >= 3
                ):
                    movie_details = fetcher(
                        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US&append_to_response=videos,release_dates,videos,credits"
                    )
                    if movie_details["imdb_id"] != None:
                        print(
                            f"Adding: [{movie_details['id']}] - {movie_details['title']}"
                        )
                        sleep(0.2)
                        database["movie_list"].append(
                            movie_constructor(movie_details, True)
                        )
                elif release_date >= today.date() and movie["popularity"] >= 3:
                    movie_details = fetcher(
                        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US&append_to_response=videos,release_dates,videos,credits"
                    )
                    if movie_details["imdb_id"] != None:
                        print(
                            f"Adding: [{movie_details['id']}] - {movie_details['title']}"
                        )
                        sleep(0.2)
                        database["movie_list"].append(
                            movie_constructor(movie_details, False)
                        )
        if page_key < total_pages:
            page_key += 1
            sleep(0.2)
            get_movies(page_key)

    get_movies()
    database["date_created"] = today.strftime("%d-%m-%Y %H:%M:%S")

print(f"Movies in Database: {len(database['movie_list'])}")
