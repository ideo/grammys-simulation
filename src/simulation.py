import os
import sys
import random
from collections import Counter
from pathlib import Path
from random import shuffle

import numpy as np
import pandas as pd
from stqdm import stqdm


# from .voters import Townsperson
# from .condorcet_counting import CondorcetCounting
# from .ranked_choice_voting import RankChoiceVoting
from src.townspeople import Townsperson
from src.condorcet_counting import Condorcet
from src.ranked_choice_voting import RankChoiceVoting


# Move this!
np.random.seed(42)


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
    
    # Bring in fun names for top songs.
    song_df = song_df.sort_values(by="Objective Ratings", ascending=False).reset_index()
    song_df["ID"] = song_df.index
    song_df.drop(columns="index", inplace=True)

    filename = "Grammys-Simuation_Song-Names - Top Scoring Songs.csv"
    fictional_names = pd.read_csv(DATA_DIR / filename)
    fictional_names = fictional_names["Song Name by Artist"].values
    shuffle(fictional_names)
    for ii, song_name in enumerate(fictional_names):
        song_df["ID"].iloc[ii] = song_name

    return song_df


class Simulation:
    def __init__(
            self, song_df, num_voters, st_dev=1.0, 
            listen_limit=None, ballot_limit=None, num_winners=10, 
            num_mafiosos=None, mafia_size=None,
            name=None,  
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

        # Initalizing
        self.ballots = pd.DataFrame(list(self.song_df.index), columns = ["ID"])
        self.objective_winner = self.song_df["Objective Ratings"].idxmax()
        self.success = False
        self.rankings = None


    @property
    def params(self):
        param_dict = {
            "name":         self.name,
            "num_voters":   self.num_voters,
            "listen_limit":   self.listen_limit,
            "st_dev":       self.st_dev,
        }
        return param_dict


    def simulate(self):
        """TODO: For unittests, we can update this to have inputs and outputs"""
        self.cast_ballots()
        if self.num_mafiosos:
            self.non_corrupt_ballots = self.ballots.copy()
            self.corrupt_ballots()
        self.winner = self.tally_votes()
        self.record_outcome()      


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
            song_sample = self.song_df.sample(n=self.listen_limit, replace=False)
            bllt = song_sample["Objective Ratings"].apply(listen_and_vote)
            # if recording the number of listens each song gets, we need to
            # to that here.
            if self.ballot_limit is not None:
                bllt = bllt.sort_values(ascending=False).head(self.ballot_limit)
            # self.ballots[f"Scores {ii}"] = bllt
            self.ballots[ii] = bllt
            # self.ballots is initialized in __init__

        # return self.ballots


    def corrupt_ballots(self):
        """TKTK"""      
        high_score = self.ballots.max().max()

        percentile = 66
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
            percentile -= 2


    def tally_votes(self):
        winner = self.tally_by_condorcet_method()
        return winner


    def tally_by_condorcet_method(self):
        """
        Simplified Condorcet method that simply returns the top 10 nominees.
        """
        self.condorcet = Condorcet(self.ballots, self.num_winners)
        winner = self.condorcet.top_nominee_ids[0]
        return winner


    def record_outcome(self):
        """This is here in case we need to expand it"""
        # TODO: we need consistency in how we save the winner, name or ID
        if isinstance(self.winner, str):
            # winner is a name, convert to ID
            ind = self.song_df[self.song_df["Entrant"] == self.winner].index[0]
            self.winner = ind

        self.success = self.winner == self.objective_winner


# The previous simulation was set up to incorporate multiple tallying 
# techniques. Leaving this code commented out here to preserve that intent, 
# since it may very well come back.

    # def tally_votes(self, ballots):
    #     if self.method == "sum":
    #         winner = self.tally_by_summing()

    #     elif self.method == "condorcet":
    #         winner = self.tally_by_condorcet_method()

    #     elif self.method == "rcv":
    #         winner = self.tally_by_ranked_choice(N=self.rank_limit)

    #     elif self.method == "fptp":
    #         winner = self.tally_by_first_past_the_post(ballots)

    #     return winner

        
    # def tally_by_summing(self):
    #     """This function determines the winner considering the sum.

    #     Returns:
    #         integer: guac ID of winner
    #     """
    #     #putting the results together
    #     self.ballots.set_index(["ID"], inplace = True)
    #     self.ballots["sum"] = self.ballots.sum(axis=1)
        
    #     #sort the scores to have the sum at the top
    #     sorted_scores = self.ballots.sort_values(by="sum", ascending=False)
    #     sorted_scores['ID'] = sorted_scores.index

    #     #extract highest sum        
    #     winning_sum = sorted_scores.iloc[0]["sum"]

    #     #create a dictionary of sums - winners to catch multiple winners
    #     sum_winners_dict = {}
    #     for s, w in zip(sorted_scores["sum"].tolist(), sorted_scores['ID'].tolist()):
    #         if s in sum_winners_dict.keys():
    #             sum_winners_dict[s].append(w)
    #         else:
    #             sum_winners_dict[s] = [w]

    #     self.sum_winners = sum_winners_dict[winning_sum]
    #     self.sum_winner = self.sum_winners[0]
    #     # self.sum_success = self.sum_winner == self.objective_winner

    #     if len(self.sum_winners) > 1:
    #         print("\n\n\nMultiple sum winners, picking one at random...\n\n\n")

    #     return self.sum_winner


    # def tally_by_condorcet_method(self):
    #     #finding the mean score for each nominee
    #     columns_to_consider = self.ballots.set_index("ID").columns
    #     # columns_to_consider.remove("sum")
    #     self.ballots["Mean"] = self.ballots[columns_to_consider].mean(axis=1)

    #     #creating the list that will contain each matrix ballot (needed for condorcet)
    #     # ballots_matrix_list = []
        
    #     #filling in the ballots dataframe, for the various characters
    #     # condorcet_elements = None
    #     condorcet_elements, ballots_matrix_list = self.condorcet_results()
    #     self.ballots_matrix_list = ballots_matrix_list
    #     self.condorcet_winner = condorcet_elements.declare_winner(self.ballots, ballots_matrix_list)
    #     self.condorcet_winners = condorcet_elements.winners
    #     # self.condo_success = self.condorcet_winner == self.objective_winner
    #     return self.condorcet_winner


    # def condorcet_results(self, ballots_matrix_list=[]):
    #     """This function collects the results of a simulation on a set of people

    #     Args:
    #         num_people (int): number of town people
    #         mean_offset (float): offset to apply to the objective score (we use this to account for personas)
    #         ballots_matrix_sum (numpy matrix): matrix needed for the calculation of the condorcet winner

    #     Returns:
    #         condorcet counting object containing the details of the condorcet method to compute the winner
    #     """
    #     condorcet_elements = None

    #     print("Tallying")
    #     for person in stqdm(self.voters):

    #         #creating the el
    # ements to compute the condorcet winner
    #         condorcet_elements = CondorcetCounting(self.song_df, person.ballot)
    #         # condorcet_elements = person.taste_and_vote(self.song_df)

    #         #collect ballox matrices
    #         ballots_matrix_list.append(condorcet_elements.ballot_matrix)

    #         #add the results to the results dataframe with a new column name
    #         # self.ballots[f"Scores {person.number}"] = self.song_df["ID"].apply(lambda x: condorcet_elements.ballot_dict.get(x, None))

    #         if len(self.ballots[self.ballots[f"Scores {person.number}"].isnull()]) == len(self.ballots):
    #             sys.exit(f"No scores recorder from person.number {person.number}. Something is wrong...") 
            
    #     #returning the last condorcet element calculated. 
    #     return condorcet_elements, ballots_matrix_list


    # def tally_by_ranked_choice(self, N=None):
    #     """TODO: Incorporate N"""

    #     # I want to display their names not their IDs
    #     self.ballots["Entrant"] = self.song_df["Entrant"]
    #     self.ballots.set_index("Entrant", inplace=True)
    #     self.ballots.drop(columns=["ID"], inplace=True)

    #     rcv = RankChoiceVoting(N)
    #     ranks = rcv.convert_score_ballots_to_implicit_ranks(self.ballots)
    #     self.rankings = rcv.tally_results(ranks)
    #     self.rcv = rcv
    #     return self.rankings[0][0]


    # def tally_by_first_past_the_post(self, ballots):
    #     """
    #     Interpret each voter's top score as their one favorite choice. Tally
    #     all these single choices with first-past-the-post.

    #     If there is a tie, it is broken randomly simply by calling .idxmax()
    #     """
    #     ballots.drop(columns=["ID"], inplace=True)
    #     names = self.song_df["Entrant"]
    #     votes = []

    #     choose_fav = lambda ballot: votes.append(names.iloc[ballot.idxmax()])
    #     ballots.apply(choose_fav, axis=0)

    #     tallies = [(name, count) for name, count in Counter(votes).items()]
    #     self.rankings = sorted(tallies, key=lambda x: x[1], reverse=True)
    #     return self.rankings[0][0]