from typing import List
from collections import defaultdict

class WordleSolver:

    def __init__(self, guess_file, answer_file=""):
        self._guess_words = self._load_words(guess_file)
        self._answer_words = self._load_words(answer_file) if answer_file != "" else [w for w in self._guess_words]
        self._bitvectors = [0] * len(self._answer_words)
        self._combo_counts = [defaultdict(int) for _ in range(len(self._guess_words))]
        self._worsts = [0] * len(self._guess_words)
        self._avgs = [0] * len(self._guess_words)

    def get_optimal_first_word(self):
        # associate each possible answer word with its bitvector
        for j in range(len(self._answer_words)):
            self._bitvectors[j] = self._word_to_bitvector(self._answer_words[j])
        # for each guessable word - enumerate the possible outcomes & map every answer word to an outcome
        for i in range(len(self._guess_words)):
            combo_counts = self._combo_counts[i]
            mask = self._word_to_mask(self._guess_words[i])
            for j in range(len(self._answer_words)):
                combo = self._bitvectors[j] & mask
                combo_counts[combo] += 1
            # worst case - the outcome with most words left
            self._worsts[i] = max(combo_counts.values())
            # avg case - a wtd avg of words left in each possible outcome
            total = sum(combo_counts.values())
            weighted_avgs = [(x / total) * x for x in combo_counts.values()]
            self._avgs[i] = sum(weighted_avgs)
        # list the words with the fewest words remaining in worst and average cases
        worst = [(self._worsts[i], self._guess_words[i]) for i in range(len(self._guess_words))]
        worst.sort()
        avg = [(int(self._avgs[i]), self._guess_words[i]) for i in range(len(self._guess_words))]
        avg.sort()
        return worst[:10], avg[:10]

    @staticmethod
    def _word_to_bitvector(word: str) -> int:
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
    def _word_to_mask(word: str) -> int:
        mask = 0
        for pos, letter in enumerate(word):
            c = ord(letter) - 97  # ord('a') = 97
            mask |= ((int("111", 2) << 3 * 26 * pos) << 3 * c)
        return mask

    @staticmethod
    def _load_words(filename: str) -> List[str]:
        with open(filename, "r") as f:
            words = f.read().splitlines()
        return words


if __name__ == '__main__':
    w = WordleSolver("wordle-allowed.txt", "wordle-answers.txt")
    worst, avg = w.get_optimal_first_word()
    print(worst)
    print(avg)
