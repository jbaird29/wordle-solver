import os.path
import sys
from src.wordle_solver_interface import WordleSolverInterface
from os.path import join

feedback_prompt = "NOTE! Please input guess feedback as a 5-letter string where G=Green, Y=Yellow, B=Black(grey)\n" \
    "As an example, if the game reads (from left to right) Green, Yellow, Black, Black, Black -> enter GYBBB"

def main():
    print("Welcome! If you don't have a 'cache' file, please wait ~20 minutes as we build the decision tree.")
    print("----------------")
    solver = WordleSolverInterface(guess_file=os.path.join("dictionaries", "wordle-allowed.txt"),
                                   answer_file=os.path.join("dictionaries", "wordle-answers.txt"))
    print("Starting the program!")
    print("----------------")
    print(feedback_prompt)
    print("----------------")
    while True:
        guess = solver.get_guess()
        print(f"Here is the optimal next guess: {guess}")
        if solver.next_guess_is_winner():
            print("Congrats - that guess will be the correct answer! Thanks for playing!\n")
            sys.exit()
        feedback = input("Please enter the game feedback: ").upper()
        if feedback == "GGGGG":
            print("Congrats - looks like we found the correct answer! Thanks for playing!\n")
            sys.exit()
        if not all(c in "GYB" for c in feedback):
            print("Error - invalid input!")
            sys.exit()
        solver.set_feedback(feedback)


if __name__ == '__main__':
    main()
