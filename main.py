import sys

from wordle_solver import WordleSolver
from os.path import join as pjoin

feedback_prompt = "Please input the feedback the game gave you. G = Green, Y = Yellow, B = Black (Grey)\n" \
    "As an example, if the game reads (from left to right) Green, Yellow, Black, Black, Black -> enter GYBBB"

class WordlePlayer:

    def __init__(self):
        print("Welcome! If this is your first time, please wait a couple minutes as we set up the program.")
        self._w = WordleSolver(pjoin("dictionaries", "wordle-allowed.txt"), pjoin("dictionaries", "wordle-answers.txt"))

    def main(self):
        print("----------------")
        self._new_game_prompt()
        print("----------------")
        print("Starting the program!")
        self._run_game_loop()

    def _new_game_prompt(self):
        print("Are you starting a new game from scratch, or have you already entered guesses yourself?")
        response = input("Enter 1 for a new game, 2 if you already entered guesses: ")
        if response == '2':
            self._input_game_state()
        elif response != '1':
            print("Error - invalid input!")
            sys.exit()

    def _input_game_state(self):
        count = int(input("How many guesses have you entered already? Enter the number:  "))
        for i in range(count):
            print("----------------")
            guess = input(f"What was guess #{i+1}? Enter here:  ").lower()
            print(feedback_prompt)
            feedback = input("Enter the feedback:  ").upper()
            self._w.update_with_guess_feedback(feedback, guess)

    def _run_game_loop(self):
        while True:
            print("----------------")
            guess = self._w.get_optimal_guess()
            print(f"Here is the optimal next guess: {guess}")
            if self._w.get_potential_answers_length() == 1:
                print("Congrats - that guess will be the correct answer! Thanks for playing!")
                sys.exit()
            response = input("Did you enter this guess? Enter 1 for Yes, 2 for No: ")
            if response == "2":
                guess = input("Please input the guess you made: ").lower()
            elif response != "1":
                print("Error - invalid input!")
                sys.exit()
            print("----------------")
            print(feedback_prompt)
            feedback = input("Please enter the game feedback: ").upper()
            if feedback == "GGGGG":
                print("Congrats - looks like we found the correct answer! Thanks for playing!")
                sys.exit()
            if not all(c in "GYB" for c in feedback):
                print("Error - invalid input!")
                sys.exit()
            self._w.update_with_guess_feedback(feedback, guess=guess)


if __name__ == '__main__':
    WordlePlayer().main()