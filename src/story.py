# from re import M


STORY = {
    "introduction":  [
        """
        Welcome to the Isle of Musica — an idyllic locale where every citizen lives, breathes, even eats to make music. The Isle of Musica is inhabited by talented professional musicians, engineers, songwriters, and producers — all with different expertises and genre focuses. They all live on the Isle of Musica because of the one value they have in common: their reverence, respect, and passion for music.
        """,
        """
        That is the one thing everyone can agree on here on the Isle: music is something to be studied and taken seriously. No one can agree, however, on which artists, albums, or songs are the “best,” – and if asked, they’d probably nominate themselves, or a close collaborator. So in the spirit of wanting to give her citizens their well-deserved props, Mayor Melody suggests the town hold a first annual contest to decide which of this year’s songs was SONG OF THE YEAR.   
        """,
        """
        Anyone who believes a song they wrote this year is particularly special can nominate it for the contest. num_voters people live on the Isle, and when Mayor Melody sees the lists of nominees, surprise surprise, num_voters songs have been nominated. Everyone must have picked their personal best. 
        """,
        """
        Running a contest with this many entrants is going to be tricky, but the mayor has a plan. First step, instead of trying to declare one winner in one go, Mayor Melody decides the first round of the contest should be to determine a short list of finalists.
        """,
    ],

    "simulation_1": [
        """
        Mayor Melody wants to make sure her citizens have time to judge each song fairly, so she’s given everyone the month off to ensure they can take the time to listen and assess each one. Her and her staff have also printed off massive ballots. She knows her citizens want to know who their competition is, so it’s important the voters submit an ordered ranking of all num_songs songs.
        """,
    ],

    "simulation_1_repeated": [
        """
        The power of simulations is that we can repeat events multiple times to assess the range of possible outcomes. Below we can see how many times songs were ranked within the top num_winners after simulating this contest num_contests times. We will use these results to establish our baseline, i.e. which num_winners songs deserve to win this contest? If subsequent contests deviate from these results, we know the voting method is flawed.
        """,
    ],

    "simulation_2": [
        """
        Of course, voting this way would take a long time. Plus, the citizens of the Isle don’t actually want a month of work – their work is their passion.They have albums to produce, sound edits to make – they don’t want to drop everything to listen and rate every single song. Plus, even for music lovers, working through num_songs sounds exhausting. Would everything just start to sound the same after awhile? Music lovers are superhuman, but not like that!      
        """,
        """
        So Mayor Melody has a better plan that will still ensure a fair election, and it relies on the fact that there are so many dedicated voters. Instead of receiving all num_songs songs, citizens will be sent a randomly chosen subset. This will be much more practical anyway, since the latest technology takes awhile to make it out to the Isle. Mayor Melody was worried voters wouldn’t have room for all num_songs on their Zunes.
        """,
        """
        One thing to remember is that every voter has subjective preference. While the citizens are musical experts and may generally agree on the overall quality of the song, when it comes to choosing between songs of similar quality, we should expect voters to have differing opinions. 
        """,
    ],

    "heatmap": [
        "The sample size controls how many songs voters get to listen to. The ballot size controls how many songs receive vote tallies. Below are the results of running multiple contests at a variety of configurations. Play with the controls below to explore various outcomes. Use your cursor to inspect individual tiles of the heatmap."
    ],

    "heatmap_conclusion": [
        """
        Exploring the outcomes of different configurations, you may notice it appears that the best we can do is just one shy of a perfect score. Nine out of ten of the finalists were correct (or 14 out of 15, or 19 out of 20).
        """,
        """
        Since not every voter gets to listen to every song, not every voter will have heard each of the finalists. That means when we compile the rankings of rankings, we often end up with some ties, e.g. two songs tied for second place, three songs tied at fourth place, etc. By setting the cutoff right at ten or fifteen, we often slice right through a tie.
        """,
        """
        How should we work with ties? There is some complex math to break ties within rankings of rankings voting systems. However since this first round the contest is not to find one ultimate winner but merely to produce a list of finalists, it may be simpler and more transparent to include all tying finalists.
        """,
        """
        For the purposes of this simulation, one shy of a perfect score can still be considered a fair outcome. For the purposes of a real contest, this creates an opportunity to have an dynamic number of finalists – to let the voters and quality of nominees determine if this year should have nine or twelve finalists, for example.
        """,
    ],

    "simulation_3": [
        """
        While making her rounds in the town square, Mayor Melody got a whiff that individual loyalties might threaten to throw off the otherwise fair Song of the Year contest. After some investigation, the cronyism going on between the heads of certain neighborhoods became clear. For example, in Double Reed Village, Al Pacone was running a campaign to get people to vote for his buddy Kid Lincoln's song, “Defenestration", by offering them a free session at his state-of-the-art studio. And Lucky Luke, over on de Sousa Cul de Sac, was telling his neighbors that if they voted for his song, “Entrepreneur,” that he’d do them a big musical favor at a later date.
        """,
        """
        Mayor Melody had a feeling that this could possibly happen, so she began to think about how to mitigate this issue and ensure it didn’t highjack voting enough to skew the final results. Use the sliders below to see how much (or how little) cronyism affects the final result of the contest.
        """,
    ],

    "simulation_3_conclusion": [
        """
        Even when every single voter is in cahoots with someone, the randomization of the contest prevents coordination – not enough of them get the chance to vote for their ring leader. At worst, by not voting for the deserved best song, rather than promote a corrupt song into the finalists, they open up a chance for a near-finalist to make into the list. This phenomen nullifies any attempts at collusion.
        """,
    ],

    "conclusion": [
        """
        Say smart things to wrap it up.
        """,
    ]
}


INSTRUCTIONS = {
    "select_num_winners": [
        "This contest will determine a small list of finalists from the larger pool of nominees. How many finalists should there be?"
    ],

    "simulation_1": [
        "This first contest sets the baseline that we can compare against in subsequent contests. All num_voters voters listen and vote on all num_songs songs. "
    ],

    "simulation_2": [
        "In our second contest, voters are randomly assigned a smaller subset of songs to listen to. They then submit a ballot ranking their top picks from that sample. Change the listening sample and ballot sizes to explore different outcomes."
    ],

     "simulation_3": [
        "In our third contest, members of a corrupt voting bloc will rank their leader's song at the top of the ballot no matter what, contorting the results. The corrupt songs are good but not great – about a B+. They're not bad, but shouldn't count among finalists."
    ],
}


# SUCCESS_MESSAGES = {
#     "simulation_1": {
#         True:  [
#             "Success! Even though people had so many guacs to try, and probably became quite full by the end, having everyone taste in random orders ensured the contest still had a fair result.",
#             ],
#         False:  [
#             "Oh no! The contest didn't reach a fair conclusion. That's not supposed to happen!"
#         ]
#     },

#     "simulation_2": {
#         True:   [
#             "Success! Even though the tasters missed out on trying MISSING_GUACS guacs each, we had enough participants that we still reached a fair result.",
#             "Try again! Can we push that number even lower than GUAC_LIMIT still get a fair result?"
#         ],
#         False:  [
#             "Oh no! Looks like missing out on trying MISSING_GUACS guacs each was too many to skip. Perhaps if we had more tasters we could've compensated."
#         ]
#     },

#     "simulation_3": {
#         True:  [
#             "Success!",
#             ],
#         False:  [
#             "Oh no!"
#         ]
#     },

#     "100_times": {
#         True:   [
#             "Across 100 simulations, NAME still took home the trophy more than anyone else, winning PERCENT of the contents. Take a look at who else took home the trophy at times and whether or not their guacamole deserved the win.",
#         ],
#         False:  [
#             "Across 100 simulations, NAME took home the trophy more than anyone else, but they did so less than half the time. In PERCENT of our contents, someone other than whom you decided had the best guacamole took home the win. Take a look at who they were and if they deserved it.",
#         ],
#     },

#     "condorcet": {
#         True:  [
#             "Success!",
#             ],
#         False:  [
#             "Oh no!"
#         ]
#     },

#     "sandbox": {
#         True:  [
#             "Success!",
#             ],
#         False:  [
#             "Oh no!"
#         ]
#     },
    
# }