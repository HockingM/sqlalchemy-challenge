import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
# Homepage listing all routes that are available

def homepage():
    """Climate Analysis Home Page"""
    return (
        f"List of Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Last 12 months precipation</a><br/>"
        f"<a href='/api/v1.0/stations'>List of all stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>Last 12 months temperatures for the most active station</a><br/>"
        f"<a href='/api/v1.0/user_dates/<start_date>/<end_date>'>Enter start and/or end dates into the URL in the format YYYY-MM-DD<start_date,end_date></a>"
    )


@app.route("/api/v1.0/precipitation")
# Convert the query results to a dictionary using date as the key and prcp as the value
# Return the JSON representation of your dictionary

def precipitation():
   
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve the last 12 months of precipation data and return a json dictionary of results
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = last_date[0]
    last_date  = dt.datetime.strptime(last_date, '%Y-%m-%d')
    first_date = last_date - dt.timedelta(days=365)
    
    annual_rainfall = session.query(measurement.date, 
           measurement.prcp).\
        filter(measurement.date >= first_date).\
        filter(measurement.date <= last_date).all()

    session.close()

    all_rainfall = []

    for measurement.date, measurement.prcp in annual_rainfall:
        rainfall_dict = {}
        rainfall_dict["date"] = measurement.date
        rainfall_dict["rainfall"] = measurement.prcp
        all_rainfall.append(rainfall_dict)

    return jsonify(all_rainfall)
    

@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset

def stations():
  
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(station.name).all()

    session.close()

    # Create a list of stations from the dataset
    station_list = list(np.ravel(results))

    # Return JSON list of stations from the dataset
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data
# Return a JSON list of temperature observations (TOBS) for the previous year

def tobs():

    # Create session (link) from Python to the DB
    session = Session(engine)

    # List the stations and the counts in descending order to find station with highest number of temperature observations
    stn_most_temps = session.query(measurement.station, func.count(measurement.tobs)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.tobs).desc()).first()

    # Find the last date for the station
    stn_last_date = session.query(measurement.date).\
        filter(measurement.station == stn_most_temps[0]).\
            order_by(measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point for the station
    stn_last_date = stn_last_date[0]
    stn_last_date  = dt.datetime.strptime(stn_last_date, '%Y-%m-%d')
    stn_first_date = stn_last_date - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station
    station_temps = session.query(measurement.tobs).\
        filter(measurement.station == stn_most_temps[0]).\
        filter(measurement.date >= stn_first_date).\
        filter(measurement.date <= stn_last_date).all()

    session.close()

    # Create a list of temperature observations (TOBS) for the previous year
    station_temps_list = list(np.ravel(station_temps))

    # Return JSON list temperature observations (TOBS) for the previous year
    return jsonify(station_temps_list)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/user_dates/<start_date>/<end_date>")
def user_dates(start_date = None, end_date = None):   
    # Create session (link) from Python to the DB
    session = Session(engine)    

    if end_date == None:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).all()
        return jsonify(results)
    else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
        return jsonify(results)

    session.close()

if __name__ == '__main__':
    app.run(debug=True)  # restarts server on update of code