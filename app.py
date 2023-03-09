import streamlit as st

from src import logic as lg
from src import load_or_generate_objective_scores


# TODO: Include the num_winners as a user visible variable
# TODO: Display how many times the right top 10 existed.
# TODO: Add to the story "good but not great" B+
# TODO: How many times did a crony get to contort their ballot


st.set_page_config(
    page_title="Isle of Musica",
    page_icon="img/grammys_logo.png",
    initial_sidebar_state="expanded")

lg.initialize_session_state()
# lg.sidebar()


num_voters = st.session_state["num_voters"]
num_songs = st.session_state["num_songs"]
num_winners = st.session_state["num_winners"]
song_df = load_or_generate_objective_scores(num_songs)


# Simulation Explanation and Interactive Demo
lg.write_story("Voting Simulations", header_level=1)
lg.interactive_demo(song_df)

section_title = "Establish a Baseline"
baseline_titles, _ = lg.establish_baseline(song_df)


section_title = "The Isle of Musica"
lg.write_story(section_title, header_level=1)
lg.select_num_winners()


# Alphabetical
section_title = "Keep it Simple"
lg.write_story(section_title)
subtitle = f"Each voter casts {num_winners} votes, but no voter has time to listen to every song."
sim_alpha, _ = lg.simulation_section(song_df, section_title, 
                                     alphabetical=True,
                                     baseline_results=baseline_titles,
                                     subtitle=subtitle)

# Impractical
section_title = "Ensuring Fairness"
lg.write_story(section_title)
subtitle = f"All voters take the time to listen and rank all {num_songs} songs."
sim1, sim1_chart_df = lg.simulation_section(song_df, section_title,
                                            baseline_results=baseline_titles,
                                            subtitle=subtitle)


# Random Samples
section_title = "The Power of Randomness"
lg.write_story(section_title)

col1, col2 = st.columns(2)
label = "How many songs does each voter get to listen to?"
listen_limit = col1.slider(label, 
    value=st.session_state["listen_limit"], 
    min_value=50, 
    max_value=num_songs,
    step=50,
    key=section_title+"_listen_limit")
label = "How many songs does each voter get to rank?"
initial = st.session_state["ballot_limit"] 
ballot_limit = col2.slider(label, 
    value=initial if initial < listen_limit else listen_limit,
    min_value=25, 
    max_value=listen_limit,
    step=25,
    key=section_title+"_ballot_limit")
    
sim2, _ = lg.simulation_section(song_df, section_title, 
    listen_limit=listen_limit,
    ballot_limit=ballot_limit,
    baseline_results=baseline_titles)


# Bloc Voting
section_title = "Nullifying Bloc Voting"
lg.write_story(section_title)

col1, col2 = st.columns(2)
label = "How many songs does each voter get to listen to?"
listen_limit = col1.slider(label, 
    value=st.session_state["listen_limit"],
    min_value=50, 
    max_value=num_songs,
    step=10,
    key=section_title+"_listen_limit")
label = "How many songs does each voter get to rank?"
initial = st.session_state["ballot_limit"] 
ballot_limit = col2.slider(label, 
    value=initial if initial < listen_limit else listen_limit,
    min_value=10, 
    max_value=listen_limit,
    step=10,
    key=section_title+"_ballot_limit")

label = "How many corrupt artists are there?"
num_mafiosos = col1.number_input(label,
    value=2,
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
    baseline_results=baseline_titles,
    num_mafiosos=num_mafiosos, mafia_size=mafia_size)

lg.write_story("bloc_voting_conclusion", header_level=None)