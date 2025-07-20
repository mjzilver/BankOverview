def format_month(period_str):
    year, month = period_str.split("-")
    dutch_months = [
        "Alle maanden",
        "januari",
        "februari",
        "maart",
        "april",
        "mei",
        "juni",
        "juli",
        "augustus",
        "september",
        "oktober",
        "november",
        "december",
    ]
    return f"{dutch_months[int(month)]} {year}"
