from app import db
from datetime import datetime

from flask.ext.login import current_user

search_entry_links = db.Table('search_entry_links',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id')),
    db.Column('lbc_entry_id', db.Integer, db.ForeignKey('lbc_entries.id'))
)

search_user_links = db.Table('search_user_links',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'))
)

class Search(db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    terms = db.Column(db.String())
    category = db.Column(db.Integer)
    minprice = db.Column(db.Integer)
    maxprice = db.Column(db.Integer)
    lbc_entries = db.relationship('LBCentry', secondary=search_entry_links, backref=db.backref('searches'))

    def __init__(self, title = "", terms = "", category = None, minprice = None, maxprice = None, user = current_user):
        self.title = title
        self.terms = terms
        if category is not None:
            self.category = category
        self.minprice = minprice
        if maxprice is not None:
            self.maxprice = maxprice
        if user is not None:
            self.users.append(user)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def get_url(self):
        base_url = "https://mobile.leboncoin.fr/templates/api/list.json?&app_id=leboncoin_android&key=d2c84cdd525dddd7cbcc0d0a86609982c2c59e22eb01ee4202245b7b187f49f1546e5f027d48b8d130d9aa918b29e991c029f732f4f8930fc56dbea67c5118ce"
        url = base_url + "&q=" + self.terms
        if self.category is not None:
            url = url + "&c=" + str(self.category)
        return url

class LBCentry(db.Model):
    __tablename__ = 'lbc_entries'

    id = db.Column(db.Integer, primary_key=True)
    linkid = db.Column(db.Integer)
    title = db.Column(db.String())
    category = db.Column(db.String())
    location = db.Column(db.String())
    time = db.Column(db.DateTime)
    price = db.Column(db.Integer)
    imgurl = db.Column(db.String())
    imgnumber = db.Column(db.Integer)
    new = db.Column(db.Boolean)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.new = True

    def __repr__(self):
        return '<linkid {}>'.format(self.linkid)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    searches = db.relationship("Search", secondary=search_user_links, backref=db.backref('users'))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<userid {}>'.format(self.id)
