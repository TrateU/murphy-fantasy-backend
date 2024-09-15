import requests
import json
import pandas as pd
import liveStatus

def getDetailedMatchup(year,week):
    # Define league IDs and year
    league_id_A = 52278251
    league_id_B = 1306743362

    # Define URLs
    url_A = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_A}'
    url_B = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id_B}'

    # Custom data
    custom_data = [
        {"member_id": "{4AAD9058-FC75-407D-901F-5F00BE21E7CB}", "name": "Matt"},
        {"member_id": "{0F87DB98-AAD6-4018-8A99-4CE4EE5F71C6}", "name": "Jack Em"},
        {"member_id": "{110EE426-6B0F-4FB9-B080-39EC67F770A2}", "name": "Brian Jr"},
        {"member_id": "{57685D79-5D3D-49FE-A85D-795D3DD9FEF0}", "name": "Trate"},
        {"member_id": "{88D64FB7-44C6-4DB5-AFBF-D3136E76744E}", "name": "Sean"},
        {"member_id": "{C732A445-7027-4B50-82BE-9B37760B36A7}", "name": "Jack Jr"},
        {"member_id": "{EA136F56-F17F-4118-936F-56F17F4118A1}", "name": "Michael"},
        {"member_id": "{F98A212C-11B8-4354-8A21-2C11B8E35492}", "name": "Colin"},
        {"member_id": "{FAFD64E5-BFD6-4DFD-BAC5-6F92DB1E33D6}", "name": "Scott"},
        {"member_id": "{0C3DEE60-4AB3-454A-9925-78D9E65D1A1D}", "name": "Brady"},
        {"member_id": "{437A967B-2085-46F3-A046-63D4FA60691B}", "name": "Tyler"},
        {"member_id": "{59565568-0CFC-4DFD-8499-4238E679CD6C}", "name": "Dennis"},
        {"member_id": "{6D56A84B-3DC8-4CB2-AA10-427DE47CF022}", "name": "Peyton"},
        {"member_id": "{AD0C8351-96CF-4C5D-9E9B-0004BA3FD667}", "name": "Dan"},
        {"member_id": "{C3FA1FC7-613C-4FE7-A05C-02608D26ACA4}", "name": "Brian G"},
        {"member_id": "{E126E0E8-A4B6-470C-ACBB-4FFB80D3D383}", "name": "Kyle"},
        {"member_id": "{2C2C9FFD-CDA3-4381-AC9F-FDCDA3A381C7}", "name": "John"},
        {"member_id": "{36C370D4-D94B-4B1C-8C3C-ABB2A5A95DE7}", "name": "Brian Sr"}
    ]

    rosters_response_A = requests.get(url_A, params={"view": "mRoster","scoringPeriodId":week}).json()
    rosters_response_B = requests.get(url_B, params={"view": "mRoster","scoringPeriodId":week}).json()
    team_response_A = requests.get(url_A, params={"view": "mTeam"}).json()
    team_response_B = requests.get(url_B, params={"view": "mTeam"}).json()
    

    

    rosters = {"teams":[]}
    proTeamInfo = liveStatus.getLiveStatus(year,week)

    def populateRosters(rosterResponse, teamResponse, week):
        for team in rosterResponse["teams"]:
            add_team = {}
            add_team['totalPoints'] = 0
            add_team['donePlay'] = 0
            add_team['inPlay'] = 0
            add_team['leftToPlay'] = 0
            add_team['projPoints'] = 0
            for fullTeam in teamResponse["teams"]:
                if fullTeam['id'] == team['id']:
                    add_team['Team'] = fullTeam['name']
                    add_team['ownerId'] = fullTeam['primaryOwner']
            add_team['roster'] = []
            for player in team["roster"]["entries"]:
                new_player = {}
                new_player['points'] = 0
                new_player['projPoints'] = 0
                new_player['status'] = ''
                new_player['proTeamId'] = player['playerPoolEntry']['player']['proTeamId']
                new_player['isFinal'] = False

                for proTeam in proTeamInfo['teams']:
                    if proTeam['id'] == new_player['proTeamId']:
                        new_player["proTeamAbbrev"] = proTeam["abbrev"]
                        new_player["status"] = proTeam['gameStatus']
                        new_player['startTime'] = proTeam['start']

                for stat in player["playerPoolEntry"]["player"]["stats"]:
                    if stat["scoringPeriodId"] == week and stat["statSourceId"] == 0:
                        new_player['points'] = stat['appliedTotal']
                    if stat["scoringPeriodId"] == week and stat["statSourceId"] == 1 and stat["statSplitTypeId"] == 1:
                        new_player["projPoints"] = stat['appliedTotal']

                
                new_player['name'] = player["playerPoolEntry"]["player"]["fullName"]
                match player["lineupSlotId"]:
                    case 0:
                        new_player['position'] = "QB"
                    case 2:
                        new_player['position'] = "RB"
                    case 4:
                        new_player["position"] = "WR"
                    case 6:
                        new_player["position"] = "TE"
                    case 16:
                        new_player["position"] = "D/ST"
                    case 17:
                        new_player["position"] = "K"
                    case 20:
                        new_player["position"] = "Bench"
                    case 21:
                        new_player["position"] = "IR"
                    case 23:
                        new_player["position"] = "FLEX"
                    
                if new_player['position'] != 'Bench' and new_player['position'] != 'IR':
                    add_team['totalPoints'] += new_player['points']
                    match new_player['status']:
                        case 'STATUS_SCHEDULED':
                            add_team["leftToPlay"] += 1
                            add_team['projPoints'] += new_player['projPoints']
                        case 'STATUS_IN_PROGRESS':
                            add_team['inPlay'] += 1
                            add_team['projPoints'] += new_player['projPoints']
                        case 'STATUS_HALFTIME':
                            add_team['inPlay'] += 1
                            add_team['projPoints'] += new_player['projPoints']
                        case 'STATUS_FINAL':
                            add_team['donePlay'] += 1
                            new_player['projPoints'] = new_player['points']
                            add_team['projPoints'] += new_player['points']
                            new_player['isFinal'] = True
                if new_player['status'] == 'STATUS_FINAL':
                    new_player['projPoints'] = new_player['points']
                    new_player['isFinal'] = True


                        
                add_team['roster'].append(new_player)

            rosters["teams"].append(add_team)
    
    populateRosters(rosters_response_A,team_response_A,week)
    populateRosters(rosters_response_B,team_response_B,week)

    for team in rosters["teams"]:
        for owner in custom_data:
            if team["ownerId"] == owner["member_id"]:
                team['Name'] = owner["name"]
                break
            else:
                team['Name'] = 'Unknown Owner'
        if team['Name'] == 'Brian G' and team['Team'] == 'The BumperKarls':
            team['Name'] = 'Kyle'
        if team['Name'] == 'Trate' and team['Team'] == 'Jack Emmett':
            team['Name'] = 'Jack Em'
        if team['Name'] == 'Unknown Owner' and team['Team'] == "I'm Up Right":
            team['Name'] = 'Tyler'
        if team['Name'] == 'Brian Jr' and team['Team'] == "P U ":
            team['Name'] = 'Brian Sr'

    #with open('test.json', 'w') as f:
       # json.dump(rosters,f)
    return rosters

#getDetailedMatchup(2024,1)