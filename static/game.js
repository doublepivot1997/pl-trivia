// PL Trivia - Game Logic

let currentQuestion = 0;
let score = 0;
let timeLeft = 20;
let timerInterval = null;
let extendUsed = false;
let answered = false;

const TIMER_CIRCUMFERENCE = 283; // 2 * PI * 45

// DOM Elements
const questionText = document.getElementById('question-text');
const optionsContainer = document.getElementById('options');
const timerText = document.getElementById('timer');
const timerCircle = document.getElementById('timer-circle');
const currentDisplay = document.getElementById('current');
const extendBtn = document.getElementById('extend-btn');
const nextBtn = document.getElementById('next-btn');
const gameContainer = document.getElementById('game');
const gameOverContainer = document.getElementById('game-over');
const finalScoreDisplay = document.getElementById('final-score');

// Initialize game
function init() {
    loadQuestion();
    startTimer();

    extendBtn.addEventListener('click', handleExtend);
    nextBtn.addEventListener('click', nextQuestion);
}

// Load current question
function loadQuestion() {
    const q = QUESTIONS[currentQuestion];
    questionText.textContent = q.question;
    currentDisplay.textContent = currentQuestion + 1;

    optionsContainer.innerHTML = '';
    q.options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'option';
        btn.textContent = option;
        btn.addEventListener('click', () => handleAnswer(index));
        optionsContainer.appendChild(btn);
    });

    answered = false;
    nextBtn.classList.add('hidden');
    timeLeft = 20;
    updateTimerDisplay();
}

// Start countdown timer
function startTimer() {
    if (timerInterval) clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            handleTimeout();
        }
    }, 1000);
}

// Update timer visual
function updateTimerDisplay() {
    timerText.textContent = timeLeft;

    // Calculate progress (full circle = 283)
    const maxTime = extendUsed && timeLeft > 20 ? 50 : 20;
    const progress = (timeLeft / maxTime) * TIMER_CIRCUMFERENCE;
    timerCircle.style.strokeDashoffset = TIMER_CIRCUMFERENCE - progress;

    // Color warnings
    timerCircle.classList.remove('warning', 'danger');
    if (timeLeft <= 5) {
        timerCircle.classList.add('danger');
    } else if (timeLeft <= 10) {
        timerCircle.classList.add('warning');
    }
}

// Handle answer selection
function handleAnswer(selectedIndex) {
    if (answered) return;
    answered = true;
    clearInterval(timerInterval);

    const q = QUESTIONS[currentQuestion];
    const options = optionsContainer.querySelectorAll('.option');

    // Disable all options
    options.forEach(opt => opt.disabled = true);

    // Mark selected answer
    options[selectedIndex].classList.add('selected');

    // Check answer
    if (selectedIndex === q.correct) {
        options[selectedIndex].classList.remove('selected');
        options[selectedIndex].classList.add('correct');
        score++;
    } else {
        options[selectedIndex].classList.add('wrong');
        // Show correct answer
        options[q.correct].classList.add('reveal-correct');
    }

    // Show next button
    nextBtn.classList.remove('hidden');
}

// Handle timeout (no answer)
function handleTimeout() {
    if (answered) return;
    answered = true;

    const q = QUESTIONS[currentQuestion];
    const options = optionsContainer.querySelectorAll('.option');

    // Disable all options
    options.forEach(opt => opt.disabled = true);

    // Show correct answer
    options[q.correct].classList.add('reveal-correct');

    // Show next button
    nextBtn.classList.remove('hidden');
}

// Handle extend button
function handleExtend() {
    if (extendUsed || answered) return;

    extendUsed = true;
    timeLeft += 30;
    extendBtn.classList.add('used');
    extendBtn.disabled = true;
    updateTimerDisplay();
}

// Go to next question
function nextQuestion() {
    currentQuestion++;

    if (currentQuestion >= QUESTIONS.length) {
        endGame();
    } else {
        loadQuestion();
        startTimer();
    }
}

// End game and submit score
function endGame() {
    clearInterval(timerInterval);

    gameContainer.classList.add('hidden');
    gameOverContainer.classList.remove('hidden');
    finalScoreDisplay.textContent = score;

    // Submit score to server
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: PLAYER_NAME,
            score: score,
            date: GAME_DATE
        })
    })
    .then(response => response.json())
    .then(data => {
        // Redirect to results
        window.location.href = `/results?name=${encodeURIComponent(PLAYER_NAME)}&score=${score}`;
    })
    .catch(error => {
        console.error('Error submitting score:', error);
        // Still redirect even on error
        window.location.href = `/results?name=${encodeURIComponent(PLAYER_NAME)}&score=${score}`;
    });
}

// Start the game when page loads
document.addEventListener('DOMContentLoaded', init);
