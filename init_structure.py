import os

BASE_DIR = r"C:\Users\TIRTHENDU\OneDrive\Desktop\intelligrievance-ai"

dirs = [
    os.path.join(BASE_DIR, "backend", "app", "api", "v1", "endpoints"),
    os.path.join(BASE_DIR, "backend", "app", "core"),
    os.path.join(BASE_DIR, "backend", "app", "models"),
    os.path.join(BASE_DIR, "backend", "app", "schemas"),
    os.path.join(BASE_DIR, "backend", "app", "ml"),
    os.path.join(BASE_DIR, "backend", "app", "services"),
    os.path.join(BASE_DIR, "backend", "tests"),
    os.path.join(BASE_DIR, "ml", "data"),
    os.path.join(BASE_DIR, "ml", "training"),
    os.path.join(BASE_DIR, "ml", "models"),
    os.path.join(BASE_DIR, "ml", "reports"),
    os.path.join(BASE_DIR, "docs", "architecture"),
    os.path.join(BASE_DIR, "docs", "diagrams"),
    os.path.join(BASE_DIR, "frontend"),
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created: {d}")

print("Directories initialized successfully.")
