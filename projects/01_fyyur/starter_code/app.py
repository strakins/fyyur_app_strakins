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
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  session, 
  url_for
)
from flask_moment import Moment
from sqlalchemy import desc
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

#Models was here

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
    # venues_recent = Venue.query.order_by(desc(Venue.)).limit(3).all()
    # artists_recent = Venue.query.order_by(desc(Artist.id)).limit(3).all()
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
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
    venueItems.append(temp_venue)
  print(venueList)
  return render_template('pages/venues.html', areas=venueItems);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venueQuery = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
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
  try:
    form = VenueForm()
    # print(form.data)
    if form.validate_on_submit():
      venuedata = Venue(**form.data)
      db.session.add(venuedata)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      # on successful db insert, flash success
    else :
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try: 
    delVenue = Venue.query.get(venue_id)
    db.session.delete(delVenue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
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
  data = Artist.query.filter_by(id = artist_id).first()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
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
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
  try: 
    form = ArtistForm()
    print(form.data)
    if form.validate_on_submit():
      artistdata = Artist(**form.data)
    db.session.add(artistdata)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully Added to our Artist List!')
  # on successful db insert, flash success
  except:
   print(sys.exc_info())
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed in Our Database.')
  finally:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
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
