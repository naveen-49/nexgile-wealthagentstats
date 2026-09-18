def get_risk_category(score):

    if score <= 30:
        return "CONSERVATIVE"

    if score <= 60:
        return "MODERATE"

    return "AGGRESSIVE"


def calculate_risk_score(answers):

    score = 0

    for answer in answers:
        score += int(answer)

    score = min(score, 100)

    return score, get_risk_category(score)