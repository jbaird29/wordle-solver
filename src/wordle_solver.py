from typing import List, Optional
from collections import defaultdict, Counter
from functools import reduce
import os
import pickle
from src.wordle_feedback_cache import WordleFeedbackCache


class WordleSolver:

    def __init__(self, cache=None, guess_file="", answer_file=""):
        """An instance of Wordle Solver; the answer is hidden, only dictionaries of possible guesses & answers is known
        :param cache: an optional WordleFeedbackCache object to speed up game processing
        :param guess_file: the filepath as .txt holding the list of allowing guessable words
        :param answer_file: the filepath as .txt holding the list of possible hidden answers
        *Either a cache must be provided, or a guess & answer file must be provided*
        """
        if cache is None and guess_file == "":
            raise Exception("Please provide a cache, or the filepath of a guess/answer file")
        self._cache: WordleFeedbackCache = WordleFeedbackCache(guess_file, answer_file) if cache is None else cache
        self._potential_answers = [w for w in self.get_answers_dictionary()]  # mutable: filtered as guesses are made
        self._guesses_made = []  # mutable -> the guesses that were made -> str
        self._feedbacks_given = []  # mutable -> the feedbacks given on those guesses -> str

    def reset_game(self):
        """Reset the game state to a new state"""
        self._potential_answers = [w for w in self.get_answers_dictionary()]
        self._guesses_made = []
        self._feedbacks_given = []

    def get_potential_answers(self) -> List[str]:
        """Returns the list of words which could still possibly be the answer"""
        return self._potential_answers

    def get_answers_dictionary(self) -> List[str]:
        """Returns the list of all possible answer words (loaded from the input dictionary file)"""
        return self._cache.get_answer_words()

    def get_guess_dictionary(self) -> List[str]:
        """Returns the list of all possible guess words (loaded from the input dictionary file)"""
        return self._cache.get_guess_words()

    def get_optimal_guess(self) -> str:
        """Returns the optimal guess word, based on the game state and feedback given so far"""
        if 1 <= len(self.get_potential_answers()) <= 2:
            guess = self._potential_answers[0]  # base case - if there are only 1 or 2 possible answer left, try one
        elif len(self._guesses_made) == 0:
            guess = "roate"  # optimization - if this is the first guess, go with the pre-calculated best guess
        else:
            guess = self._calculate_optimal_guess()  # otherwise, calculate the best guess based on current game state
        self._guesses_made.append(guess)
        return guess

    def _calculate_optimal_guess(self) -> str:
        # "factors" holds optimization factors (wtd avg); enumerations is the word partitions
        factors = [0] * len(self.get_guess_dictionary())
        all_enumerations = [defaultdict(int) for _ in range(len(self.get_guess_dictionary()))]
        # for each guessable word - enumerate the possible outcomes & map every answer word to an outcome
        for i, guess in enumerate(self.get_guess_dictionary()):
            enumerations = all_enumerations[i]
            for answer in self.get_potential_answers():
                feedback = self._cache.get_feedback(answer, guess)
                enumerations[feedback] += 1
            # take a wtd avg of words left in each possible outcome; the optimal next guess will minimize that value
            total = sum(enumerations.values())
            weighted_avgs = [(x / total) * x for x in enumerations.values()]
            factors[i] = sum(weighted_avgs)
        # return the optimal word - the minimum of the wtd average outcomes
        # print(sorted([(factors[i], self._guess_words[i]) for i in range(len(factors))])[0:10])  # the top 10 options
        min_index = reduce(lambda p, c: c if factors[c] < factors[p] else p, range(len(factors)))
        return self.get_guess_dictionary()[min_index]

    def update_with_guess_feedback(self, feedback: str, guess="") -> None:
        """
        Updates the game state with feedback given a guess
        :param feedback: the 5-letter feedback (from left to right) like 'GGYYB' -> G=Green, Y=Yellow, B=Black(grey)
        :param guess: the guess that was made; if empty, assumes the guess was the previously given optimal guess
        """
        self._feedbacks_given.append(feedback)
        if guess != "":
            if len(self._guesses_made) == 0:
                self._guesses_made.append(guess)  # first guess -> append to the list
            else:
                self._guesses_made[-1] = guess  # second+ guess -> replace the last list element
        guess = self._guesses_made[-1]  # e.g. 'raise'
        # filter the word list based on the feedback; answers_remaining is tuple of (j, answer)
        new = filter(lambda answer: self._cache.get_feedback(answer, guess) == feedback, self.get_potential_answers())
        self._potential_answers = list(new)
