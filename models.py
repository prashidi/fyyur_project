from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue_Genre(db.Model):
    __tablename__ = "venue_genres"
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        "venues.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Genre venue_id:{self.venue_id} genre: {self.genre}>"


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.relationship(
        'Venue_Genre', passive_deletes=True, backref="venue", lazy=True)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.image_link}>'


class Artist_Genre(db.Model):
    __tablename__ = "artist_genres"
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "artists.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Genre venue_id:{self.artist_id} genre: {self.genre}>"


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship("Artist_Genre", backref="artist", lazy=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True, default="")
    website = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.genres}>'


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete="CASCADE"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.venue_id} {self.artist_id}>'
