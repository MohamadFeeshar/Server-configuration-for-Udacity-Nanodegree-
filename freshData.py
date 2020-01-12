from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Genre, Base, Book
engine = create_engine('sqlite:///bookstore.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

genre1 = Genre(name="Comedy", description="Funny stories",
               created_by_name="ali",
               created_by_email="ali@company.com")

session.add(genre1)
session.commit()

genre2 = Genre(name="Drama", description="Sad stories",
               created_by_name="ali",
               created_by_email="ali@company.com")

session.add(genre2)
session.commit()

genre3 = Genre(name="Horror", description="Scary stories",
               created_by_name="ali",
               created_by_email="ali@company.com")

session.add(genre3)
session.commit()


book2 = Book(name="Bloody blood", description="The book of bloody things",
             author="UNKNOWN", price="$70.50",
             created_by_email="mister@example.com",
             created_by_name="Ali",
             isbn="0-4902-0121-0", numberOfPages=203, genre=genre3)

session.add(book2)
session.commit()


book3 = Book(name="murder mystery", description="mystery Cases",
             author="Sherlok", price="$2.99",
             created_by_email="mister@example.com",
             created_by_name="Ali",
             isbn="0-4902-0131-0", numberOfPages=389, genre=genre3)

session.add(book3)
session.commit()

book4 = Book(name="Jokes", description="Funny Jokes", price="$30.99",
             author="Mr Funny", created_by_email="mister@example.com",
             created_by_name="Ali",
             isbn="0-4905-3121-0", numberOfPages=389, genre=genre1)

session.add(book4)
session.commit()

book5 = Book(name="u will laugh about this", description="laughing situations",
             author="Mr Funny", price="$50.50", created_by_name="Ali",
             created_by_email="mister@example.com",
             isbn="0-4972-3121-0", numberOfPages=150, genre=genre1)

session.add(book5)
session.commit()
