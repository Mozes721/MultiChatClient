import re

def extract_raw_ticker(query: str) -> list[str]:
    ticker_pattern = re.compile(r'\b[A-Z]{2,6}\b')
    return ticker_pattern.findall(query)
