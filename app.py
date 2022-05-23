#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import field
from datetime import datetime
import json
import os
import sys
from urllib import response
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from sqlalchemy import distinct, null
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# Import models
from models import Venue, Venue_Genre, Artist, Artist_Genre, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    try:
        data = []
        locations = db.session.query(distinct(Venue.city), Venue.state).all()

        for location in locations:
            city = location[0]
            state = location[1]
            venue_per_location = {"city": city, "state": state, "venues": []}
            venues = Venue.query.filter_by(city=city, state=state).all()

            for venue in venues:
                venue_id = venue.id
                venue_name = venue.name

                venue_details = {"id": venue_id, "name": venue_name}

                venue_per_location["venues"].append(venue_details)

            print(venue_per_location)

            data.append(venue_per_location)
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venues could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    try:
        search_term = request.form.get('search_term', '').strip()
        response = {"count": 0, "data": []}
        search_results = Venue.query.filter(
            Venue.name.ilike('%' + search_term + '%')).all()
        response["count"] = len(search_results)

        for result in search_results:
            data = {"id": result.id, "name": result.name}
            response["data"].append(data)
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venues could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    try:
        data = {}
        genres = []
        upcoming_shows = []
        past_shows = []
        venue = Venue.query.get(venue_id)
        venue_genres = Venue_Genre.query.filter_by(venue_id=venue_id).all()
        for genre in venue_genres:
            genres.append(genre.genre)

        upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
            Show.start_time >= datetime.now()).all()

        for show in upcoming_shows_query:
            artist = Artist.query.get(show.artist_id)
            show_details = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_details)

        past_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        for show in past_shows_query:
            artist = Artist.query.get(show.artist_id)
            show_details = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_details)

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              venue_id + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        try:
            st = False
            name = request.form.get("name")
            address = request.form.get("address")
            city = request.form.get("city")
            state = request.form.get("state")
            phone = request.form.get("phone")
            website = request.form.get("website_link")
            genres = request.form.getlist("genres")
            facebook_link = request.form.get("facebook_link")
            seeking_talent = request.form.get("seeking_talent")
            seeking_description = request.form.get("seeking_description")
            image_link = request.form.get("image_link")

            if seeking_talent == 'y':
                st = True

            new_venue = Venue(
                name=name,
                address=address,
                city=city,
                state=state,
                phone=phone,
                website=website,
                facebook_link=facebook_link,
                seeking_talent=st,
                seeking_description=seeking_description,
                image_link=image_link,
            )
            print(new_venue)
            db.session.add(new_venue)
            db.session.flush()
            db.session.commit()

            for genre in genres:
                venue_genre = Venue_Genre(genre=genre, venue_id=new_venue.id)
                db.session.add(venue_genre)
                db.session.commit()

            db.session.refresh(new_venue)
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message))
        return render_template('forms/new_venue.html', form=form)


    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id).name
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash("Venue " + venue + " was successfully deleted!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              venue + ' could not be deleted.')
    finally:
        db.session.close()
        return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    try:
        data = []
        artist_list = Artist.query.all()

        for artist in artist_list:
            artist_details = {
                "id": artist.id,
                "name": artist.name
            }

            data.append(artist_details)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Artists could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
        search_term = request.form.get('search_term', '').strip()
        response = {"count": 0, "data": []}
        search_results = Artist.query.filter(
            Artist.name.ilike('%' + search_term + '%')).all()
        response["count"] = len(search_results)

        num_upcoming_shows = 0

        for result in search_results:
            num_upcoming_shows = db.session.query(
                Show).filter_by(artist_id=result.id).count()
            data = {"id": result.id, "name": result.name,
                    "num_upcoming_shows": num_upcoming_shows}
            response["data"].append(data)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Not able to search for artist.')
    finally:
        db.session.close()

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    try:
        data = {}
        genres = []
        upcoming_shows = []
        past_shows = []
        artist = Artist.query.get(artist_id)
        artist_genres = Artist_Genre.query.filter_by(artist_id=artist_id).all()
        for genre in artist_genres:
            genres.append(genre.genre)

        upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
            Show.start_time >= datetime.now()).all()

        for show in upcoming_shows_query:
            venue = Venue.query.get(show.venue_id)
            show_details = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_details)

        past_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
        for show in past_shows_query:
            venue = Venue.query.get(show.venue_id)
            show_details = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            print(venue)
            past_shows.append(show_details)

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Artist could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist:
        form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Update artist record with ID <artist_id> using the new attributes
    try:
        sv = False
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        image_link = request.form.get("image_link")
        facebook_link = request.form.get("facebook_link")
        seeking_venue = request.form.get("seeking_venue")
        seeking_description = request.form.get("seeking_description")
        website = request.form.get("website_link")
        genres = request.form.getlist("genres")

        if seeking_venue == 'y':
            sv = True

        artist = Artist.query.get(artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone,
        artist.image_link = image_link,
        artist.facebook_link = facebook_link
        artist.seeking_venue = sv
        artist.seeking_description = seeking_description
        artist.website = website

        db.session.flush()
        db.session.commit()

        Artist_Genre.query.filter_by(artist_id=artist_id).delete()

        for genre in genres:
            artist_genre = Artist_Genre(genre=genre, artist_id=artist_id)
            db.session.add(artist_genre)
            db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Artist could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    try:
        st = False
        name = request.form.get("name")
        genres = request.form.getlist("genres")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        website = request.form.get("website_link")
        facebook_link = request.form.get("facebook_link")
        seeking_talent = request.form.get("seeking_talent")
        seeking_description = request.form.get("seeking_description")
        image_link = request.form.get("image_link")
        if seeking_talent == 'y':
            st = True

        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.address = address
        venue.city = city
        venue.state = state
        venue.phone = phone,
        venue.image_link = image_link,
        venue.facebook_link = facebook_link
        venue.seeking_talent = st
        venue.seeking_description = seeking_description
        venue.website = website

        db.session.flush()
        db.session.commit()

        Venue_Genre.query.filter_by(venue_id=venue_id).delete()

        for genre in genres:
            venue_genre = Venue_Genre(genre=genre, venue_id=venue_id)

            db.session.add(venue_genre)
            db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Create new artist
    form = ArtistForm()
    if form.validate_on_submit():
        try:
            sv = False
            name = request.form.get("name")
            genres = request.form.getlist("genres")
            city = request.form.get("city")
            state = request.form.get("state")
            phone = request.form.get("phone")
            website = request.form.get("website_link")
            facebook_link = request.form.get("facebook_link")
            seeking_venue = request.form.get("seeking_venue")
            seeking_description = request.form.get("seeking_description")
            image_link = request.form.get("image_link")

            if seeking_venue == 'y':
                sv = True

            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                website=website,
                facebook_link=facebook_link,
                seeking_venue=sv,
                seeking_description=seeking_description,
                image_link=image_link,
            )
            print(new_artist)
            db.session.add(new_artist)
            db.session.flush()
            db.session.commit()

            # Save the artist's genres in the Artist_Genre Table
            for genre in genres:
                artist_genre = Artist_Genre(genre=genre, artist_id=new_artist.id)
                db.session.add(artist_genre)
                db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            print(sys.exc_info())
            db.session.rollback()
            flash('An error occurred. Artist ' +
                request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
            # In all case return to home page
            return render_template('pages/home.html')
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message))
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    try:
        data = []

        # Get all shows
        shows = Show.query.all()

        # Get show's venue name and artist performing at that venue
        for show in shows:
            venue_id = show.venue_id
            artist_id = show.artist_id

            show_details = {
                "show_id": show.id,
                "venue_name": Venue.query.get(venue_id).name,
                "venue_id": Venue.query.get(venue_id).id,
                "artist_name": Artist.query.get(artist_id).name,
                "artist_id": Artist.query.get(artist_id).id,
                "artist_image_link": Artist.query.get(artist_id).image_link,
                "start_time": str(show.start_time),
            }
            data.append(show_details)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash("An error occurred. Shows could not be listed.")

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")

        # Checking artist id and venue id in the database
        validate_artist = Artist.query.get(artist_id)
        if validate_artist is None:
            flash('The provided artist id is invalid')

        validate_venue = Venue.query.get(venue_id)
        if validate_venue is None:
            flash('The provided artist id is invalid')

        # if artist_id is valide, save new show in the database
        if validate_artist is not None and validate_venue is not None:
            new_show = Show(
                artist_id=validate_artist.id,
                venue_id=validate_venue.id,
                start_time=start_time,
            )

            db.session.add(new_show)
            db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# # Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
