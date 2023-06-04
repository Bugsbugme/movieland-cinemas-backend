from httpx import Client

import _api as api


def fetcher(url: str, client: Client):
    """
    This function takes a URL and a Client object, and returns the JSON data from the URL

    :param url: The URL of the API endpoint
    :type url: str
    :param client: The Client object that will be used to make the request
    :type client: Client
    :return: A list of dictionaries
    """
    try:
        response = client.get(url)
        response.raise_for_status()
        print(response.url)
    except:
        # TODO: Add logging function
        raise
    else:
        data = response.json()
        return data


def movie_constructor(data: dict):
    """
    It takes in a dictionary of movie data and a boolean value, and returns a dictionary of movie data
    with various details about the movie.

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

    # This code block is checking if there is any data available for the movie's release dates. If
    # there is data available, it calls the `get_release_info` function from the `_api` module to get
    # the release date and certification information. If there is no data available, it sets the
    # release date to the default value of `data["release_date"]` and the certification to "TBD". The
    # resulting `release_date` and `certification` values are then used to construct the `movie`
    # dictionary in the `movie_constructor` function.
    release_dates = data["release_dates"]["results"]
    if len(release_dates) != 0:
        release_info = api.get_release_info(release_dates)
        release_date = (
            release_info["release_date"]
            if len(release_info["release_date"]) != 0
            else data["release_date"]
        )
        certification = (
            release_info["certification"]
            if len(release_info["certification"]) != 0
            else "TBD"
        )
    else:
        release_date = data["release_date"]
        certification = "TBD"

    # This code block is checking if there are any trailers available for the movie. If there are
    # trailers available, it calls the `get_trailer` function from the `_api` module to get the
    # trailer link. If there are no trailers available, it sets the `trailer` variable to `None` and
    # prints a message indicating that trailer information is not available. The resulting `trailer`
    # value is then used to construct the `movie` dictionary in the `movie_constructor` function.
    trailers = data["videos"]["results"]
    if len(trailers) != 0:
        trailer_info = api.get_trailer(trailers)
        trailer = trailer_info["link"] if trailer_info else None
    else:
        print("Trailer Info: Not Available")
        trailer = None

    movie = {
        "tmdb_id": data["id"],
        "imdb_id": data["imdb_id"],
        "title": data["title"],
        "tagline": data["tagline"],
        "released": True if data["status"] == "Released" else False,
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
