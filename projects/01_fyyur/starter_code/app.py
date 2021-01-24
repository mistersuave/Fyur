# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


migrate = Migrate(app, db)
#db.create_all()

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
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


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venues = Venue.query.order_by(Venue.state, Venue.city).all()
    for venue in venues:
        upcoming_shows = [show for show in venue.shows if show.start_time > datetime.today()]
        venuedata = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': upcoming_shows}
        if not data:
            data.append({'city': venue.city, 'state': venue.state, 'venues': [venuedata]})
        elif data[-1]['city'] == venue.city and data[-1]['state'] == venue.state:
            data[-1]['venues'].append(venuedata)
        else:
            data.append({'city': venue.city, 'state': venue.state, 'venues': [venuedata]})

    # print(data)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    data = []
    search_term = request.form['search_term']
    venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    for venue in venues:
        data.append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(venue.shows)})

    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    venue_upcoming_shows = [show for show in venue.shows if show.start_time > datetime.today()]

    upcoming_shows = []
    for show in venue_upcoming_shows:
        upcoming_shows.append({'artist_id': show.artist_id,
                               'artist_name': show.artist.name,
                               'artist_image_link': show.artist.image_link,
                               'start_time': show.start_time.isoformat()})

    venue_past_shows = [show for show in venue.shows if show.start_time < datetime.today()]

    past_shows = []
    for show in venue_past_shows:
        past_shows.append({'artist_id': show.artist_id,
                           'artist_name': show.artist.name,
                           'artist_image_link': show.artist.image_link,
                           'start_time': show.start_time.isoformat()})

    data = {'id': venue.id,
            'name': venue.name,
            'city': venue.city,
            'state': venue.state,
            'address': venue.address,
            'phone': venue.phone,
            'genres': venue.genres,
            'image_link': venue.image_link,
            'facebook_link': venue.facebook_link,
            'website': venue.website,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)}

    # print(data)
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False

    try:

        venue = Venue(
          name=request.form['name'],
          city=request.form['city'],
          state=request.form['state'],
          address=request.form['address'],
          phone=request.form['phone'],
          genres=request.form.getlist('genres'),
          facebook_link=request.form.get('facebook_link'),
          website=request.form.get('website'),
          image_link=request.form.get('image_link'),
          seeking_talent=request.form.get('seeking_talent') == 'y',
          seeking_description=request.form.get('seeking_description')
        )

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('Internal server error: Unable to create a new venue ' + request.form['name'] + '!')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    venue = Venue.query.get(venue_id)
    name = venue.name

    try:
        db.session.delete(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
             flash('Internal server error: Venue - ' + name + ' could not be deleted.')
        else:
             flash('Venue ' + name + ' was deleted successfully!')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    data = []
    search_term = request.form['search_term']
    artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    for artist in artists:
        data.append({'id': artist.id, 'name': artist.name, 'num_upcoming_shows': len(artist.shows)})

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real artist data from the artists table, using artist_id
    data = []
    artist = Artist.query.get(artist_id)
    artist_upcoming_shows = [show for show in artist.shows if show.start_time > datetime.today()]

    upcoming_shows = []
    for show in artist_upcoming_shows:
        upcoming_shows.append({'venue_id': show.venue_id,
                               'venue_name': show.venue.name,
                               'venue_image_link': show.venue.image_link,
                               'start_time': show.start_time.isoformat()})

    artist_past_shows = [show for show in artist.shows if show.start_time < datetime.today()]

    past_shows = []
    for show in artist_past_shows:
        past_shows.append({'venue_id': show.venue_id,
                           'venue_name': show.venue.name,
                           'venue_image_link': show.venue.image_link,
                           'start_time': show.start_time.isoformat()})

    data.append({'id': artist.id,
                 'name': artist.name,
                 'city': artist.city,
                 'state': artist.state,
                 'phone': artist.phone,
                 'genres': artist.genres,
                 'image_link': artist.image_link,
                 'facebook_link': artist.facebook_link,
                 'website': artist.website,
                 'seeking_venue': artist.seeking_venue,
                 'seeking_description': artist.seeking_description,
                 'past_shows': past_shows,
                 'upcoming_shows': upcoming_shows,
                 'past_shows_count': len(past_shows),
                 'upcoming_shows_count': len(upcoming_shows)})

    # print(data)
    return render_template('pages/show_artist.html', artist=data[0])


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form.get('image_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website')
        artist.seeking_venue = request.form.get('seeking_venue') == 'y'
        artist.seeking_description = request.form.get('seeking_description')
        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('Internal server error: Failed to save the edited info for Artist: ' + request.form['name'] + '!')
        else:
            flash('Artist ' + request.form['name'] + ' info was updated successfully!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TODO: populate form with values from venue with ID <venue_id>
    return redirect(url_for('show_venue', venue_id=Venue.query.get(venue_id)))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form.get('image_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website')
        venue.seeking_talent = request.form.get('seeking_talent') == 'y'
        venue.seeking_description = request.form.get('seeking_description')
        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('Internal server error: Failed to save the edited info for venue: ' + request.form['name'] + '!')
        else:
            flash('Venue ' + request.form['name'] + ' info was updated successfully!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        artist = Artist(
          name=request.form['name'],
          city=request.form['city'],
          state=request.form['state'],
          phone=request.form['phone'],
          genres=request.form.getlist('genres'),
          image_link=request.form.get('image_link'),
          facebook_link=request.form.get('facebook_link'),
          website=request.form.get('website'),
          seeking_venue=request.form.get('seeking_venue') == 'y',
          seeking_description=request.form.get('seeking_description')
        )

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('Internal server error: Unable to create a new artist ' + request.form['name'] + '!')
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    shows = Show.query.all()
    for show in shows:
        data.append({'venue_id': show.venue.id,
                     'venue_name': show.venue.name,
                     'artist_id': show.artist.id,
                     'artist_name': show.artist.name,
                     'artist_image_link': show.artist.image_link,
                     'start_time': show.start_time.isoformat()
                     })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'],
                    start_time=request.form['start_time'])

        db.session.add(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('Internal Error: Unable to add a show!')
        else:
            flash('Show was successfully listed!')

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
