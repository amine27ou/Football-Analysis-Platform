import pandas as pd
pv = pd.read_csv("data/raw/player_valuations.csv")

by_id = pv[pv["current_club_id"] == 131]
by_name = pv[pv["current_club_name"] == "FC Barcelona"]

print(f"Filter by club_id 131: {len(by_id)}")
print(f"Filter by name 'FC Barcelona': {len(by_name)}")

# Rows in name filter but NOT in id filter
only_in_name = by_name[~by_name.index.isin(by_id.index)]
print(f"Rows only caught by name filter: {len(only_in_name)}")