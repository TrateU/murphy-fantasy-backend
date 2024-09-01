import json
import getTeamStats
import getMatchup
import weeklyScores


with open('test.json','w') as f:
    
    json.dump(getTeamStats.getStats(2023), f)