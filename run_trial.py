from wordle_solver import WordleSolver
from statistics import mean


def run_trial(w: WordleSolver, answer: str) -> int:
    """
    Runs the optimizer and returns the number of guesses until it got the answer
    :param answer: the word that is the puzzle's correct solution
    """
    guess_count = 0
    while True:
        guess_count += 1
        guess = w.get_optimal_guess()
        if guess == answer:
            w.reset_game()
            return guess_count
        feedback = w._calculate_feedback(answer, guess)
        w.update_with_guess_feedback(feedback)
        if w.get_potential_answers_length() == 0:
            raise Exception('Answers list is zero')


if __name__ == '__main__':
    w = WordleSolver("dictionaries/wordle-allowed.txt", "dictionaries/wordle-answers.txt", method="worst")
    words = WordleSolver._load_words("dictionaries/wordle-answers.txt")
    guess_counts = []
    above_6 = []
    for i, word in enumerate(words):
        count = run_trial(w, word)
        guess_counts.append(count)
        if count > 6:
            above_6.append(word)
    print(f"Mean: {mean(guess_counts)}")
    print(f"Above 6 ({len(above_6)} out of {len(words)}): {above_6}")