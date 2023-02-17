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
        That Sunday at Bangers Only O’Clock, at Bass Clef Stadium, the entire Isle of Musica– that’s num_voters people!-- show up to participate in the search for the SONG OF THE YEAR. There were num_songs songs nominated, and all the artists gathered in the center of the plaza. Woah, Mayor Melody thinks to herself. We’ve got a lot of people participating, and a LOT of songs to decide between. How to fairly choose just one?? 
        """,
    ],

    "simulation_1": [
        """
        Mayor Melody begins by making sure everyone has every song loaded onto their music players.
        """,
        """
        """,
        """
        """,
    ],

    "simulation_2": [
        """
        TKTK        
        """,
        """
        """,
        """
        """,
    ],
}


INSTRUCTIONS = {
    "simulation_1": [
        "Here are some instructions TKTKTKTKT."
    ],

    "simulation_2": [
        "Here are some instructions TKTKTKTKT."
    ],
}


SUCCESS_MESSAGES = {
    "simulation_1": {
        True:  [
            "Success! Even though people had so many guacs to try, and probably became quite full by the end, having everyone taste in random orders ensured the contest still had a fair result.",
            ],
        False:  [
            "Oh no! The contest didn't reach a fair conclusion. That's not supposed to happen!"
        ]
    },

    "simulation_2": {
        True:   [
            "Success! Even though the tasters missed out on trying MISSING_GUACS guacs each, we had enough participants that we still reached a fair result.",
            "Try again! Can we push that number even lower than GUAC_LIMIT still get a fair result?"
        ],
        False:  [
            "Oh no! Looks like missing out on trying MISSING_GUACS guacs each was too many to skip. Perhaps if we had more tasters we could've compensated."
        ]
    },

    "simulation_3": {
        True:  [
            "Success!",
            ],
        False:  [
            "Oh no!"
        ]
    },

    "100_times": {
        True:   [
            "Across 100 simulations, NAME still took home the trophy more than anyone else, winning PERCENT of the contents. Take a look at who else took home the trophy at times and whether or not their guacamole deserved the win.",
        ],
        False:  [
            "Across 100 simulations, NAME took home the trophy more than anyone else, but they did so less than half the time. In PERCENT of our contents, someone other than whom you decided had the best guacamole took home the win. Take a look at who they were and if they deserved it.",
        ],
    },

    "condorcet": {
        True:  [
            "Success!",
            ],
        False:  [
            "Oh no!"
        ]
    },

    "sandbox": {
        True:  [
            "Success!",
            ],
        False:  [
            "Oh no!"
        ]
    },
    
}