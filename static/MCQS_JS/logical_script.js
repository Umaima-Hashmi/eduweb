// static/script.js
//LOGICAL_questions

// static/script.js
let questions = [];
let currentQuestionIndex = 0;
let score = 0;

document.addEventListener("DOMContentLoaded", () => {
  const questionElement = document.getElementById("question");
  const answerButtons = document.getElementById("answer-buttons");
  const nextButton = document.getElementById("next-btn");

  // Fetch questions from the server once
  fetch("/LOGICAL_questions")
    .then((response) => response.json())
    .then((data) => {
      questions = data;
      startQuiz();
    });

  function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    nextButton.innerHTML = "Next";
    nextButton.style.display = "none";
    showQuestion();
  }

  function showQuestion() {
    resetState();
    let currentQuestion = questions[currentQuestionIndex];
    questionElement.innerHTML = `${currentQuestionIndex + 1}. ${
      currentQuestion.question
    }`;

    currentQuestion.answers.forEach((answer) => {
      const button = document.createElement("button");
      button.innerHTML = answer.text;
      button.classList.add("btn");
      answerButtons.appendChild(button);
      button.addEventListener("click", () =>
        selectAnswer(button, currentQuestion)
      );
    });
  }

  function resetState() {
    nextButton.style.display = "none";
    while (answerButtons.firstChild) {
      answerButtons.removeChild(answerButtons.firstChild);
    }
  }

  function selectAnswer(button, question) {
    const isCorrect = question.answers.find(
      (answer) => answer.text === button.innerHTML
    ).correct;
    if (isCorrect) {
      button.classList.add("correct");
      score++;
    } else {
      button.classList.add("incorrect");
    }
    Array.from(answerButtons.children).forEach((btn) => {
      const answer = question.answers.find(
        (answer) => answer.text === btn.innerHTML
      );
      if (answer.correct) {
        btn.classList.add("correct");
      }
      btn.disabled = true;
    });
    nextButton.style.display = "block";
  }

  nextButton.addEventListener("click", () => {
    if (nextButton.innerHTML === "Attempt again!") {
      startQuiz();
    } else {
      currentQuestionIndex++;
      if (currentQuestionIndex < questions.length) {
        showQuestion();
      } else {
        showScore();
      }
    }
  });

  function showScore() {
    resetState();
    questionElement.innerHTML = `You scored ${score} out of ${questions.length}!`;
    nextButton.innerHTML = "Attempt again!";
    nextButton.style.display = "block";

    // Send the Physics score to the server
    fetch("/save_logical_score", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ score: score }), // Send the Physics score
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.error) {
          console.error("Error saving score:", data.error);
        } else {
          console.log("Score saved successfully:", data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});
