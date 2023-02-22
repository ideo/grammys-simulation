# from re import M


STORY = {
    "introduction":  [
        """
        Welcome to the Isle of Musica — an idyllic locale where every citizen lives, breathes, even eats to make music. The Isle of Musica is inhabited by talented professional musicians, engineers, songwriters, and producers— all with different expertises and genre focuses. They all live on Isle of Musica because of the one value they have in common: their reverence, respect, and passion for MUSIC.
        """,
        """
        That’s one thing everyone can agree on on the Isle: that music is something to be studied and taken seriously. The problem is, no one can agree which artists, albums, or songs are the “best,” – and if asked, they’d probably nominate themselves, or a close collaborator. So in the spirit of wanting to give her citizens their well-deserved props, Mayor Melody suggests the town hold a first annual contest to decide which of this year’s song was SONG OF THE YEAR.  
        """,
        """
        Anyone who believes a song they wrote within the last year is particularly special can bring a clip of it to the town plaza on an upcoming Sunday at Bangers Only O’Clock. This is when all the citizens of the Isle of Musica can gather, listen to every song entered, and vote for their favorite. Citizens are so excited to participate in this celebration of their community. Word gets around, and everyone signs up.
        """,
        """
        That Sunday at Bangers Only O’Clock, at Bass Clef Stadium, the entire Isle of Musica - that’s num_voters people! - show up to participate in the search for the SONG OF THE YEAR. There were num_songs songs nominated, and all the artists gathered in the center of the plaza. Woah, Mayor Melody thinks to herself. We’ve got a lot of people participating, and a LOT of songs to decide between. How to fairly choose just one??  
        """,
    ],

    "simulation_1": [
        """
        Mayor Melody begins by making sure everyone has every song loaded onto their music players.
        """,
        """
        She hands out score cards, so citizens can score each song on a scale from 1-10. In a perfect world, the Mayor would ask everyone to listen to each song and then rank them from best to worst, but there are quite a lot of songs– and music can so often be a matter of taste. Trying to keep track of num_songs songs would simply be too hard and overwhelming. If they did set aside time to do it this way, it would be an objective way to figure out who wins SONG OF THE YEAR– from this, Musica could determine the best num_winners songs and ultimately, a number one winner.
        """,
        """
        """,
    ],

    "simulation_2": [
        """
        Of course, fair voting this way would take a long time. The citizens of the Isle had albums to produce, sound edits to make– every citizen of the Isle couldn’t drop everything, listen and rate every single song without missing a lot of time off work and play. Plus by the time they got to 1,000 songs, they might be exhausted, and all the songs after that will end up sounding the same. Music lovers are superhuman, but not like that!      
        """,
        """
        Now, let’s say Mayor Melody parsed out the songs between the voters, so that voters listened to a random sample of songs and ranked those. Say each voter gets 100 songs and submits a ballot with their top fifty.
        """,
        """
        One thing to remember is that every voter has subjective preferences. Even if a voter is a highly-trained music expert, it’s possible that they might rate one song slightly higher or lower than what it actually deserves. This could be for a variety of reasons: Shekka Sketcha might’ve loved the song she listened to right before she scored "You Beach Beach" by MK Timber, so “You Beach Beach” might have gotten a lower score than if it was the only song she listened to that day. 
        """,
    ],

    "simulation_3": [
        """
        While making her rounds in the town square, Mayor Melody got a whiff that individual loyalties between citizens might threaten to throw off the otherwise fair Song of the Year contest. After some investigation, the cronyism going on between the Heads of certain neighborhoods became clear. For example, in Double Reed Village, Al Pacone was running a campaign to get people to vote for his buddy’s song, “Defenestration" by Kid Lincoln, by offering them a free session at his state-of-the-art studio. And Lucky Luke, over on de Sousa Cul de Sac, was telling his neighbors that if they voted for his song, “Entrepreneur,” that he’d do them a big musical favor at a later date. Mayor Melody had a feeling that this could possibly happen, so she began to think about how to mitigate this issue, to ensure that it didn’t overtake the voting enough to skew the final results. Use the sliders below to see how much (or how little) cronyism affects the final result of the contest.      
        """,
    ],

    "conclusion": [
        """
        Say smart things to wrap it up.
        """,
    ]
}


INSTRUCTIONS = {
    "simulation_1": [
        "This first contest sets the baseline that we can compare against in subsequent contests. All num_voters voters listen and vote on all num_songs songs. "
    ],

    "simulation_2": [
        "In our second contest, voters are randomly assigned simulation_2_listen_limit songs of the num_songs nominated. They then submit a ballot ranking their top simulation_2_ballot_limit choices from that sample."
    ],

     "simulation_3": [
        "In our third contest, slsls."
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