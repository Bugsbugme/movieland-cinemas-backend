def get_release_info(data: list):
    """
    Find the theatrical(type 3) release date and the certification for NZ.
        If there is no type 3 release date for NZ, take the type 3 date from AU
        If there is no type 3 certification, take the type 2 NZ one, else types 3 or 2 from AU or US

    :param data: List with details of each release of the movie.
    :type data: list
    :return: A dictionary with the release date and certification.
    """

    release_info = {"release_date": "", "certification": ""}

    for release in data:
        release_date = len(release_info["release_date"])
        certification = len(release_info["certification"])
        region = release["iso_3166_1"]
        if region == "NZ":
            for i in release["release_dates"]:
                if i["type"] == 3:
                    release_info["release_date"] = i["release_date"]
                    release_info["certification"] = i["certification"]
                elif i["type"] == 2 and certification == 0:
                    release_info["certification"] = i["certification"]
        if region == "AU":
            for i in release["release_dates"]:
                if i["type"] == 3:
                    if release_date == 0:
                        release_info["release_date"] = i["release_date"]
                    if certification == 0:
                        release_info["certification"] = i["certification"]
                elif i["type"] == 2 and certification == 0:
                    release_info["certification"] = i["certification"]
        if region == "US":
            for i in release["release_dates"]:
                if i["type"] == 3 and certification == 0:
                    release_info["certification"] = i["certification"]
                elif i["type"] == 2 and certification == 0:
                    release_info["certification"] = i["certification"]

    print(release_info)
    return release_info


def get_trailer(data: list):
    """
    Takes the video results from the movie details query then filters and sorts out the ones
    that are official English trailers.
    Returns the first best result, or a None value.

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
        print(f"Trailer Info: {trailer_info['name']} - Link: {trailer_info['link']}\n")
        return trailer_info
    else:
        print("Trailer Info: Not Available", end="\n\n")
        return None
