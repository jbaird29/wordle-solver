// Helper method; returns true if the feedback is valid, 5-letter sequence; else false
const isValidFeedback = (feedback) => {
    if(feedback.length !== 5) return false;
    for (let c of feedback) {
        if (c !== 'G' && c !== 'Y' && c !== 'B') {
            return false;
        }
    }
    return true;
}


// The interface for solving the game; methods to traverse decision tree & return next guess
class WordleSolver {
    #tree; #curr; #next; #lastFeedback
    constructor(decisionTree) {
        this.#tree = decisionTree;  // the solution decision tree
        this.#curr = this.#tree;  // the current node in the tree
        this.#next = null;  // the next node in the tree to be traversed to
        this.#lastFeedback = "root";  // the last feedback that was entered
    }

    getGuess() {
        const [guess, next] = this.#curr[this.#lastFeedback] ?? [null, null];
        this.#next = next;
        return guess;
    }

    setFeedback(feedback) {
        if(this.#next !== null) {
            this.#lastFeedback = feedback;
            this.#curr = this.#next;
        }
    }

    next_guess_is_winner() {
        return Object.keys(this.#next).length === 0;
    }

    resetGame() {
        this.#curr = this.#tree;  // the current node in the tree
        this.#next = null;  // the next node in the tree to be traversed to
        this.#lastFeedback = "root";  // the last feedback that was entered
    }
}


// The interface to update the DOM based on user actions
class WordleSolverPage {
    #guessDOM; #formDOM; #submitDOM; #feedbackDOM; #guessHeaderDOM; #resetBtnDOM
    constructor(decisionTree) {
        this.solver = new WordleSolver(decisionTree)
        this.#guessDOM = document.getElementById("guess");
        this.#guessHeaderDOM = document.getElementById("guess-header")
        this.#submitDOM = document.getElementById("submit");
        this.#feedbackDOM = document.getElementById("feedback");
        this.#formDOM = document.getElementById("feedback-form");
        this.#resetBtnDOM = document.getElementById("reset-game");
        this.#updateGuess(this.solver.getGuess())  // display the starting word as the first guess
        this.#updateGuessHeader("The optimal next guess is:");
        this.#addEventListeners()
    }

    #updateGuessHeader(text) {
        this.#guessHeaderDOM.innerText = text
    }

    #updateGuess(guess) {
        this.#guessDOM.innerText = guess
    }

    #clearFeedback() {
        this.#feedbackDOM.value = ""
    }

    #hideShowFeedbackForm(shouldHide) {
        this.#formDOM.style.display = shouldHide ? "none" : "block";
    }

    #displayGameWon() {
        this.#updateGuessHeader("Congratulations! We've won the game!");
        this.#updateGuess("");
        this.#clearFeedback();
        this.#hideShowFeedbackForm(true);
    }

    #addEventListeners() {
        this.#submitDOM.addEventListener("click", (e) => this.#feedbackUpdateEventListener(e));
        this.#resetBtnDOM.addEventListener("click", (e) => this.#resetGameEventListener(e));
    }

    #feedbackUpdateEventListener(event) {
        event.preventDefault()
        const feedback = this.#feedbackDOM.value
        // Ensure feedback was entered validly
        if(!isValidFeedback(feedback)) {
            this.#updateGuessHeader("Error: feedback was entered incorrectly.");
            this.#clearFeedback()
            return
        }
        // Check for game won condition
        if(feedback === "GGGGG") {
            this.#displayGameWon();
            return
        }
        // Otherwise update game state with that feedback
        this.solver.setFeedback(feedback)
        const guess = this.solver.getGuess()
        if(guess === null) {
            this.#updateGuessHeader("Error: we've reached an invalid state. You must've " +
                "entered feedback incorrectly. Try re-inputting it or resetting the game.");
            this.#clearFeedback();
            return
        }
        if(this.solver.next_guess_is_winner()) {
            this.#updateGuessHeader("Congratulations! The next guess will be the winner!");
        } else {
            this.#updateGuessHeader("The optimal next guess is:");
        }
        this.#updateGuess(guess)  // display the starting word as the first guess
        this.#clearFeedback()
    }

    #resetGameEventListener(event) {
        event.preventDefault();
        this.solver.resetGame();
        this.#updateGuess(this.solver.getGuess());
        this.#hideShowFeedbackForm(false);
        this.#clearFeedback();
        this.#updateGuessHeader("The optimal next guess is:");
    }
}


// Loads the decision tree JSON
const loadJSON = async () => {
    const response = await fetch("decision_tree_cache.json");
    return await response.json()
}


const main = async () => {
    const decisionTree = await loadJSON()
    new WordleSolverPage(decisionTree)
}

main()