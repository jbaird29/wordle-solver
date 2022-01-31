from typing import List, Optional
from collections import defaultdict, Counter
import os
from src.wordle import Wordle

class WordleFeedbackCache:

    def __init__(self, guess_file: str, answer_file=""):
        """
        Helper class; creates a cache which holds the feedback for each (answer, guess) combination,
        to speed up the solver processing
        :param guess_file: the filepath as .txt holding the list of allowing guessable words
        :param answer_file: the filepath as .txt holding the list of possible hidden answers
        """
        print("Creating feedbacks cache. Please wait...")
        self._guess_file = guess_file
        self._answer_file = answer_file if answer_file != "" else guess_file
        self._guess_words = self.load_words(self._guess_file)
        self._answer_words = self.load_words(self._answer_file)
        self._feedbacks = self._create_feedbacks_cache(self._answer_words, self._guess_words)
        print("Feedbacks cache created.")

    def get_feedback(self, answer: str, guess: str) -> str:
        """
        Returns the feedback associated with a given guess and answer word
        :param answer: the hidden answer word
        :param guess: the guess word
        :return: the feedback as a string like "GGYYB"
        """
        return self._feedbacks[(answer, guess)]

    def get_answer_words(self) -> List[str]:
        """Returns list of possible hidden answer words"""
        return self._answer_words

    def get_guess_words(self) -> List[str]:
        """Returns list of possible guessable words"""
        return self._guess_words

    def get_guess_filename(self) -> str:
        return os.path.splitext(os.path.split(self._guess_file)[-1])[0]

    def get_answer_filename(self) -> str:
        return os.path.splitext(os.path.split(self._answer_file)[-1])[0]

    @staticmethod
    def _create_feedbacks_cache(answers, guesses) -> dict:
        """Creates the cache of feedbacks for each (answer, guess) combination"""
        feedbacks = dict()
        for answer in answers:
            wordle = Wordle(answer)
            for guess in guesses:
                feedback = wordle.calculate_feedback(guess)
                feedbacks[(answer, guess)] = feedback
        return feedbacks

    @staticmethod
    def load_words(filename: str) -> List[str]:
        with open(filename, "r") as f:
            words = f.read().splitlines()
        return words


