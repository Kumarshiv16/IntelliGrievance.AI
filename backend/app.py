import os, random, sqlite3, datetime as dt
from collections import Counter
from flask import Flask, jsonify, request, send_from_directory
from sklearn.feature_extraction.text import CountVectorizer
from ml import Engine, sample, LOCS

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "grievances.db")
app = Flask(__name__, static_folder=None)
E = Engine()

def q(sql, args=(), commit=False):
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    cur = c.execute(sql, args)
    out = cur.lastrowid if commit else [dict(r) for r in cur.fetchall()]
    c.commit(); c.close(); return out

def save(text, student, created=None, status="Open"):
    p = E.predict(text)
    return q("INSERT INTO grievances(student,text,category,confidence,priority,score,department,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
             (student, text, p["category"], p["confidence"], p["priority"], p["score"], p["department"], status,
              (created or dt.datetime.now()).isoformat(timespec="seconds")), commit=True)

def init():
    q("""CREATE TABLE IF NOT EXISTS grievances(id INTEGER PRIMARY KEY AUTOINCREMENT, student TEXT, text TEXT, category TEXT,
         confidence REAL, priority TEXT, score REAL, department TEXT, status TEXT, created_at TEXT)""", commit=True)
    if not q("SELECT 1 FROM grievances LIMIT 1"):
        rng = random.Random(7)
        for _ in range(180):
            t, _, _ = sample(rng, 0.03)
            when = dt.datetime.now() - dt.timedelta(days=rng.random() ** 1.5 * 30, hours=rng.randint(0, 23))
            save(t, f"STU{rng.randint(21001, 21400)}", when, rng.choices(["Open", "In Progress", "Resolved"], [4, 3, 3])[0])
init()

@app.get("/")
def index(): return send_from_directory(os.path.join(HERE, "..", "frontend"), "index.html")

@app.post("/api/predict")
def predict():
    t = (request.json or {}).get("text", "").strip()
    return (jsonify(E.predict(t)) if len(t) >= 10 else (jsonify(error="Enter at least 10 characters."), 400))

@app.post("/api/grievances")
def create():
    d = request.json or {}; t = d.get("text", "").strip()
    if len(t) < 10: return jsonify(error="Enter at least 10 characters."), 400
    gid = save(t, d.get("student") or "ANONYMOUS")
    return jsonify(id=gid, **E.predict(t)), 201

@app.get("/api/grievances")
def lst(): return jsonify(q("SELECT * FROM grievances ORDER BY score DESC, created_at DESC LIMIT 300"))

@app.patch("/api/grievances/<int:gid>")
def upd(gid):
    s = (request.json or {}).get("status")
    if s not in ("Open", "In Progress", "Resolved"): return jsonify(error="Invalid status"), 400
    q("UPDATE grievances SET status=? WHERE id=?", (s, gid), commit=True); return jsonify(ok=True)

@app.get("/api/stats")
def stats():
    rows = q("SELECT * FROM grievances"); n = len(rows) or 1
    cnt = lambda k: dict(Counter(r[k] for r in rows))
    today = dt.date.today()
    days = Counter(r["created_at"][:10] for r in rows)
    trend = [{"d": (today - dt.timedelta(days=i)).strftime("%d %b"), "n": days.get((today - dt.timedelta(days=i)).isoformat(), 0)} for i in range(13, -1, -1)]
    active = [r for r in rows if r["status"] != "Resolved"]
    # recurring problem areas: (category, location) pairs and frequent bigrams per category
    pairs = Counter((r["category"], l) for r in active for l in LOCS if l.lower() in r["text"].lower())
    areas = [{"category": c, "area": l, "count": k, "avg_score": round(sum(r["score"] for r in active if r["category"] == c and l.lower() in r["text"].lower()) / k, 1)}
             for (c, l), k in pairs.most_common(6) if k >= 3]
    terms = []
    for c in cnt("category"):
        tx = [r["text"] for r in rows if r["category"] == c]
        try:
            cv = CountVectorizer(ngram_range=(2, 2), stop_words="english").fit(tx); s = cv.transform(tx).sum(0).A1
            terms += [{"category": c, "term": w, "count": int(k)} for w, k in sorted(zip(cv.get_feature_names_out(), s), key=lambda x: -x[1])[:2] if k >= 4]
        except ValueError: pass
    return jsonify(kpi={"total": len(rows), "open_critical": sum(r["priority"] == "Critical" for r in active), "active": len(active),
                        "resolved_pct": round(100 * sum(r["status"] == "Resolved" for r in rows) / n), "avg_score": round(sum(r["score"] for r in rows) / n, 1)},
                   by_category=cnt("category"), by_priority=cnt("priority"), by_status=cnt("status"), trend=trend,
                   areas=areas, terms=sorted(terms, key=lambda x: -x["count"])[:8], metrics=E.metrics)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
