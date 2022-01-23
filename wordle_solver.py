from typing import List
from collections import defaultdict

class WordleSolver:

    def __init__(self, filename):
        self._words = self._load_words(filename)
        self._n = len(self._words)
        self._bitvectors = [0] * self._n
        self._combo_counts = [defaultdict(int) for _ in range(self._n)]
        self._worsts = [0] * self._n
        self._avgs = [0] * self._n

    def get_optimal_first_word(self):
        # associate each word with its bitvector
        for i in range(self._n):
            self._bitvectors[i] = self._word_to_bitvector(self._words[i])
        # for each word - form the powerset, then map every other word to an entry within that powerset
        for i in range(self._n):
            combo_counts = self._combo_counts[i]
            for j in range(self._n):
                combo = self._bitvectors[j] & self._bitvectors[i]
                combo_counts[combo] += 1
            # worst case - the outcome with most words left
            self._worsts[i] = max(combo_counts.values())
            # avg case - a wtd avg of words left in each possible outcome
            total = sum(combo_counts.values())
            weighted_avgs = [(x / total) * x for x in combo_counts.values()]
            self._avgs[i] = sum(weighted_avgs)
        # list the words with the fewest words remaining in worst and average cases
        worst = [(self._worsts[i], self._words[i]) for i in range(self._n)]
        worst.sort()
        avg = [(int(self._avgs[i]), self._words[i]) for i in range(self._n)]
        avg.sort()
        return worst[:10], avg[:10]

    @staticmethod
    def _word_to_bitvector(word: str) -> int:
        bitvector = 0
        for c in word:
            i = ord(c) - 97  # ord('a') = 97
            bitvector |= (1 << i)
        return bitvector

    @staticmethod
    def _load_words(filename: str) -> List[str]:
        with open(filename, "r") as f:
            words = f.read().splitlines()
        return words


if __name__ == '__main__':
    w = WordleSolver("wordle-answers.txt")
    worst, avg = w.get_optimal_first_word()
    print(worst)
    print(avg)
