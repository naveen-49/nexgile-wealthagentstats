from app.models import Portfolio


def calculate_holding_value(holding):
    return float(holding.quantity * holding.current_price)


def calculate_portfolio_value(portfolio):
    total = 0

    for holding in portfolio.holdings:
        total += calculate_holding_value(holding)

    return total


def calculate_portfolio_allocation(portfolio):
    total_value = calculate_portfolio_value(portfolio)

    if total_value == 0:
        return []

    result = []

    for holding in portfolio.holdings:
        value = calculate_holding_value(holding)

        percentage = (value / total_value) * 100

        result.append({
            "symbol": holding.symbol,
            "value": value,
            "allocation_percentage": round(percentage, 2)
        })

    return result