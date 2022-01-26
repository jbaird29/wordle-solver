from typing import List, Optional
import os
import pickle
from src.wordle_feedback_cache import WordleFeedbackCache
from src.wordle_solver import WordleSolver
from src.wordle import Wordle


class WordleSolutionCache:

    def __init__(self, guess_file: str, answer_file=""):
        """
        Helper class; creates & saves a cache which holds the entire decision tree of optimal guesses
        Runs WordleSolver to create this decision tree; used by WordleSolverInterface to traverse the decision tree
        :param guess_file: the filepath as .txt holding the list of allowing guessable words
        :param answer_file: the filepath as .txt holding the list of possible hidden answers
        """
        answer_file = guess_file if answer_file == "" else answer_file
        g_file = os.path.splitext(os.path.split(guess_file)[-1])[0]
        a_file = os.path.splitext(os.path.split(answer_file)[-1])[0]
        save_file = os.path.join('.', 'cache', f"{a_file}__{g_file}__solutions.pkl")
        self._solution_tree = self._create_or_load_solution_cache(save_file, guess_file, answer_file)

    def get_solution_tree(self):
        return self._solution_tree

    def _create_or_load_solution_cache(self, save_file: str, guess_file: str, answer_file: str) -> dict:
        """Loads if the solution save file if it  exists, otherwise creates it"""
        try:
            with open(save_file, 'rb') as infile:
                print("Loading the solutions cache file. Please wait...")
                solutions = pickle.load(infile)
        except FileNotFoundError:
            print("Creating the solutions cache file. Please wait...")
            os.makedirs(os.path.dirname(save_file), exist_ok=True)
            solutions = self._generate_solutions_tree(guess_file, answer_file)
            with open(save_file, 'wb') as outfile:
                pickle.dump(solutions, outfile)
        print("Solution cache file loaded.")
        return solutions

    def _generate_solutions_tree(self, guess_file: str, answer_file: str) -> dict:
        """
        Creates a cached tree (dictionary) of the path for optimal guesses; dict is {feedback: (guess, next)}
            e.g. key: GGYYB, val: ( BLAST, dict ) tuple where dict is recursive (another key, tuple-val pair)
        Base case is when dict is empty, then the solution was guaranteed found
        """
        cache = WordleFeedbackCache(guess_file, answer_file)
        wordle_solver = WordleSolver(cache=cache)
        solutions = dict()
        for answer in wordle_solver.get_answers_dictionary():
            wordle = Wordle(answer, cache=cache)
            self._run_solver(wordle_solver, wordle, solutions)
            wordle_solver.reset_game()
        return solutions

    @staticmethod
    def _run_solver(wordle_solver: WordleSolver, wordle: Wordle, solutions: dict) -> None:
        """Given a hidden answer word, runs the solver and caches the results in the 'solutions' dict"""
        feedback = None  # the root 'feedback' key of the tree is None -> for the initial guess
        curr = solutions
        while feedback != "GGGGG":  # when feedback is all green - the game is won
            guess = wordle_solver.get_optimal_guess()  # get the next guess
            guess, curr = curr.setdefault(feedback, (guess, dict()))  # insert this node in the tree and traverse to it
            feedback = wordle.make_guess(guess)
            wordle_solver.update_with_guess_feedback(feedback)
            if len(wordle_solver.get_potential_answers()) == 0:
                raise Exception('Answers list is zero')
            if wordle.get_guess_count() > 6:
                raise Exception('Answer was not found within 6 guesses')


