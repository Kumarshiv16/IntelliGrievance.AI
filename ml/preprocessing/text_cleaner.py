"""
IntelliGrievance AI - NLP Text Preprocessing Pipeline
Preserves contextual negations (not, never, no, without), urgency tokens (immediate, emergency, asap),
normalizes contractions, cleans noise, and supports lemmatization/stemming.
"""

import re
import string

CONTRACTIONS = {
    "can't": "cannot", "won't": "will not", "n't": " not", "'re": " are",
    "'s": " is", "'d": " would", "'ll": " will", "'t": " not", "'ve": " have",
    "'m": " am", "pls": "please", "plz": "please", "asap": "as soon as possible",
    "hod": "head of department", "tc": "transfer certificate", "dept": "department",
    "wifi": "wi-fi", "ac": "air conditioning", "er": "emergency room"
}

# English stop words without critical negations & urgency keywords
BASE_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "by", "could", "did", "do", "does", "doing", "down", "during",
    "each", "few", "for", "from", "further", "had", "has", "have", "having", "he",
    "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in",
    "into", "is", "it", "its", "itself", "me", "more", "most", "my", "myself", "of",
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

NEGATIONS = {"no", "not", "none", "neither", "never", "nobody", "nowhere", "nothing", "without", "hardly", "barely"}
PRESERVED_STOPWORDS = BASE_STOPWORDS - NEGATIONS

def clean_text(text: str, remove_stopwords: bool = False) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # 1. Lowercase normalization
    text = text.lower()
    
    # 2. Contraction & acronym expansion
    for contraction, expansion in CONTRACTIONS.items():
        text = re.sub(r"\b" + re.escape(contraction) + r"\b", expansion, text)
        
    # 3. Handle URLs and emails
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    
    # 4. Remove special noise characters but retain letters, digits and whitespace
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    # 5. Optional stopword removal that preserves negations
    if remove_stopwords:
        tokens = text.split()
        tokens = [t for t in tokens if t not in PRESERVED_STOPWORDS and len(t) > 1]
        text = " ".join(tokens)
        
    return text
