import pandas as pd

def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["home_club_goals", "away_club_goals"])
    return df


def clean_appearances(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["minutes_played"] > 0].copy()
    df["goals"] = df["goals"].fillna(0)
    df["assists"] = df["assists"].fillna(0)
    df["yellow_cards"] = df["yellow_cards"].fillna(0)
    df["red_cards"] = df["red_cards"].fillna(0)
    df = df.drop_duplicates(subset=["game_id", "player_id"])
    return df


def clean_transfers(df: pd.DataFrame) -> pd.DataFrame:
    df["transfer_date"] = pd.to_datetime(df["transfer_date"])
    df["transfer_fee"] = df["transfer_fee"].fillna(0)
    return df

def clean_player_valuations(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["current_club_name"] == "FC Barcelona"]
    df["date"] = pd.to_datetime(df["date"])
    df = df[
        (df["date"] >= "2012-08-01") &
        (df["date"] < "2026-08-01")
    ]
    return df