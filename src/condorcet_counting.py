'''
A good chunk of this script is courtesy of 
Alex Fink and Russell McClellan,aka the original iZotope 
guac voting system creators
'''
from unittest import runner
import numpy as np
import pandas as pd
import sys
from stqdm import stqdm


class Condorcet:
    def __init__(self, ballot_df, n_winners=10):
        """
        To move quickly, for the MVP, this method computes rankings but cannot
        distinguish between ties. More work is needed for that, and we are 
        just banking that the numbers we're using are high enough that ties 
        should be rare.
        """
        self.ballot_df = self.clean_ballot_df(ballot_df)
        self.n_winners = n_winners
        self.pairwise_sums = self.compute_sum_of_ballot_pairwise_comparisons()
        self.preferences = CondorcetCounting.get_schwartz_relations_matrix(self.pairwise_sums)
        self.top_nominee_ids, self.top_vote_counts = self.top_nominees(self.preferences)


    def clean_ballot_df(self, ballot_df):
        """
        The current simluation code adds some extraneous columns
        """
        columns = ["ID", "Mean"]
        columns_to_drop = [col for col in columns if col in ballot_df.columns]
        if columns_to_drop:
            ballot_df.drop(columns=columns_to_drop, inplace=True)
        return ballot_df


    def compute_sum_of_ballot_pairwise_comparisons(self):
        """
        TKTK
        """
        n_nominees = self.ballot_df.shape[0]
        pairwise_sums = np.zeros((n_nominees, n_nominees))
        for col in stqdm(self.ballot_df.columns, desc="Tallying votes"):
            ballot = self.ballot_df[col]
            pairwise_sums += self.pairwise_comparison(ballot)
        return pairwise_sums


    def pairwise_comparison(self, ballot):
        """
        ballot (pd.Series): 
            One column of the ballot_df. A single voters's ballot.

        Computes pairwise comparisons. Row-Col, was nominee at row ranked 
        higher than nominee at col?
        """
        # Need to sort by the index because the ballot is returned in the
        # order of the random sample
        ballot = ballot.sort_index()

        # This is numpy magic for doing a pairwise comparison
        pairwise_comparison = (ballot.values[:, None] > ballot.values)

        # Transforms from bool to int
        pairwise_comparison = pairwise_comparison * 1 
        return pairwise_comparison


    def top_nominees(self, pairwise_sums):
        """
        Input can be either pairwise_sums or boolean preferences
        """
        if self.n_winners > pairwise_sums.shape[0]:
            self.n_winners = pairwise_sums.shape[0]

        row_sums = pairwise_sums.sum(axis=1)
        ii = np.argpartition(row_sums, -self.n_winners)[-self.n_winners:]
        ii = ii[np.argsort(row_sums[ii])]
        ii = np.flip(ii)
        return ii, row_sums[ii]

    
    # def get_top_songs(self, song_names):
    #     preferences = CondorcetCounting.get_schwartz_relations_matrix(self.pairwise_sums)
    #     smith_schwartz_set = CondorcetCounting.get_smith_or_schwartz_set_statuses(preferences, song_names)
    #     return preferences, smith_schwartz_set




class CondorcetCounting():
    def __init__(
            self, 
            guac_df, 
            sample_guac_df,
            cazzo=False):
        
        self.winners=[]
        self.winner=None

        self.smith_schwartz_set_df=pd.DataFrame()
        #for debugging
        self.cazzo = cazzo
        self.guac_df = guac_df
        self.guac_names = list(guac_df.index)
        self.num_guacs = len(guac_df)
        self.sample_guac_df = sample_guac_df
        
        # self.ballot_dict = self.get_ballot_dictionary()        
        self.ballot_matrix = self.create_ballot_matrix()


    def create_ballot_matrix(self):
        # Need to sort by the index because the ballot is returned in the
        # order of the random sample
        ballot = self.sample_guac_df.sort_index()["Subjective Ratings"].values

        # This is numpy magic for doing a pairwise comparison
        pairwise_comparison = (ballot[:, None] > ballot)

        # Transforms from bool to int
        pairwise_comparison = pairwise_comparison * 1 
        return pairwise_comparison



    # def create_ballot_matrix(self):
    #     """This function converts a ballot containing a score for each guac into
    #     a matrix of runner (rows) vs opponent (columns), where wins (and only wins) are marked as 1.

    #     Returns:
    #         numpy ballot matrix
    #     """
        
    #     # Create the ballot matrix, row by row.
    #     ballot_matrix = []

    #     #loop on runners
    #     for runner in self.guac_names:   

    #         #if this runner wasn't in the ballot, then fill in with 0s and move to the next
    #         if runner not in self.ballot_dict.keys():
    #             ballot_matrix.append([0 for i in range(len(self.guac_names))])
    #             continue

    #         ballot_array = []
    #         #loop on opponents
    #         for opponent in self.guac_names:

    #             #if this opponent wasn't in the ballot, add a 0 and move to the next
    #             if opponent not in self.ballot_dict.keys():
    #                 ballot_array.append(0)
    #                 continue
                    
    #             #if runner beats the opponent, record the win
    #             if self.ballot_dict[runner] > self.ballot_dict[opponent]:
    #                 ballot_array.append(1)
    #             else: 
    #                 ballot_array.append(0)

    #         #append to then create a ballot matrix
    #         ballot_matrix.append(ballot_array)
    
    #     ballot_matrix = np.matrix(ballot_matrix)

    #     return ballot_matrix


    # def get_ballot_dictionary(self):
    #     """This function extract a dictionary with guac and vote

    #     Returns:
    #         guac:vote dictionary
    #     """
    #     ballot_dict = dict(zip(self.sample_guac_df['ID'], self.sample_guac_df['Subjective Ratings']))        
    #     return ballot_dict


    @staticmethod
    def get_schwartz_relations_matrix(sum_ballots_matrix):
        """This function creates a matrix of the preferences.
         True is in positions where a runner is preferred more than the opponent.

        Args:
            sum_ballots_matrix (numpy matrix): matrix containing the sums of all the wins

        Returns:
            matrix of preferences
        """
        #initialize a matrix with all zeros 
        num_songs = sum_ballots_matrix.shape[0]
        matrix_of_more_preferred = np.zeros([num_songs, num_songs], dtype=bool) # Init to False (loss)
        #loop through all guacs and check the runner vs opponent preferences. 
        #when the runner is more preferred than the opponent (by more votes), flip the matrix location to True
        for runner in range(num_songs):
            for opponent in range(num_songs):
                if runner == opponent: continue
                if (sum_ballots_matrix[runner][opponent] > sum_ballots_matrix[opponent][runner]):
                    matrix_of_more_preferred[runner][opponent] = True # Victory (no tie)

        return matrix_of_more_preferred


    @staticmethod
    def get_smith_or_schwartz_set_statuses(matrix_of_more_preferred, song_names):
        """Uses Floyd-Warshall algorithm to find out which candidates are in the Smith or Schwartz Set.
        The set returned is dependent on the calculation of the relations.
        Modeled after https://wiki.electorama.com/wiki/Maximal_elements_algorithms

        Args:
            matrix_of_more_preferred (numpy matrix): matrix containing True when a runner is preferred more than the opponent.

        """
        #assume every guac belongs, then knock them off
        num_songs = matrix_of_more_preferred.shape[0]
        is_in_smith_or_schwartz_set = np.ones(num_songs, dtype=bool) #Init to True

        # Use transitive properties to determine winners. 
        # E.g., if B > A and A > C then B > C
        matrix_of_more_preferred_tp = matrix_of_more_preferred.copy()
        for runner in range(num_songs):
            for opponent in range(num_songs):
                if runner != opponent:
                    for middle_guac in range(num_songs):
                        if ((runner != middle_guac) and (opponent != middle_guac)):
                            if (matrix_of_more_preferred_tp[opponent][runner] and matrix_of_more_preferred_tp[runner][middle_guac]):
                                matrix_of_more_preferred_tp[opponent][middle_guac] = True
        
        for runner in range(num_songs):
            for opponent in range(num_songs):
                if (runner != opponent):
                    if (matrix_of_more_preferred_tp[opponent][runner] and not matrix_of_more_preferred_tp[runner][opponent]):
                        is_in_smith_or_schwartz_set[runner] = False
                        break
        smith_schwartz_set_df = pd.DataFrame(index = song_names)
        smith_schwartz_set_df['in_set'] = is_in_smith_or_schwartz_set
        return smith_schwartz_set_df
        

    def declare_winner(self, ballots, ballots_matrix_list, ballot_matrices_sum):
        """This function computes the condorcet winner by ranking the guacs
        belonging to the smith set and ranking them by their average score

        Args:
            ballots (dataframe): dataframe with the scores
            ballots_matrix_list (list): list of numpy matrices
        Returns:
            winning guac
        """
        #sum all ballot matrices
        # ballot_matrices_sum = sum(bm for bm in ballots_matrix_list)
        # assert(ballot_matrices_sum.shape == ballots_matrix_list[0].shape)

        #find the runners more preferred
        matrix_of_more_preferred = self.get_schwartz_relations_matrix(ballot_matrices_sum)

        #find the sets of winners and loosers
        self.smith_schwartz_set_df = self.get_smith_or_schwartz_set_statuses(matrix_of_more_preferred)
        
        #add to the sets of winners and loosers the mean to find the absolute winner
        self.smith_schwartz_set_df = self.smith_schwartz_set_df.join(ballots[['Mean']]) 
        self.smith_schwartz_set_df['ID'] = self.smith_schwartz_set_df.index

        #filter out the winners
        self.winner = self.get_winners(ballots_matrix_list, ballots)
        return self.winner


    # @staticmethod
    def get_winners(self, ballots_matrix_list, ballots):
        """This function computes the winner(s) from the smith_or_schwartz sets

        Args:
            ballots_matrix_list (list): list of numpy matrices with the ballots

        Returns:
            integer winner
        """

        #filter out the winners
        winners_df = self.smith_schwartz_set_df[self.smith_schwartz_set_df['in_set'] == True].copy()
        winners_df.sort_values(by = ['Mean'], ascending = False, inplace = True)

        #if there's no winner
        if len(winners_df)  == 0:
            sys.exit("No condorcet winner")         
        
        #get the winning mean
        winning_mean = winners_df.iloc[0]['Mean']
        
        #create a dictionary of means - winners to catch multiple winners
        mean_winners_dict = {}
        for m, w in zip(winners_df['Mean'].tolist(), winners_df['ID'].tolist()):
            if m in mean_winners_dict.keys():
                mean_winners_dict[m].append(w)
            else:
                mean_winners_dict[m] = [w]
        
        #extract the winners from the dictionary
        winners = mean_winners_dict[winning_mean]

        #if there's 1 winner
        if len(winners)  == 1:
            return winners[0]
        #if there are multiple winners
        else:
            # break_tie(ballots_matrix_list, ballots)
            # print ("Picking winner at random among winners, for simplicity")

            # print(f"\n\n\nWinner = {winners.iloc[0]['ID']}")
            return winners[0]


    #this below is WIP
    def break_tie(self, ballots_matrix_list, results_df):

        #select columns with a score
        scores_cols = [i for i in results_df.columns if "Scores" in i]

        #slice the results to only concentrate on the winners
        results_df_slice = results_df[results_df.index.isin(self.winners)].copy()

        #create the ballot matrices and the ballot matrix sum
        ballot_matrix_list = []
        # import pdb;pdb.set_trace()

        for sc in scores_cols:
            #get ballot for that person:
            results_df_slice[sc].fillna(0, inplace=True)
            ballot_dict = dict(zip(results_df_slice.index, results_df_slice[sc].tolist()))
            ballot_matrix_list.append(self.create_ballot_matrix())
        
        # import pdb;pdb.set_trace()
        self.declare_winner(results_df, ballots_matrix_list)



        # # winners_id = [9,12]
        # to_delete = [i for i in self.guac_df['ID'].tolist() if i not in self.winners]

        # ballots_matrix_winners_list = []
        # for mb in ballots_matrix_list:
        #     #delete the rows and columns of non winning guacs
        #     mb_lite = np.delete(mb, to_delete, 0)
        #     mb_lite = np.delete(mb_lite, to_delete, 1)
        #     print(mb_lite.shape)

        #     ballots_matrix_winners_list.append(mb_lite)
            
        
        pass

    # def sum_ballot_matrices(self, ballots_matrix_list):
    #     """This function sums all the ballot matrices

    #     Args:
    #         ballots_matrix_list (list): list of numpy matrices

    #     Returns:
    #         numpy matrix containing the sum of matrix ballots
    #     """
    #     null_matrix = np.zeros([len(self.guac_df),len(self.guac_df)])
    #     print("null_matrix.shape: ", null_matrix.shape)
        
    #     ballots_matrix_sum = null_matrix.copy()
    #     print("ballots_matrix_list[0].shape: ", ballots_matrix_list[0].shape)
        
    #     for bm in ballots_matrix_list:
    #         ballots_matrix_sum += bm

    #     if np.array_equal(ballots_matrix_sum, null_matrix) == True:
    #         # import pdb;pdb.set_trace()
    #         sys.exit("Ballot matrix sum is null, something is wrong...") 

    #     return ballots_matrix_sum
