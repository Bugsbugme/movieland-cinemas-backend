from httpx import Client


def fetcher(url: str, client: Client):
    """
    > This function takes a URL and a Client object, and returns the JSON data from the URL

    :param url: The URL of the API endpoint
    :type url: str
    :param client: The Client object that will be used to make the request
    :type client: Client
    :return: A list of dictionaries
    """
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
