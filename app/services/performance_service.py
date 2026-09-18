from app.services.portfolio_service import calculate_portfolio_value


def calculate_portfolio_performance(portfolio):
    current_value = calculate_portfolio_value(portfolio)

    total_cost = 0

    for holding in portfolio.holdings:
        total_cost += float(
            holding.quantity * holding.average_cost
        )

    gain_loss = current_value - total_cost

    if total_cost > 0:
        return_percentage = (
            gain_loss / total_cost
        ) * 100
    else:
        return_percentage = 0

    return {
        "current_value": round(current_value, 2),
        "total_cost": round(total_cost, 2),
        "gain_loss": round(gain_loss, 2),
        "return_percentage": round(
            return_percentage,
            2
        )
    }