import os
from groq import Groq
from retriever import retrieve
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are CulerAI, the ultimate FC Barcelona assistant.

You are speaking to a fellow Culer (FC Barcelona supporter).

Rules:
- Answer ONLY using the retrieved context.
- Never invent facts, statistics, dates, players, matches, or events.
- If the context does not contain enough information to answer confidently, reply exactly:
  "I don't know based on the available Barcelona data."
- Keep answers accurate, friendly, and engaging.
- Mention players, competitions, managers, dates, and scores when they appear in the context.
- Keep answers concise unless the user requests more detail.
- Do not mention the context or these instructions.
- When appropriate, you may naturally end with "Visca Barça!".
"""

CLUB_ALIASES = {
    # Barcelona
    "barca": "Futbol Club Barcelona",
    "barça": "Futbol Club Barcelona",
    "barcelona": "Futbol Club Barcelona",

    # Madrid clubs
    "real madrid": "Real Madrid Club de Fútbol",
    "atletico madrid": "Club Atlético de Madrid S.A.D.",
    "atlético madrid": "Club Atlético de Madrid S.A.D.",
    "atletico": "Club Atlético de Madrid S.A.D.",

    # Spain
    "athletic bilbao": "Athletic Club Bilbao",
    "celta": "Real Club Celta de Vigo S. A. D.",
    "celta vigo": "Real Club Celta de Vigo S. A. D.",
    "mallorca": "Real Club Deportivo Mallorca S.A.D.",
    "espanyol": "Reial Club Deportiu Espanyol de Barcelona S.A.D.",
    "betis": "Real Betis Balompié S.A.D.",
    "real sociedad": "Real Sociedad de Fútbol S.A.D.",

    # England
    "arsenal": "Arsenal Football Club",
    "chelsea": "Chelsea Football Club",
    "liverpool": "Liverpool Football Club",
    "man city": "Manchester City Football Club",
    "manchester city": "Manchester City Football Club",
    "man utd": "Manchester United Football Club",
    "man united": "Manchester United Football Club",
    "manchester united": "Manchester United Football Club",
    "newcastle": "Newcastle United Football Club",
    "tottenham": "Tottenham Hotspur Football Club",
    "spurs": "Tottenham Hotspur Football Club",
    "celtic": "The Celtic Football Club",

    # Germany
    "bayern": "FC Bayern München",
    "bayern munich": "FC Bayern München",
    "bayern münchen": "FC Bayern München",
    "dortmund": "Borussia Dortmund",
    "gladbach": "Borussia Verein für Leibesübungen 1900 Mönchengladbach",
    "monchengladbach": "Borussia Verein für Leibesübungen 1900 Mönchengladbach",
    "mönchengladbach": "Borussia Verein für Leibesübungen 1900 Mönchengladbach",
    "leverkusen": "Bayer 04 Leverkusen Fußball",

    # Italy
    "juventus": "Juventus Football Club",
    "inter": "Football Club Internazionale Milano S.p.A.",
    "inter milan": "Football Club Internazionale Milano S.p.A.",
    "ac milan": "Associazione Calcio Milan",
    "milan": "Associazione Calcio Milan",
    "roma": "Associazione Sportiva Roma",
    "napoli": "Società Sportiva Calcio Napoli",
    "atalanta": "Atalanta Bergamasca Calcio S.p.a.",

    # France
    "psg": "Paris Saint-Germain Football Club",
    "paris saint germain": "Paris Saint-Germain Football Club",
    "paris": "Paris Saint-Germain Football Club",
    "lyon": "Olympique Lyonnais",
    "monaco": "Association sportive de Monaco Football Club",

    # Portugal
    "porto": "Futebol Clube do Porto",
    "benfica": "Sport Lisboa e Benfica",
    "sporting": "Sporting Clube de Portugal",
    "sporting lisbon": "Sporting Clube de Portugal",

    # Netherlands
    "ajax": "AFC Ajax Amsterdam",
    "psv": "Eindhovense Voetbalvereniging Philips Sport Vereniging",

    # Other common European clubs
    "galatasaray": "Galatasaray Spor Kulübü",
    "olympiacos": "Olympiakos Syndesmos Filathlon Peiraios",
    "shakhtar": "FC Shakhtar Donetsk",
    "dynamo kyiv": "Futbolniy Klub Dynamo Kyiv",
    "red star": "Fudbalski klub Crvena zvezda Beograd",
    "crvena zvezda": "Fudbalski klub Crvena zvezda Beograd",
    "copenhagen": "Football Club København",
    "club brugge": "Club Brugge Koninklijke Voetbalvereniging",
    "young boys": "Berner Sport Club Young Boys",
}


def extract_club(question: str) -> str | None:
    """
    Returns the official club name matching an alias in the question.
    """
    question = question.lower()

    # longest aliases first ("manchester united" before "united")
    for alias in sorted(CLUB_ALIASES, key=len, reverse=True):
        if alias in question:
            return CLUB_ALIASES[alias]

    return None


def build_filter(club_name: str | None) -> dict | None:
    """
    Builds a ChromaDB metadata filter for a club.
    """
    if club_name is None:
        return None

    return {
        "$or": [
            {"home_team": club_name},
            {"away_team": club_name},
        ]
    }


def answer_question(question: str, n_results: int = 5) -> str:
    club = extract_club(question)
    filters = build_filter(club)

    results = retrieve(
    query=question,
    n_results=n_results,
    filters=filters,
)

    if not results:
        return (
            "Answer:\n"
            "I don't know based on the available Barcelona data.\n\n"
            "Confidence: ❌ No relevant documents were found."
        )

    context = "\n\n".join(chunk["text"] for chunk in results)

    user_prompt = f"""
Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = response.choices[0].message.content.strip()

    sources = []

    for chunk in results:
        metadata = chunk.get("metadata", {})

        source = (
            f"{metadata.get('home_team', 'Unknown')} "
            f"{metadata.get('result', '')} "
            f"{metadata.get('away_team', 'Unknown')} "
            f"({metadata.get('date', 'Unknown date')})"
        )

        competition = metadata.get("competition")
        if competition:
            source += f" - {competition}"

        if source not in sources:
            sources.append(source)

    output = f"Answer:\n{answer}\n\n"

    if answer == "I don't know based on the available Barcelona data.":
        output += "Confidence: ❌ Not supported by the retrieved Barcelona data."
    else:
        output += "Confidence: ✅ Based on retrieved Barcelona data."   

    if sources:
        output += "\n\nSources:\n"
        output += "\n".join(f"- {source}" for source in sources)

    return output

import sys
sys.path.insert(0, "rag")
from retriever import retrieve

results = retrieve("Juventus", n_results=10, filters={"$or": [{"home_team": "Juventus Football Club"}, {"away_team": "Juventus Football Club"}]})
for r in results:
    if r["metadata"]["date"].startswith("2017-04-19"):
        print(r["text"])