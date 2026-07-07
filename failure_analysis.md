# Failure Analysis

## 1. German Club Names Not Cleaned
**What happened:** Club name cleaning only strips English legal suffixes
("Football Club", "Association"). German clubs with "Fußball" in their
name (e.g. "1. Fußball- und Sportverein Mainz 05", "1. Fußball-Club Köln")
pass through unchanged.

**Impact:** Inconsistent club names in match summaries. English clubs are
normalized, German clubs are not. This adds noise to embedded documents
and may reduce retrieval quality for German club queries.

**Fix:** Not applied. German football club naming conventions are complex
and varied — a robust solution would require a lookup table or external
normalization library. Scope was not justified for this project.

**Lesson:** String replacement is brittle for multilingual data. A
club name normalization table keyed on club_id would be more reliable
than pattern matching on raw strings.

---
## Barca home detection
**What happened:** Initial implementation used string matching 
("Barcelona" in home_club_name) to determine home/away context.
**Risk:** Fragile — club name format varies across the dataset.
**Fix:** Replaced with club_id comparison (home_club_id == 131), 
which is stable and unambiguous.
## Embedder indentation bug — 0 vectors stored
**What happened:** Result logic, metadata construction, and 
collection.add() were all outside the for loop due to incorrect 
indentation. The loop iterated over all 800 files but only 
processed the last one, and only if it was a Draw.
**Symptom:** collection.count() returned 0.
**Fix:** Moved all processing logic inside the for loop. 
Moved BARCA_ID to module level as a constant.
**Lesson:** Always verify collection.count() immediately after 
embedding — never assume the write succeeded.
## Embedding model fails on natural-language queries
**What happened:** all-MiniLM-L6-v2 retrieved irrelevant matches for 
conversational questions like "did Messi score in the second leg 
against Juventus in 2017" — zero Juventus games in top 5 results, 
despite an exact-match Juventus game existing in the collection.
Bare keyword queries ("Juventus") worked correctly; natural sentences did not.
**Root cause:** Small embedding models lose signal on specific named 
entities when surrounded by generic conversational language.
**Fix:** Built a hardcoded club-alias map (CLUB_ALIASES) to detect 
known club names in user questions, then applied it as a ChromaDB 
metadata `$or` filter (home_team/away_team) alongside the semantic 
query — hybrid search instead of pure vector search.
**Lesson:** Pure semantic search is not reliable for entity-specific 
factual retrieval with small embedding models. Validate retrieval 
quality with realistic user phrasing, not just clean keyword queries.
## player_valuations club_id filter is unreliable
**What happened:** load.py filtered player_valuations by 
current_club_id == 131, assuming it mapped reliably to FC Barcelona.
**Reality:** club_id 131 appears on 61 different clubs in this file,
returning 884 rows — of which 317 legitimate Barcelona rows were 
missed because they had a different club_id value.
**Fix:** Removed club_id filter from load.py entirely. 
Added clean_player_valuations() in clean.py that filters by 
current_club_name == "FC Barcelona" — returning the correct 
927 rows after date clipping to 2012-2025.
**Lesson:** Never assume ID fields are consistent across CSV files 
in the same dataset. Verify every filter against the actual data.