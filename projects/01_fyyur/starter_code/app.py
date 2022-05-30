#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import sys
from unicodedata import name
import dateutil.parser
from dateutil import parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
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

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # venueList = Venue.query.all()
  groupedVenue = Venue.query.distinct(Venue.state, Venue.city).all()
  venueList = Venue.query.all()
  current_time = datetime.now()
  # venue_state_with_city = ''
  venueItems = []
  for venue in groupedVenue:
    temp_venue = {
      "city": venue.city,
      "state": venue.state,
      "venues": []
    }
    for subVenue in venueList:
      if subVenue.city == venue.city and subVenue.state==venue.state: 
        temp_venue["venues"].append({
        "id": subVenue.id,
        "name": subVenue.name,
        "num_upcoming_shows": len([show for show in subVenue.shows if parser.parse(show.start_time) > current_time])
      })
    # venue_state_with_city == venue.city + ', ' + venue.state
    venueItems.append(temp_venue)
  print(venueList)
  return render_template('pages/venues.html', areas=venueItems);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venueQuery = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  # venueQuery = session.query(Venue).filter(Venue.name.like( request.form['search_term'] + '%')).all()
  data = []
  
  for venue in venueQuery:
    data.append({
        "id": venue.id,
        "name": venue.name,
        # "num_upcoming_shows": 0,
      })
  response= {
      "count": len(data),
      "data": data,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter_by(id = venue_id).first()
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
  try:
    # form = VenueForm(request.form.get)
    # name = request.form['name']
    # name = request.form.get('name')
    # print(name)
    # city = request.form.get('city')
    # address = request.form.get('address')
    # genres = request.form.get('genres')
    # state = request.form.get('state')
    # phone = request.form.get('phone')
    # facebook_link = request.form.get('facebook_link')
    # image_link = request.form.get('image_link')
    # website_link = request.form.get('website_link')
    # seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    # seeking_description = request.form.get('seeking_description')
    # venuedata = Venue(name=name, city=city, address=address, genres=genres, state=state, phone=phone, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    # Used an Alternative mode 
    form = VenueForm()
    print(form.data)
    if form.validate_on_submit():
      venuedata = Venue(**form.data)
        # flash('Venue ' + request.form['name'] + ' was successfully listed!')
      db.session.add(venuedata)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # on successful db insert, flash success
      print(venuedata)
    else :
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      print(form.errors) 
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try: 
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artistQuery = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  artistList = []
  for artiste in artistQuery:
    artistList.append({
        "id": artiste.id,
        "name": artiste.name,
        "num_upcoming_shows": 0,
      })
  response={
      "count": len(artistList),
      "data": artistList
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter_by(id = artist_id).first()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  # data = Artist.query.filter_by(artist_id)
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # name = request.form['name']
  
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  for index, value in form.data.items(): 
    setattr(artist, index, value)
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  for index, value in form.data.items():
    setattr(venue, index, value)
  db.session.add
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
  # form = ArtistForm()
  try: 
    name = request.form.get('name')
    print(name)
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website')
    seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    seeking_description = request.form.get('seeking_description')
    artistdata = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    print(artistdata)
    db.session.add(artistdata)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully Added to our Artist List!')
  # on successful db insert, flash success
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
   print(sys.exc_info())
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed in Our Database.')
  finally:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  display_show=Show.query.outerjoin(Venue, Venue.id==Show.venue_id).outerjoin(Artist, Artist.id==Show.venue_id).all()
  show_list = []
  for shows in display_show:
      # print(shows.Artist)
      # print(shows.Venue)
    show_list.append({
      "venue_id": shows.Venue.id, 
      "venue_name": shows.Venue.name,
      "artist_id": shows.Artist.id,
      "artist_image_link": shows.Artist.image_link,
      "start_time": shows.start_time
    })

  print(display_show)
  return render_template('pages/shows.html', shows=show_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()
    print(form.data)
    if form.validate_on_submit():
      newShow_data = Show(**form.data)
  # on successful db insert, flash success
      flash('Show was successfully listed!')
      db.session.add(newShow_data)
      db.session.commit()
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
