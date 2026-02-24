from app.models import PriorityLevel, Domain

def calculate_priority(token, queue):
    if token.domain == Domain.HEALTHCARE:
        if token.severity_score and token.severity_score >= 8:
            return PriorityLevel.EMERGENCY
        if token.user.is_senior_citizen:
            return PriorityLevel.HIGH

    if token.domain == Domain.BANKING:
        if token.user.is_vip:
            return PriorityLevel.HIGH
        if token.user.is_senior_citizen:
            return PriorityLevel.MEDIUM

    return PriorityLevel.NORMAL
