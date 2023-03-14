import statbotics, tbapy
import matplotlib.pyplot as plt
import pandas
from os import environ
from dotenv import load_dotenv
load_dotenv()

#Initialize Stuff
api_key = environ.get("TBA_API_KEY")
event_code = "2023utwv"

sb = statbotics.Statbotics()
tba = tbapy.TBA(api_key)

#Get avg EPA over all teams
avg_epa = sb.get_event(event_code, ["epa_mean"])["epa_mean"]
print("AVG EPA:", avg_epa)

#Get list of teams
teams = [str(team["team_number"]) for team in tba.event_teams(event_code)]
#Get all the different epa, but we only really need one, I chose before playoffs because it had the smallest prediction error

# teams_epa_mean = {team_num: sb.get_team_event(int(team_num), event_code, ["epa_mean"])["epa_mean"] for team_num in teams}
# teams_epa_end = {team_num: sb.get_team_event(int(team_num), event_code, ["epa_end"])["epa_end"] for team_num in teams}
teams_epa_qual = {team: sb.get_team_event(int(team), event_code, ["epa_pre_playoffs"])["epa_pre_playoffs"] for team in teams}

epa_used = teams_epa_qual

#Get formatted dictionary of ranks
ranks = {team["team_key"][3:]: team["rank"] for team in tba.event_rankings(event_code)['rankings']}
rank_to_epa_ratio = {team: ranks[team]/epa_used[team] for team in teams}

#Format match schedule
matches = [m for m in tba.event_matches(event_code, simple=True) if m['comp_level'] == 'qm']
qual_matches = [None] * len(matches)

for i, match in enumerate(matches):
  blue = [team[3:] for team in match['alliances']['blue']['team_keys']]
  red = [team[3:] for team in match['alliances']['red']['team_keys']]

  qual_matches[match['match_number']-1] = {"red": red, "blue": blue}

#Initialize dictionary of teams advantages
team_adv = {team: [] for team in teams}

#used to find the error
predict_err = []

#WHERE THE MAGIC HAPPENS
for i, match in enumerate(qual_matches):
  #Sums the epas for each alliance
  red_epas = [epa_used[team] for team in match["red"]]
  blue_epas = [epa_used[team] for team in match["blue"]]
  
  #Finds advantage for red (difference of sums)
  red_advantage = sum(red_epas) - sum(blue_epas)
  #Gets match from blue alliance api and adds the prediction error of the match to the array
  m = tba.match(year=2023, event=event_code, type="qm", number=i+1)
  real_diff = m["alliances"]["red"]["score"] - m["alliances"]["blue"]["score"]
  predict_err.append(abs(real_diff - red_advantage))

  #For each alliance, add the advantage (flipped if for blue) and then subsitute the team's EPA for avg EPA to remove bias
  for team in match["red"]:
    team_adv[team].append(red_advantage - epa_used[team] + avg_epa)

  for team in match["blue"]:
    team_adv[team].append(-(red_advantage) - epa_used[team] + avg_epa)

print(sum(predict_err)/len(predict_err))

#Finds average point advantages for each team
team_luck = {team: sum(team_adv[team])/len(team_adv[team]) for team, diff in team_adv.items()}
#Sort dictionary
team_luck = dict(sorted(team_luck.items(), key=lambda x: x[1]))

#Put things in a csv file and plot
data = [(team,diff,epa_used[team], len(teams)+1-ranks[team], rank_to_epa_ratio[team]) for team, diff in team_luck.items()]
df = pandas.DataFrame(data, columns=("team", "luck", "epa", "rank", "rank_epa_ratio"))

df.to_csv("./data.csv")

ax = df.plot.bar(x="team", y=["luck", "epa"], rot=60)

plt.show()
