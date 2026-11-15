import os
import sys
from pathlib import Path
import uuid
from datetime import date, timedelta
import html

import streamlit as st
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="TripMind AI | Travel Intelligence", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stApp"] {background:#f5f7fb;color:#17263f;}
[data-testid="stSidebar"] {background:#101e35;}
[data-testid="stSidebar"] * {color:#f3f7ff;}
[data-testid="stSidebar"] input {color:#17263f!important;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {color:#d6e0f1!important;}
.block-container {padding-top:2.3rem;max-width:1250px;}
h1,h2,h3 {font-family:'Manrope',sans-serif!important;letter-spacing:-.035em;}
.hero {background:linear-gradient(115deg,#122b50,#1b4b73);color:white;padding:38px 42px;border-radius:22px;margin-bottom:24px;position:relative;overflow:hidden;}
.hero .eyebrow {color:#8dded6;font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase;}
.hero h1 {font-size:38px;margin:9px 0 10px;color:white;}
.hero p {color:#d3e1ee;max-width:630px;margin:0;line-height:1.65;}
.hero .symbol {position:absolute;right:55px;top:26px;font-size:95px;opacity:.18;transform:rotate(-16deg);}
.section-title {font-size:19px;font-weight:800;color:#152a49;margin:16px 0 8px;}
.muted {color:#65758d;font-size:14px;margin-bottom:14px;}
.kpi {border:1px solid #e3e9f2;background:white;padding:18px 20px;border-radius:16px;}
.kpi-label {font-size:12px;color:#70819a;text-transform:uppercase;letter-spacing:1px;font-weight:700;}
.kpi-value {font-size:21px;font-weight:800;color:#182d4c;margin-top:6px;}
.result-card {background:#fff;border:1px solid #e3e9f2;border-radius:16px;padding:21px;margin:8px 0 15px;line-height:1.65;}
[data-testid="stForm"] {background:white;border:1px solid #e3e9f2;border-radius:18px;padding:20px 22px;}
.stButton>button[kind="primary"], [data-testid="stFormSubmitButton"] button {background:#167d86!important;border:none!important;color:white!important;border-radius:10px!important;font-weight:700!important;min-height:44px;}
[data-testid="stTabs"] button {font-weight:700;}
footer {visibility:hidden;}
/* Visual upgrade: motion is subtle and respects accessibility preferences */
@keyframes fadeRise {from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes floatPlane {0%,100%{transform:translateY(0) rotate(-12deg)}50%{transform:translateY(-13px) rotate(-8deg)}}
@keyframes shimmer {from{background-position:200% 0}to{background-position:-200% 0}}
.hero {min-height:255px;display:flex;flex-direction:column;justify-content:center;
 background:linear-gradient(90deg,rgba(8,24,48,.91) 0%,rgba(8,24,48,.73) 52%,rgba(8,24,48,.15) 100%),url('https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1800&q=85') center 45%/cover;
 box-shadow:0 16px 40px rgba(10,37,69,.16);animation:fadeRise .7s ease both;}
.hero h1{font-size:clamp(35px,4vw,54px);line-height:1.1;max-width:650px}
.hero .symbol{opacity:.75;animation:floatPlane 5s ease-in-out infinite;right:35px;top:22px;font-size:55px}
.hero .eyebrow{color:#a5f1e8}
.gallery{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:15px;margin:6px 0 28px}
.destination-tile{min-height:164px;position:relative;overflow:hidden;border-radius:18px;background-position:center;background-size:cover;box-shadow:0 9px 22px rgba(19,39,65,.12);transition:transform .28s ease,box-shadow .28s ease;animation:fadeRise .7s ease both}
.destination-tile:hover{transform:translateY(-5px);box-shadow:0 16px 32px rgba(19,39,65,.2)}
.destination-tile:before{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(4,17,33,.78),transparent 72%)}
.tile-content{position:absolute;bottom:17px;left:18px;color:white}
.tile-content strong{display:block;font-size:18px}.tile-content small{color:#e1f0fa}
.step-line{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 25px}
.step-pill{padding:10px 15px;background:#fff;border:1px solid #e0e9f1;border-radius:100px;font-size:12px;font-weight:700;color:#24425d}
.result-banner{background:linear-gradient(110deg,#e8f7f4,#eff6ff);border:1px solid #d3e9e5;border-radius:16px;padding:18px 22px;margin:15px 0 20px;animation:fadeRise .6s ease both}
[data-testid="stForm"]{box-shadow:0 14px 35px rgba(21,48,79,.06)}
[data-testid="stFormSubmitButton"] button{transition:transform .2s ease,box-shadow .2s ease}
[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(22,125,134,.22)}
[data-testid="stExpander"]{border-radius:14px!important;background:white}
@media(max-width:800px){.gallery{grid-template-columns:1fr 1fr}.destination-tile:first-child{grid-column:1/-1}.hero{padding:27px;min-height:225px}.hero .symbol{display:none}}
@media(prefers-reduced-motion:reduce){.hero,.destination-tile,.result-banner{animation:none!important}.hero .symbol{animation:none!important}.destination-tile,.stButton button{transition:none!important}}

</style>''', unsafe_allow_html=True)

# Import after page configuration. main.py must guard CLI-only execution.
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "frontend" else Path(__file__).resolve().parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from main import app
except Exception as exc:
    st.error("Could not import the LangGraph application from main.py. Make sure terminal-only code is under `if __name__ == '__main__':`.")
    st.exception(exc)
    st.stop()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

with st.sidebar:
    st.markdown("## ✈️ TripMind **AI**")
    st.caption("INTELLIGENT TRAVEL STUDIO")
    st.divider()
    st.markdown("### Your workspace")
    st.markdown("🧭  **Trip planner**")
    st.markdown("🗓️  **Custom itineraries**")
    st.markdown("🏨  **Hotel discovery**")
    st.markdown("🛫  **Flight intelligence**")
    st.divider()
    st.markdown("### Session")
    st.caption(f"Thread: `{st.session_state.thread_id[:8]}`")
    if st.button("＋ Start new trip", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_result = None
        st.session_state.last_query = ""
        st.rerun()
    st.markdown("---")
    st.caption("Powered by LangGraph · Groq · PostgreSQL")

st.markdown('''<div class="hero"><div class="eyebrow">YOUR JOURNEY, INTELLIGENTLY PLANNED</div><h1>Where to next?</h1><p>From flight research to curated stays and day-by-day experiences, your personal AI travel team brings every detail together.</p><div class="symbol">✈</div></div>''', unsafe_allow_html=True)

st.markdown('''<div class="section-title">Discover your next escape</div>
<div class="muted">A little inspiration before your agents plan the details.</div>
<div class="gallery">
  <div class="destination-tile" style="background-image:url('https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=900&q=80')"><div class="tile-content"><strong>Tokyo, Japan</strong><small>City lights & culture</small></div></div>
  <div class="destination-tile" style="background-image:url('https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=700&q=80')"><div class="tile-content"><strong>Bali, Indonesia</strong><small>Island adventures</small></div></div>
  <div class="destination-tile" style="background-image:url('https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=700&q=80')"><div class="tile-content"><strong>Explore more</strong><small>Anywhere in the world</small></div></div>
</div>
<div class="step-line"><span class="step-pill">✈ Flight research</span><span class="step-pill">⌂ Hotel discovery</span><span class="step-pill">☀ Personalized itinerary</span><span class="step-pill">✦ One best plan</span></div>''', unsafe_allow_html=True)

st.markdown('<div class="section-title">Plan a new journey</div><div class="muted">Tell us a little about your trip. We’ll build a personalized plan.</div>', unsafe_allow_html=True)

with st.form("travel_form"):
    a, b = st.columns(2, gap="large")
    with a:
        origin = st.text_input("Departure city", placeholder="e.g. Hyderabad, India")
        destination = st.text_input("Destination", placeholder="e.g. Tokyo, Japan")
        departure_date = st.date_input("Departure date", value=date.today() + timedelta(days=30), min_value=date.today())
    with b:
        days = st.number_input("Trip duration (days)", min_value=1, max_value=60, value=5)
        travelers = st.number_input("Travelers", min_value=1, max_value=20, value=2)
        budget = st.number_input("Total budget (₹)", min_value=1000, max_value=10000000, value=200000, step=5000)
    preferences = st.multiselect("What do you enjoy?", ["Culture & history", "Food & cafes", "Nature", "Adventure", "Shopping", "Relaxation", "Nightlife", "Family-friendly"], default=["Culture & history", "Food & cafes"])
    notes = st.text_area("Anything else we should know?", placeholder="e.g. Prefer budget hotels, vegetarian meals, and public transport", height=90)
    submitted = st.form_submit_button("✦ Generate my travel plan", type="primary", use_container_width=True)

if submitted:
    if not origin.strip() or not destination.strip():
        st.warning("Please enter both a departure city and a destination.")
    else:
        query = (f"Plan a complete {int(days)}-day trip from {origin.strip()} to {destination.strip()} "
                 f"starting {departure_date.isoformat()} for {int(travelers)} traveler(s), "
                 f"within a total budget of INR {int(budget):,}. Choose exactly ONE best flight and ONE best hotel, with reasons and total estimated cost. Do not list alternatives. Include flight information, "
                 f"hotel suggestions, and a detailed day-by-day sightseeing itinerary. "
                 f"Interests: {', '.join(preferences) if preferences else 'general sightseeing'}. "
                 f"Additional preferences: {notes.strip() or 'none'}. "
                 "Clearly distinguish verified prices and availability from estimates. Never invent flight numbers, fares, or availability. If flight search fails, explicitly state that flight details are unverified.")
        # New plan, new thread: prevents prior trip checkpoints from contaminating this plan.
        st.session_state.thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.status("Your AI travel team is planning your journey…", expanded=True) as status:
            st.write("Searching flights, discovering hotels, and building your itinerary.")
            try:
                result = app.invoke({"user_query": query, "messages": [HumanMessage(content=query)], "llm_calls": 0}, config=config)
                st.session_state.last_result = result
                st.session_state.last_query = query
                status.update(label="Your travel plan is ready", state="complete", expanded=False)
            except Exception as exc:
                status.update(label="Planning could not be completed", state="error", expanded=True)
                st.error("The AI workflow returned an error. Review the details below.")
                st.exception(exc)

result = st.session_state.last_result
if result is not None:
    st.markdown('<div class="section-title">Your travel blueprint</div><div class="muted">A unified view of the research and recommendations generated by your agents.</div>', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    for col, label, value in [(k1,"PLANNING ENGINE","Multi-agent"),(k2,"TRAVEL BRIEF","Personalized"),(k3,"SESSION","Saved checkpoint")]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)
    messages = result.get("messages") or []
    last_message = messages[-1] if messages else None
    final_text = result.get("final_response") or (getattr(last_message, "content", None) if last_message else None)
    st.markdown('<div class="result-banner"><strong>✦ Your personalized journey is ready</strong><div style="font-size:13px;color:#50677b;margin-top:4px">One curated recommendation, backed by your agents’ research. Verify prices and availability before booking.</div></div>', unsafe_allow_html=True)
    st.markdown("### ✨ Your recommended trip")
    if final_text:
        st.markdown(final_text)
    else:
        st.warning("The final agent did not produce a travel plan.")

    with st.expander("🛫 Flight research details", expanded=True):
        flight_data = result.get("flight_results")
        if flight_data:
            st.write(flight_data)
        else:
            st.warning("No flight data was saved in the graph state. Check search_flights(), its API response, and the flight_results state field. No flight availability has been verified.")

    with st.expander("🏨 Hotel research details"):
        hotel_data = result.get("hotel_results")
        if hotel_data:
            st.write(hotel_data)
        else:
            st.warning("No hotel data was returned by the hotel agent.")

    with st.expander("🗓️ Detailed itinerary"):
        if result.get("itinerary"):
            st.markdown(str(result["itinerary"]))
        else:
            st.warning("No itinerary was returned by the itinerary agent.")

    with st.expander("🔧 Debug: LangGraph output keys"):
        st.code(repr(list(result.keys())))
        st.caption("Check whether flight_results is present and contains actual flight data.")
    with st.expander("View the travel request sent to the agents"):
        st.write(st.session_state.last_query)
    st.download_button("↓ Download travel plan", data=str(final_text or result), file_name="tripmind-travel-plan.md", mime="text/markdown")
else:
    st.info("Your travel plan will appear here after you submit the form.")
