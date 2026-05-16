from app.models.lead import Lead


def score_lead(name: str, email: str | None, phone: str | None, interest: str | None) -> tuple[int, str]:
    score = 0
    if email:
        score += 20
    if phone:
        score += 20
    if interest:
        score += min(len(interest) // 10, 40)

    if score >= 60:
        return score, "hot"
    if score >= 35:
        return score, "warm"
    return score, "cold"


def update_lead_with_score(lead: Lead) -> Lead:
    score, status = score_lead(lead.name, lead.email, lead.phone, lead.interest)
    lead.score = score
    lead.status = status
    return lead
