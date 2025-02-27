from pydantic import ValidationError
from model.api_models import ExtractedEntities, TickerValue, KeywordExtractor
import transformers
import torch
import re


class LLM:
    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1

        self.classifier = transformers.pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=device
        )

        self.keyword_extractor = transformers.pipeline(
            "token-classification",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            device=device
        )

        self.mapper = transformers.pipeline(
            "text2text-generation",
            model="t5-small"
        )

        self.categories = ["crypto", "stock", "weather"]

    def _extract_category(self, query: str) -> str:
        category_result = self.classifier(query, candidate_labels=self.categories)
        return category_result["labels"][0]

    def _extract_keywords(self, query: str, category: str) -> list[str] | None:
        keyword_results = self.keyword_extractor(query)
        print("Raw keyword results:", keyword_results)

        # Extract uppercase words (potential tickers), prioritizing stock and crypto tickers.
        ticker_candidates = re.findall(r"\b[A-Z]{2,6}\b", query)
        print("Ticker candidates from regex:", ticker_candidates)

        # Group NER entities
        entities = []
        current_entity = ""
        current_entity_type = None

        for result in keyword_results:
            word = result["word"]
            entity_type = result["entity"]

            # Group consecutive entities (I- prefix)
            if entity_type.startswith("I-") and current_entity_type == entity_type:
                current_entity += word if word.startswith("'") else f" {word}"
            else:
                if current_entity:
                    entities.append((current_entity.strip(), current_entity_type))
                current_entity = word
                current_entity_type = entity_type

        # Append last entity
        if current_entity:
            entities.append((current_entity.strip(), current_entity_type))

        print("Grouped entities:", entities)

        # Depending on the category, prioritize tickers or locations
        extracted_keywords = []

        if category == "crypto" or category == "stock":
            # For crypto and stock, prioritize using the regex tickers if found
            if ticker_candidates:
                print(f"Using regex-extracted ticker: {ticker_candidates[0]}")
                extracted_keywords.append(ticker_candidates[0])
        
        # Validate and filter NER results based on category
        for entity, entity_type in entities:
            try:
                validated_keyword = KeywordExtractor(keyword=entity).keyword
                print(f"Using NER-extracted entity: {validated_keyword}")
                
                if category == "crypto" and "crypto" in entity_type.lower():
                    extracted_keywords.append(validated_keyword)
                elif category == "stock" and "stock" in entity_type.lower():
                    extracted_keywords.append(validated_keyword)
                elif category == "weather" and "location" in entity_type.lower():
                    extracted_keywords.append(validated_keyword)

            except ValidationError:
                print(f"Skipping invalid entity: {entity}")

        # Return list of valid keywords
        return extracted_keywords if extracted_keywords else None




    def map_entity_to_ticker(self, entity: str, category: str) -> str:
        try:
            # Validate and transform the entity using TickerValue
            ticker_value = TickerValue(ticker=entity, category=category)
            return ticker_value.ticker  # Return the transformed value
        except ValidationError as e:
            print(f"Validation error: {e}")
            return entity  # Return original if validation fails

    def generate_response(self, user_query: str) -> ExtractedEntities:
        category = self._extract_category(user_query)
        print("Result category:", category)

        keywords = self._extract_keywords(user_query, category)
        print("Extracted keywords:", keywords)

        extracted_entities = ExtractedEntities()

        if keywords:
            for keyword in keywords:
                mapped_ticker = self.map_entity_to_ticker(keyword, category)
                if category == "crypto":
                    extracted_entities.crypto = mapped_ticker
                elif category == "stock":
                    extracted_entities.stock = mapped_ticker
                elif category == "weather":
                    extracted_entities.location = keyword

        return extracted_entities
