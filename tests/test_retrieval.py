import pandas as pd
transfers = pd.read_csv("data/processed/transfers.csv")
print(transfers[transfers["player_name"].str.contains("Neymar", case=False)])