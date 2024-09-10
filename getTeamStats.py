import requests
import json
import pandas as pd
import weeklyScores
from datetime import datetime
import info

def getStats(year):
    # Define league IDs and year
    league_id_A = 52278251
    league_id_B = 1306743362

    # Define URLs
    url_A = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_A}'
    url_B = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_B}'

    today = datetime.today()
    load_Data = json.loads(weeklyScores.getWeeklyScores(year))

    stats = {'teamStats': []}

    def isDivision(data, teamA, teamB):
        divA = ''
        divB = ''
        for team in data['teamStats']:
            if teamA == team['Name']:
                divA = team['Division']
                continue
            if teamB == team['Name']:
                divB = team['Division']
                continue
        if divA == divB:
            return 'Y'
        else:
            return 'N'
            

    for team in load_Data['WeeklyScores'][0]['Scores']:
        new_team = {}
        new_team['Name'] = team['Name']
        new_team['Team'] = team['Team']
        stats['teamStats'].append(new_team)
    
    for team in stats['teamStats']:
        for memeber in info.custom_data:
            if team['Name'] == memeber['name']:
                team['Division'] = memeber[f'{year}div']

    for team in stats['teamStats']:
        #Setting weekly score details.
        team['Scores'] = []
        for week in load_Data['WeeklyScores']:
            new_score = {}
            new_score['Week'] = week['Week']
            new_score['Opponent'] = ""
            new_score['isDivision'] = ''
            for matchup in week['Matchups']:
                if matchup['teamA'] == team['Name']:
                    new_score['Opponent'] = matchup['teamB']
                    new_score['isDivision'] = isDivision(stats,team['Name'],new_score['Opponent'])
                    break
                if matchup['teamB'] == team['Name']:
                    new_score['Opponent'] = matchup['teamA']
                    new_score['isDivision'] = isDivision(stats,team['Name'],new_score['Opponent'])
                    break
            new_score['For'] = 0
            new_score['Against'] = 0
            for teamScores in week['Scores']:
                if teamScores['Name'] == team['Name']:
                    new_score['For'] = teamScores['Score']
                if teamScores['Name'] == new_score['Opponent']:
                    new_score['Against'] = teamScores['Score']
            team['Scores'].append(new_score)
        
        #Setting Wins,Losses,Points For, Points Against, Division Wins, Division Losses
        team['Wins'] = 0
        team['Losses'] = 0
        team['TotalFor'] = 0.0
        team['TotalAgainst'] = 0.0
        team['DivWins'] = 0
        team['DivLosses'] = 0
        for score in team['Scores']:
            if score['Week'] > 14:
                break
            score["Result"] = 'NA'
            isPast = False
            if year < info.currentYear:
                isPast = True
            else:
                for weeks in info.weekdates2024:
                    if weeks['Week'] == score['Week']:
                        if today >= datetime.strptime(weeks['end'],"%Y-%m-%d"): 
                            isPast = True
            if isPast:
                team['TotalFor'] += score['For']
                team['TotalAgainst'] += score['Against']
                if score['For'] > score['Against']: 
                    team['Wins'] += 1
                    score['Result'] = 'W'
                    if score['isDivision'] == 'Y':
                        team['DivWins'] += 1
                if score['For'] < score['Against']: 
                    team['Losses'] += 1
                    score['Result'] = 'L'
                    if score['isDivision'] == 'Y':
                        team['DivLosses'] += 1
        team['PointDiff'] = team['TotalFor'] - team['TotalAgainst']
        team['wPercentage'] = 0.0
        team['wDivPercentage'] = 0.0

        if team['Wins'] + team['Losses'] > 0:
            team['wPercentage'] = team['Wins'] / (team['Wins'] + team['Losses'])
        if team['DivWins'] + team['DivLosses'] > 0:
            team['wDivPercentage'] = team['DivWins'] / (team['DivWins'] + team['DivLosses'])
    
    return stats
