from flask import Flask, jsonify
import sqlalchemy

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)



@app.route("/")
def home():
    return (
        f"<h3>Available routes:</h3>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"To filter for tobs from a start date to the last date:<br/>" 
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"<br/>"
        f"To filter for tobs from a start date to a specified end date:<br/>" 
        f"/api/v1.0/start-yyyy-mm-dd/end-yyyy-mm-dd"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    all_prcp = []
    for date, precipitation in results:
        prcp_dictionary = {}
        prcp_dictionary[date] = precipitation
        all_prcp.append(prcp_dictionary)
        
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= query_date).all()
    session.close()

    all_tobs = list(np.ravel(results))
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.date),func.min(Measurement.tobs),func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs),2)).\
        filter(Measurement.date >= start).all()
    session.close()

    summary_tobs = []
    for result in results:
        if result[0] == start:
            tobs_dict = {}
            tobs_dict["Minimum temperature"] = result[1]
            tobs_dict["Maximum temperature"] = result[2]
            tobs_dict["Average temperature"] = result[3]
            summary_tobs.append(tobs_dict)
            return jsonify(summary_tobs)
            
    
    return jsonify({"error":f"The date {start} is not found, use format yyyy-mm-dd"}), 404


@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.date),func.max(Measurement.date),func.min(Measurement.tobs),func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs),2)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    summary_tobs = []
    for result in results:
        if result[0] == start and result[1] == end:
            tobs_dict = {}
            tobs_dict["Minimum temperature"] = result[2]
            tobs_dict["Maximum temperature"] = result[3]
            tobs_dict["Average temperature"] = result[4]
            summary_tobs.append(tobs_dict)
            return jsonify(summary_tobs)
            
    
    return jsonify({"error":f"The date {start} or {end} is not found, use format yyyy-mm-dd"}), 404

if __name__ == "__main__":
    app.run(debug=True)
