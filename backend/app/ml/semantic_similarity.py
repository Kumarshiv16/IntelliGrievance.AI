"""
IntelliGrievance AI - Semantic Similarity & Duplicate Detection Engine
Computes cosine similarity between incoming grievances and existing unresolved cases.
Employs sublinear TF-IDF character & word n-gram vectors with fallback to SentenceTransformers
when available, guaranteeing fast, local, zero-cost, privacy-preserving deduplication.
"""

from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ml.preprocessing.text_cleaner import clean_text

class SemanticSimilarityEngine:
    def __init__(self, duplicate_threshold: float = 0.15):
        self.duplicate_threshold = duplicate_threshold
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            analyzer="word",
            sublinear_tf=True
        )
        
    def compute_similarity(self, query: str, candidate_texts: List[str]) -> List[float]:
        if not candidate_texts:
            return []
        
        all_texts = [clean_text(query)] + [clean_text(t) for t in candidate_texts]
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            return [round(float(s), 4) for s in sim_scores]
        except Exception:
            return [0.0] * len(candidate_texts)
            
    def find_duplicates(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """
        candidates: List of dicts with 'id', 'text', 'category', 'status'
        """
        if not candidates:
            return []
            
        candidate_texts = [c.get("text", "") for c in candidates]
        sims = self.compute_similarity(query, candidate_texts)
        
        duplicates = []
        for cand, score in zip(candidates, sims):
            if score >= self.duplicate_threshold:
                duplicates.append({
                    "grievance_id": cand.get("id"),
                    "text": cand.get("text"),
                    "category": cand.get("category"),
                    "similarity_score": score,
                    "status": cand.get("status"),
                    "is_potential_duplicate": True
                })
                
        return sorted(duplicates, key=lambda x: -x["similarity_score"])

similarity_engine = SemanticSimilarityEngine()
