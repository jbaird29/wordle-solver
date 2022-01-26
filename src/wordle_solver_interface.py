from src.wordle_solution_cache import WordleSolutionCache


class WordleSolverInterface:

    def __init__(self, cache=None, guess_file="", answer_file=""):
        """
        A public interface to WordleSolver; use this class's methods to solve the game
        :param cache: an optional WordleSolutionCache object to speed up game processing
        :param guess_file: the filepath as .txt holding the list of allowing guessable words
        :param answer_file: the filepath as .txt holding the list of possible hidden answers
        *Either a cache must be provided, or a guess & answer file must be provided*
        """
        if cache is None and guess_file == "":
            raise Exception("Please provide a WordleSolutionCache, or the filepath of a guess/answer file")
        self._cache = WordleSolutionCache(guess_file, answer_file) if cache is None else cache
        self._tree = self._cache.get_solution_tree()
        self._curr = self._tree  # the current location in the tree; start at the root
        self._next = None  # holds the next location in the tree; will be updated after a 'set_feedback()' call
        self._last_feedback = None  # the first feedback is 'None', otherwise it is last feedback like 'GGYYB'

    def reset_game(self):
        """Resets the game state"""
        self._curr = self._tree  # the current location in the tree; start at the root
        self._next = self._tree  # holds the next location in the tree; will updated after a 'set_feedback()' call
        self._last_feedback = None  # the first feedback is 'None', otherwise it is last feedback like 'GGYYB'

    def get_guess(self, new_game=False) -> str:
        """
        Traverses decision tree & returns the next optimal guess based on game state (prior guesses & feedbacks)
        :param new_game: True if we're starting a new game (resets game state); default is False (continuing a game)
        :return: the guess that should be made as a string
        """
        if new_game or len(self._curr) == 0 or self._last_feedback == "GGGGG":
            self.reset_game()
        guess, self._next = self._curr[self._last_feedback]
        return guess

    def set_feedback(self, feedback: str):
        """
        Updates the decision tree with the last feedback received by the user
        :param feedback: a 5-letter string like "GGYYB" -> G=Green, Y=Yellow, B=Black(grey)
        """
        if self._next is not None:  # ensure that a call to get_guess() preceded this
            self._last_feedback = feedback  # update the feedback
            self._curr = self._next  # iterate to the next branch in the tree

    def next_guess_is_winner(self):
        return len(self._next) == 0
