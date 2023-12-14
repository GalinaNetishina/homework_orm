import os
import json
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import *


def get_DSN():
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print("not found .env")
    driver = os.environ.get("DRIVER", "postgresql")
    username = os.environ.get("USER", "postgres")
    password = os.environ.get("PASSWORD", "postgres")
    server = os.environ.get("SERVER", "localhost:5432")
    bd_name = os.environ.get("BD_NAME")
    return f"{driver}://{username}:{password}@{server}/{bd_name}"


def db_fill(file):
    with open(file, "r") as f:
        data = json.load(f)
    models = {
        "book": Book,
        "publisher": Publisher,
        "sale": Sale,
        "shop": Shop,
        "stock": Stock
    }
    for line in data:
        model = line.get("model")
        m = models.get(model)(**line.get("fields"))
        session.add(m)
    session.commit()


def author_info():
    q = input("Enter id or name of publisher:\n")
    if q.isdigit():
        id = session.query(Publisher).filter(Publisher.id == int(q)).subquery("id")
    else:
        id = session.query(Publisher).filter(Publisher.name.like(f"%{q}%")).subquery("id")
    query = session.query(Book, Stock, Sale, Shop).filter(sq.and_(
        Book.id_publisher == id.c.id,
        Stock.id_book == Book.id,
        Shop.id == Stock.id_shop,
        Sale.id_stock == Stock.id
    ))
    for book, stock, sale, shop in query.all():
        print(f"{book.title:40}|{shop.name:20}|{sale.price:^7}|{sale.date_sale:%d-%m-%y}")



if __name__ == "__main__":
    DSN = get_DSN()
    engine = sqlalchemy.create_engine(DSN)
    create_tables(engine)
    session = sessionmaker(bind=engine)()
    file = "fixtures/tests_data.json"
    db_fill(file)
    author_info()
    
    session.close()
