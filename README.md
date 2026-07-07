# CulerAI — FC Barcelona Performance & Transfer Analytics (2012–2025)

An AI-powered analytics platform for FC Barcelona, built on 14 seasons of match,
transfer, and squad valuation data from Transfermarkt. Combines an ETL pipeline,
a RAG (Retrieval-Augmented Generation) query engine, and an interactive Streamlit
dashboard.

---

## What It Does

- **Ask CulerAI** — Natural language Q&A about Barcelona's history, grounded in
  real match data. No hallucinations: the LLM is constrained to answer only from
  retrieved match summaries.
- **Match Browser** — Filter and browse all 800 Barcelona matches by season,
  competition, and result.
- **Squad Value Timeline** — Track the squad's total market value across 14
  seasons, from the peak Messi era to the financial crisis and the current rebuild.
- **Transfer Activity** — Season-by-season spend, income, and net transfer
  balance, with a table of all major transfers (≥ €20M).

---

## Dataset

**Source:** [Transfermarkt dataset by davidcariboo](https://www.kaggle.com/datasets/davidcariboo/player-scores)

Download the dataset from Kaggle and place the CSV files in `data/raw/`. The
following files are required:

```
data/raw/
├── games.csv
├── appearances.csv
├── clubs.csv
├── competitions.csv
├── players.csv
├── transfers.csv
└── player_valuations.csv
```

> `data/raw/` is **read-only**. Never modify these files directly.

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

Get a free API key at [console.groq.com](https://console.groq.com).

```bash
# macOS / Linux
export GROQ_API_KEY="your_key_here"

# Windows (PowerShell)
$env:GROQ_API_KEY = "your_key_here"
```

### 4. (Optional) Add the Barcelona logo

Place a logo image at `app/assets/logo.avif`. The dashboard will display a
fallback icon if the file is not found.

---

## Running the Project

Run these steps **in order**. Each step depends on the output of the previous one.

### Step 1 — ETL Pipeline

Filters all raw CSVs to FC Barcelona (club_id 131), cleans the data, and
generates 800 match summary `.txt` files in `summaries/matches/`.

```bash
cd etl
python pipeline.py
```

Expected output:
```
=== Pipeline Complete ===
Games: 800
Appearances: 11371
Transfers: 319
Match summaries created: 800
Players: 927
Output folder: summaries/matches
```

### Step 2 — Embed Summaries

Embeds all 800 match summaries using `all-MiniLM-L6-v2` and stores them in a
ChromaDB vector database at `chroma_store/`.

```bash
cd ..
python -c "
import sys
sys.path.insert(0, 'etl')
from load import load_raw_data
from clean import clean_games
from pathlib import Path
from rag.embedder import embed_summaries

data = load_raw_data('data/raw')
games = clean_games(data['games'])
embed_summaries(Path('summaries/matches'), games)
"
```

Verify the vector count after embedding:
```bash
python -c "
import chromadb
c = chromadb.PersistentClient(path='chroma_store')
print('Vectors stored:', c.get_collection('barca_history').count())
"
```

Expected: `Vectors stored: 800`

### Step 3 — Run the Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Project Structure

```
football_analysis/
│
├── data/
│   ├── raw/                  # Kaggle CSVs — read-only
│   └── processed/            # Reserved for future SQLite output
│
├── etl/
│   ├── load.py               # Load and filter CSVs to Barcelona
│   ├── clean.py              # Data cleaning and normalization
│   ├── transform.py          # Match summary text generation
│   ├── aggregations.py       # Squad value and transfer aggregations
│   └── pipeline.py           # Orchestrates ETL end-to-end
│
├── rag/
│   ├── embedder.py           # Embeds summaries into ChromaDB
│   ├── retriever.py          # Semantic + metadata hybrid search
│   └── query_engine.py       # Groq LLM query engine (CulerAI)
│
├── summaries/
│   └── matches/              # 800 .txt match summaries (ETL output)
│
├── chroma_store/             # ChromaDB persistent vector store
│
├── app/
│   ├── streamlit_app.py      # Dashboard UI
│   └── assets/
│       └── logo.avif         # Club logo (not included in repo)
│
├── failure_analysis.md       # Documented bugs and engineering decisions
├── requirements.txt
└── README.md
```

---

## Architecture

```
Kaggle CSVs
    │
    ▼
ETL Pipeline (etl/)
    │  Filter to FC Barcelona (club_id 131 / name matching)
    │  Clean dates, nulls, deduplication
    │  Generate match summaries (.txt)
    │
    ▼
RAG Pipeline (rag/)
    │  Embed summaries → all-MiniLM-L6-v2 → ChromaDB
    │  Hybrid retrieval: semantic + club-name metadata filter
    │  LLM grounding: Groq llama-3.1-8b-instant
    │
    ▼
Streamlit Dashboard (app/)
    │  4 tabs: Chat, Match Browser, Squad Value, Transfers
    │  Barcelona branding: maroon #A50044, blue #004D98
```

---

## Known Limitations

**1. Opponent scorer data is unavailable.**
Match summaries only capture Barcelona players' contributions (goals, assists).
If a question asks who scored *against* Barcelona, the system will correctly
say it doesn't know — this is not a hallucination but a genuine data gap.
Penalty shootout goals are also not recorded in `appearances.csv`.

**2. Semantic retrieval degrades with natural-language phrasing.**
The embedding model (`all-MiniLM-L6-v2`) loses signal on named entities when
surrounded by conversational language. This is mitigated by a club-alias
metadata filter (`CLUB_ALIASES` in `query_engine.py`) that detects known club
names in user questions and applies a hard ChromaDB `$or` filter. Queries
mentioning no specific club rely on pure semantic search and may return less
relevant results.

**3. player_valuations club_id is unreliable.**
`current_club_id == 131` maps to 61 different clubs in this file. All filtering
on player valuations uses `current_club_name == "FC Barcelona"` instead.
See `failure_analysis.md` for full details.

**4. Season scope is 2012–2025.**
The Transfermarkt dataset extends further, but this project is scoped to the
seasons present in `games.csv` for Barcelona. All aggregations (squad value,
transfers) are clipped to this range for consistency.

---

## Dependencies

Key libraries:
- `pandas` — data manipulation
- `sentence-transformers` — text embedding (`all-MiniLM-L6-v2`)
- `chromadb` — vector database
- `groq` — LLM API client
- `streamlit` — dashboard UI
- `plotly` — interactive charts

Full list: see `requirements.txt`.