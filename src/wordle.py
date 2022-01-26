from typing import List, Optional
from collections import defaultdict, Counter
import src.wordle_feedback_cache

class Wordle:

    def __init__(self, answer, cache=None):
        """An instance of a Wordle game with a given hidden answer word;
        cache is an optional WordleFeedbackCache object to speed up game processing"""
        self.cache: Optional[wordle_feedback_cache.WordleFeedbackCache] = cache
        self.answer = answer
        self._answer_letter_counts = Counter(answer)  # count of letters in answer, to speed up calc_feedback() function
        self._guesses_made = []  # mutable -> the guesses that were made -> str
        self._feedbacks_given = []  # mutable -> the feedbacks given on those guesses -> str

    def make_guess(self, guess: str) -> str:
        """Makes a guess and returns the feedback associated with that guess"""
        self._guesses_made.append(guess)
        feedback = self.calculate_feedback(guess) if self.cache is None else self.cache.get_feedback(self.answer, guess)
        self._feedbacks_given.append(feedback)
        return feedback

    def get_guess_count(self) -> int:
        """Returns the number of guesses made"""
        return len(self._guesses_made)

    def calculate_feedback(self, guess: str) -> str:
        """Given a guess and a hidden answer, returns the feedback the game would give
            as a string like GGYYB where G=Green, Y=Yellow, B=Black(grey)"""
        if len(self.answer) != len(guess):
            raise Exception('Answer and guess are different lengths')
        feedback = [''] * len(guess)
        guess_letter_counts = defaultdict(int)
        # first pass - mark the greens
        for i, letter in enumerate(guess):
            if letter == self.answer[i]:
                feedback[i] = 'G'  # if letters match, this spot is a green
                guess_letter_counts[letter] += 1
        # second pass - mark the yellows & blacks (grey)
        for i, letter in enumerate(guess):
            if letter != self.answer[i]:  # skip any spots already marked green
                if guess_letter_counts[letter] < self._answer_letter_counts[letter]:
                    feedback[i] = 'Y'  # if another instance of this letter is left in the word, this spot is yellow
                    guess_letter_counts[letter] += 1
                else:
                    feedback[i] = 'B'  # otherwise this spot is black (grey)
        return ''.join(feedback)


