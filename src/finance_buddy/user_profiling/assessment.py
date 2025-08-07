from typing import List, Dict, Any

QUESTIONS = [
    {
        "id": "q1",
        "text": "When you think about investing, what comes to mind first?",
        "options": [
            {"text": "The potential for high returns, even if it means taking on significant risk.", "score": 3},
            {"text": "A balance between reasonable growth and keeping my initial investment safe.", "score": 2},
            {"text": "The importance of preserving my capital, even if it means lower returns.", "score": 1}
        ]
    },
    {
        "id": "q2",
        "text": "Imagine the stock market drops 20% in a month. How would you react to your portfolio?",
        "options": [
            {"text": "See it as a buying opportunity and invest more.", "score": 3},
            {"text": "Feel nervous but hold my positions, trusting in a long-term recovery.", "score": 2},
            {"text": "Sell some or all of my investments to prevent further losses.", "score": 1}
        ]
    },
    {
        "id": "q3",
        "text": "What is your primary goal for your investments?",
        "options": [
            {"text": "Aggressive growth for long-term goals like early retirement.", "score": 3},
            {"text": "Moderate growth to build wealth over time.", "score": 2},
            {"text": "Generating a stable income or preserving wealth.", "score": 1}
        ]
    }
]

def get_risk_assessment_questions() -> List[Dict[str, Any]]:
    """
    Returns the list of questions for the risk assessment.
    """
    return QUESTIONS

def assess_risk_tolerance(answers: Dict[str, int]) -> str:
    """
    Assesses risk tolerance based on a dictionary of answers.
    The answers should be a dictionary mapping question_id to the chosen option's score.

    Example: {'q1': 3, 'q2': 2, 'q3': 1}
    """
    total_score = sum(answers.values())

    if total_score <= 4:
        return 'low'
    elif total_score <= 7:
        return 'medium'
    else:
        return 'high'
