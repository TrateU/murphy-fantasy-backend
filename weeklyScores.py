
import requests
import json
import pandas as pd

def getWeeklyScores(year):
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

    # Convert custom data to a dictionary for quick lookups
    custom_member_map = {entry['member_id']: entry['name'] for entry in custom_data}

    # Define a function to enrich teams with owner names using custom data
    def enrich_teams_with_owners(teams, member_map):
        for team in teams:
            owner_id = team.get('primaryOwner')  # Use .get() to avoid KeyError
            if owner_id:
                team['ownerName'] = member_map.get(owner_id, 'Unknown Owner')
            else:
                team['ownerName'] = 'Unknown Owner'  # Default value if 'primaryOwner' is not present
            team['teamId'] = team['id']
            team['teamName'] = team['name']  # Combine location and nickname to form team name
        return teams

    # Fetch data from both URLs
    matchup_response_A = requests.get(url_A, params={"view": "mMatchup"})
    team_response_A = requests.get(url_A, params={"view": "mTeam"})
    matchup_response_B = requests.get(url_B, params={"view": "mMatchup"})
    team_response_B = requests.get(url_B, params={"view": "mTeam"})

    # Transform the response into JSON
    matchup_json_A = matchup_response_A.json()
    team_json_A = team_response_A.json()
    matchup_json_B = matchup_response_B.json()
    team_json_B = team_response_B.json()

    # Extract teams and members
    members_A = team_json_A['members']
    teams_A = team_json_A['teams']
    members_B = team_json_B['members']
    teams_B = team_json_B['teams']

    # Enrich teams with owner names using custom data
    teams_A_enriched = enrich_teams_with_owners(teams_A, custom_member_map)
    teams_B_enriched = enrich_teams_with_owners(teams_B, custom_member_map)

    # Convert enriched team data to DataFrames
    team_df_A = pd.json_normalize(teams_A_enriched)
    team_df_B = pd.json_normalize(teams_B_enriched)

    # Define the column names needed for matchups
    matchup_column_names = {
        'matchupPeriodId':'Week', 
        'away.teamId':'Team1', 
        'away.totalPoints':'Score1',
        'home.teamId':'Team2', 
        'home.totalPoints':'Score2',
    }

    # Transform and process DataFrames for dataset A
    matchup_df_A = pd.json_normalize(matchup_json_A['schedule'])
    matchup_df_A = matchup_df_A.reindex(columns=matchup_column_names).rename(columns=matchup_column_names)

    matchup_df_A = matchup_df_A.rename(columns={"Team1":"id"})
    matchup_df_A = matchup_df_A.merge(team_df_A[['teamId', 'ownerName', 'teamName']], left_on='id', right_on='teamId', how='left')
    matchup_df_A = matchup_df_A.rename(columns={'ownerName': 'Name1', 'teamName': 'TeamName1'})
    matchup_df_A = matchup_df_A[['Week', 'Name1', 'TeamName1', 'Score1', 'Team2', 'Score2']]

    matchup_df_A = matchup_df_A.rename(columns={"Team2":"id"})
    matchup_df_A = matchup_df_A.merge(team_df_A[['teamId', 'ownerName', 'teamName']], left_on='id', right_on='teamId', how='left')
    matchup_df_A = matchup_df_A.rename(columns={'ownerName': 'Name2', 'teamName': 'TeamName2'})
    matchup_df_A = matchup_df_A[['Week', 'Name1', 'TeamName1', 'Score1', 'Name2', 'TeamName2', 'Score2']]

    # Transform and process DataFrames for dataset B
    matchup_df_B = pd.json_normalize(matchup_json_B['schedule'])
    matchup_df_B = matchup_df_B.reindex(columns=matchup_column_names).rename(columns=matchup_column_names)

    matchup_df_B = matchup_df_B.rename(columns={"Team1":"id"})
    matchup_df_B = matchup_df_B.merge(team_df_B[['teamId', 'ownerName', 'teamName']], left_on='id', right_on='teamId', how='left')
    matchup_df_B = matchup_df_B.rename(columns={'ownerName': 'Name1', 'teamName': 'TeamName1'})
    matchup_df_B = matchup_df_B[['Week', 'Name1', 'TeamName1', 'Score1', 'Team2', 'Score2']]

    matchup_df_B = matchup_df_B.rename(columns={"Team2":"id"})
    matchup_df_B = matchup_df_B.merge(team_df_B[['teamId', 'ownerName', 'teamName']], left_on='id', right_on='teamId', how='left')
    matchup_df_B = matchup_df_B.rename(columns={'ownerName': 'Name2', 'teamName': 'TeamName2'})
    matchup_df_B = matchup_df_B[['Week', 'Name1', 'TeamName1', 'Score1', 'Name2', 'TeamName2', 'Score2']]

    # Create scores_df for dataset A
    scores_df_A = pd.DataFrame()
    scores_df_A = scores_df_A._append(matchup_df_A[['Week', 'Name1', 'TeamName1', 'Score1']].rename(columns={'Name1': 'Name', 'TeamName1': 'Team', 'Score1': 'Score'}))
    scores_df_A = scores_df_A._append(matchup_df_A[['Week', 'Name2', 'TeamName2', 'Score2']].rename(columns={'Name2': 'Name', 'TeamName2': 'Team', 'Score2': 'Score'}))
    scores_df_A = scores_df_A.dropna().reset_index(drop=True)

    # Create scores_df for dataset B
    scores_df_B = pd.DataFrame()
    scores_df_B = scores_df_B._append(matchup_df_B[['Week', 'Name1', 'TeamName1', 'Score1']].rename(columns={'Name1': 'Name', 'TeamName1': 'Team', 'Score1': 'Score'}))
    scores_df_B = scores_df_B._append(matchup_df_B[['Week', 'Name2', 'TeamName2', 'Score2']].rename(columns={'Name2': 'Name', 'TeamName2': 'Team', 'Score2': 'Score'}))
    scores_df_B = scores_df_B.dropna().reset_index(drop=True)

    # Combine scores_df_A and scores_df_B
    scores_df = pd.concat([scores_df_A, scores_df_B], ignore_index=True)

    # Sort by Name and then Week
    scores_df = scores_df.sort_values(by=['Name','Team' ,'Week', ], ascending=[True, True, True]).reset_index(drop=True)

    scores_df.loc[(scores_df['Name'] == 'Brian G') & (scores_df['Team'] == 'The BumperKarls'), 'Name'] = 'Kyle'
    scores_df.loc[(scores_df['Name'] == 'Trate') & (scores_df['Team'] == 'Jack Emmett'), 'Name'] = 'Jack Em'
    scores_df.loc[(scores_df['Name'] == 'Unknown Owner') & (scores_df['Team'] == "I'm Up Right"), 'Name'] = 'Tyler'
    scores_df.loc[(scores_df['Name'] == 'Brian Jr') & (scores_df['Team'] == "P U "), 'Name'] = 'Brian Sr'
    # Save to CSV
    #scores_df.to_csv(f'./public/data/scores{year}.csv', index=False)

    result = scores_df.groupby('Week').apply(lambda x: x[['Name', 'Team', 'Score']].to_dict(orient='records')).reset_index()

    # Rename columns for the final output
    result.columns = ['Week', 'Scores']

    # Convert the DataFrame to the desired JSON format
    weekly_scores = {"WeeklyScores": result.to_dict(orient='records')}
    
    schedule_json = json.load(open(f'schedules/{year}_schedule.json'))

    matchups_mapping = {entry['Week']: entry['Matchups'] for entry in schedule_json['Schedule']}

    for week_entry in weekly_scores['WeeklyScores']:
        week = week_entry['Week']
        if week in matchups_mapping:
            week_entry['Matchups'] = matchups_mapping[week]
    
    if year == 2021:
        week = {"Week": 17, 
                "Scores": [
                    {"Name":"Scott","Team":"I Love Monday Points!","Score":156.76},
                    {"Name":"Dan","Team":"Future #1 Outlaw","Score":176.06}
                ],
                "Matchups": [{"teamA":"Scott","teamB":"Dan"}]
                }
        weekly_scores['WeeklyScores'].append(week)
        for week_entry in weekly_scores['WeeklyScores']:
            if week_entry['Week'] == 16:
                for team in week_entry['Scores']:
                    if team['Name'] == 'Kyle':
                        team['Score'] = 141.10
                    if team['Name'] == 'Scott':
                        team['Score'] = 180.22
                    if team['Name'] == 'Dan':
                        team['Score'] = 198.92
                    if team['Name'] == 'Peyton':
                        team['Score'] = 132.24

        



    weekly_scores = json.dumps(weekly_scores, indent=1)
    
    return weekly_scores