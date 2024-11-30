from flask import Flask, jsonify
from data_store import NHLData
from markupsafe import escape

app = Flask(__name__)
nhl = NHLData()

@app.route("/")
def print_schedule():
    sched = nhl.get_schedule()
    return f"<p>{escape(sched[0])}</p>"