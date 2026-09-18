def required_fields(data, fields):
    missing = []

    for field in fields:
        if data.get(field) in (None, ""):
            missing.append(field)

    return missing


def positive_number(value):
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False