# WordleSolver

A wordle solver algorithm & associated program I designed and implemented in Python.

Given game state, presents the user with the optimal next guess, which is the guess that has the fewest 
possible remaining solutions (on average) after making that guess.

Run the program as using: `python3 main.py`, which will walk through instructions step-by-step.

Over the ~2000 word trial of possible answers, the number of guesses until a solution is found are as follows:
- **Mean**: 3.545
- **Min**: 2
- **25th**: 3
- **50th**: 4
- **75th**: 4
- **Max**: 5

(See `run_trial.py` for the trial run implementation)