import collections
from typing import List
from collections import defaultdict, Counter
from functools import reduce
import os
import pickle

class WordleSolver:

    def __init__(self, guess_file: str, answer_file="", method="average"):
        g_file = os.path.splitext(os.path.split(guess_file)[-1])[0]
        a_file = os.path.splitext(os.path.split(answer_file)[-1])[0]
        self._save_file = os.path.join('', 'cache', f"{a_file}__{g_file}.pkl")
        self._method = method  # either "average" or "worst"
        self._guess_words = self._load_words(guess_file)
        self._answer_words = self._load_words(answer_file) if answer_file != "" else [w for w in self._guess_words]
        self._answers_remaining = [_ for _ in enumerate(self._answer_words)]  # mutable -> filtered as guesses are made
        self._guesses_made = []  # mutable -> the guesses that were made -> tuple of (index: int, word: str)
        self._feedbacks_given = []  # mutable -> the feedbacks given on those guesses -> str
        try:
            with open(self._save_file, 'rb') as infile:
                print("Loading the cache file...")
                self._feedbacks = pickle.load(infile)
        except FileNotFoundError:
            print("Creating the cache file. Please wait...")
            os.makedirs(os.path.dirname(self._save_file), exist_ok=True)
            self._feedbacks = self._populate_feedbacks()
            with open(self._save_file, 'wb') as outfile:
                pickle.dump(self._feedbacks, outfile)
        if len(self._feedbacks[0]) != len(self._answer_words) or len(self._feedbacks) != len(self._guess_words):
            print("Cache file does not match the dictionary. Recreating it...")
            self._feedbacks = self._populate_feedbacks()
            with open(self._save_file, 'wb') as outfile:
                pickle.dump(self._feedbacks, outfile)
        print("Set-up complete.")

    def reset_game(self):
        """
        Reset the game state to a new state
        """
        self._answers_remaining = [_ for _ in enumerate(self._answer_words)]
        self._guesses_made = []
        self._feedbacks_given = []

    def get_optimal_guess(self) -> str:
        """
        Returns the optimal guess word, based on the game state and feedback given so far
        """
        # base case - if there are only 1 or 2 possible answer left, try one of those
        if 1 <= self.get_potential_answers_length() <= 2:
            j, guess = self._answers_remaining[0]
            i = self._get_word_index(guess, "guesses")
        # # optimization - if this is the first guess, go with the pre-calculated best guess
        elif len(self._guesses_made) == 0 and self._method == "average":
            i, guess = self._get_word_index("roate", "guesses"), "roate"
        elif len(self._guesses_made) == 0 and self._method == "worst":
            i, guess = self._get_word_index("aesir", "guesses"), "aesir"
        # otherwise, calculate the best guess based on current game state
        else:
            i, guess = self._calculate_optimal_guess()
        self._guesses_made.append((i, guess))
        return guess

    def _calculate_optimal_guess(self) -> (int, str):
        # "factors" holds optimization factors (either worst case or avg); enumerations is the word partitions
        factors = [0] * len(self._guess_words)
        all_enumerations = [defaultdict(int) for _ in range(len(self._guess_words))]
        # for each guessable word - enumerate the possible outcomes & map every answer word to an outcome
        for i, guess in enumerate(self._guess_words):
            enumerations = all_enumerations[i]
            for j, answer in self._answers_remaining:
                feedback = self._feedbacks[i][j]
                enumerations[feedback] += 1
            # worst case - the outcome with most words left
            if self._method == "worst":
                factors[i] = max(enumerations.values())
            # avg case - a wtd avg of words left in each possible outcome
            elif self._method == "average":
                total = sum(enumerations.values())
                weighted_avgs = [(x / total) * x for x in enumerations.values()]
                factors[i] = sum(weighted_avgs)
        # return the optimal word - the minimum of the factors
        # print(sorted([(factors[i], self._guess_words[i]) for i in range(len(factors))])[0:10])  # the top 10 options
        min_index = reduce(lambda p, c: c if factors[c] < factors[p] else p, range(len(factors)))
        return min_index, self._guess_words[min_index]

    def update_with_guess_feedback(self, feedback: str, guess="") -> None:
        """
        Updates the game state with feedback given a guess
        :param feedback: a five-letter string of G (green) Y (yellow) B (black/grey); e.g. if guess was CAB and
            the solution was BAD, feedback would be the string: "BGY"
        :param guess: the guess that was made; if empty, assumes the guess was the previously given optimal guess
        """
        self._feedbacks_given.append(feedback)
        if guess != "":
            i = self._get_word_index(guess, "guesses")
            if len(self._guesses_made) == 0:
                self._guesses_made.append((i, guess))
            else:
                self._guesses_made[-1] = (i, guess)
        else:
            i, guess = self._guesses_made[-1]  # e.g. 'raise'
        # filter the word list (and its associated bitvectors) based on the feedback
        new_answers_remaining = []
        for j, answer in self._answers_remaining:
            if self._feedbacks[i][j] == feedback:
                new_answers_remaining.append((j, self._answer_words[j]))
        self._answers_remaining = new_answers_remaining
        return

    def get_potential_answers_length(self):
        """
        Returns the length of possible answers remaining, based on guesses made / feedback given so far
        """
        return len(self._answers_remaining)

    def _populate_feedbacks(self) -> List[List[str]]:
        # feedbacks is a matrix of guess_words (rows) x answer_words (cols)
        feedbacks = [[""] * len(self._answer_words) for _ in range(len(self._guess_words))]
        for j, answer in enumerate(self._answer_words):
            answer_letter_counts = Counter(answer)
            for i, guess in enumerate(self._guess_words):
                feedback = self._calculate_feedback(answer, guess, answer_letter_counts)
                feedbacks[i][j] = feedback
        return feedbacks

    def _get_word_index(self, word, dictionary):
        index = -1
        if dictionary == 'guesses':
            index = binary_search(self._guess_words, word)
        elif dictionary == 'answers':
            index = binary_search(self._answer_words, word)
        if index == -1:
            raise Exception(f"Word: {word} was not found in the {dictionary} dictionary.")
        return index

    @staticmethod
    def _calculate_feedback(answer, guess, answer_letter_counts=None):
        if len(answer) != len(guess):
            raise Exception('Answer and guess are different lengths')
        feedback = [''] * len(guess)
        if answer_letter_counts is None:
            answer_letter_counts = Counter(answer)  # immutable - passed in as argument for time/space efficiency
        guess_letter_counts = defaultdict(int)  # mutable - must be created for each guess
        # first pass - mark the greens
        for i, letter in enumerate(guess):
            if letter == answer[i]:
                feedback[i] = 'G'  # if letters match, this spot is a green
                guess_letter_counts[letter] += 1
        # second pass - mark the yellows & blacks (grey)
        for i, letter in enumerate(guess):
            if letter != answer[i]:  # skip any spots already marked green
                if guess_letter_counts[letter] < answer_letter_counts[letter]:
                    feedback[i] = 'Y'  # if another instance of this letter is left in the word, this spot is yellow
                    guess_letter_counts[letter] += 1
                else:
                    feedback[i] = 'B'  # otherwise this spot is black (grey)
        return ''.join(feedback)

    @staticmethod
    def _load_words(filename: str) -> List[str]:
        with open(filename, "r") as f:
            words = f.read().splitlines()
        return words


def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if target == arr[mid]:
            return mid
        elif target > arr[mid]:
            left = mid + 1
        else:
            right = mid - 1
    return -1
