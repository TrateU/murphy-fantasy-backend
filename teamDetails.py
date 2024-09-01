import json
import getTeamStats
import requests

def getTeamDetails(year):
    league_id_A = 52278251
    league_id_B = 1306743362

    url_A = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_A}'
    url_B = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_B}'
    url = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}'

    rosters_response_A = requests.get(url_A, params={"view": "mRoster"}).json()
    rosters_response_B = requests.get(url_B, params={"view": "mRoster"}).json()
    team_response_A = requests.get(url_A, params={"view": "mTeam"}).json()
    team_response_B = requests.get(url_B, params={"view": "mTeam"}).json()
    proTeam_response = requests.get(url, params={"view":"proTeamSchedules_wl"}).json()

    

    teamStats = getTeamStats.getStats(year)

    rosters = {"teams":[]}

    def populateRosters(rosterResponse, teamResponse):
        for team in rosterResponse["teams"]:
            add_team = {}
            for fullTeam in teamResponse["teams"]:
                if fullTeam['id'] == team['id']:
                    add_team['Team'] = fullTeam['name']
                    add_team['ownerId'] = fullTeam['primaryOwner']
            add_team['roster'] = []
            for player in team["roster"]["entries"]:
                new_player = {}
                
                new_player['name'] = player["playerPoolEntry"]["player"]["fullName"]
                match player["lineupSlotId"]:
                    case 0:
                        new_player['slot'] = "QB"
                    case 2:
                        new_player['slot'] = "RB"
                    case 4:
                        new_player["slot"] = "WR"
                    case 6:
                        new_player["slot"] = "TE"
                    case 16:
                        new_player["slot"] = "D/ST"
                    case 17:
                        new_player["slot"] = "K"
                    case 20:
                        new_player["slot"] = "Bench"
                    case 21:
                        new_player["slot"] = "IR"
                    case 23:
                        new_player["slot"] = "FLEX"
                match player["playerPoolEntry"]["player"]["defaultPositionId"]:
                    case 1:
                        new_player['position'] = "QB"
                    case 2:
                        new_player['position'] = "RB"
                    case 3:
                        new_player["position"] = "WR"
                    case 4:
                        new_player["position"] = "TE"
                    case 5:
                        new_player["position"] = "K"
                    case 16:
                        new_player["position"] = "D/ST"

                id = player['playerPoolEntry']['player']['proTeamId']

                for proTeam in proTeam_response['settings']['proTeams']:
                    if id == proTeam['id']:
                        new_player['team'] = proTeam['abbrev']
                        new_player['bye'] = proTeam['byeWeek']

                new_player['averagePoints'] = 0
                new_player['totalPoints'] = 0
                for stat in player['playerPoolEntry']['player']['stats']:
                    if stat['scoringPeriodId'] == 0 and stat['statSourceId'] == 0:
                        new_player['averagePoints'] = stat['appliedAverage']
                        new_player['totalPoints'] = stat['appliedTotal']
                        break
                new_player["posRank"] = player['playerPoolEntry']["ratings"]["0"]["positionalRanking"]

                    
                add_team['roster'].append(new_player)

            rosters["teams"].append(add_team)

    populateRosters(rosters_response_A,team_response_A)
    populateRosters(rosters_response_B,team_response_B)

    for team in teamStats["teamStats"]:
        team['Roster'] = []
        for roster in rosters['teams']:
            if roster['Team'] == team['Team']:
                team["Roster"] = roster['roster']
                break
    
    return teamStats
