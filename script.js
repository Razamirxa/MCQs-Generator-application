document.addEventListener('DOMContentLoaded', () => {
    const generateQuizBtn = document.getElementById('generate-quiz');
    const submitQuizBtn = document.getElementById('submit-quiz');
    const quizForm = document.getElementById('quiz-form');
    const quizContainer = document.getElementById('quiz-container');
    const resultsContainer = document.getElementById('results-container');
    const questionsContainer = document.getElementById('questions');
    const questionResults = document.getElementById('question-results');
    const scoreElement = document.getElementById('score');
    const loadingElement = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const videoUrlInput = document.getElementById('video-url');
    const numQuestionsInput = document.getElementById('num-questions');

    let quiz = null;

    generateQuizBtn.addEventListener('click', generateQuiz);
    videoUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            generateQuiz();
        }
    });

    async function generateQuiz() {
        const videoUrl = videoUrlInput.value.trim();
        const numQuestions = parseInt(numQuestionsInput.value);

        // Validate input
        if (!videoUrl) {
            showError('Please enter a YouTube video URL.');
            return;
        }

        if (isNaN(numQuestions) || numQuestions < 1 || numQuestions > 20) {
            showError('Please enter a number of questions between 1 and 20.');
            return;
        }

        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('loading-text').textContent = 'Generating quiz...';

        fetch('/generate_quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ video_url: videoUrl, num_questions: numQuestions }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                quiz = data.questions;  // Store the quiz questions globally
                displayQuiz(quiz);
                displayTranscription(data.transcription);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while generating the quiz. Please try again.');
        })
        .finally(() => {
            document.getElementById('loading').classList.add('hidden');
        });
    }

    function displayQuiz(questions) {
        questionsContainer.innerHTML = '';
        questions.forEach((question, index) => {
            const questionElement = document.createElement('div');
            questionElement.classList.add('question');
            questionElement.innerHTML = `
                <h3>Question ${index + 1}: ${question.question}</h3>
                <ul class="options">
                    ${question.options.map((option, optionIndex) => `
                        <li>
                            <input type="radio" name="q${index}" value="${option}" id="q${index}o${optionIndex}" required>
                            <label for="q${index}o${optionIndex}">${option}</label>
                        </li>
                    `).join('')}
                </ul>
            `;
            questionsContainer.appendChild(questionElement);
        });

        quizForm.classList.add('hidden');
        quizContainer.classList.remove('hidden');
    }

    function displayTranscription(transcription) {
        const transcriptionContainer = document.getElementById('transcription-container');
        const transcriptionText = document.getElementById('transcription-text');
        const toggleButton = document.getElementById('toggle-transcription');

        transcriptionText.textContent = transcription;
        transcriptionContainer.classList.remove('hidden');

        toggleButton.addEventListener('click', () => {
            const transcriptionContent = document.getElementById('transcription-content');
            transcriptionContent.classList.toggle('hidden');
        });
    }

    submitQuizBtn.addEventListener('click', submitQuiz);

    function submitQuiz() {
        if (!quiz) {
            showError('No quiz has been generated yet.');
            return;
        }

        const userAnswers = [];
        let allAnswered = true;

        quiz.forEach((question, index) => {
            const selectedOption = document.querySelector(`input[name="q${index}"]:checked`);
            if (selectedOption) {
                userAnswers.push(selectedOption.value);
            } else {
                allAnswered = false;
            }
        });

        if (!allAnswered) {
            showError('Please answer all questions before submitting.');
            return;
        }

        displayResults(userAnswers);
    }

    function displayResults(userAnswers) {
        let score = 0;
        questionResults.innerHTML = '';

        quiz.forEach((question, index) => {
            const userAnswer = userAnswers[index];
            const isCorrect = userAnswer === question.correct_answer;
            if (isCorrect) score++;

            const resultElement = document.createElement('div');
            resultElement.classList.add('result');
            resultElement.innerHTML = `
                <h4>Question ${index + 1}: ${question.question}</h4>
                <p>Your answer: ${userAnswer}</p>
                <p>Correct answer: ${question.correct_answer}</p>
                <p class="${isCorrect ? 'correct' : 'incorrect'}">${isCorrect ? 'Correct!' : 'Incorrect'}</p>
            `;
            questionResults.appendChild(resultElement);
        });

        scoreElement.textContent = `Your Score: ${score}/${quiz.length}`;
        quizContainer.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        // Add home button
        const homeButton = document.createElement('button');
        homeButton.textContent = 'Back to Home';
        homeButton.addEventListener('click', () => {
            location.reload(); // Reload the page to start over
        });
        resultsContainer.appendChild(homeButton);
    }

    function showLoading(message) {
        loadingText.textContent = message;
        loadingElement.classList.remove('hidden');
    }

    function hideLoading() {
        loadingElement.classList.add('hidden');
    }

    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.classList.add('error-message');
        errorElement.textContent = message;
        
        // Remove any existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        quizForm.insertBefore(errorElement, generateQuizBtn);

        setTimeout(() => {
            errorElement.remove();
        }, 5000); // Remove the error message after 5 seconds
    }

    // Update the number input attributes
    numQuestionsInput.setAttribute('min', '1');
    numQuestionsInput.setAttribute('max', '20');
    numQuestionsInput.setAttribute('value', '5');
});