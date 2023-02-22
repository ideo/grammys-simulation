import streamlit as st

from src import logic as lg
from src import load_or_generate_objective_scores


st.set_page_config(
    page_title="Grammys Simulation",
    page_icon="img/grammys_logo.png",
    initial_sidebar_state="expanded")

lg.initialize_session_state()
# lg.sidebar()


st.title("The Isle of Musica")
num_voters = st.session_state["num_voters"]
num_songs = st.session_state["num_songs"]
num_winners = st.session_state["num_winners"]
lg.write_story("introduction")
song_df = load_or_generate_objective_scores(num_songs)


# Baseline
section_title = "simulation_1"
st.subheader("Establishing a Baseline")
lg.write_story(section_title)
sim1, sim1_chart_df = lg.simulation_section(song_df, section_title)


st.markdown("##### Repeated Contests")
num_contests=100
st.session_state["num_contests"] = num_contests
lg.write_story("simulation_1_repeated")
repeated_results = lg.display_results_of_repeated_contests(sim1, num_contests)
baseline_results = repeated_results.head(num_winners)["ID"].tolist()


# Random Samples
section_title = "simulation_2"
st.subheader("The Power of Randomness")
lg.write_story(section_title)

col1, col2 = st.columns(2)
label = "How many songs does each voter get to listen to?"
listen_limit = col1.slider(label, 
    value=num_songs//2, 
    min_value=10, 
    max_value=num_songs,
    key=section_title+"_listen_limit")
label = "How many songs does each voter get to rank?"
ballot_limit = col2.slider(label, 
    value=num_songs//4, 
    min_value=10, 
    max_value=listen_limit,
    key=section_title+"_ballot_limit")
    
sim2, _ = lg.simulation_section(song_df, section_title, 
    listen_limit=listen_limit,
    ballot_limit=ballot_limit,
    baseline_results=baseline_results,
    disabled=not sim1_chart_df["sum"].sum())


# Bloc Voting
section_title = "simulation_3"
st.subheader("Nullifying Bloc Voting")
lg.write_story(section_title)

col1, col2 = st.columns(2)
label = "How many songs does each voter get to listen to?"
listen_limit = col1.slider(label, 
    value=num_songs//2, 
    min_value=10, 
    max_value=num_songs,
    key=section_title+"_listen_limit")
label = "How many songs does each voter get to rank?"
ballot_limit = col2.slider(label, 
    value=num_songs//4, 
    min_value=10, 
    max_value=listen_limit,
    key=section_title+"_ballot_limit")

label = "How many corrupt artists are there?"
num_mafiosos = col1.number_input(label,
    value=1,
    min_value=0,
    max_value=10,
    step=1)
label = "How large are each of their mafias?"
max_mafia_size = num_voters//10
mafia_size = col2.slider(label, 
    value=max_mafia_size//2, 
    min_value=0, 
    max_value=max_mafia_size,
    step=5)
    
sim3, _ = lg.simulation_section(song_df, section_title, 
    listen_limit=listen_limit, ballot_limit=ballot_limit,
    baseline_results=baseline_results,
    num_mafiosos=num_mafiosos, mafia_size=mafia_size,
    disabled=not sim1_chart_df["sum"].sum())


st.subheader("Conclusion")
lg.write_story("conclusion")
lg.print_params([sim1, sim2, sim3])