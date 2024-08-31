from flask import Flask
from flask_cors import CORS
import weeklyScores
import getMatchup
import getTeamStats

api = Flask(__name__)
CORS(api)

@api.route('/scores/<year>')
def get_scores(year):
    scores = weeklyScores.getWeeklyScores(int(year))
    response_body = scores

    return response_body

@api.route('/matchups/<year>/<week>')
def get_matchups(year,week):
    return getMatchup.getDetailedMatchup(year,int(week))

@api.route('/stats/<year>')
def get_teamstats(year):
    return getTeamStats.getStats(int(year))