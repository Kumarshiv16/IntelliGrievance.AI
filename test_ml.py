import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.ml.category_classifier import category_engine
from backend.app.ml.severity_predictor import severity_engine
from backend.app.ml.explainability import explainability_engine
from backend.app.ml.routing_engine import routing_engine
from backend.app.ml.semantic_similarity import similarity_engine

query = "There is zero running water in Block C washrooms since morning. Over 300 students have no water and exam starts tomorrow."

print("--- Testing Category Classification ---")
cat_res = category_engine.predict(query)
print("Category:", cat_res["category"], "Confidence:", cat_res["confidence"])

print("\n--- Testing Severity Prediction ---")
sev_res = severity_engine.predict(query, predicted_category=cat_res["category"])
print("Priority:", sev_res["priority"], "Raw Priority:", sev_res["raw_model_priority"])
print("Safeguard Applied:", sev_res["safeguard_override"], "SLA Hours:", sev_res["sla_hours"])

print("\n--- Testing Explainable AI ---")
exp_res = explainability_engine.explain_prediction(query)
print("Top Features:", exp_res["top_contributing_features"][:4])
print("Severity Drivers:", exp_res["severity_drivers"])

print("\n--- Testing Department Routing ---")
route_res = routing_engine.route_grievance(cat_res["category"], sev_res["priority"])
print("Target Department:", route_res["recommended_department"])
print("Escalation Hierarchy:", route_res["escalation_hierarchy"])

print("\n--- Testing Semantic Similarity ---")
candidates = [
    "No running water in hostel bathroom and taps are dry",
    "WiFi in library 2nd floor is not connecting",
    "Bus broke down on outer ring road"
]
sims = similarity_engine.compute_similarity(query, candidates)
print("Similarities to candidates:", sims)

print("\nAll ML components tested successfully!")
