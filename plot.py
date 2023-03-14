import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("./data.csv")
ax = df.plot.bar(x="team", rot=60)

plt.show()
# plt.plot(team_tough.keys(), d, label="Luck of team")
  
# plt.plot(team_tough.keys(), epas, label="EPA of team")
# plt.xlabel("Team Number")
# plt.xticks(rotation = 45)

# plt.title("Luck and EPA for each team at Utah")
# plt.legend()
# plt.show()