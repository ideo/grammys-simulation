import sys
import random
from xml.dom.pulldom import parseString

import pandas as pd

from .townspeople import Townsperson
from .condorcetcounting import Condorcetcounting


# TEST_JENNAS_NUMBERS = False
class Simulation:
    def __init__(
            self, guac_df, num_townspeople=200, st_dev=1.0, fullness_factor = 0.0,
            assigned_guacs=20, perc_fra=0.0, perc_pepe=0.0, perc_carlos=0.0,
            method="sum", seed=None
        ):
        self.guac_df = guac_df
        self.num_townspeople = num_townspeople
        self.townspeople = []
        self.st_dev = st_dev
        self.fullness_factor = fullness_factor
        self.assigned_guacs = assigned_guacs
        self.perc_fra = perc_fra
        self.perc_pepe = perc_pepe
        self.perc_carlos = perc_carlos
        self.results_df = None
        self.objective_winner = guac_df[["Objective Ratings"]].idxmax()[0]
        self.sum_winner = None
        self.sum_winners = []
        self.success = False
        self.condorcet_winners = []
        self.condorcet_winner = None
        self.method = method.lower()
        if seed:
            random.seed(seed)


        # if TEST_JENNAS_NUMBERS:
        #     self.num_townspeople = 7
        #     self.assigned_guacs = 6
        #     self.guac_df = pd.DataFrame([0,1,2,3,4,5], columns = ['Entrant'])
        #     self.guac_df['Objective Ratings'] = 0


    def simulate(self, cazzo=False):

        self.create_agents()
        self.taste_and_vote()
        self.tally_votes()
        self.success = self.winner == self.objective_winner


    def create_agents(self):
        """Create the agents to be used in the simulation

        Returns: None
        """

        #Pepes tend to score people higher
        if self.perc_pepe > 0:
            num_pepes = self.num_townspeople * self.perc_pepe
            num_pepes = int(round(num_pepes))
            pepe = Townsperson(
                st_dev=self.st_dev, 
                assigned_guacs=self.assigned_guacs, 
                mean_offset=3, 
                carlos_crony=False,
                )
            self.townspeople += [pepe]*num_pepes

        #Fras tend to score people lower
        if self.perc_fra > 0:
            num_fras = self.num_townspeople * self.perc_fra
            num_fras = int(round(num_fras))
            fra = Townsperson(
                st_dev=self.st_dev, 
                assigned_guacs=self.assigned_guacs, 
                mean_offset=-3, 
                carlos_crony=False,
                )
            self.townspeople += [fra]*num_fras

        #Carlos's Cronies are colluding to vote Carlos the best
        if self.perc_carlos > 0:
            num_carlos = self.num_townspeople * self.perc_carlos
            num_carlos = int(round(num_carlos))
            carlos_crony = Townsperson(
                st_dev=self.st_dev, 
                assigned_guacs=self.assigned_guacs, 
                mean_offset=0, 
                carlos_crony=True,
                )
            self.townspeople += [carlos_crony]*num_carlos
        
        #Reasonable townspeopole tend to score people fairly
        num_reasonable = self.num_townspeople - len(self.townspeople)
        regular_hard_working_folk = Townsperson(
                st_dev=self.st_dev, 
                assigned_guacs=self.assigned_guacs, 
                mean_offset=0, 
                carlos_crony=False,
                )
        self.townspeople += [regular_hard_working_folk]*num_reasonable

        for ii, person in enumerate(self.townspeople):
            person.number = ii


    def taste_and_vote(self):
        #Creating the DF that will store the ballots
        df = pd.DataFrame(list(self.guac_df.index), columns = ["ID"])

        for person in self.townspeople:
            ballot = person.taste_and_vote(self.guac_df)
            df[f"Score Person {person.number}"] = ballot["Subjective Ratings"]

        self.results_df = df


    def tally_votes(self):
        if self.method == "sum":
            self.winner = self.tally_by_summing()

        elif self.method == "condorcet":
            self.winner = self.tally_by_condorcet_method()

        
    def tally_by_summing(self):
        """This function determines the winner considering the sum.

        Returns:
            integer: guac ID of winner
        """
        #putting the results together
        self.results_df.set_index(["ID"], inplace = True)
        columns_to_consider = self.results_df.columns
        self.results_df["sum"] = self.results_df[columns_to_consider].sum(axis=1)
        # self.results_df["Mean"] = self.results_df[columns_to_consider].mean(axis=1)
        
        #sort the scores to have the sum at the top
        this_score = 'sum'
        sorted_scores = self.results_df.sort_values(by=this_score, ascending=False)
        sorted_scores['ID'] = sorted_scores.index

        #extract highest sum        
        winning_sum = sorted_scores.iloc[0][this_score]

        #create a dictionary of sums - winners to catch multiple winners
        sum_winners_dict = {}
        for s, w in zip(sorted_scores[this_score].tolist(), sorted_scores['ID'].tolist()):
            if s in sum_winners_dict.keys():
                sum_winners_dict[s].append(w)
            else:
                sum_winners_dict[s] = [w]

        self.sum_winners = sum_winners_dict[winning_sum]
        self.sum_winner = self.sum_winners[0]
        self.sum_success = self.sum_winner == self.objective_winner

        if len(self.sum_winners) > 1:
            print("\n\n\nMultiple sum winners, picking one at random...\n\n\n")

        return self.sum_winner


    def tally_by_condorcet_method(self):
        #finding the mean
        columns_to_consider = self.results_df.columns
        # columns_to_consider.remove("sum")
        self.results_df["Mean"] = self.results_df[columns_to_consider].mean(axis=1)

        #creating the list that will contain each matrix ballot (needed for condorcet)
        # ballots_matrix_list = []
        
        #filling in the ballots dataframe, for the various characters
        # condorcet_elements = None
        condorcet_elements, ballots_matrix_list = self.condorcet_results()
        self.condorcet_winner = condorcet_elements.declare_winner(self.results_df, ballots_matrix_list)
        self.condorcet_winners = condorcet_elements.winners
        self.condo_success = self.condorcet_winner == self.objective_winner
        return self.condorcet_winner


    def condorcet_results(self, ballots_matrix_list=[]):
        """This function collects the results of a simulation on a set of people

        Args:
            num_people (int): number of town people
            mean_offset (float): offset to apply to the objective score (we use this to account for personas)
            ballots_matrix_sum (numpy matrix): matrix needed for the calculation of the condorcet winner

        Returns:
            condorcet counting object containing the details of the condorcet method to compute the winner
        """
        condorcet_elements = None

        for person in self.townspeople:

            #creating the elements to compute the condorcet winner
            condorcet_elements = Condorcetcounting(self.guac_df, person.ballot)
            # condorcet_elements = person.taste_and_vote(self.guac_df)

            #collect ballox matrices
            ballots_matrix_list.append(condorcet_elements.ballot_matrix)

            #add the results to the results dataframe with a new column name
            # self.results_df[f"Score Person {person.number}"] = self.guac_df["ID"].apply(lambda x: condorcet_elements.ballot_dict.get(x, None))

            if len(self.results_df[self.results_df[f"Score Person {person.number}"].isnull()]) == len(self.results_df):
                sys.exit(f"No scores recorder from person.number {person.number}. Something is wrong...") 
            
        #returning the last condorcet element calculated. 
        return condorcet_elements, ballots_matrix_list
        