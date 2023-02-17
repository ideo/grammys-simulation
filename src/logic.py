import os

import streamlit as st
import pandas as pd
import time
# import inflect

# from .story import STORY, INSTRUCTIONS, SUCCESS_MESSAGES
# from .config import COLORS, ENTRANTS, DEMO_CONTEST
# from .simulation import Simulation
from src.story import STORY, INSTRUCTIONS, SUCCESS_MESSAGES
from src.config import COLORS, ENTRANTS, DEMO_CONTEST
from src.simulation import Simulation, DATA_DIR


import warnings
# warnings.simplefilter(action='ignore', category=UserWarning)
warnings.filterwarnings('ignore')

# p = inflect.engine()


def initialize_session_state():
    """
    Like all functions, this is called each time the page loads. But because
    it's depended upon state change, the code here is only executed upon page
    refresh.
    """
    initial_values = {
        "reset_visuals":        True,
        "num_voters":           200,
        "num_songs":            100,
        "num_nominees":         10,
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


def write_story(section_title, **kwargs):
    for paragraph in STORY[section_title]:
        for key, value in kwargs.items():
            key, value = str(key), str(value)
            if key in paragraph:
                paragraph = paragraph.replace(key, value)
        st.write(paragraph)


def write_instructions(section_title, st_col=None):
    for paragraph in INSTRUCTIONS[section_title]:
        if st_col is not None:
            st_col.caption(paragraph)
        else:
            st.caption(paragraph)


def success_message(section_key, success, guac_limit=None, name=None, percent=None):
    for paragraph in SUCCESS_MESSAGES[section_key][success]:
        if guac_limit is not None:
            st.caption(paragraph.replace("GUAC_LIMIT", str(guac_limit)).replace("MISSING_GUACS", str(20-guac_limit)))
        if name is not None:
            st.caption(paragraph.replace("NAME", name).replace("PERCENT", percent))
        else:
            st.caption(paragraph)


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

    label = "How many nominees move to the next round?"
    _ = st.sidebar.slider(label,
        min_value=5, 
        max_value=20,
        step=1,
        key="num_nominees",
        on_change=reset_visuals)

    st.sidebar.subheader("Under the Hood Variables")
    label = "What is the st. dev. of voters randomly generated scores?"
    _ = st.sidebar.number_input(label,
        min_value=1,
        max_value=20,
        step=1,
        key="st_dev")


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


def simulation_section(song_df, section_title, song_limit=None):
    """
    A high level container for running a simulation.
    """
    num_voters = st.session_state["num_voters"]
    num_nominees = st.session_state["num_nominees"]
    sim = Simulation(song_df, num_voters, 
        song_limit=song_limit,
        num_nominees=num_nominees,
        name=section_title)

    col1, col2 = st.columns([2, 5])

    with col1:
        write_instructions(section_title)
        _, cntr, _ = st.columns([1,5,1])
        with cntr:
            start_btn = st.button("Simulate", key=section_title)

    if start_btn:
        sim.simulate()
        chart_df = format_condorcet_results_chart_df(sim)
        save_chart_df(chart_df, section_title)

    with col2:
        chart_df = load_chart_df(section_title)
        chart_df, spec = format_spec(chart_df, sim)
        st.vega_lite_chart(chart_df, spec, use_container_width=True)
    
    return sim


def initialize_empty_chart_df():
    """
    To display an empty bar chart before the simulation runs
    """
    num_nominees = st.session_state["num_nominees"]
    data = [0]*num_nominees
    chart_df = pd.DataFrame(data, columns=["sum"])
    chart_df["Entrant"] = chart_df.index
    return chart_df


def format_condorcet_results_chart_df(sim):
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
    chart_df["Entrant"] = sim.song_df["ID"]
    return chart_df


def print_params(simulations):
    """
    TKTK
    """
    # st.text("Parameter Summary:")
    with st.expander("Parameter Summaries", expanded=False):
        for sim in simulations:
            tab_width = 6
            msg = "{\n"
            for k, v in sim.params.items():
                v = f"'{v}'" if isinstance(v, str) else v
                num_tabs = 3 - len(k)//tab_width
                tabs = "\t"*num_tabs
                msg += f"\t'{k}':{tabs}{v},\n"
            msg += "}"
            st.code(msg)


# def animate_results(sim, key):
#     """The one function to be called in app.py"""
#     if sim.method == "sum":
#         animate_summation_results(sim, key=key)
#     elif sim.method == "condorcet":
#         animate_condorcet_simulation(sim, key=key)
#     elif sim.method == "rcv":
#         show_rcv_rankings(sim)
#     elif sim.method == "fptp":
#         show_fptp_rankings(sim.rankings, sim.num_townspeople)     


# def animate_summation_results(sim, key):
#     """
#     Creates the `Simulate` button, animated chart, and success/fail message
#     """
#     col1, col2 = st.columns([2,5])
#     # start_btn = col1.button("Simulate", key=key)

#     bar_chart = None
#     # if start_btn:
#     if sim.townspeople:

#         # results_df = sim.results_df.copy()
#         # results_df.drop(columns=["sum"], inplace=True)
#         chart_df = format_condorcet_results_chart_df(sim)
#         st.write(chart_df)
#         subtitle = "And the winner is... "
#         y_max = int(chart_df["sum"].max())
#         # y_max = sim.condorcet.top_vote_counts.max()


#         animation_duration = 10 #second
#         time_per_frame = animation_duration / chart_df.shape[0] / 20

#     # bar_chart = None
#     # if start_btn:
#         st.session_state[f"{key}_keep_chart_visible"] = True
#         for NN in range(chart_df.shape[1]):
#             chart_df, spec = format_spec(sim, subtitle, y_max, col_limit=NN)
#             if bar_chart is not None:
#                 bar_chart.vega_lite_chart(chart_df, spec, use_container_width=True)
#             else:
#                 bar_chart = col2.vega_lite_chart(chart_df, spec, use_container_width=True)

#             # time.sleep(.01/2)
#             time.sleep(time_per_frame)

#     if sim.townspeople and st.session_state[f"{key}_keep_chart_visible"]:
#         # Ensure the final chart stays visible
#         chart_df, spec = format_spec(sim, subtitle, y_max)
#         if bar_chart is not None:
#             bar_chart.vega_lite_chart(chart_df, spec, use_container_width=True)
#         else:
#             bar_chart = col2.vega_lite_chart(chart_df, spec, use_container_width=True)

#         # message_var = None
#         # if sim.assigned_guacs < results_df.shape[0]:
#         #     message_var = results_df.shape[0] - sim.assigned_guacs
#         # success_message(key, sim.success, message_var)


# #this is an experiment, to include an image with the winner        
# def get_winner_image(sim, key):
#     col1, col2 = st.columns([2,5])
#     start_btn = col1.button("Simulate", key=key)

#     if start_btn:
#         col1, col2, col3 = st.columns(3)
#         col2.image("img/badge2.png", width=100, caption="badge test.")


# def format_spec(sim, subtitle, y_max, col_limit=None):
def format_spec(chart_df, sim):
    """Format the chart to be shown in each frame of the animation"""

    # subtitle = "Subtitle"
    spec = {
            "height":   275,
            "mark": {"type": "bar"},
            "encoding": {
                "x":    {
                    "field": "Entrant", 
                    "type": "nominal", 
                    # "sort": "ID",
                    "axis": {"labelAngle": -45}},
                "y":    {
                    "field": "sum", "type": "quantitative", 
                    # "scale": {"domain": [0, y_max]},
                    "title": "Vote Tallies"},
                # "color":    color_spec,
            },
            "title":    {
                "text": f"Simulation Results",
                # "subtitle": subtitle, 
            }  
        }
    return chart_df, spec


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
