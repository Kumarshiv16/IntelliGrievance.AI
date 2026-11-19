"""NLP engine: TF-IDF + Logistic Regression for category AND priority, plus safety-rule override."""
import random, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

LOCS = ["Hostel Block A", "Hostel Block C", "Block B", "Main Library", "Lab 3", "Route 7", "Canteen"]
LOC_W = [2, 5, 2, 1, 1, 2, 1]
DEPT = {"Academic": "Dean Academics", "Administrative": "Registrar Office", "Hostel": "Hostel Warden Office",
        "Examination": "Controller of Examinations", "Financial": "Accounts & Scholarship Cell",
        "Transportation": "Transport Department", "Other": "Student Welfare Office"}
SLA = {"Critical": 4, "High": 24, "Medium": 72, "Low": 168}          # hours
W = {"Low": 15, "Medium": 40, "High": 70, "Critical": 95}            # severity weights
CRIT = re.compile(r"rag(ging|ged)|harass|assault|threat|fire|burning|short circuit|accident|suicide|ambulance|unsafe|bitten|emergency|molest", re.I)

TPL = {
 "Academic": [("The professor of the course is not completing the syllabus and classes are often cancelled", "Medium"),
              ("Equipment in {l} is outdated so practical sessions cannot be performed properly", "Medium"),
              ("Please add more elective subjects and update the curriculum", "Low"),
              ("Faculty has been absent for weeks and no substitute is arranged before the semester ends", "High")],
 "Administrative": [("Bonafide certificate is pending for two weeks despite repeated applications", "Medium"),
              ("Staff at the office behaves rudely and the ID card is still not issued", "Low"),
              ("Transfer certificate is needed urgently for a job joining but the office is not responding", "High"),
              ("Suggestion to digitise the document request process", "Low")],
 "Hostel": [("There is no water supply in {l} for three days", "High"),
            ("Mess food quality is poor and unhygienic", "Medium"),
            ("Wi-Fi in {l} is very slow and keeps disconnecting", "Low"),
            ("Seniors are ragging and harassing juniors in {l}, students feel unsafe", "Critical"),
            ("Short circuit with sparks and burning smell in the room at {l}", "Critical")],
 "Examination": [("Hall ticket is not generated and my exam is tomorrow", "Critical"),
            ("Result shows wrong marks, I request revaluation", "High"),
            ("Two papers are scheduled at the same time in the timetable", "High"),
            ("Please provide more reference books before the exams", "Low"),
            ("The re-exam form portal is slow and times out", "Medium")],
 "Financial": [("Scholarship amount has not been credited for six months", "High"),
            ("Fee receipt shows the amount charged twice", "Medium"),
            ("Fee deadline is today and the payment gateway keeps failing, a fine will be charged", "High"),
            ("Request an instalment option for fee payment", "Low")],
 "Transportation": [("The bus on {l} is always late and students miss the first lecture", "Medium"),
            ("The bus driver was driving rashly and nearly caused an accident", "Critical"),
            ("Please start a new bus route for the city side", "Low"),
            ("Buses break down daily and are overcrowded on {l}", "Medium")],
 "Other": [("Canteen prices are too high for students", "Low"),
            ("Stray dogs near {l}, a student was bitten yesterday", "High"),
            ("Air conditioning in the {l} is not working", "Low"),
            ("Medical emergency, there was no ambulance or doctor at the health centre", "Critical"),
            ("Parking space on campus is insufficient", "Low")],
}
PRE = ["", "", "Sir, ", "Respected madam, ", "Urgent: ", "I want to complain that ", "Kindly note that "]
SUF = ["", "", ". Please take action.", ". This is affecting my studies.", ". Kindly resolve soon."]
FLAT = [(c, t, p) for c, v in TPL.items() for t, p in v]

def sample(rng, noise=0.07):
    c, t, p = rng.choice(FLAT)
    t = rng.choice(PRE) + t.format(l=rng.choices(LOCS, LOC_W)[0]) + rng.choice(SUF)
    words = [w for w in t.split() if rng.random() > noise]
    return " ".join(words), c, p

class Engine:
    def __init__(self, seed=42, n=4000):
        rng = random.Random(seed)
        data = [sample(rng) for _ in range(n)]
        X, yc, yp = zip(*data)
        Xtr, Xte, ctr, cte, ptr, pte = train_test_split(X, yc, yp, test_size=0.2, random_state=seed, stratify=yc)
        mk = lambda: make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2),
                                   LogisticRegression(C=8, max_iter=2000))
        self.cat, self.pri = mk().fit(Xtr, ctr), mk().fit(Xtr, ptr)
        self.metrics = {k: {"accuracy": round(accuracy_score(t, m.predict(Xte)), 4),
                            "f1_macro": round(f1_score(t, m.predict(Xte), average="macro"), 4)}
                        for k, m, t in (("category", self.cat, cte), ("priority", self.pri, pte))}
        self.metrics.update(train_size=len(Xtr), test_size=len(Xte))

    def predict(self, text):
        pc = self.cat.predict_proba([text])[0]; pp = self.pri.predict_proba([text])[0]
        cat = self.cat.classes_[pc.argmax()]
        probs = dict(zip(self.pri.classes_, pp))
        score = sum(probs[k] * W[k] for k in probs)
        pri = max(probs, key=probs.get)
        rule = bool(CRIT.search(text))
        if rule and pri != "Critical":
            pri, score = "Critical", max(score, 92.0)
        top = sorted(zip(self.cat.classes_, pc), key=lambda x: -x[1])[:3]
        return {"category": cat, "confidence": round(float(pc.max()), 3), "department": DEPT[cat],
                "priority": pri, "score": round(float(score), 1), "sla_hours": SLA[pri], "rule_override": rule,
                "top_categories": [{"label": k, "p": round(float(v), 3)} for k, v in top],
                "priority_probs": {k: round(float(v), 3) for k, v in probs.items()}}
