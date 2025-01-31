import os
# import json
import math
# import pickle
# from collections import defaultdict

import streamlit as st
# import altair as alt
import pandas as pd
import numpy as np
import inflect

from .config import COLORS
from .simulation import Simulation, DATA_DIR
import src.utils as utils
import emoji

import warnings
# warnings.simplefilter(action='ignore', category=UserWarning)
warnings.filterwarnings('ignore')

GRAMMAR = inflect.engine()


def initialize_session_state():
    """
    Like all functions, this is called each time the page loads. But because
    it's depended upon state change, the code here is only executed upon page
    refresh.
    """
    initial_values = {
        "reset_visuals":            True,
        "num_voters":               1000,
        "num_songs":                500,
        "num_winners":              5,
        "finalist_options":         [5, 10],
        "listen_limit":             250,
        "ballot_limit":             50,
        "st_dev":                   10,
        "total_time_str":           None,
        "show_state" :              0,
        "persist_demo_takeaway":    0
    }
    for key, value in initial_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state["total_time_str"] is None:
        st.session_state["total_time_str"] = format_total_time()

    if st.session_state["reset_visuals"]:
        reset_visuals()
        st.session_state["reset_visuals"] = False    


def reset_visuals():
    for filename in os.listdir(DATA_DIR):
        if "chart_df" in filename:
            os.remove(DATA_DIR / filename)


def update_show_state(section_number):
    if st.session_state["show_state"] < section_number:
        st.session_state["show_state"] = section_number


def proceed_button(col, label, show_state):
    if st.session_state["show_state"] <= show_state:
        next_show_state = show_state + 1
        on_click = lambda: update_show_state(next_show_state)
        _ = col.button(label, on_click=on_click)


def this_section_is_viewable(show_state):
    return st.session_state["show_state"] >= show_state


def insert_variables(paragraph, section_title, story=True):
    for key, value in st.session_state.items():
        if type(value) in [int, float, str]:
            key, value = str(key), str(value)
            for _ in range(paragraph.count(key)):
                paragraph = paragraph.replace(key, value, 1)                
    return paragraph
        

def write_story(section_title, st_col=st, header_level=3, key="story"):
    if header_level is not None:
        header = "#"*header_level
        if key == "takeaway":
            st_col.markdown(f"{header} Takeaway")
        else:
            st_col.markdown(f"{header} {section_title}")

    story = utils.load_text()[section_title][key]
    for paragraph in story:
        paragraph = insert_variables(paragraph, section_title)
        st_col.write(paragraph)


def write_instructions(section_title, st_col=st):
    instructions = utils.load_text()[section_title]["instructions"]
    for paragraph in instructions:
        paragraph = insert_variables(paragraph, section_title, story=False)
        st_col.caption(paragraph)
        # st_col.markdown(f"**{paragraph}**")


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

    st.sidebar.subheader("Under the Hood Variables")
    label = "What is the st. dev. of voters randomly generated scores?"
    _ = st.sidebar.number_input(label,
        min_value=1,
        max_value=20,
        step=1,
        key="st_dev",
        disabled=False)
    

def select_num_winners(section_title):
    """
    Let the reader determine how many 'winners' we determine. How long is the 
    final list of nominees?
    """
    col1, _, col2 = st.columns([5,1,5])
    write_instructions(section_title, col1)

    label = "Choose the number of contest finalists."
    options = st.session_state["finalist_options"]
    num_winners = col2.radio(label, options)
    st.session_state["num_winners"] = num_winners


def interactive_demo(song_df):
    """The interactive portion of the simulation explanation"""
    st.write("")
    section_title = "How might we test different voting systems before deciding whether to use them in the real world?"
    st.markdown(f"##### {section_title}")
    write_story("Imaginary Songs", header_level=None)
    col1, col2 = st.columns([6,4])

    demo_songs = [
        "“It’s Unbelievable” by The Mischa Bartons",
        '"Clique Claque" by Bored Teens',
        '"Deathlehem" by Pluton Monolith',
        '"Kiddie Pool" by Glitterfreckle',
        '"Natural Causes" by Knuckles Johnson',
    ]

    with col1:
        candidates = song_df[song_df["ID"].isin(demo_songs)]
        candidates = candidates.sort_values("Objective Ratings", ascending=False)
        label = "Example Songs"
        options = candidates["ID"].values
        selection = st.radio(label, options, label_visibility="hidden")

    with col2:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        sCol1 , sCol2 = st.columns(2)
        with sCol1:
            column = "Objective Ratings"
            score = candidates[candidates["ID"] == selection][column].iloc[0]
            score = round(score/10, 1)
            st.metric("Objective Score", score)
        with sCol2:
            st.text("")
            if score > 8:
                explanation = "This song is **amazing**!"
            elif score > 6:
                explanation = "This song is **pretty good**"
            elif score > 4:
                explanation = "This song is **pretty average**"
            else:
                explanation = "This song is **not great**"
            st.markdown(f"##### {explanation}")
        
    st.write("")
    st.write("")
    section_title = "Imaginary Voters"
    write_story(section_title, header_level=5)
    st.write("")
    _, cntr, _ = st.columns([2,2,2])
    clicked = cntr.button('Simulate "Subjective" Scores')

    # Define negative values and we can show the vega-lite chart but the 
    # scores will be below the visible limit.
    LOVE, SMILE, NEUTRAL, MEH, POOP = [":heart_eyes:",":smirk:",":expressionless:",":unamused:",":hankey:"]
    num_example_voters = 7
    subj_scores = [-1]*num_example_voters
    if clicked:
        st.session_state["persist_demo_takeaway"] = 1
        columns = st.columns(num_example_voters)
        
        for ii, col in enumerate(columns):
            st_dev = st.session_state["st_dev"]/10
            subjective_score = np.random.normal(loc=score, scale=st_dev)
            subjective_score = round(subjective_score, 1)

            if subjective_score <= 0.0:
                subjective_score = 0.0
            if subjective_score >= 10.0:
                subjective_score = 10.0

            if subjective_score > 8:
                emoj = LOVE
            elif subjective_score > 6:
                emoj = SMILE
            elif subjective_score > 4:
                emoj = NEUTRAL
            elif subjective_score > 2: 
                emoj = MEH
            else:
                emoj = POOP
            col.markdown(emoji.emojize(emoj))
            col.metric(f"Voter #{ii+1}", subjective_score)
            subj_scores.append(subjective_score)
    
    visualize_example_votes(score, subj_scores, selection)

    if st.session_state["persist_demo_takeaway"]:
        write_story(section_title, header_level=5, key="takeaway")


def visualize_example_votes(obj_score, subj_scores, song_name):
    chart_df = pd.DataFrame(subj_scores, columns=["Votes"])
    chart_df["Objective Score"] = [obj_score]*chart_df.shape[0]

    objective_spec = {
        "mark": {
            "type":  "rule",
            "clip": True,
            },
        "encoding": {
            "x":    {
                "field":    "Objective Score",
                "type":     "quantitative",
                "scale":    {"domain": [0, 10]},
                "title":    ["Songs' Objective and 'Subjective' Scores", "Scored out of 10"],
            },
            "size": {"value": 4},
            "color": {"value": COLORS["green"]},
        },
    }

    subjective_spec = {
        "mark": {
            "type":  "rule",
            "clip": True,
            },
        "encoding": {
            "x":    {
                "field":    "Votes",
                "type":     "quantitative",
                "scale":    {"domain": [0, 10]},
                "axis": {"tickMinStep": 1},
                "title":    "",
            },
            "size": {"value": 2},
            "color": {"value": COLORS["blue"]},   
        },
    }

    spec = {
        "height":   300,
        "title":    {
            "text":     song_name,
            "subtitle": "This song's objective score in green and each simulated voter's subjective score in blue."
            },
        "layer":    [objective_spec, subjective_spec],
    }
    st.vega_lite_chart(chart_df, spec, use_container_width=True)


def load_chart_df(key, method):
    filename = f"chart_df_{key}_{method}.pkl"
    filepath = DATA_DIR / filename
    if os.path.exists(filepath):
        chart_df = pd.read_pickle(filepath)
    else:
        chart_df = initialize_empty_chart_df()
    return chart_df


def save_chart_df(chart_df, key, method):
    filename = f"chart_df_{key}_{method}.pkl"
    filepath = DATA_DIR / filename
    chart_df.to_pickle(filepath)
    

def simulation_section(song_df, section_title,
        num_voters=None, num_winners=None,
        listen_limit=None, ballot_limit=None,
        baseline_results=None,
        num_mafiosos=0, mafia_size=0,
        disabled=False,
        alphabetical=False, 
        subtitles={}):
    """
    A high level container for running a simulation.
    """
    st.write("")
    if num_voters is None:
        num_voters = st.session_state["num_voters"]
    if num_winners is None:
        num_winners = st.session_state["num_winners"]

    methods = subtitles.keys()

    sim = Simulation(song_df, num_voters, 
        st_dev=st.session_state["st_dev"],
        listen_limit=listen_limit,
        ballot_limit=ballot_limit,
        num_winners=num_winners,
        name=section_title,
        num_mafiosos=num_mafiosos, 
        mafia_size=mafia_size,
        alphabetical=alphabetical,
        methods=methods)

    # if section_title != "Sandbox":
    write_instructions(section_title)
        
    _, cntr, _ = st.columns([3,1,3])
    with cntr:
        start_btn = st.button("Simulate", 
            key=section_title, 
            disabled=disabled)

    if start_btn:
        sim.simulate()
        for method in methods:
            chart_df = format_chart_df(sim, baseline_results, method=method)
            save_chart_df(chart_df, section_title, method)

    for method in methods:
        chart_df = load_chart_df(section_title, method)
        num_corrupt_voters = sim.num_mafiosos * sim.mafia_size
        subtitle = subtitles[method]
        if sim.listen_limit is not None:
            if hasattr(sim, "listen_counts"):
                average_listen_count = sim.listen_counts.mean()
            else:
                average_listen_count = None

        chart_df, spec = format_spec(chart_df, num_voters=num_voters,
                                    num_corrupt_voters=num_corrupt_voters, 
                                    subtitle=subtitle, method=method,
                                    average_listen_count=average_listen_count)
        st.vega_lite_chart(chart_df, spec, use_container_width=True)

    # if listen_limit is not None:
    #     listen_count_histogram(sim)

    if chart_df["Vote Tallies"].sum() > 0 and section_title != "Sandbox":
        write_story(section_title, header_level=5, key="takeaway")

        if section_title == "The Power of Randomness":
            repeated_sim_text()
    
    return sim, chart_df


def initialize_empty_chart_df():
    """
    To display an empty bar chart before the simulation runs
    """
    num_winners = st.session_state["num_winners"]
    data = [0]*num_winners
    chart_df = pd.DataFrame(data, columns=["Vote Tallies"])
    chart_df["Entrant"] = chart_df.index
    return chart_df


def format_chart_df(sim, baseline=None, method="condorcet"):
    """
    Take the pariwise sums from the condorcet results and return a dataframe
    that matches the input that we had previously fed the tally by sums chart
    animation
    """
    if method == "condorcet":
        _sums = sim.condorcet.preferences
        ii = sim.condorcet.top_nominee_ids
    
    if method == "current":
        _sums = sim.current_method.tallies
        ii = sim.current_method.winners

    chart_df = pd.DataFrame(_sums)
    chart_df["Ballot Position"] = sim.song_df.index.values
    chart_df = chart_df.iloc[ii]

    chart_df["Vote Tallies"] = chart_df.sum(axis=1)
    chart_df["Entrant"] = sim.song_df["ID"].astype(str)
    objective_rankings = sim.song_df.sort_values("Objective Ratings", ascending=False).copy()
    objective_rankings["Rank"] = np.arange(0, objective_rankings.shape[0])
    objective_rankings["Rank"] += 1
    chart_df["Rank"] = objective_rankings["Rank"].apply(lambda x: f"{GRAMMAR.ordinal(x)} Place")
    chart_df["Score"] = objective_rankings["Objective Ratings"].apply(lambda x: round(x/10, 2))
    chart_df["Ballot Position"] = chart_df["Ballot Position"].apply(lambda x: f"{x} out of {sim.song_df.shape[0]}")

    if baseline:
        chart_df["Success"] = chart_df["Entrant"].isin(baseline)
    return chart_df


def format_spec(chart_df, num_voters=None, num_corrupt_voters=0, subtitle=None, method="condorcet", average_listen_count=None):
    """Format the chart to be shown in each frame of the animation"""

    red = COLORS["red"]
    green = COLORS["avocado-green"]

    if "Success" in chart_df.columns:
        chart_df["Color"] = chart_df["Success"].apply(
            lambda x: green if x else red)
        chart_df["Deserved Winner?"] = chart_df["Success"].apply(
            lambda x: "Yes" if x else "No")

    else:
        chart_df["Color"] = [COLORS["blue"]]*chart_df.shape[0]

    # TODO: Subtitle could display simulation settings.
    if chart_df["Vote Tallies"].sum() == 0:
        title = "Simulation Results"
        subtitle_text = "Click 'Simulate' to see the results"
    else:
        if method == "condorcet":
            title = "Results with Ranked Ballots"
        else:
            title = "Results with Simple Vote Ballots"

        subtitle_text = [f"Vote tallies of the {chart_df.shape[0]} highest scoring songs."]
        if subtitle is not None:         
            if average_listen_count is not None:
                listen_count_note = f" On average, each song was assigned to {int(average_listen_count)} voters."
                subtitle += listen_count_note
            subtitle_text.append(subtitle)

        if num_corrupt_voters:
            if num_voters is None:
                num_voters = st.session_state["num_voters"]
            percent = round(100 * num_corrupt_voters / num_voters)
            subtitle_text += [f"{percent}% of the voters are corrupt."]
    

    upper_lim = chart_df["Vote Tallies"].max()
    round_to = 100 if upper_lim > 500 else 10
    upper_lim = int(math.ceil(upper_lim / round_to)) * round_to
    
    lower_lim = chart_df["Vote Tallies"].min() - 25
    lower_lim = int(math.floor(lower_lim / round_to)) * round_to

    spec = {
            # "height":   275,
            "mark": {
                "type": "bar",
                "clip": True,
                },
            "encoding": {
                "y":    {
                    "field":    "Entrant", 
                    "type":     "nominal", 
                    "sort":     "-x",
                    "axis":     {"labelAngle": 0, "labelLimit": 0},
                    "title":    None,
                    },
                "x":    {
                    "field":    "Vote Tallies", 
                    "type":     "quantitative", 
                    "title":    "Vote Tallies",
                    "scale":    {"domain": [lower_lim, upper_lim]},
                    },
                "color": {
                    # "field":    "Color",
                    # "scale":    None,
                    "field":    "Deserved Winner?",
                    "type":     "nominal",
                    "scale":    {
                        "domain":   ["No", "Yes"],
                        "range":   [COLORS["red"], COLORS["green"]],
                        }
                    },
                "tooltip": [
                    {"field": "Entrant", "type": "nominal"},
                    {"field": "Vote Tallies", "type": "quantitative"},
                    {"field": "Score", "type": "quantitative"},
                    {"field": "Rank", "type": "nominal"},
                    {"field": "Deserved Winner?", "type": "nominal"},
                    {"field": "Ballot Position", "type": "nominal"},
                ]
            },
            "title":    {
                "text":     title,
                "subtitle": subtitle_text, 
            },
            "config": {
                "legend": {
                    "orient": "bottom", 
                    "direction":    "horizontal",
                    "titleOrient": "left",
                    "layout": {"bottom": {"anchor": "end"}},
                    }
            }
        }
    return chart_df, spec


def format_filepath(sim):
    n_songs = sim.song_df.shape[0]
    n_voters = sim.num_voters
    filename = f"Repeated-Simulations_Sums_{n_songs}-Songs_{n_voters}-Voters.pkl"
    filepath = DATA_DIR / filename
    return filepath


def listen_count_histogram(sim):
    if hasattr(sim, "listen_counts"):
        spec = {
            "height":   300,
            "title":    {
                "text": "How Many Voters Vote on Each Song?",
                "subtitle": ""
                },
            "mark": "bar",
            "encoding": {
                "x": {
                    "bin":  True,
                    "binned":  {"step": 10},
                    "field": "Listen Count",
                    "title": ["How many times a song was assigned to a voter", "(Binned)"],
                    },
                "y": {
                    "aggregate": "count",
                    "title":    "No. of times"
                    }
            }
        }
        st.vega_lite_chart(sim.listen_counts, spec, use_container_width=True)


# def display_results_of_repeated_contests(sim):
#     """This establishes the baseline for Simulation One"""
#     filepath = format_filepath(sim)
#     with open(filepath, "rb") as pkl_file:
#         repeated_contests = pickle.load(pkl_file)

#     sums_per_song = repeated_contests.sum_of_rankings.sum(axis=1)
#     chart_df = pd.DataFrame(sums_per_song)

#     title = "Who Deserves to Win?"
#     subtitle = f"Vote tallies of the {sim.num_winners} highest scoring songs after running {repeated_contests.num_contests} simulated contests."
#     x_label = f"Vote Tallies"
#     chart_df["Color"] = [COLORS["blue"]]*chart_df.shape[0]
#     chart_df["ID"] = sim.song_df["ID"]
#     chart_df.rename(columns={0: x_label}, inplace=True)
#     chart_df = chart_df.head(sim.num_winners)
    
#     spec = {
#             "mark": {"type": "bar"},
#             "encoding": {
#                 "y":    {
#                     "field": "ID", 
#                     "type": "nominal", 
#                     "sort": "-x",
#                     "axis": {"labelAngle": 0, "labelLimit": 0},
#                     "title":    None,
#                     },
#                 "x":    {
#                     "field": x_label, 
#                     "type": "quantitative", 
#                     # "title": "Vote Tallies"
#                     },
#                 "color": {
#                     "field":    "Color",
#                     "type":     "nominal",
#                     "scale":    None,
#                     },
#             },
#             "title":    {
#                 "text": title,
#                 "subtitle": subtitle, 
#             }  
#         }
#     st.write("")
#     st.vega_lite_chart(chart_df, spec, use_container_width=True)
#     return chart_df


def top_songs_chart(song_df, start_loc, end_loc):
    df = song_df.sort_values("Objective Ratings", ascending=False).copy()
    df = df.iloc[start_loc:end_loc][["Objective Ratings", "ID"]]
    df.rename(columns={"ID": "Song & Artist"}, inplace=True)
    df["Objective Ratings"] = df["Objective Ratings"].apply(lambda x: round(x/10, 2))
    df = df.rename(columns={"Objective Ratings": "Score"}).set_index("Score")
    st.dataframe(df)


def establish_baseline(song_df, num_winners=None, no_story=False):
    if not no_story:
        st.write("")
        st.markdown("##### Establishing a Baseline")
        col1, col2 = st.columns(2)
        with col1:
            top_songs_chart(song_df, 0, 5)
        
        with col2:
            top_songs_chart(song_df, 5, 10)

        write_story("Establishing a Baseline", header_level=None)
    
    if num_winners is None:
        num_winners = st.session_state["num_winners"]
    top_songs = song_df.sort_values("Objective Ratings", ascending=False).head(num_winners)
    baseline_titles = top_songs["ID"].tolist()
    baseline_indices = top_songs.index.tolist()
    return baseline_titles, baseline_indices


# def print_params(simulations):
#     """
#     TKTK
#     """
#     # st.text("Parameter Summary:")
#     with st.expander("Parameter Summaries", expanded=False):
#         for sim in simulations:
#             tab_width = 8
#             msg = "{\n"
#             for key, value in sim.params.items():
#                 value = f"'{value}'" if isinstance(value, str) else value
#                 num_tabs = 3 - (len(key)+1)//tab_width
#                 tabs = "\t"*num_tabs
#                 msg += f"\t'{key}':{tabs}{value},\n"
#             msg += "}"
#             st.code(msg)


def repeated_sim_text():
    num_winners = st.session_state["num_winners"]
    st.write("")
    st.markdown("##### Repeated Simulations")
    st.write("The benefit of simulations is we can run things many times and explore the range of outcomes. We simulated a contest where 1000 voters listened to 50 songs each.")

    col1, col2 = st.columns(2)

    with col1:
        # Condorcet
        five_winner_text = "Using ballots where voters rank their top 25 songs, 59% of the time 4 out of 5 of the finalists were deserved winners; an additional 34% of the time, 3 out 5 finalists were deserved winners. No times did no deserved winners make it into the list of five finalists."
        ten_winner_text = "Using ballots where voters rank their top 25 songs, 78% of the time 8 out of 10 of the finalists were deserved winners; an additional 18% of the time, 7 out 10 finalists were deserved winners. No times did less than 6 deserved winners make it into the list of ten finalists."

        if num_winners == 5:
            st.write(five_winner_text)
        if num_winners == 10:
            st.write(ten_winner_text)

    with col2:
        five_winner_text = "Using ballots where voters cast one vote each for their favorite 5 songs, 67% of the time 4 out of 5 of the finalists were deserved winners; an additional 27% of the time, 3 out 5 finalists were deserved winners. No times did no deserved winners make it into the list of five finalists."
        ten_winner_text = "Using ballots where voters cast one vote each for their favorite 5 songs, 25% of the time 8 out of 10 of the finalists were deserved winners; an additional 33% of the time, 7 out 10 finalists were deserved winners. No times did less than 4 deserved winners make it into the list of ten finalists."

        if num_winners == 5:
            st.write(five_winner_text)
        if num_winners == 10:
            st.write(ten_winner_text)


def format_total_time():
    num_songs = st.session_state["num_songs"]
    avg_song_length = 3.5   #minutes
    total_time = num_songs * avg_song_length
    # total_time /= 30

    # Format
    minutes_in_a_day = 60*24
    days = total_time // minutes_in_a_day
    leftover = total_time % minutes_in_a_day

    hours = leftover // 60
    minutes = leftover % 60

    days, hours, minutes = int(days), int(hours), int(minutes)
    total_time_str = f"{days} days, {hours} hours, and {minutes} minutes"
    return total_time_str