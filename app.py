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


section_title = "simulation_1"
st.subheader("Let's Listen and Vote!")
lg.write_story(section_title)
sim1, chart_df = lg.simulation_section(song_df, section_title)
theoretical_results = chart_df["Entrant"].tolist()



section_title = "simulation_2"
st.subheader("Next Section!")
lg.write_story(section_title)

col1, col2 = st.columns(2)
label = "How many songs does each voter get to listen to?"
listen_limit = col1.slider(label, 
    value=num_songs//2, 
    min_value=10, 
    max_value=num_songs)
label = "How many songs does each voter get to rank?"
ballot_limit = col2.slider(label, 
    value=num_songs//4, 
    min_value=10, 
    max_value=listen_limit)
    
sim2, chart_df = lg.simulation_section(song_df, section_title, 
    listen_limit=listen_limit,
    ballot_limit=ballot_limit,
    theoretical_results=theoretical_results)


lg.print_params([sim1, sim2])




# st.subheader(section_title.replace("_", " ").title())

# num_voters = st.session_state["num_voters"]
# st_dev = st.session_state["st_dev"]

# # sim1 = Simulation(song_df, num_voters, st_dev, assigned_guacs=num_songs)
# st.write("Each voter votes on every nominee.")
# sim1 = lg.run_a_simulation(song_df, num_voters, num_songs, section_title)
# # sim1.simulate()
# # lg.animate_results(sim1, key=section_title)
# lg.animate_summation_results(sim1, section_title)
# # if st.session_state[f"{section_title}_keep_chart_visible"]:
# #     lg.success_message(section_title, sim1.success)


# st.markdown("---")
# section_title = "simulation_2"
# st.subheader(section_title.replace("_", " ").title())

# col1, col2 = st.columns(2)
# # lg.write_instructions(section_title, col1)
# guac_limit2 = col2.slider(
#     "How many songs does each voter get to listen to?",
#     value=50, 
#     min_value=10, 
#     max_value=num_songs)

# # sim2 = Simulation(song_df, num_voters, st_dev, assigned_guacs=guac_limit2)
# # sim2.simulate()

# sim2 = lg.run_a_simulation(song_df, num_voters, guac_limit2, section_title)
# lg.animate_summation_results(sim2, key=section_title)
# # if st.session_state[f"{section_title}_keep_chart_visible"]:
# #     lg.success_message(section_title, sim2.success, guac_limit2)

# # st.write("")
# # st.write("")
# # lg.write_story("simulation_2_a")
# # lg.animate_results_of_100_runs(sim2, scenario, section_title)


# # st.markdown("---")
# # lg.write_story("transition_2_to_3")
# # st.subheader("Different People, Different Tastes")
# # section_title = "simulation_3"
# # lg.write_story(section_title)
# # st.text("")
# # lg.write_instructions(section_title+"_a")
# # pepe, fra, carlos = lg.types_of_voters(section_title)
# # col1, col2 = st.columns(2)
# # lg.write_instructions(section_title+"_b", col1)
# # guac_limit3 = col2.slider(
# #     "How many guacamoles does each voter get to try?",
# #     value=15, 
# #     min_value=1, 
# #     max_value=20,
# #     key=section_title)

# # sim3 = Simulation(song_df, num_voters, st_dev, 
# #     assigned_guacs=guac_limit3,
# #     perc_fra=fra,
# #     perc_pepe=pepe,
# #     perc_carlos=carlos)
# # sim3.simulate()
# # lg.animate_results(sim3, key=section_title)
# # lg.success_message(section_title, sim3.success)

# # num_cronies = sum(townie.carlos_crony for townie in sim3.townspeople)
# # num_effective_cronies = sum(townie.voted_for_our_boy for townie in sim3.townspeople)
# # st.caption(f"Also, {num_cronies} of Carlos's cronies voted in the contest and {num_effective_cronies} were able to vote for him.")


# # st.markdown("---")
# # st.subheader("A New Idea")
# # section_title = "condorcet"
# # lg.write_story(section_title + "_1")
# # st.image("img/napkin_ballot.jpg", width=400)
# # lg.write_story(section_title + "_2")

# # st.text("")
# # st.text("")
# # lg.write_instructions(section_title)
# # pepe_4, fra_4, carlos_4 = lg.types_of_voters(section_title, pepe, fra, carlos)
# # col1, col2 = st.columns(2)
# # guac_limit4 = col1.slider(
# #     "How many guacamoles does each voter get to try?",
# #     value=guac_limit3, 
# #     min_value=1, 
# #     max_value=20,
# #     key=section_title)
# # num_voters4 = col2.slider(
# #     "How many townspeople vote in the contest?",
# #     value=num_voters,
# #     min_value=10,
# #     max_value=500,
# #     step=10,
# #     key=section_title)

# # sim4 = Simulation(song_df, num_voters4, st_dev, 
# #     assigned_guacs=guac_limit4,
# #     perc_fra=fra,
# #     perc_pepe=pepe,
# #     perc_carlos=carlos,
# #     method="condorcet")
# # sim4.simulate()
# # lg.animate_results(sim4, key=section_title)
# # lg.success_message(section_title, sim4.success)

# # num_cronies = sum(townie.carlos_crony for townie in sim4.townspeople)
# # num_effective_cronies = sum(townie.voted_for_our_boy for townie in sim4.townspeople)
# # st.caption(f"Also, {num_cronies} of Carlos's cronies voted in the contest and {num_effective_cronies} were able to vote for him.")


# # st.markdown("---")
# # st.subheader("Out in the Real World")
# # lg.write_story("conclusion")


# # st.markdown("---")
# # st.subheader("Sandbox")
# # section_title = "sandbox"
# # lg.write_story(section_title)
# # sandbox_df, sandbox_scenario = lg.choose_scenario(key=section_title)
# # pepe_sb, fra_sb, carlos_sb = lg.types_of_voters(section_title, pepe, fra, carlos)
# # col1, col2 = st.columns(2)
# # guac_limit_sb = col1.slider(
# #     "How many guacamoles does each voter get to try?",
# #     value=guac_limit3, 
# #     min_value=1, 
# #     max_value=20,
# #     key=section_title)
# # num_voters_sb = col2.slider(
# #     "How many townspeople vote in the contest?",
# #     value=num_voters,
# #     min_value=10,
# #     max_value=500,
# #     step=10,
# #     key=section_title)

# # methods = {
# #     "Summing the Scores":           "sum", 
# #     "Tallying Implicit Rankings":   "condorcet",
# #     "Ranked Choice Voting":         "rcv",
# # }
# # method_chosen = st.selectbox("How should we tally the votes?",
# #     options=methods.keys())

# # sandbox_sim = Simulation(sandbox_df, num_voters_sb, st_dev, 
# #     assigned_guacs=guac_limit_sb,
# #     perc_fra=fra_sb,
# #     perc_pepe=pepe_sb,
# #     perc_carlos=carlos_sb,
# #     method=methods[method_chosen])
# # sandbox_sim.simulate()
# # lg.animate_results(sandbox_sim, key=section_title)
# # lg.success_message(section_title, sandbox_sim.success)