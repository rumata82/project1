import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():

    # Query user reviews
    reviews = db.execute(
        """SELECT id_book, id_user,
           rating, review, time, username
           FROM reviews, users
           WHERE id_user = users.id
           AND reviews.id_book = :id_book""",
        {"id_book": "2653"}).fetchall()

    for review in reviews:
        print(review)

    reviewed = any(r.id_user == 6 for r in reviews)
    print(reviewed)


if __name__ == "__main__":
    main()
