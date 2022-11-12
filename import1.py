import csv
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from group import db
from group.models import Products


def main():
    f = open("new_wearables.csv.csv")
    reader = csv.reader(f)
    for name, price, body_loc, category, img in reader:
        product = Products(name=name, price=price, body_loc=body_loc, category=category, img=img)
        db.session.add(product)
        print(f"Added product {name}, {price}, {body_loc}")
    db.session.commit()