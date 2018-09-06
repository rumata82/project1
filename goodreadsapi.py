import requests

goodreadskey = "pbx1XtPnZ3i94x8NB40w"


def goodread(isbns):
    """
    Request Goodreads API for reviews count and average rating
    """

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": goodreadskey, "isbns": isbns})

    if res.status_code == 200:
        rating = {}
        rating["count"] = res.json()["books"][0]["work_ratings_count"]
        rating["average"] = res.json()["books"][0]["average_rating"]
        return rating

    else:
        return None


print(goodread("1250091845"))
