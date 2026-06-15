// TNPSC AI Hub - Frontend JavaScript

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initBookmarks();
    initQuiz();
});

/* ==========================================
   1. Theme Management (Dark / Light Mode)
   ========================================== */
function initTheme() {
    const themeToggler = document.getElementById('themeToggler');
    const themeIcon = document.getElementById('themeIcon');
    if (!themeToggler) return;

    // Get theme from local storage or system default
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggler.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    if (!themeIcon) return;
    if (theme === 'dark') {
        themeIcon.className = 'bi bi-sun-fill text-warning';
    } else {
        themeIcon.className = 'bi bi-moon-stars-fill text-primary';
    }
}

/* ==========================================
   2. Bookmarking System (AJAX)
   ========================================== */
function initBookmarks() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const newsId = btn.getAttribute('data-news-id');
            const icon = btn.querySelector('i');
            
            try {
                const response = await fetch(`/bookmarks/toggle/${newsId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.is_bookmarked) {
                        icon.className = 'bi bi-bookmark-fill text-warning';
                        showToast('Article Bookmarked');
                    } else {
                        icon.className = 'bi bi-bookmark text-muted';
                        showToast('Bookmark Removed');
                    }
                }
            } catch (error) {
                console.error('Bookmark toggle failed:', error);
            }
        });
    });
}

// Simple dynamic Toast notification
function showToast(message) {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }
    
    const toastHtml = `
        <div class="toast align-items-center text-bg-primary border-0 show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="2000">
            <div class="d-flex">
                <div class="toast-body fw-medium">
                    <i class="bi bi-info-circle-fill me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    const toastWrapper = document.createElement('div');
    toastWrapper.innerHTML = toastHtml;
    const toastEl = toastWrapper.firstElementChild;
    toastContainer.appendChild(toastEl);
    
    setTimeout(() => {
        toastEl.classList.remove('show');
        setTimeout(() => toastEl.remove(), 500);
    }, 2500);
}

/* ==========================================
   3. Interactive Quiz Engine
   ========================================== */
let quizQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let selectedCategory = 'All';
let questionCount = 10;
let userAnswers = []; // to track correctness

function initQuiz() {
    const startBtn = document.getElementById('startQuizBtn');
    if (!startBtn) return;

    startBtn.addEventListener('click', startQuiz);
}

async function startQuiz() {
    const categorySelect = document.getElementById('quizCategory');
    const countSelect = document.getElementById('quizCount');
    
    selectedCategory = categorySelect.value;
    questionCount = parseInt(countSelect.value);

    // Show Loading
    document.getElementById('quizSetup').classList.add('d-none');
    const quizPlay = document.getElementById('quizPlay');
    quizPlay.classList.remove('d-none');
    quizPlay.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-muted">Fetching MCQs...</p>
        </div>
    `;

    try {
        const res = await fetch(`/quiz/questions/?category=${selectedCategory}&count=${questionCount}`);
        const data = await res.json();
        quizQuestions = data.questions;

        if (quizQuestions.length === 0) {
            quizPlay.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-emoji-frown text-danger display-4"></i>
                    <h4 class="mt-3">No MCQs Available</h4>
                    <p class="text-muted">There are no generated MCQs for the selected category yet.</p>
                    <button class="btn btn-primary btn-sm mt-3" onclick="location.reload()">Go Back</button>
                </div>
            `;
            return;
        }

        // Initialize state
        currentQuestionIndex = 0;
        score = 0;
        userAnswers = [];
        showQuestion();
    } catch (err) {
        console.error(err);
        quizPlay.innerHTML = `<p class="text-danger text-center">Failed to load quiz. Please try again.</p>`;
    }
}

function showQuestion() {
    const q = quizQuestions[currentQuestionIndex];
    const quizPlay = document.getElementById('quizPlay');
    
    let progressPct = ((currentQuestionIndex) / quizQuestions.length) * 100;
    
    let optionsHtml = '';
    for (const [key, value] of Object.entries(q.options)) {
        optionsHtml += `
            <div class="quiz-option-card card p-3 mb-2 border rounded cursor-pointer" data-option="${key}">
                <div class="d-flex align-items-center gap-3">
                    <span class="badge bg-secondary rounded-circle px-2 py-2">${key}</span>
                    <span class="fw-medium">${value}</span>
                </div>
            </div>
        `;
    }

    quizPlay.innerHTML = `
        <div class="card shadow-sm animate-fade-in">
            <div class="card-header bg-body-secondary py-3 d-flex justify-content-between align-items-center">
                <span class="badge bg-primary">${q.category}</span>
                <span class="text-muted small fw-bold">Question ${currentQuestionIndex + 1} of ${quizQuestions.length}</span>
            </div>
            
            <div class="progress" style="height: 4px; border-radius: 0;">
                <div class="progress-bar bg-primary" role="progressbar" style="width: ${progressPct}%"></div>
            </div>

            <div class="card-body p-4">
                <h5 class="card-title fw-bold mb-4">${q.question}</h5>
                <div class="options-container mb-4">
                    ${optionsHtml}
                </div>
                
                <!-- Feedback Box -->
                <div id="quizFeedback" class="d-none alert p-3 mb-4 rounded border"></div>

                <div class="d-flex justify-content-between">
                    <button class="btn btn-outline-secondary" onclick="location.reload()"><i class="bi bi-x-circle"></i> Quit</button>
                    <button id="submitAnswerBtn" class="btn btn-primary" disabled>Submit Answer</button>
                </div>
            </div>
        </div>
    `;

    // Add option select listener
    let selectedOption = null;
    const optionCards = quizPlay.querySelectorAll('.quiz-option-card');
    
    optionCards.forEach(card => {
        card.addEventListener('click', () => {
            if (document.getElementById('submitAnswerBtn').innerText === 'Next Question' || 
                document.getElementById('submitAnswerBtn').innerText === 'Finish Quiz') {
                return; // answer already checked
            }
            
            optionCards.forEach(c => c.classList.remove('border-primary', 'bg-body-secondary'));
            card.classList.add('border-primary', 'bg-body-secondary');
            selectedOption = card.getAttribute('data-option');
            document.getElementById('submitAnswerBtn').removeAttribute('disabled');
        });
    });

    // Submit listener
    document.getElementById('submitAnswerBtn').addEventListener('click', () => {
        const btn = document.getElementById('submitAnswerBtn');
        
        if (btn.innerText === 'Submit Answer') {
            checkAnswer(selectedOption, q);
        } else if (btn.innerText === 'Next Question') {
            currentQuestionIndex++;
            showQuestion();
        } else if (btn.innerText === 'Finish Quiz') {
            finishQuiz();
        }
    });
}

function checkAnswer(selected, q) {
    const feedback = document.getElementById('quizFeedback');
    const btn = document.getElementById('submitAnswerBtn');
    const isCorrect = selected === q.answer;
    
    if (isCorrect) score++;
    userAnswers.push(isCorrect);

    // Style option cards
    const optionCards = document.querySelectorAll('.quiz-option-card');
    optionCards.forEach(card => {
        const opt = card.getAttribute('data-option');
        if (opt === q.answer) {
            card.classList.add('border-success', 'bg-success-subtle');
        } else if (opt === selected && !isCorrect) {
            card.classList.add('border-danger', 'bg-danger-subtle');
        }
    });

    feedback.className = `alert p-3 mb-4 rounded border ${isCorrect ? 'alert-success border-success' : 'alert-danger border-danger'} animate-fade-in`;
    feedback.innerHTML = `
        <div class="d-flex align-items-start gap-2">
            <i class="bi ${isCorrect ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'} fs-4"></i>
            <div>
                <h6 class="fw-bold mb-1">${isCorrect ? 'Correct!' : 'Incorrect'}</h6>
                <p class="mb-2 text-muted small">${q.explanation}</p>
                <a href="${q.url}" target="_blank" class="small text-decoration-none"><i class="bi bi-link-45deg"></i> Read full study article</a>
            </div>
        </div>
    `;
    feedback.classList.remove('d-none');

    // Update Action Button
    if (currentQuestionIndex < quizQuestions.length - 1) {
        btn.innerText = 'Next Question';
    } else {
        btn.innerText = 'Finish Quiz';
    }
}

async function finishQuiz() {
    const quizPlay = document.getElementById('quizPlay');
    quizPlay.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-muted">Compiling final score...</p>
        </div>
    `;

    const questionIds = quizQuestions.map(q => q.id);
    
    // Post quiz statistics to server
    try {
        await fetch('/quiz/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify({
                category: selectedCategory,
                total: quizQuestions.length,
                correct: score,
                question_ids: questionIds
            })
        });
    } catch (e) {
        console.error('Failed to submit score:', e);
    }

    // Render results view
    const pct = Math.round((score / quizQuestions.length) * 100);
    let gradeMsg = '';
    let gradeIcon = '';
    
    if (pct >= 80) {
        gradeMsg = 'Excellent! You are on the right track for TNPSC Group 2!';
        gradeIcon = 'bi-trophy-fill text-warning';
    } else if (pct >= 50) {
        gradeMsg = 'Good effort! A bit more revision and you will score higher.';
        gradeIcon = 'bi-award-fill text-primary';
    } else {
        gradeMsg = 'Keep reading daily current affairs. Consistency is key.';
        gradeIcon = 'bi-book-half text-danger';
    }

    quizPlay.innerHTML = `
        <div class="card shadow border-0 text-center p-5 animate-fade-in">
            <div class="card-body">
                <i class="bi ${gradeIcon} display-1 mb-4"></i>
                <h2 class="fw-bold">Quiz Finished!</h2>
                <p class="text-muted fs-5 mb-4">${gradeMsg}</p>
                
                <div class="d-inline-block p-4 bg-body-tertiary rounded-4 border mb-4">
                    <h1 class="display-3 fw-extrabold text-primary mb-0">${score} / ${quizQuestions.length}</h1>
                    <span class="text-muted small fw-bold">Accuracy: ${pct}%</span>
                </div>
                
                <div class="d-flex justify-content-center gap-3">
                    <button class="btn btn-primary" onclick="location.reload()"><i class="bi bi-arrow-repeat"></i> Play Again</button>
                    <a class="btn btn-outline-secondary" href="/"><i class="bi bi-house"></i> Home</a>
                </div>
            </div>
        </div>
    `;
}
