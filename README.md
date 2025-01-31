# avocado-allegory

This simulation was inspired by a story shared by IDEOer Jenna Fizel about a guacamole contest their partner had helped organize. The contest had a simple problem: so many people wanted to join in on the fun of tasting guac and voting for the best, but the contestans just hadn't made enough guacamole to feed all those eager mouths. The solution was quite clever. By using a non-traditional method of vote counting, it's not necessary for each voter to try every guacamole for the contest to still reach a fair conclusion. This method allows more people to particiapte, both as guac-chefs and guac-critis.

Many exisiting voting simulations are civics-orientied, e.g. the presidential election. This simulation differs in that we delibrately limit voters to a subset of candidates. Obvisouly, that would never fly in a governmental election; we could never say, "Hey, 13 candidates are in this primary, but we're only going to let you voice your opinion on 3 of them!" But a guacamole contest is a useful metaphor for competitions in the arts. For example, maybe we want to consider 50 movies for Best Picture at the Oscars next year. It would liekly be too burdensome to ask the Academy's voters to watch all 50 movies and fairly critique each one. But these simulations show that randomly assigning 5 different movies to each voter will make it feasible to have that many candidates for Best Picture and still have a fair outcome. It also opens the door to include more voters, as doing so only makes the election more robust and watching only 5 movies is not too much to ask of someone.

While the story that inspired this work relied on one particular voting method, this simulation has been designed to test whatever methods we are curious about. To join in on the fun, see below!


### Running the App
This project relies on Poetry and Streamlit. To start the app, run:
```bash
poetry run streamlit run app.py
```

The file `app.py` contains our current work in progress story and simulation. The intent is to publish this as a blog post once it is further along. The current draft was very much a build-to-think product. It explores useful story metaphors and interactive widgets but still lacks a clear articulation of what problem needs to be solved.

More useful at this stage will be:
```bash
poetry run streamlit run sandbox_app.py
```

The `sandbox_app.py` has been set up to explore different voting methods, consistency of outcomes, and help craft the specifc simulation set ups we'll want to inculde in the story. This is where we are currenlty spending our time. If you have a voting method you want to try out, this can be a good place to start. Alternatively, feel free to take a look at our [big ole list of issues](https://github.com/ideo/avocado-allegory/projects/1).


### The Code
The code written in `src/simulation.py` has been written to be highly modular with ths intent of making it easy to drop in new voting methods over time. The simulated agents definied in `src/townspeople.py` vote by sampling from a normal distribution with the mean set to (or offset from) the "objective score" set by the reader. The agents return a score ballot. Those score ballots are then converted into relevant and necessary ballots by the voting methods classes. For example, in our implementation of Ranked Choice Voting, agents still submit score ballots, but the `RankChoiceVoting` class coverts them into rankings before tallying.

Voting methods are handled by separate classes. The idea is to write them so they could one day be used independently of this simulation. The only two have so far are `src/condorecet_counting.py` and `src/ranked_choice_voting.py`. Please contribute by by adding new ones or stress testing the existing ones!

The high level structre of the streamlit app is defined in `app.py`, the heavy lifting is contained in `src/logic.py`, and then the story is copied and pasted from [Google Docs](https://docs.google.com/document/d/1CA9NXp8I9b6ds16khcJLrY1ZL7ZBABK6KRu9SvBL5JI/edit?usp=sharing) into `src/story.py`.


### Version Control
Streamlit will let you develop locally with the latest python (3.9.x) but can only host up to python 3.7.12. Please don't change the python or any package versions specified in `pyproject.toml`. Poetry generally handles version properly when attempting to add a package, but sometimes you need to google around a bit to find the right package version to specify.


### Testing
Run the unit tests from the command line with 
```bash
poetry run python -m unittest test.test_simulation
poetry run python -m unittest test.test_condorcet_method
```

If you add a new voting method class, please also add tests to `tests/` to verify it. You can use the existing tests as templates.


### Development Notes

1. Streamlit Cloud doesn't provide away to do a `--without dev` install of dependencies when using Poetry. However, if there is a `requirements.txt` file, Streamlit Cloud will install from that first and ignore any other dependency files. The below command exports only production dependencies to a requirements file.
    ```bash
    poetry export --without-hashes --without dev --format=requirements.txt > requirements.txt
    ```

1. Optionally, if you would like to work with jupyter notebooks while using poetry, after running `poetry install`, run:
   ```bash
   poetry run python -m ipykernel install --user --name song-contest
   poetry run jupyter lab
   ```
   And then select the newly created kernel, `song-contest`.
