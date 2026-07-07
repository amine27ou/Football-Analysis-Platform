from load import load_raw_data
from clean import (
    clean_games,
    clean_appearances,
    clean_transfers,
    clean_player_valuations
)
from transform import save_match_summary

DATA_DIR = "data/raw"


def main():
    # Load raw data
    raw = load_raw_data(DATA_DIR)

    # Clean datasets
    games_clean = clean_games(raw["games"])
    appearances_clean = clean_appearances(raw["appearances"])
    transfers_clean = clean_transfers(raw["transfers"])
    player_valuations_clean = clean_player_valuations(raw["player_valuations"])

    # Keep only players with a goal or assist
    performers = appearances_clean[
        (appearances_clean["goals"] + appearances_clean["assists"]) > 0
    ]

    # Build game_id -> performers mapping
    performers_by_game = {
        game_id: group
        for game_id, group in performers.groupby("game_id")
    }

    # Generate summaries
    output_dir = save_match_summary(
        games_clean,
        performers_by_game
    )

    print("\n=== Pipeline Complete ===")
    print(f"Games: {len(games_clean)}")
    print(f"Appearances: {len(appearances_clean)}")
    print(f"Transfers: {len(transfers_clean)}")
    print(f"Match summaries created: {len(games_clean)}")
    print(f"Players {len(player_valuations_clean)}")
    print(f"Output folder: {output_dir}")


if __name__ == "__main__":
    main()