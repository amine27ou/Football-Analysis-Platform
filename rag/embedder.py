from pathlib import Path

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

BARCA_ID = 131 

def embed_summaries(summaries_dir: Path, games_df: pd.DataFrame) -> None:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path="chroma_store")
    collection = chroma_client.get_or_create_collection(name="barca_history")

    for txt_file in summaries_dir.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()

        game_id = int(txt_file.stem.split("_")[-1])
        game = games_df[games_df["game_id"] == game_id]

        if game.empty:
            print(f"Game {game_id} not found.")
            continue

        game = game.iloc[0]

        # result logic here, inside the loop
        if game["home_club_id"] == BARCA_ID:
            barca_goals = game["home_club_goals"]
            opponent_goals = game["away_club_goals"]
        else:
            barca_goals = game["away_club_goals"]
            opponent_goals = game["home_club_goals"]

        if barca_goals > opponent_goals:
            result = "Win"
        elif barca_goals < opponent_goals:
            result = "Loss"
        else:
            result = "Draw"

        # metadata, embedding, collection.add all here, inside the loop
        metadata = {
            "game_id": str(game_id),
            "date": str(game["date"]),
            "season": int(game["season"]),
            "competition": game["competition_id"],
            "home_team": game["home_club_name"],
            "away_team": game["away_club_name"],
            "home_goals": int(game["home_club_goals"]),
            "away_goals": int(game["away_club_goals"]),
            "result": result,
        }

        embedding = model.encode(text).tolist()

        collection.add(
            ids=[str(game_id)],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    print("Finished embedding summaries.")

# import chromadb

# client = chromadb.PersistentClient(path="chroma_store")
# collection = client.get_collection("barca_history")

# print(f"Total vectors: {collection.count()}")

# # Test a real query
# results = collection.query(
#     query_texts=["Champions League final"],
#     n_results=3
# )

# for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
#     print(f"\n--- Result {i+1} ---")
#     print(f"Competition: {meta['competition']}")
#     print(f"Date: {meta['date']}")
#     print(f"Result: {meta['result']}")
#     print(doc[:200])
