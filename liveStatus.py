import json
import requests

def getLiveStatus(year,week):
    url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={year}&week={week}'


    scoreboard_response = requests.get(url).json()

    teams = {"teams":[]}
    for i in range(1,35):
        teams["teams"].append({"id": i})

    for team in teams["teams"]:
        for event in scoreboard_response['events']:
            for competitor in event["competitions"][0]["competitors"]:
                if int(competitor['id']) == team['id']:
                    team['name'] = competitor['team']['name']
                    team['abbrev'] = competitor['team']['abbreviation']
                    team['gameStatus'] = event['status']['type']['name']
                    break


    #with open('test_2.json', 'w') as f:
        #json.dump(teams,f)

    return teams


#getLiveStatus(2024,1)