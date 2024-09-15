import json
import requests
from datetime import datetime
import pytz

def getStart(time):
    dt_utc = datetime.strptime(time, "%Y-%m-%dT%H:%MZ")
    dt_utc = dt_utc.replace(tzinfo=pytz.utc)
    est = pytz.timezone("US/Eastern")
    dt_est = dt_utc.astimezone(est)

    day_of_week = dt_est.strftime("%a")
    time_of_day = dt_est.strftime("%I:%M").lstrip('0')

    return f'{day_of_week} - {time_of_day}'


def getLiveStatus(year,week):
    url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={year}&week={week}'


    scoreboard_response = requests.get(url).json()

    teams = {"teams":[]}
    for i in range(1,35):
        teams["teams"].append({"id": i})

    for team in teams["teams"]:
        team['name'] = ""
        team['abbrev'] = ""
        team['gameStatus'] = ""
        team['start'] = ""
        for event in scoreboard_response['events']:
            for competitor in event["competitions"][0]["competitors"]:
                if int(competitor['id']) == team['id']:
                    if 'name' in competitor['team']:
                        team['name'] = competitor['team']['name']
                    team['abbrev'] = competitor['team']['abbreviation']
                    team['gameStatus'] = event['status']['type']['name']
                    team['start'] = getStart(event['date'])
                    break
        


    with open('test_2.json', 'w') as f:
        json.dump(teams,f)

    return teams


getLiveStatus(2024,2)