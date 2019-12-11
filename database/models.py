# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(11))
    lastname = db.Column(db.String(11))
    

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname
       

    def __repr__(self):
        return '<User %r>' % self.firstname

