

import pandas as pd

TARGET_CLUB_ID = 131
TARGET_CLUB_NAME = "FC Barcelona"


def load_games(data_dir: str) -> pd.DataFrame:
    games = pd.read_csv(f"{data_dir}/games.csv")

    games = games.loc[
        (games["home_club_id"] == TARGET_CLUB_ID)
        | (games["away_club_id"] == TARGET_CLUB_ID)
    ]

    return games


def load_appearances(data_dir: str, valid_game_ids: set) -> pd.DataFrame:
    appearances = pd.read_csv(f"{data_dir}/appearances.csv")

    appearances = appearances.loc[
        appearances["player_club_id"] == TARGET_CLUB_ID
    ]

    appearances = appearances.loc[
        appearances["game_id"].isin(valid_game_ids)
    ]

    return appearances


def load_transfers(data_dir: str) -> pd.DataFrame:
    transfers = pd.read_csv(f"{data_dir}/transfers.csv")

    transfers = transfers.loc[
        (transfers["from_club_id"] == TARGET_CLUB_ID)
        | (transfers["to_club_id"] == TARGET_CLUB_ID)
    ]

    return transfers


def load_player_valuations(data_dir: str) -> pd.DataFrame:
    player_valuations = pd.read_csv(
        f"{data_dir}/player_valuations.csv"
    )
    return player_valuations


def load_raw_data(data_dir: str) -> dict:
    games = load_games(data_dir)

    valid_game_ids = set(games["game_id"])

    appearances = load_appearances(
        data_dir,
        valid_game_ids
    )

    transfers = load_transfers(data_dir)

    player_valuations = load_player_valuations(data_dir)

    return {
        "games": games,
        "appearances": appearances,
        "transfers": transfers,
        "player_valuations": player_valuations,
    }


