# PL Trivia - Premier League Quiz Game
# Flask application

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import random
from datetime import datetime

app = Flask(__name__)

# File paths
QUESTIONS_FILE = "data/questions.json"
SCORES_FILE = "data/scores.json"


# =============================================================================
# DATA FUNCTIONS
# =============================================================================

def load_questions():
    """Load all questions from file"""
    try:
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def load_scores():
    """Load all scores from file"""
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_score(name, score, date):
    """Save a new score"""
    scores = load_scores()
    scores.append({
        "name": name,
        "date": date,
        "score": score,
        "time": datetime.now().isoformat()
    })
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def get_daily_questions(date_str):
    """Get 10 questions for a specific date (same for everyone)"""
    questions = load_questions()
    if len(questions) < 10:
        return questions

    # Use date as seed for consistent daily selection
    seed = int(date_str.replace("-", ""))
    random.seed(seed)
    daily = random.sample(questions, 10)
    random.seed()  # Reset seed
    return daily


def get_daily_leaderboard(date_str):
    """Get leaderboard for a specific date"""
    scores = load_scores()
    daily_scores = [s for s in scores if s["date"] == date_str]
    # Sort by score descending, then by time ascending
    daily_scores.sort(key=lambda x: (-x["score"], x["time"]))
    return daily_scores


def get_alltime_leaderboard():
    """Get all-time leaderboard (best score per player)"""
    scores = load_scores()

    # Get best score per player
    best_scores = {}
    for s in scores:
        name = s["name"]
        if name not in best_scores or s["score"] > best_scores[name]["score"]:
            best_scores[name] = s

    # Sort by score descending
    leaderboard = sorted(best_scores.values(), key=lambda x: -x["score"])
    return leaderboard


# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def index():
    """Home page - enter name to start"""
    return render_template("index.html")


@app.route("/play")
def play():
    """Start the game"""
    name = request.args.get("name", "").strip()
    if not name:
        return redirect(url_for("index"))

    today = datetime.now().strftime("%Y-%m-%d")
    questions = get_daily_questions(today)

    return render_template("game.html",
                         name=name,
                         questions=questions,
                         date=today)


@app.route("/submit", methods=["POST"])
def submit():
    """Submit game results"""
    data = request.get_json()
    name = data.get("name", "").strip()
    score = data.get("score", 0)
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    if name:
        save_score(name, score, date)

    return jsonify({"success": True})


@app.route("/results")
def results():
    """Show results and leaderboard"""
    name = request.args.get("name", "")
    score = int(request.args.get("score", 0))
    today = datetime.now().strftime("%Y-%m-%d")

    daily_lb = get_daily_leaderboard(today)
    alltime_lb = get_alltime_leaderboard()

    # Find player's rank
    daily_rank = None
    for i, s in enumerate(daily_lb):
        if s["name"] == name:
            daily_rank = i + 1
            break

    return render_template("results.html",
                         name=name,
                         score=score,
                         daily_rank=daily_rank,
                         daily_leaderboard=daily_lb[:10],
                         alltime_leaderboard=alltime_lb[:10],
                         date=today)


@app.route("/leaderboard")
def leaderboard():
    """Full leaderboard view"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_lb = get_daily_leaderboard(today)
    alltime_lb = get_alltime_leaderboard()

    return render_template("results.html",
                         name=None,
                         score=None,
                         daily_rank=None,
                         daily_leaderboard=daily_lb,
                         alltime_leaderboard=alltime_lb,
                         date=today)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route("/api/questions")
def api_questions():
    """Get today's questions (for AJAX)"""
    today = datetime.now().strftime("%Y-%m-%d")
    questions = get_daily_questions(today)
    # Don't send correct answers to client
    safe_questions = []
    for q in questions:
        safe_questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    return jsonify(safe_questions)


@app.route("/api/check", methods=["POST"])
def api_check():
    """Check if answer is correct"""
    data = request.get_json()
    question_id = data.get("id")
    answer = data.get("answer")

    questions = load_questions()
    for q in questions:
        if q["id"] == question_id:
            correct = q["correct"] == answer
            return jsonify({
                "correct": correct,
                "correct_answer": q["correct"]
            })

    return jsonify({"error": "Question not found"}), 404


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)
