from typing import List, ClassVar


class Constants:
    """Configuration constants for the application."""
    
    # API URLs
    WEATHER_URL: ClassVar[str] = (
        "http://api.openweathermap.org/data/2.5/weather?appid={api_key}"
        "&q={location}&units=metric"
    )
    
    # Classifier configuration
    CLASSIFIER_TASK: ClassVar[str] = "zero-shot-classification"
    CLASSIFIER_MODEL: ClassVar[str] = "facebook/bart-large-mnli"
    CLASSIFIER_CATEGORIES: ClassVar[List[str]] = ["crypto", "stock", "weather"]
    
    # Embedding model configuration
    EMBEDDING_MODEL: ClassVar[str] = "all-MiniLM-L6-v2"
    
    # Pinecone index names
    STOCK_INDEX: ClassVar[str] = "stock-index"
    CRYPTO_INDEX: ClassVar[str] = "crypto-index"
    CITY_INDEX: ClassVar[str] = "city-index"
    
    # Response generator configuration
    RESPONSE_MODEL: ClassVar[str] = "Mozes721/crypto-stock-weather-agent"
    RESPONSE_MAX_LENGTH: ClassVar[int] = 256
    RESPONSE_DO_SAMPLE: ClassVar[bool] = False
    # Prompt format - matches training format exactly
    RESPONSE_PROMPT_FORMAT: ClassVar[str] = "{instruction} | Values: {input}"
    
    # API retry configuration
    MAX_RETRIES: ClassVar[int] = 3
    RETRY_DELAY: ClassVar[int] = 2
    RETRY_BACKOFF: ClassVar[float] = 2.0