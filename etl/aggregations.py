import pandas as pd
import numpy as np

def get_squad_value_by_season(pv_df: pd.DataFrame) -> pd.DataFrame:
    pv_df = pv_df.copy()

    pv_df["date"] = pd.to_datetime(pv_df["date"])

    pv_df = pv_df[
        (pv_df["date"] >= "2012-08-01") &
        (pv_df["date"] < "2026-08-01")
    ]

    pv_df["season"] = pv_df["date"].dt.year
    pv_df.loc[pv_df["date"].dt.month < 8, "season"] -= 1   
    latest = (
        pv_df
        .sort_values("date")
        .groupby(["season","player_id"],as_index=False)
        .last()
    )
    squad_value = (
        latest
        .groupby("season", as_index=False)["market_value_in_eur"]
        .sum()
        .rename(columns={"market_value_in_eur": "total_squad_value"})
    )
    return squad_value  


def get_transfer_activity(transfers_df: pd.DataFrame) -> pd.DataFrame:
    # 1. Copy the dataframe
    transfers_df = transfers_df.copy()

    # 2. Convert transfer_date to datetime
    transfers_df["transfer_date"] = pd.to_datetime(transfers_df["transfer_date"])

    # 3. Extract season using August cutoff
    transfers_df["season"] = transfers_df["transfer_date"].dt.year
    transfers_df.loc[transfers_df["transfer_date"].dt.month < 8, "season"] -= 1

    # 4. Filter to 2012-2025
    transfers_df = transfers_df[
        (transfers_df["season"] >= 2012) &
        (transfers_df["season"] <= 2025)
    ]

    # Keep only Barcelona transfers
    transfers_df = transfers_df[
        (transfers_df["to_club_id"] == 131) |
        (transfers_df["from_club_id"] == 131)
    ]

    # 5. Create direction column
    transfers_df["direction"] = np.where(
        transfers_df["to_club_id"] == 131,
        "In",
        "Out"   
    )

    # 6. Group by season and direction
    transfer = (
        transfers_df
        .groupby(["season", "direction"], as_index=False)["transfer_fee"]
        .sum()
    )

    # 7. Pivot
    transfer = (
        transfer
        .pivot(index="season", columns="direction", values="transfer_fee")
        .fillna(0)
        .rename(columns={               
            "In": "spend",
            "Out": "income"
        })
        .reset_index()
    )

    # Ensure columns exist
    if "spend" not in transfer.columns:
        transfer["spend"] = 0
    if "income" not in transfer.columns:
        transfer["income"] = 0

    # 8. Calculate net
    transfer["net"] = transfer["income"] - transfer["spend"]

    return transfer

from clean import clean_transfers

transfers = pd.read_csv("data/raw/transfers.csv")
transfers = clean_transfers(transfers)

result = get_transfer_activity(transfers)
print(result.to_string())