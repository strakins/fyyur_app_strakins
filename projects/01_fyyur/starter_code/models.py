from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Areas(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    venues = db.relationship('Venue', backref='area')

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(250))
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} >'
        
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(200))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.phone} {self.genres} {self.facebook_link} {self.city} {self.image_link}>'

class Show(db.Model):
  __tablename__ = "show"
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id))
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id))
  start_time = db.Column(db.String(), nullable=False)