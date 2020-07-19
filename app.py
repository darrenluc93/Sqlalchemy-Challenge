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

# Save reference to the table
Measurement= Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
#     #Create our session (link) from Python to the DB
    session = Session(engine)


    session.query(func.max(Measurement.date)).all()
    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)

    result = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).order_by(Measurement.date).all()

#     # Create a dictionary from the row data and append to a list of all_dates
    all_dates = []
    for date, prcp in result:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] =prcp
        all_dates.append(precipitation_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    top_station = session.query(Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).\
                    subquery()
    lastdate = session.query(func.max(Measurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date.between(startdate,lastdate)).\
                filter(Measurement.station.in_(top_station)).\
                all()
    session.close()
    #topStation = list(np.ravel(results))
    #return jsonify(topStation)
    topStation = []
    for date, tobs in results:
            tobs_dict ={}
            tobs_dict['date'] = date
            tobs_dict['tobs'] = tobs
            topStation.append(tobs_dict)
    return jsonify(topStation)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def rangestart(start,end=None):
    session=Session(engine)
    if end == None:
        enddate = session.query(func.max(Measurement.date)).\
                    scalar()
    else:
        enddate = str(end)
    startdate = str(start)
    results = session.query(func.min(Measurement.tobs).label('min_temp'),
                            func.avg(Measurement.tobs).label('avg_temp'),
                            func.max(Measurement.tobs).label('max_temp')).\
                filter(Measurement.date.between(startdate,enddate)).\
                first()
    session.close()
    datapoints = list(np.ravel(results))
    return jsonify(datapoints)
    
if __name__ == '__main__':
    app.run(debug=True)