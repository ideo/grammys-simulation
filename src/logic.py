import os
# from copy import deepcopy
# from collections import Counter
import pickle

import streamlit as st
import pandas as pd
import inflect

from .story import STORY, INSTRUCTIONS
from .config import COLORS
from .simulation import Simulation, DATA_DIR


import warnings
# warnings.simplefilter(action='ignore', category=UserWarning)
warnings.filterwarnings('ignore')

p = inflect.engine()


def initialize_session_state():
    """
    Like all functions, this is called each time the page loads. But because
    it's depended upon state change, the code here is only executed upon page
    refresh.
    """
    initial_values = {
        "reset_visuals":        True,
        "num_voters":           1000,
        "num_songs":            1000,
        "num_winners":          15,
        "st_dev":               10,    #This will need to change
    }
    for key, value in initial_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state["reset_visuals"]:
        reset_visuals()
        st.session_state["reset_visuals"] = False


def reset_visuals():
    for filename in os.listdir(DATA_DIR):
        if "chart_df" in filename:
            os.remove(DATA_DIR / filename)


def insert_variables(paragraph, section_title):
    for key, value in st.session_state.items():
        if type(value) in [int, float]:
            key, value = str(key), value
            if key in paragraph:
                
                if section_title == "introduction" and key == "num_voters":
                    threshold = None
                    value = p.number_to_words(value, threshold=threshold)
                    value = value.capitalize()
                else:
                    threshold = 10
                    value = p.number_to_words(value, threshold=threshold)

                paragraph = paragraph.replace(key, value)
    return paragraph
        

def write_story(section_title):
    for paragraph in STORY[section_title]:
        paragraph = insert_variables(paragraph, section_title)
        st.write(paragraph)


def write_instructions(section_title, st_col=None):
    for paragraph in INSTRUCTIONS[section_title]:
        paragraph = insert_variables(paragraph, section_title)
        if st_col is not None:
            st_col.caption(paragraph)
        else:
            st.caption(paragraph)


# def success_message(section_key, success, guac_limit=None, name=None, percent=None):
#     for paragraph in SUCCESS_MESSAGES[section_key][success]:
#         if guac_limit is not None:
#             st.caption(paragraph.replace("GUAC_LIMIT", str(guac_limit)).replace("MISSING_GUACS", str(20-guac_limit)))
#         if name is not None:
#             st.caption(paragraph.replace("NAME", name).replace("PERCENT", percent))
#         else:
#             st.caption(paragraph)


def sidebar():
    """
    Let's put all the sidebar controls here!
    """
    st.sidebar.markdown("# Simulation Parameters")
    msg = """
        We can use this sidebar to tune the simulation as we develop it. We'll 
        disable this section once we're ready to hand it off to the client.
    """
    st.sidebar.write(msg)

    st.sidebar.subheader("Reader Visible Variables")
    label = "How many members vote in the contest?"
    _ = st.sidebar.slider(label, 
        min_value=100, 
        max_value=3000,
        step=100,
        key="num_voters",
        on_change=reset_visuals)

    label = "How many songs have been nominated?"
    _ = st.sidebar.slider(label,
        min_value=50, 
        max_value=5000,
        step=50,
        key="num_songs",
        on_change=reset_visuals)

    label = "How many winning songs are declared?"
    _ = st.sidebar.slider(label,
        min_value=5, 
        max_value=20,
        step=1,
        key="num_winners",
        on_change=reset_visuals)

    st.sidebar.subheader("Under the Hood Variables")
    label = "What is the st. dev. of voters randomly generated scores?"
    _ = st.sidebar.number_input(label,
        min_value=1,
        max_value=20,
        step=1,
        key="st_dev",
        disabled=True)


def load_chart_df(key):
    filename = f"chart_df_{key}.pkl"
    filepath = DATA_DIR / filename
    if os.path.exists(filepath):
        chart_df = pd.read_pickle(filepath)
    else:
        chart_df = initialize_empty_chart_df()
    return chart_df


def save_chart_df(chart_df, key):
    filename = f"chart_df_{key}.pkl"
    filepath = DATA_DIR / filename
    chart_df.to_pickle(filepath)
    

def simulation_section(song_df, section_title, 
        listen_limit=None, ballot_limit=None,
        baseline_results=None,
        num_mafiosos=None, mafia_size=None,
        disabled=False):
    """
    A high level container for running a simulation.
    """
    st.write("")
    num_voters = st.session_state["num_voters"]
    num_winners = st.session_state["num_winners"]
    sim = Simulation(song_df, num_voters, 
        listen_limit=listen_limit,
        ballot_limit=ballot_limit,
        num_winners=num_winners,
        name=section_title,
        num_mafiosos=num_mafiosos, 
        mafia_size=mafia_size)

    col1, col2 = st.columns([2, 5])

    with col1:
        write_instructions(section_title)
        _, cntr, _ = st.columns([1,5,1])
        with cntr:
            start_btn = st.button("Simulate", 
                key=section_title, 
                disabled=disabled)

    if start_btn:
        # delete_chart_df(section_title)
        sim.simulate()
        chart_df = format_condorcet_results_chart_df(sim, baseline_results)
        save_chart_df(chart_df, section_title)

    with col2:
        chart_df = load_chart_df(section_title)
        chart_df, spec = format_spec(chart_df)
        st.vega_lite_chart(chart_df, spec, use_container_width=True)
    
    return sim, chart_df


def initialize_empty_chart_df():
    """
    To display an empty bar chart before the simulation runs
    """
    num_winners = st.session_state["num_winners"]
    data = [0]*num_winners
    chart_df = pd.DataFrame(data, columns=["sum"])
    chart_df["Entrant"] = chart_df.index
    return chart_df


def format_condorcet_results_chart_df(sim, theoretical_results=None):
    """
    Take the pariwise sums from the condorcet results and return a dataframe
    that matches the input that we had previously fed the tally by sums chart
    animation
    """
    _sums = sim.condorcet.pairwise_sums
    ii = sim.condorcet.top_nominee_ids
    chart_df = pd.DataFrame(_sums).iloc[ii]

    # Assign names to top nominees
    chart_df["sum"] = chart_df.sum(axis=1)
    chart_df["Entrant"] = sim.song_df["ID"].astype(str)
    if theoretical_results:
        chart_df["Success"] = chart_df["Entrant"].isin(theoretical_results)
    return chart_df


def print_params(simulations):
    """
    TKTK
    """
    # st.text("Parameter Summary:")
    with st.expander("Parameter Summaries", expanded=False):
        for sim in simulations:
            tab_width = 8
            msg = "{\n"
            for key, value in sim.params.items():
                value = f"'{value}'" if isinstance(value, str) else value
                num_tabs = 3 - (len(key)+1)//tab_width
                tabs = "\t"*num_tabs
                msg += f"\t'{key}':{tabs}{value},\n"
            msg += "}"
            st.code(msg)


def format_spec(chart_df):
    """Format the chart to be shown in each frame of the animation"""

    red = COLORS["red"]
    green = COLORS["avocado-green"]

    if "Success" in chart_df.columns:
        chart_df["Color"] = chart_df["Success"].apply(
            lambda x: green if x else red)

    else:
        chart_df["Color"] = [COLORS["blue"]]*chart_df.shape[0]

    # TODO: Subtitle could display simulation settings.
    if chart_df["sum"].sum() == 0:
        subtitle = "Click 'Simulate' to see the results"
    else:
        subtitle = "Vote tallies of the highest scoring songs."

    spec = {
            # "height":   275,
            "mark": {"type": "bar"},
            "encoding": {
                "y":    {
                    "field": "Entrant", 
                    "type": "nominal", 
                    "sort": "-x",
                    "axis": {"labelAngle": 0, "labelLimit": 0},
                    "title":    None,
                    },
                "x":    {
                    "field": "sum", 
                    "type": "quantitative", 
                    "title": "Vote Tallies"
                    },
                "color": {
                    "field":    "Color",
                    "type":     "nominal",
                    "scale":    None,
                    },
            },
            "title":    {
                "text": f"Simulation Results",
                "subtitle": subtitle, 
            }  
        }
    return chart_df, spec


def format_filepath(sim):
    n_songs = sim.song_df.shape[0]
    n_voters = sim.num_voters
    filename = f"Repeated-Simulations_Sums_{n_songs}-Songs_{n_voters}-Voters.pkl"
    filepath = DATA_DIR / filename
    return filepath


def display_results_of_repeated_contests(sim):
    """This establishes the baseline for Simulation One"""
    filepath = format_filepath(sim)
    with open(filepath, "rb") as pkl_file:
        repeated_contests = pickle.load(pkl_file)

    title = "Who Deserves to Win?"
    subtitle = f"Vote tallies after running {repeated_contests.num_contests} simulated contests."
    x_label = f"Vote Tallies"

    sums_per_song = repeated_contests.sum_of_sums.sum(axis=1)
    chart_df = pd.DataFrame(sums_per_song)
    chart_df["Color"] = [COLORS["blue"]]*chart_df.shape[0]
    chart_df["ID"] = sim.song_df["ID"]
    chart_df.rename(columns={0: x_label}, inplace=True)
    chart_df = chart_df.head(sim.num_winners)
    
    spec = {
            "mark": {"type": "bar"},
            "encoding": {
                "y":    {
                    "field": "ID", 
                    "type": "nominal", 
                    "sort": "-x",
                    "axis": {"labelAngle": 0, "labelLimit": 0},
                    "title":    None,
                    },
                "x":    {
                    "field": x_label, 
                    "type": "quantitative", 
                    # "title": "Vote Tallies"
                    },
                "color": {
                    "field":    "Color",
                    "type":     "nominal",
                    "scale":    None,
                    },
            },
            "title":    {
                "text": title,
                "subtitle": subtitle, 
            }  
        }
    st.write("")
    st.vega_lite_chart(chart_df, spec, use_container_width=True)
    return chart_df


def establish_baseline(repeated_results):
    x_label = f"Vote Tallies"
    repeated_results = repeated_results.sort_values(x_label, ascending=False)

    num_winners = st.session_state["num_winners"]
    baseline_results = repeated_results.head(num_winners)["ID"].tolist()
    return baseline_results



# def format_bar_colors(chart_df, should_win, actually_won):
#     chart_df["Color"] = pd.Series([COLORS["blue"]]*chart_df.shape[0], index=chart_df.index)
#     chart_df.at[actually_won, "Color"] = COLORS["red"]
#     chart_df.at[should_win, "Color"] = COLORS["green"]
#     return chart_df


# def animate_results_of_100_runs(sim, scenario, key):
#     col1, col2 = st.columns([2,5])
#     start_btn = col1.button("Simulate 100 Times", key=key)

#     chart_df = get_row_and_format_dataframe(sim, scenario)
#     spec = format_N_times_chart_spec(chart_df)
#     bar_chart = col2.vega_lite_chart(chart_df, spec)

#     list_who_else_won(chart_df, sim)


# def get_row_and_format_dataframe(sim, scenario):
#     df = pd.read_csv("data/simulate_100_times_sum.csv")
#     df.drop(columns=["Unnamed: 0"], inplace=True)
#     chart_df = df[
#         (df["num_townspeople"] == sim.num_townspeople) & \
#         (df["st_dev"] == sim.st_dev) & \
#         (df["assigned_guacs"] == sim.assigned_guacs) & \
#         (df["perc_fra"] == sim.perc_fra) & \
#         (df["perc_pepe"] == sim.perc_pepe) & \
#         (df["perc_carlos"] == sim.perc_carlos) & \
#         (df["scenario"] == scenario)
#     ]
#     columns = [
#         "num_townspeople",
#         "st_dev",
#         "assigned_guacs",
#         "perc_fra",
#         "perc_pepe",
#         "perc_carlos",
#         "scenario",
#     ]
#     should_win = {
#         "One Clear Winner":     5,
#         "A Close Call":         9,
#         "A Lot of Contenders":  12,
#     }

#     chart_df.drop(columns=columns, inplace=True)
#     chart_df.fillna(value=0.0, inplace=True)
#     _index = chart_df.index[0]
#     chart_df = chart_df.T
#     chart_df.rename(columns={_index: "No Times Won"}, inplace=True)
#     chart_df["No Times Won"] = chart_df["No Times Won"].astype(int)
#     chart_df.index = chart_df.index.astype(int)
#     chart_df = format_bar_colors(chart_df, should_win[scenario], chart_df["No Times Won"].idxmax())
#     chart_df.index.name = "ID"
#     chart_df.reset_index(inplace=True)
#     chart_df.sort_values(by="ID", inplace=True)
#     chart_df["Entrant"] = chart_df["ID"].apply(lambda x: [ent["Entrant"] for ent in ENTRANTS if ent["ID"]==x][0])
#     return chart_df


# def format_N_times_chart_spec(chart_df):
#     spec = {
#             "height":   250,
#             "mark": {"type": "bar"},
#             "encoding": {
#                 "x":    {
#                     "field": "Entrant", "type": "nominal", "sort": "ID",
#                     "axis": {"labelAngle": 45}},
#                 "y":    {
#                     "field": "No Times Won", "type": "quantitative", 
#                     "scale": {"domain": [0, 100]},
#                     "title": "No. Times Won"},
#                 "color":    {
#                     "field": "Color", 
#                     "type": "nomical", 
#                     "scale": None},
#             },
#             "title":    {
#                 "text": f"Simulating the Contest 100 Times",
#                 "subtitle": "How often was each person's guac voted best?", 
#             }  
#         }
#     return spec


# def list_who_else_won(df, sim):
#     df = df[df["No Times Won"] > 0].copy()
#     df.sort_values(by="No Times Won", ascending=False, inplace=True)
    
#     name = df.iloc[0]["Entrant"]
#     wins = df.iloc[0]["No Times Won"]
#     success = wins > 50
#     if success:
#         percent = f"{wins}%"
#     else:
#         percent = f"{100 - wins}%"
#     success_message("100_times", success, name=name, percent=percent)

#     msg = f"**{p.plural('Result', df.shape[0])} of 100 Contests**"
#     for ii in range(0, df.shape[0]):
#         entrant = df.iloc[ii]["Entrant"]
#         obj_score = sim.guac_df[sim.guac_df["Entrant"] == entrant]["Objective Ratings"].iloc[0]
#         wins = df.iloc[ii]["No Times Won"]
#         msg += f"\n- {entrant}, with an objective guac score of {obj_score}, won **{wins}** {p.plural('time', wins)}"

#     st.markdown(msg)


# def types_of_voters(key, pepe=None, fra=None, carlos=None):
#     col1, col2, col3 = st.columns(3)
#     pepe = col1.slider(
#         """
#         What percentage of people in town are like Perky Pepe, who loves 
#         guacamole so much he'll have a hard time giving anyone a bad score?
#         """,
#         value=int(pepe*100) if pepe else 10,
#         min_value=0,
#         max_value=30,
#         format="%g%%",
#         key=key+"pepe")

#     fra = col2.slider(
#         """
#         What percentage of people in town are like Finicky Francisca, who
#         thinks all guacamole is basically mush and won't score any entry too high?
#         """,
#         value=int(fra*100) if fra else 8,
#         min_value=0,
#         max_value=30,
#         format="%g%%",
#         key=key+"fra")

#     carlos = col3.slider(
#         """
#         What percentage of people in town are friends with Cliquey Carlos, and
#         will score high guacamole as high as possible no matter what?
#         """,
#         value=int(carlos*100) if carlos else 12,
#         min_value=0,
#         max_value=30,
#         format="%g%%",
#         key=key+"carlos")

#     pepe /= 100
#     fra /= 100
#     carlos /= 100
#     return pepe, fra, carlos

    
# def animate_condorcet_simulation(sim, key=None):
#     col1, col2 = st.columns([2,5])
#     start_btn = col1.button("Simulate", key=key)

#     if start_btn:
#         sim.simulate()
#         st.session_state[f"{key}_keep_chart_visible"] = True
        
#     if st.session_state[f"{key}_keep_chart_visible"]:
#         results_msg = format_condorcet_results(sim)
#         col2.markdown(results_msg)


# def format_condorcet_results(sim):
#     if len(sim.condorcet_winners) > 1:
#         msg = "And the winners are..."
#         for ii, entrant_id in enumerate(sim.condorcet_winners):
#             name = sim.guac_df["Entrant"].iloc[entrant_id]
#             msg += f"\n - {ii}: Guacamole No. {entrant_id} by {name}!"
    
#     else:
#         entrant_id = sim.condorcet_winner
#         name = sim.guac_df["Entrant"].iloc[entrant_id]
#         msg = f"""
#             And the winner is...
#             1. Guacamole No. {entrant_id} by {name}!
#         """
#     return msg


# def demo_contest(scenario, st_dev):
#     """TKTK"""
#     if scenario == "One Clear Winner":
#         data = [ENTRANTS[5], ENTRANTS[11], ENTRANTS[12]]
#     elif scenario == "A Close Call":
#         data = [ENTRANTS[9], ENTRANTS[11], ENTRANTS[12]]
#     elif scenario == "A Lot of Contenders":
#         data = [ENTRANTS[12], ENTRANTS[0], ENTRANTS[9]]

#     df = pd.DataFrame(data=data)
#     df["ID"] = pd.Series([0, 1, 2])
#     df.rename(columns={scenario: "Objective Ratings"}, inplace=True)
#     df = df[["ID", "Entrant", "Objective Ratings"]].copy()

#     sim = Simulation(df, 5, st_dev, 
#         assigned_guacs=df.shape[0],
#         fullness_factor=0,
#         seed=42)
#     sim.simulate()

#     start_btn = next_contestant(sim)
#     if start_btn:
#         st.button("Next Contestant", on_click=increment_entrant_num)
    

# def next_contestant(sim):
#     col1, col2, col3 = st.columns(3)
#     entrant_num = st.session_state["entrant_num"]
#     col1.image(f"img/guac_icon_{entrant_num}.png", width=100)

#     name =  sim.guac_df.loc[entrant_num]['Entrant']
#     score = sim.guac_df.loc[entrant_num]['Objective Ratings']
#     score = int(round(score))
#     col2.markdown(f"**{name}'s Guacamole**")
#     col2.metric("Your Assesment:", score)

#     start_btn = col3.button("Taste and Score")

#     if start_btn:
#         columns = st.columns(5)
#         for ii, col in enumerate(columns):
#             person = sim.townspeople[ii]
#             score = person.ballot.loc[entrant_num]["Subjective Ratings"]
#             score = int(round(score))
#             col.metric(f"Taster No. {person.number}", score)

#     return start_btn


# def increment_entrant_num():
#     if st.session_state["entrant_num"] < 2:
#         st.session_state["entrant_num"] += 1
#     else:
#         st.session_state["entrant_num"] = 0


# def show_rcv_rankings(sim):
#     rankings = sim.rankings
#     winner = sim.rankings[0][0]

#     msg = "Our winner is...  \n"
#     winning_vote = rankings[0][1]
#     perc = lambda vc: f"{int(round(vc/sim.num_townspeople*100, 0))}%"
#     msg += f"> 1. **{winner}** with {winning_vote} votes! That's {perc(winning_vote)} of the vote.  \n"

#     if sim.rcv.eliminations == 0:
#         msg += f"""{winner} won an outright majority, with no need for 
#             elimination rounds!  \n"""
#     else:
#         original_tally = int(sim.rcv.original_vote_counts.loc[winner, 1])
#         msg += f"""{winner} had an original first-place-vote count of 
#             {original_tally} votes (only {perc(original_tally)} of the vote), 
#             but won a {sim.rcv.win_type} after {sim.rcv.eliminations} rounds of 
#             elimination.  \n"""

#     if len(rankings) > 1:
#         msg += f"\nAnd our runners up are...  \n"
#         for prsn in range(1, min(6, len(rankings))):
#             msg += f"> {prsn+1}. {rankings[prsn][0]} with {rankings[prsn][1]} votes. That's {perc(rankings[prsn][1])} of the vote.  \n"
#         st.markdown(msg)


# def show_fptp_rankings(rankings, num_townspeople):
#     msg = "Our winner is...  \n"
#     winning_vote = rankings[0][1]
#     perc = lambda vc: int(round(vc/num_townspeople*100, 0))

#     msg += f"> 1. **{rankings[0][0]}** with {winning_vote} votes! That's {perc(winning_vote)}% of the vote.  \n"
#     if len(rankings) > 1:
#         msg += f"And our runners up are...  \n"
#         for prsn in range(1, min(6, len(rankings))):
#             msg += f"> {prsn+1}. {rankings[prsn][0]} with {rankings[prsn][1]} votes. That's {perc(rankings[prsn][1])}% of the vote.  \n"
#         st.markdown(msg)
