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

# Impractical
st.markdown("---")
_, cen, _ = st.columns([3,2,2])
def start_story_state():
    st.session_state['show_state'] = 1

start_story = cen.button("Let's go",key=0,on_click=start_story_state)

    

if st.session_state['show_state'] >= 1:
    # Alphabetical
    section_title = "The Isle of Musica"
    lg.write_story(section_title, header_level=1)
    lg.select_num_winners()

    st.markdown("---")
    _, cen, _ = st.columns([2,2,2])
    def alphabetical():
        st.session_state['show_state'] = 2
    
    start_story = cen.button("Let's simulate the first contest!",key=1,on_click=alphabetical)

if st.session_state["show_state"] >= 2:
    section_title = "Keep it Simple"
    lg.write_story(section_title)
    subtitle = f"Each voter casts {num_winners} votes, but no voter has time to listen to every song."

    takeaway = "**TAKEAWAY**: In this simulation, we see that when voters are shown songs in alphabetical order, the rightful songs often do not receive the most votes! Does that sound simillar to a concern in the real world?"


    sim_alpha, _ = lg.simulation_section(song_df, section_title, 
                                        alphabetical=True,
                                        baseline_results=baseline_titles,
                                        subtitle=subtitle,takeaway=takeaway)
    
    st.markdown("---")
    _, cen, _ = st.columns([2,2,2])
    def fairness():
        st.session_state['show_state'] = 3

    start_story = cen.button("Let's simulate how they can solve this issue?",key=2,on_click=fairness)

if st.session_state["show_state"] >= 3:
    section_title = "Ensuring Fairness"
    lg.write_story(section_title)
    subtitle = f"All voters take the time to listen and rank all {num_songs} songs."

    takeaway = "**TAKEAWAY**: In this simulation, Even when voters are pretty subjective, when they all listen to every song, their collective wisdom almost always picks the best songs. But this is not feasible in real life!"

    sim1, sim1_chart_df = lg.simulation_section(song_df, section_title,
                                                baseline_results=baseline_titles,
                                                subtitle=subtitle, takeaway=takeaway) 
    st.markdown("---")  
    _, cen, _ = st.columns([2,2,2])
    def randomness():
        st.session_state['show_state'] = 4

    start_story = cen.button("Is there a way that's more feasible?",key=3,on_click=randomness)

# Random Samples
if st.session_state["show_state"] >= 4:
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

    takeaway = "**TAKEAWAY**: In this simulation, we see that even if voters vote for a small subset of songs, the votes (mostly) reflect the best songs!."

    sim2, _ = lg.simulation_section(song_df, section_title, 
        listen_limit=listen_limit,
        ballot_limit=ballot_limit,
        baseline_results=baseline_titles, takeaway=takeaway)

    st.markdown("---")
    def bloc():
        st.session_state['show_state'] = 5        
    _, cen, _ = st.columns([2,2,2])
    st.text("")
    start_story = cen.button("Can this help if voters are really biased?",key=4,on_click=bloc)

# Random Samples
if st.session_state["show_state"] >= 5:

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
    
    takeaway = "**TAKEAWAY**: The performance of the above contest is surprisingly similar to that of the one before it. Even when every single voter is in cahoots with someone, the randomization of the contest prevents coordination – not enough of them get the chance to vote for their ring leader. At worst, by not voting for the deserved best song, rather than promote a corrupt song into the finalists, they open up a chance for a near-finalist to make into the list. This phenomen nullifies any attempts at collusion."
    sim3, _ = lg.simulation_section(song_df, section_title, 
        listen_limit=listen_limit, ballot_limit=ballot_limit,
        baseline_results=baseline_titles,
        num_mafiosos=num_mafiosos, mafia_size=mafia_size, takeaway=takeaway)

    # lg.write_story("bloc_voting_conclusion", header_level=None)