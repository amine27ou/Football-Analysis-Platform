import sys
import os
sys.path.insert(0, "etl")
sys.path.insert(0, "rag")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from load import load_raw_data
from clean import clean_games, clean_appearances, clean_transfers
from aggregations import get_squad_value_by_season, get_transfer_activity
from query_engine import answer_question

# ── Brand tokens ────────────────────────────────────────────────────────────
MAROON   = "#A50044"
BLUE     = "#004D98"
GOLD     = "#EDBB00"
DARK_BG  = "#0A0A14"
CARD_BG  = "#11111F"
TEXT     = "#F0F0F0"
MUTED    = "#888899"

st.set_page_config(
    page_title="CulerAI · FC Barcelona Analytics",
    page_icon="🔵🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {DARK_BG};
      color: {TEXT};
      font-family: 'Inter', sans-serif;
  }}
  [data-testid="stAppViewContainer"] > .main {{
      background-color: {DARK_BG};
  }}
  [data-testid="stHeader"] {{ background: transparent; }}

  /* Hero */
  .hero {{
      display: flex;
      align-items: center;
      gap: 24px;
      padding: 36px 0 24px;
      border-bottom: 1px solid {BLUE}44;
      margin-bottom: 32px;
  }}
  .hero-logo {{
      width: 72px;
      height: 72px;
      object-fit: contain;
      filter: drop-shadow(0 0 12px {BLUE}88);
  }}
  .hero-text h1 {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 3.4rem;
      letter-spacing: 2px;
      line-height: 1;
      background: linear-gradient(90deg, {MAROON}, {BLUE});
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0;
  }}
  .hero-text p {{
      color: {MUTED};
      font-size: 0.85rem;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin: 4px 0 0;
  }}

  /* Stat cards */
  .stat-row {{ display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }}
  .stat-card {{
      flex: 1;
      min-width: 150px;
      background: {CARD_BG};
      border: 1px solid {BLUE}33;
      border-radius: 10px;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
  }}
  .stat-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, {MAROON}, {BLUE});
  }}
  .stat-card .val {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 2rem;
      color: {TEXT};
      line-height: 1;
  }}
  .stat-card .lbl {{
      font-size: 0.72rem;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-top: 4px;
  }}

  /* Tabs */
  [data-testid="stTabs"] button {{
      font-family: 'Inter', sans-serif;
      font-weight: 600;
      font-size: 0.8rem;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: {MUTED} !important;
      border-bottom: 2px solid transparent !important;
      background: transparent !important;
  }}
  [data-testid="stTabs"] button[aria-selected="true"] {{
      color: {TEXT} !important;
      border-bottom: 2px solid {MAROON} !important;
  }}
  [data-testid="stTabsContent"] {{ padding-top: 24px; }}

  /* Chat bubbles */
  .chat-user {{
      background: {BLUE}22;
      border-left: 3px solid {BLUE};
      border-radius: 0 10px 10px 0;
      padding: 12px 16px;
      margin: 12px 0;
      font-size: 0.9rem;
  }}
  .chat-ai {{
      background: {MAROON}18;
      border-left: 3px solid {MAROON};
      border-radius: 0 10px 10px 0;
      padding: 12px 16px;
      margin: 12px 0;
      font-size: 0.9rem;
      white-space: pre-wrap;
  }}
  .chat-label {{
      font-size: 0.68rem;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 4px;
  }}
  .chat-label.user {{ color: {BLUE}; }}
  .chat-label.ai   {{ color: {MAROON}; }}

  /* Match card */
  .match-card {{
      background: {CARD_BG};
      border: 1px solid #FFFFFF11;
      border-radius: 10px;
      padding: 16px 20px;
      margin-bottom: 12px;
  }}
  .match-card .comp {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: {MUTED};
      margin-bottom: 6px;
  }}
  .match-card .score {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1.6rem;
      line-height: 1;
  }}
  .win  {{ color: #00C46A; }}
  .loss {{ color: {MAROON}; }}
  .draw {{ color: {GOLD}; }}

  /* Inputs */
  [data-testid="stTextInput"] input,
  [data-testid="stSelectbox"] select,
  div[data-baseweb="select"] {{
      background-color: {CARD_BG} !important;
      border-color: {BLUE}44 !important;
      color: {TEXT} !important;
      border-radius: 8px !important;
  }}
  [data-testid="stButton"] button {{
      background: linear-gradient(135deg, {MAROON}, {BLUE}) !important;
      color: white !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      letter-spacing: 0.5px !important;
      padding: 10px 24px !important;
  }}
  [data-testid="stButton"] button:hover {{
      opacity: 0.88 !important;
      transform: translateY(-1px);
  }}

  /* Divider */
  hr {{ border-color: {BLUE}22; }}
  
  /* Sidebar / filters */
  .filter-label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: {MUTED};
      margin-bottom: 6px;
  }}
</style>
""", unsafe_allow_html=True)


# ── Data loading (cached) ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_all():
    raw       = load_raw_data("data/raw")
    games     = clean_games(raw["games"])
    transfers = clean_transfers(raw["transfers"])
    pv        = raw["player_valuations"]
    pv        = pv[pv["current_club_name"] == "FC Barcelona"]
    squad_val = get_squad_value_by_season(pv)
    transfer_activity = get_transfer_activity(transfers)
    return games, transfers, squad_val, transfer_activity

COMPETITION_LABELS = {
    "ES1":  "La Liga",
    "CL":   "Champions League",
    "CDR":  "Copa del Rey",
    "SUC":  "Supercopa de España",
    "EL":   "Europa League",
    "KLUB": "Club World Cup",
    "USC":  "UEFA Super Cup",
}

with st.spinner("Loading Barcelona data..."):
    games_df, transfers_df, squad_val_df, transfer_act_df = load_all()

# ── Hero ─────────────────────────────────────────────────────────────────────
LOGO_PATH = "app/assets/logo.png"

import base64

def get_logo_html(path):
    if path and os.path.exists(path):
        ext = path.split(".")[-1]
        mime = "image/avif" if ext == "avif" else f"image/{ext}"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:{mime};base64,{b64}" class="hero-logo" alt="FC Barcelona"/>'
    return f'<div style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,{MAROON},{BLUE});display:flex;align-items:center;justify-content:center;font-size:2rem;box-shadow:0 0 20px rgba(0,77,152,0.4);">⚽</div>'

logo_html = get_logo_html(LOGO_PATH)

st.markdown(f"""
<div class="hero">
    {logo_html}
    <div class="hero-text">
        <h1>CulerAI</h1>
        <p>FC Barcelona · Performance & Transfer Analytics · 2012–2025</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Top-level stats ──────────────────────────────────────────────────────────
total_games = len(games_df)
wins  = int(((games_df["home_club_id"] == 131) & (games_df["home_club_goals"] > games_df["away_club_goals"])).sum() +
            ((games_df["away_club_id"] == 131) & (games_df["away_club_goals"] > games_df["home_club_goals"])).sum())
draws = int(((games_df["home_club_goals"] == games_df["away_club_goals"])).sum())
losses = total_games - wins - draws
win_pct = f"{wins/total_games*100:.0f}%"
peak_val = squad_val_df["total_squad_value"].max() / 1e6

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="val">{total_games}</div><div class="lbl">Matches (2012–2025)</div></div>
  <div class="stat-card"><div class="val">{wins}</div><div class="lbl">Wins</div></div>
  <div class="stat-card"><div class="val">{draws}</div><div class="lbl">Draws</div></div>
  <div class="stat-card"><div class="val">{losses}</div><div class="lbl">Losses</div></div>
  <div class="stat-card"><div class="val">{win_pct}</div><div class="lbl">Win Rate</div></div>
  <div class="stat-card"><div class="val">€{peak_val:.0f}M</div><div class="lbl">Peak Squad Value</div></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_chat, tab_browser, tab_value, tab_transfers = st.tabs([
    "🤖  Ask CulerAI",
    "📅  Match Browser",
    "📈  Squad Value",
    "💸  Transfers",
])


# ════════════════════════════════════════════════════════════════════
# TAB 1 · CHAT
# ════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
    <p style="color:#888899;font-size:0.85rem;margin-bottom:20px;">
    Ask anything about Barcelona's history from 2012 to 2025.
    CulerAI answers using real match, squad, and transfer data — no hallucinations.
    </p>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
              <div class="chat-label user">You</div>
              {msg["content"]}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-ai">
              <div class="chat-label ai">CulerAI</div>
              {msg["content"]}
            </div>""", unsafe_allow_html=True)

    # Suggested questions
    if not st.session_state.chat_history:
        st.markdown(f'<div class="filter-label">Try asking</div>', unsafe_allow_html=True)
        suggestions = [
            "How did Barcelona perform against Juventus in the Champions League?",
            "Who were the top scorers against Real Madrid?",
            "What happened in the 2021 season?",
            "How did Barcelona do in the Copa del Rey?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("CulerAI is thinking..."):
                    answer = answer_question(s)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        question = col_input.text_input(
            "question", label_visibility="collapsed",
            placeholder="Ask about a match, player, season, or transfer..."
        )
        submitted = col_btn.form_submit_button("Ask →")

    if submitted and question.strip():
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("CulerAI is thinking..."):
            answer = answer_question(question)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation", key="clear"):
            st.session_state.chat_history = []
            st.rerun()


# ════════════════════════════════════════════════════════════════════
# TAB 2 · MATCH BROWSER
# ════════════════════════════════════════════════════════════════════
with tab_browser:
    col_f1, col_f2, col_f3 = st.columns(3)

    seasons = sorted(games_df["season"].unique(), reverse=True)
    sel_season = col_f1.selectbox("Season", seasons, index=0)

    comp_options = ["All"] + [COMPETITION_LABELS.get(c, c) for c in sorted(games_df["competition_id"].unique())]
    sel_comp_label = col_f2.selectbox("Competition", comp_options)
    sel_comp = None if sel_comp_label == "All" else {v: k for k, v in COMPETITION_LABELS.items()}.get(sel_comp_label, sel_comp_label)

    result_options = ["All", "Win", "Draw", "Loss"]
    sel_result = col_f3.selectbox("Result", result_options)

    filtered = games_df[games_df["season"] == sel_season].copy()
    if sel_comp:
        filtered = filtered[filtered["competition_id"] == sel_comp]

    def get_result(row):
        if row["home_club_id"] == 131:
            bg, og = row["home_club_goals"], row["away_club_goals"]
        else:
            bg, og = row["away_club_goals"], row["home_club_goals"]
        if bg > og: return "Win"
        if bg < og: return "Loss"
        return "Draw"

    filtered["result"] = filtered.apply(get_result, axis=1)
    if sel_result != "All":
        filtered = filtered[filtered["result"] == sel_result]

    filtered = filtered.sort_values("date", ascending=False)

    # Season summary mini-stats
    total_s = len(filtered)
    if total_s:
        w = (filtered["result"] == "Win").sum()
        d = (filtered["result"] == "Draw").sum()
        l = (filtered["result"] == "Loss").sum()
        st.markdown(f"""
        <div class="stat-row" style="margin-bottom:20px;">
          <div class="stat-card"><div class="val">{total_s}</div><div class="lbl">Matches</div></div>
          <div class="stat-card"><div class="val win">{w}</div><div class="lbl">Wins</div></div>
          <div class="stat-card"><div class="val draw">{d}</div><div class="lbl">Draws</div></div>
          <div class="stat-card"><div class="val loss">{l}</div><div class="lbl">Losses</div></div>
        </div>
        """, unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        is_home = row["home_club_id"] == 131
        barca_goals = int(row["home_club_goals"] if is_home else row["away_club_goals"])
        opp_goals   = int(row["away_club_goals"] if is_home else row["home_club_goals"])
        opp_name    = row["away_club_name"] if is_home else row["home_club_name"]
        venue       = "Home" if is_home else "Away"
        result      = row["result"]
        result_cls  = result.lower()
        comp_label  = COMPETITION_LABELS.get(row["competition_id"], row["competition_id"])
        date_str    = row["date"].strftime("%d %b %Y")
        round_str   = row.get("round", "")

        result_badge = f'<span class="{result_cls}" style="font-size:0.75rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;">{result}</span>'

        st.markdown(f"""
        <div class="match-card">
          <div class="comp">{comp_label} · {round_str} · {date_str} · {venue}</div>
          <div class="score">
            <span style="color:{TEXT};">Barcelona</span>
            <span style="margin:0 10px;color:{MUTED};">{barca_goals}–{opp_goals}</span>
            <span style="color:{MUTED};">{opp_name}</span>
            &nbsp;&nbsp;{result_badge}
          </div>
        </div>
        """, unsafe_allow_html=True)

    if total_s == 0:
        st.info("No matches found for the selected filters.")


# ════════════════════════════════════════════════════════════════════
# TAB 3 · SQUAD VALUE
# ════════════════════════════════════════════════════════════════════
with tab_value:
    st.markdown(f'<p style="color:{MUTED};font-size:0.85rem;margin-bottom:20px;">Total squad market value at the start of each season. Source: Transfermarkt via player_valuations.csv.</p>', unsafe_allow_html=True)

    fig_val = go.Figure()

    fig_val.add_trace(go.Scatter(
        x=squad_val_df["season"],
        y=squad_val_df["total_squad_value"] / 1e6,
        mode="lines+markers",
        line=dict(color=BLUE, width=3),
        marker=dict(size=8, color=MAROON, line=dict(color=BLUE, width=2)),
        fill="tozeroy",
        fillcolor="rgba(0,77,152,0.09)",
        hovertemplate="<b>Season %{x}</b><br>Squad Value: €%{y:.0f}M<extra></extra>",
    ))

    # Annotate key moments
    annotations = [
        (2017, "Neymar exit\n+Dembélé"),
        (2021, "Financial\ncrisis"),
        (2025, "Rebuild\npeak"),
    ]
    for season, label in annotations:
        row = squad_val_df[squad_val_df["season"] == season]
        if not row.empty:
            fig_val.add_annotation(
                x=season,
                y=row["total_squad_value"].values[0] / 1e6,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowcolor=GOLD,
                font=dict(color=GOLD, size=10),
                bgcolor=DARK_BG,
                bordercolor=GOLD,
                borderwidth=1,
                ax=0, ay=-50,
            )

    fig_val.update_layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter"),
        xaxis=dict(
            title="Season", tickmode="linear", dtick=1,
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.13)",
        ),
        yaxis=dict(
            title="Market Value (€M)",
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.13)",
        ),
        margin=dict(t=20, b=40, l=60, r=20),
        height=420,
        hovermode="x unified",
    )

    st.plotly_chart(fig_val, use_container_width=True)

    # Data table
    display_val = squad_val_df.copy()
    display_val["total_squad_value"] = display_val["total_squad_value"].apply(lambda x: f"€{x/1e6:.1f}M")
    display_val.columns = ["Season", "Total Squad Value"]
    st.dataframe(display_val, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4 · TRANSFERS
# ════════════════════════════════════════════════════════════════════
with tab_transfers:
    st.markdown(f'<p style="color:{MUTED};font-size:0.85rem;margin-bottom:20px;">Transfer spend and income by season. Positive net = more received than spent.</p>', unsafe_allow_html=True)

    fig_tr = go.Figure()

    fig_tr.add_trace(go.Bar(
        x=transfer_act_df["season"],
        y=transfer_act_df["spend"] / 1e6,
        name="Spend",
        marker_color=MAROON,
        hovertemplate="<b>%{x}</b><br>Spend: €%{y:.1f}M<extra></extra>",
    ))
    fig_tr.add_trace(go.Bar(
        x=transfer_act_df["season"],
        y=transfer_act_df["income"] / 1e6,
        name="Income",
        marker_color=BLUE,
        hovertemplate="<b>%{x}</b><br>Income: €%{y:.1f}M<extra></extra>",
    ))
    fig_tr.add_trace(go.Scatter(
        x=transfer_act_df["season"],
        y=transfer_act_df["net"] / 1e6,
        name="Net",
        mode="lines+markers",
        line=dict(color=GOLD, width=2, dash="dot"),
        marker=dict(size=7, color=GOLD),
        hovertemplate="<b>%{x}</b><br>Net: €%{y:.1f}M<extra></extra>",
    ))

    fig_tr.update_layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter"),
        barmode="group",
        xaxis=dict(
            title="Season", tickmode="linear", dtick=1,
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.13)",
        ),
        yaxis=dict(
            title="Transfer Fee (€M)",
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.13)",
        ),
        legend=dict(
            bgcolor=CARD_BG,
            bordercolor="rgba(255,255,255,0.13)",
            borderwidth=1,
        ),
        margin=dict(t=20, b=40, l=60, r=20),
        height=420,
        hovermode="x unified",
    )

    st.plotly_chart(fig_tr, use_container_width=True)

    # Notable transfers table
    st.markdown(f'<div class="filter-label" style="margin-top:8px;">Notable transfers (fee ≥ €20M)</div>', unsafe_allow_html=True)

    notable = transfers_df[
        (transfers_df["transfer_fee"] >= 20_000_000) &
        (
            (transfers_df["to_club_id"] == 131) |
            (transfers_df["from_club_id"] == 131)
        )
    ].copy()

    notable["Direction"] = notable.apply(
        lambda r: "🟢 In" if r["to_club_id"] == 131 else "🔴 Out", axis=1
    )
    notable["Fee"] = notable["transfer_fee"].apply(lambda x: f"€{x/1e6:.1f}M")
    notable["transfer_date"] = pd.to_datetime(notable["transfer_date"]).dt.strftime("%b %Y")

    display_notable = notable[[
        "transfer_date", "player_name", "Direction",
        "from_club_name", "to_club_name", "Fee"
    ]].rename(columns={
        "transfer_date": "Date",
        "player_name": "Player",
        "from_club_name": "From",
        "to_club_name": "To",
    }).sort_values("Fee", ascending=False)

    st.dataframe(display_notable, use_container_width=True, hide_index=True)