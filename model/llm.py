from typing import Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from transformers import pipeline
from config.config_files import APIkeys
from config.constants import Constants
from config.abstract_methods import LLMMethods
from helper.api_client import APIClient


class EmbeddingMapper:
    def __init__(self, model_name: str, index_name: str, metadata_key: str):
        self.model = SentenceTransformer(model_name)
        pc = Pinecone(api_key=APIkeys.pinecone_api_key)
        self.index = pc.Index(index_name)
        self.metadata_key = metadata_key
    
    def get(self, query: str) -> Optional[str]:
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=1,
            include_metadata=True
        )
        if results.matches:
            return results.matches[0].metadata.get(self.metadata_key)
        return None


class LLM(LLMMethods):
    """
    LLM Logic Only:
    1. Classifier → determines stock/crypto/weather
    2. RAG (Pinecone) → maps entity to ticker/city
    3. Response Generator → generates natural response
    
    API calls are handled by APIClient in helper/api_client.py
    """
    
    def __init__(self):
        # 1. Classifier (determines stock/crypto/weather)
        self.classifier = pipeline(
            Constants.CLASSIFIER_TASK,
            model=Constants.CLASSIFIER_MODEL
        )
        self.categories = Constants.CLASSIFIER_CATEGORIES
        
        # 2. RAG Mappers (Pinecone)
        self.stock_mapper = EmbeddingMapper(
            model_name=Constants.EMBEDDING_MODEL,
            index_name=Constants.STOCK_INDEX,
            metadata_key="ticker"
        )
        self.crypto_mapper = EmbeddingMapper(
            model_name=Constants.EMBEDDING_MODEL,
            index_name=Constants.CRYPTO_INDEX,
            metadata_key="ticker"
        )
        self.city_mapper = EmbeddingMapper(
            model_name=Constants.EMBEDDING_MODEL,
            index_name=Constants.CITY_INDEX,
            metadata_key="city"
        )
        
        # 3. Fine-tuned response generator
        self.response_generator = pipeline(
            "text2text-generation",
            model=Constants.RESPONSE_MODEL,
            token=APIkeys.hf_token,
            max_length=Constants.RESPONSE_MAX_LENGTH,
            do_sample=Constants.RESPONSE_DO_SAMPLE
        )
        
    def _classify_query(self, query: str) -> str:
        """Classify query as stock/crypto/weather with keyword heuristics."""
        result = self.classifier(query, candidate_labels=self.categories)
        label = result["labels"][0]

        # Heuristic: classifier often misclassifies crypto as stock
        # These keywords help route to the correct Pinecone index
        # RAG then handles the actual entity resolution
        lowered = query.lower()
        crypto_terms = [
            "bitcoin", "btc", "ethereum", "eth", "solana", "sol", 
            "dogecoin", "doge", "cardano", "ada", "ripple", "xrp",
            "binance", "bnb", "tron", "trx", "shiba", "shib",
            "polkadot", "dot", "avalanche", "avax", "chainlink", "link",
            "litecoin", "ltc", "polygon", "matic", "stellar", "xlm",
            "crypto", "cryptocurrency", "coin", "token"
        ]
        if any(term in lowered for term in crypto_terms):
            return "crypto"

        return label

    def _extract_entity_from_query(self, query: str) -> str:
        """Extract potential entity (ticker/name) from a query sentence."""
        import re
        words = query.split()
        
        # Look for potential tickers (2-6 uppercase letters)
        for word in words:
            clean = re.sub(r'[^A-Za-z]', '', word)
            if clean.isupper() and 2 <= len(clean) <= 6:
                return clean
        
        # Look for multi-word names (e.g., "Shiba Inu", "Binance Coin")
        # Return the query without common filler words
        filler = ['what', 'is', 'the', 'price', 'of', 'how', 'much', 'worth', 'current', 'right', 'now', 'trading', 'at']
        cleaned = ' '.join(w for w in words if w.lower() not in filler and not w.endswith('?'))
        return cleaned.strip() if cleaned.strip() else query

    def _get_entity(self, query: str, category: str) -> Optional[str]:
        """
        Get ticker/city from query using RAG (Pinecone).
        First extracts the entity from the query, then looks it up.
        """
        if category == "stock":
            lookup = self._extract_entity_from_query(query)
            return self.stock_mapper.get(lookup)
        elif category == "crypto":
            lookup = self._extract_entity_from_query(query)
            return self.crypto_mapper.get(lookup)
        elif category == "weather":
            return self.city_mapper.get(query)
        else:
            return None
    
    def _fetch_data(self, entity: Optional[str], category: str) -> Optional[str]:
        """Fetch data using API client (separated from LLM logic)."""
        if not entity:
            return None
        if category in ["stock", "crypto"]:
            is_crypto = (category == "crypto")
            return APIClient.get_financial_data(entity, is_crypto)
        elif category == "weather":
            return APIClient.get_weather_data(entity)
        return None
    
    def _generate_response(self, instruction: str, input_data: str) -> str:
        """
        Generate natural response using fine-tuned model.
        
        Uses the exact prompt format from training:
        "{instruction} | Values: {input}"
        
        Matches the format used during model fine-tuning.
        """
        full_prompt = Constants.RESPONSE_PROMPT_FORMAT.format(
            instruction=instruction,
            input=input_data
        )
        response = self.response_generator(full_prompt)
        return response[0]['generated_text'].strip()
    
    def generate(self, user_query: str, debug: bool = False) -> str:
        category = self._classify_query(user_query)
        if debug:
            print(f"  [1/4] Classified as: {category}")
        
        entity = self._get_entity(user_query, category)
        if entity is None:
            if debug:
                print("  [2/4] No entity resolved from query")
            return "Could not retrieve data for your request."
        
        if debug:
            print(f"  [2/4] Resolved entity: {entity}")
        
        input_data = self._fetch_data(entity, category)
        if input_data is None:
            if debug:
                print(f"  [3/4] Failed to fetch data for entity: {entity}")
            return f"Could not retrieve data for {entity}."

        # 4) Simple, deterministic templates for numeric data (skip LLM)
        if category in ["stock", "crypto"] and input_data.startswith("price="):
            try:
                price_str = input_data.split("=", 1)[1]
                price = float(price_str)
                if category == "stock":
                    response = f"The current price of {entity} is {price:.2f} USD."
                else:
                    response = f"The current price of {entity} is {price:.2f} USD."
                if debug:
                    print(f"  [4/4] Template response (numeric price)")
                return response
            except Exception:
                # Fall back to LLM if parsing fails for any reason
                pass

        # For weather or more complex cases, use the fine-tuned response model
        response = self._generate_response(user_query, input_data)
        if debug:
            print(f"  [✓] Generated response")
        
        return response