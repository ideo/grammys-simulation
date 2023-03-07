import streamlit as st

from src import logic as lg
from src import load_or_generate_objective_scores


# TODO: Include the num_winners as a user visible variable
# TODO: Display how many times the right top 10 existed.
# TODO: Add to the story "good but not great" B+
# TODO: How many times did a crony get to contort their ballot


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


lg.select_num_winners()


# Baseline
section_title = "simulation_1"
st.subheader("Establishing a Baseline")
lg.write_story(section_title)
sim1, sim1_chart_df = lg.simulation_section(song_df, section_title)


st.markdown("##### Repeated Contests")
num_contests=100
st.session_state["num_contests"] = num_contests
lg.write_story("simulation_1_repeated")
repeated_results = lg.display_results_of_repeated_contests(sim1)

# TODO: Regenerate this data
baseline_titles, baseline_indices = lg.establish_baseline(repeated_results)
# st.write(sim1.condorcet.top_nominee_ids)


# Random Samples
section_title = "simulation_2"
st.subheader("The Power of Randomness")
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


# Heatmap
st.markdown("##### Repeated Contests")
col1, _, col2 = st.columns([5, 1, 4])
lg.write_story("heatmap", st_col=col1)

with col2:
    label="No. Finalists"
    options = st.session_state["finalist_options"]
    index = options.index(st.session_state["num_winners"])
    heatmap_num_winners = st.selectbox(label, options=options, index=index)

    label="Ballot Size"
    options = [50, 100, 150, 200, 250]
    initial_value = ballot_limit if ballot_limit in options else 50
    index = options.index(initial_value)
    heatmap_ballot_limit = st.selectbox(label, options=options, index=index)

st.write("")
regenerate = st.secrets["ENVIRONMENT"] == "local"
lg.load_or_generate_heatmap_chart(
    heatmap_num_winners, 
    heatmap_ballot_limit, 
    baseline_indices, 
    regenerate=regenerate)
lg.write_story("heatmap_conclusion")


# Bloc Voting
section_title = "simulation_3"
st.subheader("Nullifying Bloc Voting")
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

lg.write_story("simulation_3_conclusion")


# st.subheader("Conclusion")
# lg.write_story("conclusion")
# lg.print_params([sim1, sim2, sim3])