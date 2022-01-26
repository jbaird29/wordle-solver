from src.wordle_solver import Wordle, WordleSolverInterface, WordleFeedbackCache
from statistics import mean, quantiles


def run_trial(wordle: Wordle, solver: WordleSolverInterface) -> int:
    """Runs the optimizer and returns the number of guesses until it got the answer"""
    guess_count = 0
    feedback = ""
    while feedback != "GGGGG":
        guess_count += 1
        guess = solver.get_guess()
        feedback = wordle.make_guess(guess)
        solver.set_feedback(feedback)
        if wordle.get_guess_count() > 6:
            raise Exception('Answer was not found within 6 guesses')
    solver.reset_game()
    return guess_count


if __name__ == '__main__':
    solver = WordleSolverInterface(guess_file="dictionaries/wordle-allowed.txt",
                              answer_file="dictionaries/wordle-answers.txt")
    answers = WordleFeedbackCache.load_words("dictionaries/wordle-answers.txt")
    guess_counts = []
    for answer in answers:
        wordle = Wordle(answer)
        count = run_trial(wordle, solver)
        guess_counts.append(count)

    print(f"Mean:  {round(mean(guess_counts),3)}")  # 3.545
    print(f"Min:   {min(guess_counts)}")  # 2
    print(f"25th:  {quantiles(guess_counts, n=4)[0]}")  # 3
    print(f"50th:  {quantiles(guess_counts, n=4)[1]}")  # 4
    print(f"75th:  {quantiles(guess_counts, n=4)[2]}")  # 4
    print(f"Max:   {max(guess_counts)}")    # 5
