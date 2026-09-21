
import yfinance as yf


def get_stock_price(symbol):
    """
    Fetch the latest available stock price.
    Example: RELIANCE -> RELIANCE.NS
    """

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"

    try:
        stock = yf.Ticker(symbol)

        price = stock.fast_info["last_price"]

        if price is None:
            raise ValueError(
                "Stock price is not available"
            )

        return float(price)

    except Exception as error:
        raise ValueError(
            f"Unable to fetch stock price: {str(error)}"
        )