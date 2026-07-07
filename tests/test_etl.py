import pandas as pd

from etl.clean import clean_games


def test_clean_games_keeps_fiwc_2021_and_filters_competitions():
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "competition_id": "FIWC",
                "season": 2021,
                "date": "2022-12-18",
                "home_club_goals": 3,
                "away_club_goals": 2,
            },
            {
                "game_id": 2,
                "competition_id": "FIWC",
                "season": 2020,
                "date": "2021-12-18",
                "home_club_goals": 2,
                "away_club_goals": 1,
            },
            {
                "game_id": 3,
                "competition_id": "ES1",
                "season": 2022,
                "date": "2022-08-14",
                "home_club_goals": 1,
                "away_club_goals": 0,
            },
        ]
    )

    cleaned = clean_games(games, ["FIWC", "ES1"])

    assert cleaned["game_id"].tolist() == [1, 3]
