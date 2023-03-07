import pandas as pd


class OneVotePerFinalist:
    def __init__(self, ballots, num_winners):
        self.ballots = ballots
        self.num_winners = num_winners
        self.tallies = self.tally(ballots, num_winners)
        self.winners = self.declare_winners(self.tallies)


    def tally(self, ballots, num_winners):
        tallies = pd.DataFrame(index=ballots.index)

        for col in ballots:
            tallies[col] = ballots[col].nlargest(num_winners) \
                .notnull().astype(int).reindex(ballots.index)
            
        return tallies
    

    def declare_winners(self, tallies):
        winners = tallies.sum(axis=1).sort_values(ascending=False) \
            .head(self.num_winners).index.to_list()
        return winners