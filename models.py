# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)

    artist = db.relationship('Artist')
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)

    venue = db.relationship('Venue')
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    address = db.Column(db.String())
    phone = db.Column(db.String())
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    artists = db.relationship('Artist', secondary='show')
    shows = db.relationship('Show')


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    venues = db.relationship('Venue', secondary='show')
    shows = db.relationship('Show')