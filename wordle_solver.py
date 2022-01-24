from typing import List
from collections import defaultdict
from functools import reduce


class WordleSolver:
    # TODO - need to fix a 'false yellow' bug -> e.g. knoll & stoop returns BBGYB rather than BBGBB

    def __init__(self, guess_file, answer_file="", method=""):
        self._guess_words = self._load_words(guess_file)
        self._answer_words = self._load_words(answer_file) if answer_file != "" else [w for w in self._guess_words]
        self._answer_bitvectors = [0] * len(self._answer_words)
        self._method = method
        self._guesses_made = []  # the guesses that were made
        self._feedbacks_given = []  # the feedbacks given on those guesses
        # associate each possible answer word with its bitvector
        for j in range(len(self._answer_words)):
            self._answer_bitvectors[j] = self._answer_word_to_bitvector(self._answer_words[j])

    def get_optimal_guess(self) -> str:
        # base case - if there is only one possible answer left, that is the correct solution
        if len(self._answer_words) == 1:
            guess = self._answer_words[0]
        # # optimization - if this is the first guess, go with the pre-calculated best guess
        elif len(self._guesses_made) == 0 and self._method == "worst":
            guess = "aesir"
        elif len(self._guesses_made) == 0 and self._method == "average":
            guess = "roate"
        # otherwise, calculate the best guess based on current game state
        else:
            guess = self._calculate_optimal_guess()
        self._guesses_made.append(guess)
        return guess

    def _calculate_optimal_guess(self) -> str:
        # "factors" holds optimization factors (either worst case or avg); enumerations is the word partitions
        factors = [0] * len(self._guess_words)
        all_enumerations = [defaultdict(int) for _ in range(len(self._guess_words))]
        # for each guessable word - enumerate the possible outcomes & map every answer word to an outcome
        for i in range(len(self._guess_words)):
            enumerations = all_enumerations[i]
            mask = self._guess_word_to_mask(self._guess_words[i])
            for j in range(len(self._answer_words)):
                feedback_bitvector = self._answer_bitvectors[j] & mask
                enumerations[feedback_bitvector] += 1
            # worst case - the outcome with most words left
            if self._method == "worst":
                factors[i] = max(enumerations.values())
            # avg case - a wtd avg of words left in each possible outcome
            elif self._method == "average":
                total = sum(enumerations.values())
                weighted_avgs = [(x / total) * x for x in enumerations.values()]
                factors[i] = sum(weighted_avgs)
        # return the optimal word - the minimum of the factors
        min_index = reduce(lambda p, c: c if factors[c] < factors[p] else p, range(len(factors)))
        return self._guess_words[min_index]

    def update_with_guess_feedback(self, feedback_str: str, guess_word="") -> None:
        """
        Updates the game state with feedback given a guess
        :param feedback_str: a five-letter string of G (green) Y (yellow) B (black/grey); e.g. if guess was CAB and
            the solution was BAD, feedback would be the string: "BGY"
        :param guess_word: the guess that was made; if empty, assumes the guess was the previously given optimal guess
        """
        if guess_word != "":
            self._guesses_made[-1] = guess_word  # TODO - ensure this method is only called after a get_optimal_guess call
        guess_word = self._guesses_made[-1]  # e.g. 'raise'
        self._feedbacks_given.append(feedback_str)
        # convert the guess and feedback str into a bitvector / mask
        feedback_bitvector = self._feedback_str_to_bitvector(feedback_str, guess_word)
        guess_mask = self._guess_word_to_mask(guess_word)
        # filter the word list (and its associated bitvectors) based on the feedback
        new_answer_words = []
        new_answer_bitvectors = []
        for j in range(len(self._answer_words)):
            if self._answer_bitvectors[j] & guess_mask == feedback_bitvector:
                new_answer_words.append(self._answer_words[j])
                new_answer_bitvectors.append(self._answer_bitvectors[j])
        self._answer_words = new_answer_words
        self._answer_bitvectors = new_answer_bitvectors
        return

    def get_potential_answers_length(self):
        return len(self._answer_words)

    @staticmethod
    def _feedback_str_to_bitvector(feedback: str, guess: str) -> int:
        """
        Helper functions; converts the string representation of feedback to a bitvector
        :param feedback: if no feedback string given, takes the last entry
        :return: bitvector representation of that feedback
        """
        bitvector = ['000'] * 26 * 5  # 001 is green, 010 is yellow, 100 is black (grey)
        for pos, feedback_letter in enumerate(feedback):  # feedback is "GYBBY"  -> G is pos 0; Y is pos 1; etc.
            guess_letter = guess[pos]  # the 'r' in 'raise'
            c = ord(guess_letter) - 97  # ord('a') = 97
            i = len(bitvector) - 1 - (c + 26 * pos)  # bitvector is right (pos 0, letter A) to left (pos 4, letter Z)
            if feedback_letter == 'G':
                bitvector[i] = '001'
            elif feedback_letter == 'Y':
                bitvector[i] = '010'
            elif feedback_letter == 'B':
                bitvector[i] = '100'
            else:
                raise Exception('Invalid letter in the feedback string.')
        return int(''.join(bitvector), 2)

    @staticmethod
    def _feedback_bitvector_to_str(bitvector: int) -> str:
        feedback = []
        while bitvector > 0:
            result = bitvector & 0b111
            if result == 0b001:
                feedback.append('G')
            elif result == 0b010:
                feedback.append('Y')
            elif result == 0b100:
                feedback.append('B')
            bitvector >>= 3
        return ''.join(feedback)

    @staticmethod
    def _answer_word_to_bitvector(word: str) -> int:
        # 5 positions * 26 letters * 3 outcomes
        # ordered right to left: position 5..1 ( Z..A [GREY-YELLOW-GREEN] )
        bitvector = ['000'] * 26 * 5
        # iterate from back ('a' at pos 0) to front ('z' at pos 4)
        i = len(bitvector) - 1
        for p in range(5):
            for c in range(26):
                letter = chr(c+97)
                # set grey if this letter is not in the word at all
                if letter not in word:
                    bitvector[i] = '100'
                # set yellow if this letter is in the word, but not in this position
                elif word[p] != letter:
                    bitvector[i] = '010'
                # set green if this letter matches this position
                else:
                    bitvector[i] = '001'
                # decrement to the next spot in the bitvector
                i -= 1
        return int(''.join(bitvector), 2)

    @staticmethod
    def _guess_word_to_mask(word: str) -> int:
        mask = 0
        for pos, letter in enumerate(word):
            c = ord(letter) - 97  # ord('a') = 97
            mask |= ((0b111 << 3 * 26 * pos) << 3 * c)
        return mask

    @staticmethod
    def _load_words(filename: str) -> List[str]:
        with open(filename, "r") as f:
            words = f.read().splitlines()
        return words

    @staticmethod
    def _bitvector_pretty_print(bitvector: int):
        # TODO - prints a bitvector in a format like:  pos 0 -> a: Y, b: G, c: B, ... \n pos 1 -> a: G, b: B, etc.
        pass


if __name__ == '__main__':
    w = WordleSolver("wordle-allowed.txt", "wordle-answers.txt", method="average")
    guess1 = w.get_optimal_guess()
    print(guess1)
    w.update_with_guess_feedback("BYBBB")
    print(w._answer_words)
    guess2 = w.get_optimal_guess()
    print(guess2)
    w.update_with_guess_feedback("BGGBG", "snool")
    print(w._answer_words)
    guess3 = w.get_optimal_guess()
    print(guess3)