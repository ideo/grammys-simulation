import os
from copy import deepcopy
from collections import Counter
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm

from src import logic as lg
from src import RepeatedSimulations, load_or_generate_objective_scores, DATA_DIR


if __name__ == "__main__":
    num_voters = 1000
    num_songs = 1000
    num_winners = 10
    filepath = DATA_DIR / f"Repeated-Simulations_Sums_{num_songs}-Songs_{num_voters}-Voters.pkl"

    song_df = load_or_generate_objective_scores(num_songs)
    repeated_contests = RepeatedSimulations(song_df, num_voters, filepath=filepath)
    
    for _ in range(10):
        # Each call runs 10 simulations
        repeated_contests.simulate()

    print(repeated_contests.num_contests)
    print(repeated_contests.sum_of_sums)