import os
from pathlib import Path
# from random import shuffle
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm
from stqdm import stqdm

from .condorcet_counting import Condorcet
from .current_method import OneVotePerFinalist


# Move this!
# np.random.seed(42)


REPO_ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_or_generate_objective_scores(num_songs):
    """
    In order for each simulation to see the same set of songs, we need to 
    generate them once and save them.
    """
    filename = f"objective_scores_for_{num_songs}_songs.pkl"
    filepath = DATA_DIR / filename

    if os.path.exists(filepath):
        song_df = pd.read_pickle(filepath)

    else:
        song_df = generate_objective_scores(num_songs)
        song_df.to_pickle(filepath)

    return song_df


def generate_objective_scores(num_songs):
    # These parameters could become variables later, but likely not
    _mean = 50
    _std = 15

    objective_scores = np.random.normal(loc=_mean, scale=_std, size=num_songs)
    song_df = pd.DataFrame(objective_scores, columns=["Objective Ratings"])

    
    song_df = apply_song_names(song_df)
    
    return song_df


def apply_song_names(df):
    df["ID"] = df.index
    df["index"] = df.index

    filepath = DATA_DIR / "song_names/Top Scoring Songs.csv"
    top_scoring_names = pd.read_csv(filepath)
    df = df.sort_values(by="Objective Ratings", ascending=False)
    df = change_values(df, top_scoring_names)

    df = df.sort_values(by="index", ascending=True)
    df.drop(columns=["index"], inplace=True)

    filepath = DATA_DIR / "song_names/All Song Names.csv"
    first_names = pd.read_csv(filepath)
    df = change_values(df, first_names)
    return df


def change_values(df, fictional_names):
    fictional_names = fictional_names["Song Name by Artist"].values
    ii = 0
    for song_name in fictional_names:
        if song_name not in df["ID"].values:
            try:
                df["ID"].iloc[ii] = song_name
                ii += 1
            except IndexError:
                # Fictional Names is longer than song_df. This occurs when testing
                # with small numbers
                pass
    return df


class Simulation:
    def __init__(
            self, song_df, num_voters, st_dev=10.0,
            listen_limit=None, ballot_limit=None, num_winners=10, 
            num_mafiosos=0, mafia_size=0,
            name=None, alphabetical=False, methods=["condorcet"],
        ):
        self.song_df = song_df
        self.num_voters = num_voters
        self.st_dev = st_dev
        
        if listen_limit:
            self.listen_limit = listen_limit
        else:
            self.listen_limit = song_df.shape[0]
        
        self.ballot_limit = ballot_limit
        self.num_winners = num_winners
        self.num_mafiosos = num_mafiosos
        self.mafia_size = mafia_size
        self.name = name
        self.alphabetical = alphabetical
        self.methods = methods

        # Initalizing
        self.success = False
        self.rankings = None
        self.complete = False
        self.condorcet_winners = []
        self.current_method_winners = []


    @property
    def params(self):
        param_dict = {
            "name":             self.name,
            "num_voters":       self.num_voters,
            "listen_limit":     self.listen_limit,
            "st_dev":           self.st_dev,
        }
        return param_dict


    def simulate(self):
        """TODO: For unittests, we can update this to have inputs and outputs"""
        self.reset_ballots()
        self.cast_ballots()
        if self.num_mafiosos:
            self.non_corrupt_ballots = self.ballots.copy()
            self.corrupt_ballots()
        self.tally_votes()
        self.record_consistency()
        self.complete = True


    def reset_ballots(self):
        song_indices = list(self.song_df.index)
        self.ballots = pd.DataFrame(song_indices, columns=["ID"])
        self.listen_counts = pd.DataFrame(index=self.ballots.index, columns=["Listen Count"])
        self.listen_counts.fillna(value=0, inplace=True)


    def cast_ballots(self):
        """
        Here each voter "listens" to each song and returns a ballot ranking
        every song in their listen_limit. 

        The listen_limit is how many songs a voter gets to listen to, the size 
        of the random sample. The ballot_limit is how many songs they rank, the 
        top N songs our of the ones they listened to.

        This process was originally done by creating independent agents that
        each cast a vote. Once the simulation was simplified that process
        proved unnecessary.

        The objective scores are already sorted, so when enforcing a ballot
        limit, only the beginning rows of the dataframe will have results.
        """
        listen_and_vote = lambda score: np.random.normal(score, self.st_dev)

        for ii in stqdm(range(self.num_voters), desc="Voting"):

            if self.alphabetical:
                listen_limit = np.random.normal(loc=100, scale=15)
                listen_limit = int(listen_limit)
                song_sample = self.song_df.head(listen_limit).copy()
            else:
                song_sample = self.song_df.sample(n=self.listen_limit, replace=False)
                
            # Individual Ballot
            bllt = song_sample["Objective Ratings"].apply(listen_and_vote)

            # Record how many times each song was listened to.
            self.listen_counts.loc[bllt.index, "Listen Count"] = \
                self.listen_counts.loc[bllt.index, "Listen Count"] + 1
           
            if self.ballot_limit is not None:
                bllt = bllt.sort_values(ascending=False).head(self.ballot_limit)
            self.ballots[ii] = bllt


    def corrupt_ballots(self):
        """TKTK"""      
        high_score = self.ballots.max().max()

        # percentile = 66
        percentile = 88
        step_down = 1
        percentile_ranks = self.song_df["Objective Ratings"].rank(pct=True)
        for ii_boss in range(self.num_mafiosos):
            # Which song
            ii_song = self.song_df[percentile_ranks == percentile/100].index[0]

            # Which voters
            voter_start = int(ii_boss*self.mafia_size)
            voter_stop = int((ii_boss+1)*self.mafia_size)
            corrupt_voter_ids = range(voter_start, voter_stop)
            voter_columns = [col for col in self.ballots.columns if col in corrupt_voter_ids]

            # Change votes
            # By converting it to a boolean first, I only increate score values
            # if they were already non-null, i.e. votes were already cast
            vote_cast = self.ballots.loc[ii_song, voter_columns].apply(
                lambda x: int(~np.isnan(x))
            )
            voter_columns = tuple(voter_columns)
            self.ballots.at[ii_song, voter_columns] = vote_cast * high_score

            # Set Next Song
            percentile -= step_down


    def tally_votes(self):
        if "condorcet" in self.methods:
            self.condorcet_winners = self.tally_by_condorcet_method()

        if "current" in self.methods:
            self.current_method_winners = self.tally_by_current_method()


    def tally_by_condorcet_method(self):
        """
        Simplified Condorcet method that simply returns the top 10 nominees.
        """
        self.condorcet = Condorcet(self.ballots, self.num_winners)
        winners = self.condorcet.top_nominee_ids
        return winners
    

    def tally_by_current_method(self):
        self.current_method = OneVotePerFinalist(self.ballots, self.num_winners)
        winners = self.current_method.winners
        return winners


    def record_consistency(self):
        fair_winners = self.song_df.sort_values("Objective Ratings", ascending=False).head(self.num_winners).index.tolist()
        self.num_condorcet_fair_winners = len(set(self.condorcet_winners[:self.num_winners]).intersection(set(fair_winners)))
        self.num_current_method_fair_winners = len(set(self.current_method_winners[:self.num_winners]).intersection(set(fair_winners)))


#############################################################################

class RepeatedSimulations:
    def __init__(self, song_df, num_voters, 
                 listen_limit=None, ballot_limit=None, num_winners=10,
                 filepath=None):
        
        self.song_df = song_df
        self.num_voters = num_voters
        self.listen_limit = listen_limit
        self.ballot_limit = ballot_limit
        self.num_winners = num_winners
        self.filepath = filepath

        self.sim = Simulation(song_df, num_voters,
            listen_limit = listen_limit,
            ballot_limit = ballot_limit,
            num_winners = num_winners,
            methods=["condorcet", "current"])
        
        num_songs = song_df.shape[0]
        self.sum_of_sums = np.zeros((num_songs, num_songs))
        self.sum_of_rankings = np.zeros((num_songs, num_songs))
        self.condorcet_winners = {}
        self.current_method_winners = {}
        self.num_condorcet_fair_winners = []
        self.num_current_method_fair_winners = []
        self.num_contests = 0
        
        
    def simulate(self, num_repetitions=10):
        for _ in tqdm(range(num_repetitions)):
            self.sim.simulate()
            self.sum_of_sums += self.sim.condorcet.pairwise_sums
            self.sum_of_rankings += self.sim.condorcet.preferences
            self.condorcet_winners[self.num_contests] = self.sim.condorcet.top_nominee_ids
            self.current_method_winners[self.num_contests] = self.sim.current_method.winners
            self.num_condorcet_fair_winners.append(self.sim.num_condorcet_fair_winners)
            self.num_current_method_fair_winners.append(self.sim.num_current_method_fair_winners)
            self.num_contests += 1


        if self.filepath is not None:
            with open(self.filepath, "wb") as pkl_file:
                pickle.dump(self, pkl_file)