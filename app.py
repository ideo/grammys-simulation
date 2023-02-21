import streamlit as st

# from src import STORY
from src import logic as lg
from src import Simulation
from src.simulation import load_or_generate_objective_scores


st.set_page_config(
    page_title="Grammys Simulation",
    page_icon="img/grammys_logo.png",
    initial_sidebar_state="expanded")

lg.initialize_session_state()
lg.sidebar()



st.title("The Isle of Musica")
num_voters = st.session_state["num_voters"]
num_songs = st.session_state["num_songs"]
lg.write_story("introduction", num_voters=num_voters, num_songs=num_songs)


num_songs = st.session_state["num_songs"]
song_df = load_or_generate_objective_scores(num_songs)


# Baseline
section_title = "simulation_1"
st.subheader("Let's Listen and Vote!")
lg.write_story(section_title)
sim1, chart_df = lg.simulation_section(song_df, section_title)

# TODO: move to function to disable later sims if theoretical results have
# not been set.
theoretical_results = chart_df["Entrant"].tolist()
# st.session_state["theoretical_exists"] = True


# Random Samples
section_title = "simulation_2"
st.subheader("Next Section!")
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
    theoretical_results=theoretical_results)


# Bloc Voting
section_title = "simulation_3"
st.subheader("Third Times the Charm!")
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
    theoretical_results=theoretical_results,
    num_mafiosos=num_mafiosos, mafia_size=mafia_size)


lg.print_params([sim1, sim2, sim3])