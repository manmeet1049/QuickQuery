from nltk.corpus import stopwords
import spacy
from collections import defaultdict
import json
import os
from typing import List, Dict, Set, Union, DefaultDict, Any


class DocumentProcessor:
    def __init__(self):
        # Load spaCy's English model
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words: Set[str] = set(stopwords.words("english"))

    def clean_text(self, text: str) -> List[str]:
        """Cleans and tokenizes the input text."""
        doc = self.nlp(text)

        cleaned_tokens: List[str] = [
            token.lemma_.upper()
            for token in doc
            if token.is_alpha and token.text.lower() not in self.stop_words
        ]

        return cleaned_tokens

    def build_reverse_index(self, documents: List[Dict[str, Any]], index_mappings: Dict[str, Any]) -> Dict[str, List[str]]:
        """Builds a reverse index from a list of documents."""
        reverse_index: DefaultDict[str, Set[str]] = defaultdict(set)  # Use a set to avoid duplicate document IDs

        relevant_fields = index_mappings.get("properties", {}).keys()
        print("--relevant fields--", relevant_fields)
        for doc in documents:
            doc_id: str = doc.get("_id", "")
            content: Dict[str, str] = doc.get("content", {})
            relevant_content: Dict[str, str] = {
                field: content.get(field, "") for field in relevant_fields
            }

            combined_text: str = " ".join(relevant_content.values())
            # Clean and parse the content
            tokens = self.clean_text(combined_text)

            for token in tokens:
                reverse_index[token].add(doc_id)  # Map token to document ID

        # Convert sets back to lists for JSON serialization
        return {term: list(doc_ids) for term, doc_ids in reverse_index.items()}

    @staticmethod
    def export_reverse_index_to_json(reverse_index: Dict[str, List[str]], filename: str = "reverse_index.json") -> None:
        """Export the reverse index to a JSON file, appending to existing data if the file exists."""
        # Check if the file exists and load existing data if present
        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                try:
                    existing_data: Dict[str, List[str]] = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Merge the existing data with the new reverse index data
        for term, doc_ids in reverse_index.items():
            if term in existing_data:
                # Add unique document IDs to avoid duplicates
                existing_data[term].extend(
                    [doc_id for doc_id in doc_ids if doc_id not in existing_data[term]]
                )
            else:
                existing_data[term] = doc_ids

        # Write the updated data back to the file
        with open(filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

    @staticmethod
    def load_reverse_index(filename: str = "reverse_index.json") -> Dict[str, List[str]]:
        """Load the reverse index from JSON file."""
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
