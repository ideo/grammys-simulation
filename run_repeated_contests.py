import os
from copy import deepcopy
from collections import Counter, defaultdict
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm

from src import logic as lg
from src import RepeatedSimulations, load_or_generate_objective_scores, DATA_DIR


def establish_a_baseline():
    """
    This runs 100 contests where voters listen to every song. This establishes
    the baseline that is used throughout the story
    """
    num_voters = 1000
    num_songs = 1000
    filepath = DATA_DIR / f"Repeated-Simulations_Sums_{num_songs}-Songs_{num_voters}-Voters.pkl"

    song_df = load_or_generate_objective_scores(num_songs)
    repeated_contests = RepeatedSimulations(song_df, num_voters, filepath=filepath)
    
    for ii in range(10):
        # Each call runs 10 simulations
        print(f"{ii}:\tRunning 10 rounds of the contest.")
        repeated_contests.simulate()

    print(repeated_contests.num_contests)
    print(repeated_contests.sum_of_sums)


def explore_listening_limit():
    """
    Recording the 25 winners for each simulation so we have records of top 10, 
    top 15, top 20, etc.

    Right now, this function overwrites the previous save each time it runs.
    """
    num_songs = 1000
    song_df = load_or_generate_objective_scores(num_songs)
    
    ballot_lengths = [50, 100, 150, 200, 250]  
    voter_counts = [500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
    sample_sizes = [50, 100, 150, 200, 250, 300, 350, 450, 500] 

    for ballot_limit in ballot_lengths:
        filepath = DATA_DIR / f"exploring_listening_limit_{num_songs}_songs_{ballot_limit}_ballot_limit.pkl"
        with open(filepath, "rb") as pkl_file:
            results = pickle.load(pkl_file)

        for num_voters in voter_counts:
            for listen_limit in sample_sizes:
                # Starts off quick, gets slower
                # When re-running, we'll have to load the previous sim
                
                try:
                    sim = results[num_voters][listen_limit]
                except KeyError:
                    sim = RepeatedSimulations(song_df, num_voters, 
                            listen_limit=listen_limit, 
                            ballot_limit=ballot_limit,
                            num_winners=25)

                # Since this was added later. We're not using it, but maybe
                if not hasattr(sim, "sum_of_rankings"):
                    # These will be off by the first 10 contests though
                    sim.sum_of_rankings = np.zeros((num_songs, num_songs))

                if sim.num_contests < 20:
                    print(f"Simuation has already run {sim.num_contests} contests with a ballot limit of {sim.ballot_limit}.")
                    print(f"Simualting {num_voters} voters listening to {listen_limit} songs each. Ballot limit: {ballot_limit}")
                    sim.simulate()

                    # This step shouldn't be necessary, but doing it to make myself feel good.
                    results[num_voters][listen_limit] = sim

                    print(filepath)
                    with open(filepath, "wb") as pkl_file:
                        pickle.dump(results, pkl_file)
                else:
                    print(f"Skipping {num_voters} voters, {listen_limit} sample size, {ballot_limit} ballot limit.")


def test_one_configuration(num_winners):
    num_songs = 500
    num_voters = 1000
    listen_limit = 50
    ballot_limit = 25
    filepath = DATA_DIR / f"single_configuration_{num_winners}_winners.pkl"
    song_df = load_or_generate_objective_scores(num_songs)
    repeated_sim = RepeatedSimulations(song_df, num_voters, 
                              listen_limit=listen_limit, 
                              ballot_limit=ballot_limit,
                              num_winners=num_winners,
                              filepath=filepath)
    repeated_sim.simulate(num_repetitions=100)


if __name__ == "__main__":
    # pass
    # establish_a_baseline()
    # explore_listening_limit()
    test_one_configuration(5)
    # test_one_configuration(10)