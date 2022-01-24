from wordle_solver import WordleSolver
from statistics import mean
from functools import reduce

def run_trial(answer_word: str) -> int:
    """
    Runs the optimizer and returns the number of guesses until it got the answer
    :param answer_word: the word that is the puzzle's correct solution
    :return:
    """
    guess_count = 0
    w = WordleSolver("wordle-allowed.txt", "wordle-answers.txt", method="average")
    bv = w._answer_word_to_bitvector(answer_word)
    while True:
        guess_count += 1
        guess = w.get_optimal_guess()
        if guess == answer_word:
            return guess_count
        feedback = w._feedback_bitvector_to_str(bv & w._guess_word_to_mask(guess))
        w.update_with_guess_feedback(feedback)
        if w.get_potential_answers_length() == 0:
            raise Exception('Answers list is zero')


if __name__ == '__main__':
    words = WordleSolver._load_words("wordle-answers.txt")
    guess_counts = []
    above_6 = []
    for i, word in enumerate(words):
        count = run_trial(word)
        guess_counts.append(count)
        if count > 6:
            above_6.append(word)
    print(f"Mean: {mean(guess_counts)}")
    print(f"Above 6 ({len(above_6)} out of {len(words)}): {above_6}")