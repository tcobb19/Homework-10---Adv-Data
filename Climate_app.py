#import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from dateutil import parser as ps
# Flask Setup
app = Flask(__name__)

# SQLAlchemy engine setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask Routes

@app.route("/")

def home():
    return(f"Welcome to the Hawaii climate app!</br>"
           f"For precipitation by date for the past year go to /api/v1.0/precipitation</br>"
           f"For a list of stations go to /api/v1.0/stations</br>"
           f"For daily temperatures from the past year go to /api/v1.0/tobs</br></br>"
           f"For the minimum, maximum, and average temperatures in a date range please go to /api/v1.0/start-date/end-date</br>"
           f"or leave the end undefined to see all dates to most recent.</br>"
           f"Enter dates in format YYYY-MM-DD"
           )

@app.route("/api/v1.0/precipitation")

def precip():
    lastdate = ps.parse(engine.execute('Select max(date) from measurement').fetchall()[0][0])
    oneyear = dt.timedelta(days=365)
    prvdate = lastdate - oneyear
    lastdatestr = lastdate.strftime('%Y-%m-%d')
    prvdatestr = prvdate.strftime('%Y-%m-%d')
    lastyr =  session.query(Measurement.date, func.sum(Measurement.prcp)).filter(Measurement.date.between(prvdatestr, lastdatestr)).\
group_by(Measurement.date).order_by(Measurement.date).all()
    yeardict = {}
    for row in lastyr:
        yeardict[row[0]] = row[1]
    return jsonify(yeardict)

@app.route("/api/v1.0/stations")

def stations():
    stationsq =  session.query(Station.station).all()

    stations = []
    for item in stationsq:
        stations.append(item)
        
    return jsonify(stations)

@app.route('/api/v1.0/tobs')

def tobs():
    lastdate = ps.parse(engine.execute('Select max(date) from measurement').fetchall()[0][0])
    oneyear = dt.timedelta(days=365)
    prvdate = lastdate - oneyear
    lastdatestr = lastdate.strftime('%Y-%m-%d')
    prvdatestr = prvdate.strftime('%Y-%m-%d')
    lastyr =  session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date.between(prvdatestr, lastdatestr)).\
group_by(Measurement.date).order_by(Measurement.date).all()
    yeardict = {}
    for row in lastyr:
        yeardict[row[0]] = row[1]
    return jsonify(yeardict)

@app.route('/api/v1.0/<start>')

def open_temp(start):
    lastdate = engine.execute('Select max(date) from measurement').fetchall()[0][0]
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start, lastdate)).all()
    return jsonify(temps)

@app.route('/api/v1.0/<start>/<end>')

def closed_temp(start, end):
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)