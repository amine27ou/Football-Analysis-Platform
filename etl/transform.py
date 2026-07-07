import os
import re
import pandas as pd

COMPETITION_IDS = {
    "ES1": "La Liga",
    "CL": "UEFA Champions League",
    "CDR": "Copa del Rey",
    "SUC": "Supercopa de España",
    "EL": "UEFA Europa League",
    "KLUB": "FIFA Club World Cup",
    "USC": "UEFA Super Cup",
}

TARGET_CLUB_ID = 131


def generate_filename(game: pd.Series) -> str:
    home = (
        game["home_club_name"]
        .replace(" ", "_")
        .replace("_Football_Club", "")
        .replace("Association_", "")
        .replace("Futbol_Club_","")
    )

    away = (
        game["away_club_name"]
        .replace(" ", "_")
        .replace("_Football_Club", "")
        .replace("Association_", "")
        .replace("Futbol_Club_","")
    )

    date = game["date"].strftime("%Y-%m-%d")

    home_clean = re.sub(r"[^\w]", "", home)
    away_clean = re.sub(r"[^\w]", "", away)

    competition = game["competition_id"]

    return (
        f"{home_clean}_vs_{away_clean}_"
        f"{date}_{competition}_{game['game_id']}"
    )


def generate_match_summary(
    game: pd.Series,
    top_performers: pd.DataFrame
) -> str:

    home = (
        game["home_club_name"]
        .replace("Football Club", "")
        .replace("Association ", "")
        .replace("Futbol Club","")
        .strip()
    )

    away = (
        game["away_club_name"]
        .replace("Football Club", "")
        .replace("Association ", "")
        .replace("Futbol Club", "")
        .strip()
    )

    competition = COMPETITION_IDS.get(
        game["competition_id"],
        game["competition_id"]
    )

    barca_is_home = game["home_club_id"] == TARGET_CLUB_ID

    if barca_is_home:
        venue = "Home"
        opponent = away
        barca_goals = game["home_club_goals"]
        opponent_goals = game["away_club_goals"]
    else:
        venue = "Away"
        opponent = home
        barca_goals = game["away_club_goals"]
        opponent_goals = game["home_club_goals"]

    if barca_goals > opponent_goals:
        result = "W"
    elif barca_goals < opponent_goals:
        result = "L"
    else:
        result = "D"

    barca_context = (
        f"Barcelona ({venue}) vs {opponent} | "
        f"Result: {result} | "
        f"Score: {barca_goals}-{opponent_goals}"
    )

    date = game["date"].strftime("%Y-%m-%d")

    header = (
        f"{competition} | "
        f"{game['round']} | "
        f"{date} | "
        f"{game['stadium']}"
    )

    score_line = (
        f"{home} {game['home_club_goals']} - "
        f"{game['away_club_goals']} {away}"
    )

    performer_lines = []

    for _, row in top_performers.iterrows():
        performer_lines.append(
            f"- {row['player_name']}: "
            f"{row['goals']} goals, "
            f"{row['assists']} assists, "
            f"{row['minutes_played']} minutes played"
        )

    performers_text = (
        "\n".join(performer_lines)
        if performer_lines
        else "No notable attacking contributions recorded."
    )

    return (
        f"{header}\n\n"
        f"{barca_context}\n\n"
        f"{score_line}\n\n"
        f"Top Performers\n"
        f"{performers_text}"
    )


def save_match_summary(
    games: pd.DataFrame,
    performers_by_game: dict
) -> None:

    output_dir = "summaries/matches"
    os.makedirs(output_dir, exist_ok=True)


    for _, game in games.iterrows():

        filename = generate_filename(game)

        top_performers = performers_by_game.get(
            game["game_id"],
            pd.DataFrame()
        )

        summary = generate_match_summary(
            game,
            top_performers
        )

        with open(
            f"summaries/matches/{filename}.txt",
            "w",
            encoding="utf-8"
        ) as file:
            file.write(summary)
    return output_dir