import os
import json
import pickle
from collections import defaultdict

import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import inflect

from .config import COLORS
from .story import STORY, INSTRUCTIONS
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
        "listen_limit":         250,
        "ballot_limit":         50,
        "st_dev":               10,    #This will need to change
        "total_time_str":       "",
    }
    for key, value in initial_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # st.session_state["total_time_str"] = format_total_time()

    if st.session_state["reset_visuals"]:
        reset_visuals()
        st.session_state["reset_visuals"] = False    


def reset_visuals():
    for filename in os.listdir(DATA_DIR):
        if "chart_df" in filename:
            os.remove(DATA_DIR / filename)


def insert_variables(paragraph, section_title, story=True):
    for key, value in st.session_state.items():
        if type(value) in [int, float]:
            key, value = str(key), value
            for _ in range(paragraph.count(key)):
                if story:
                    str_value = p.number_to_words(value)

                    # If the word is at the start of a sentence, capitalize it
                    # This only works for the first occurrence of a variable
                    ii = paragraph.index(key)
                    if paragraph[ii-2] == ".":
                        str_value = str_value.capitalize()
                else:
                    str_value = str(value)

                paragraph = paragraph.replace(key, str_value, 1)
    return paragraph
        

def write_story(section_title, st_col=st):
    for paragraph in STORY[section_title]:
        paragraph = insert_variables(paragraph, section_title)
        st_col.write(paragraph)


def write_instructions(section_title, st_col=st):
    for paragraph in INSTRUCTIONS[section_title]:
        paragraph = insert_variables(paragraph, section_title, story=False)
        st_col.caption(paragraph)


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

    # label = "How many winning songs are declared?"
    # _ = st.sidebar.slider(label,
    #     min_value=5, 
    #     max_value=20,
    #     step=1,
    #     key="num_winners",
    #     on_change=reset_visuals)

    st.sidebar.subheader("Under the Hood Variables")
    label = "What is the st. dev. of voters randomly generated scores?"
    _ = st.sidebar.number_input(label,
        min_value=1,
        max_value=20,
        step=1,
        key="st_dev",
        disabled=True)
    

def select_num_winners():
    """
    Let the reader determine how many 'winners' we determine. How long is the 
    final list of nominees?
    """
    col1, _, col2 = st.columns([5,1,5])

    write_instructions("select_num_winners", col1)

    label = "Choose the number of contest finalists."
    options = [10, 15, 20]
    default = st.session_state["num_winners"]
    num_winners = col2.radio(label, options, index=options.index(default))
    st.session_state["num_winners"] = num_winners


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
    # _sums = sim.condorcet.pairwise_sums
    _sums = sim.condorcet.preferences
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
        subtitle = f"Vote tallies of the {chart_df.shape[0]} highest scoring songs."

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

    # TODO: Re-run these 100 simulations so you can switch it to preferences.
    sums_per_song = repeated_contests.sum_of_sums.sum(axis=1)
    # sums_per_song = repeated_contests.preferences.sum(axis=1)
    chart_df = pd.DataFrame(sums_per_song)

    title = "Who Deserves to Win?"
    subtitle = f"Vote tallies of the {sim.num_winners} highest scoring songs after running {repeated_contests.num_contests} simulated contests."
    x_label = f"Vote Tallies"
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
    baseline_titles = repeated_results.head(num_winners)["ID"].tolist()
    baseline_indices = repeated_results.head(num_winners).index.tolist()
    return baseline_titles, baseline_indices


# def format_total_time():
#     num_songs = st.session_state["num_songs"]
#     avg_song_length = 3.5   #minutes
#     total_time = num_songs * avg_song_length
#     # total_time /= 30

#     # Format
#     minutes_in_a_day = 60*24
#     days = total_time // minutes_in_a_day
#     leftover = total_time % minutes_in_a_day

#     hours = leftover // 60
#     minutes = leftover % 60

#     days, hours, minutes = int(days), int(hours), int(minutes)
#     total_time_str = f"{days} days, {hours} hours, and {minutes} minutes"
#     return total_time_str


def heatmap_filepath(num_winners, ballot_limit):
    filepath = DATA_DIR / f"heatmap_{num_winners}_winners_{ballot_limit}_ballot_limit.json"
    return filepath


def explore_changing_sample_size(ballot_limit, baseline):
    """
    This generates the spec for the heatmap. It saves it so the streamlit app
    can just load the chart, not the raw data.
    """
    # num_songs = sim.song_df.shape[0]
    num_songs = st.session_state["num_songs"]
    filepath = DATA_DIR / f"exploring_listening_limit_{num_songs}_songs_{ballot_limit}_ballot_limit.pkl"
    with open(filepath, "rb") as pkl_file:
        exploration = pickle.load(pkl_file)

    # This can all be done ahead of time. Only the chart_df needs to be saved
    # Tally, on average, how many of the top N were fair
    num_winners = len(baseline)
    outcome_quality = defaultdict(dict)
    num_contests = exploration[3000][500].num_contests
    num_contests = p.number_to_words(num_contests)
    # num_songs = p.number_to_words(num_songs)

    for num_voters, contests in exploration.items():
        for listen_limit, outcomes in contests.items():
            num_fair_winners = []
            for _, results in outcomes.contest_winners.items():
                winners = results[:num_winners]
                num_fair_winners.append(len(set(winners).intersection(set(baseline))))
            
            # outcome_quality[num_voters][listen_limit] = np.mean(num_fair_winners)
            outcome_quality[num_voters][listen_limit] = np.median(num_fair_winners)

    # Format Heatmap
    voter_range = list(outcome_quality.keys())
    sample_range = list(outcome_quality[voter_range[0]].keys())
    x, y = np.meshgrid(sample_range, voter_range)

    x_label = "Sample Size"
    y_label = "Voters"

    source = pd.DataFrame({x_label: x.ravel(), y_label: y.ravel()})
    source["z"] = source.apply(lambda row: outcome_quality.get(row[y_label], np.nan).get(row[x_label], np.nan), axis=1)

    # First time doing an actual altair chart instead of doing a vega-lite spec
    chart = alt.Chart(source).mark_rect().encode(
        x=alt.X(f"{x_label}:O", axis=alt.Axis(
            title="Sample Size: How Many Songs Voters Listened To",
            labelAngle=0,
            )), 
        y=alt.Y(f"{y_label}:O", sort='descending', axis=alt.Axis(
            title="No. Voters"
            )), 
        color=alt.Color(
            "z:Q", 
            scale=alt.Scale(scheme="RedBlue", domain=[0,num_winners]),
            title="Median",
        )
    ).properties(
        title={
            "text": "Contest Consistency",
            "subtitle": [
                f"The median number of deserved winners within the top {num_winners}.",
                f"{num_contests.capitalize()} contests at each configuation. {num_songs} nominated songs. Ballot size of {ballot_limit}.",]
        }
    )
    filepath = heatmap_filepath(num_winners, ballot_limit)
    chart.save(filepath)



def load_or_generate_heatmap_chart(num_winners, ballot_limit, baseline, regenerate=False):
    filepath = heatmap_filepath(num_winners, ballot_limit)
    
    if not os.path.exists(filepath) or regenerate:
        explore_changing_sample_size(ballot_limit, baseline) 
    
    with open(filepath, "r") as json_object:
        chart_dict = json.load(json_object)

    # Original chart specified as an Altair oject. When loaded as a dictionary
    # we display it as a vega-lite object.
    st.vega_lite_chart(chart_dict, use_container_width=True)