# Ver qué se guardó en la DB
from app.core.database import SessionLocal
from app.models.database import ValidationLog, User, ApiKey

db = SessionLocal()

# Ver logs
logs = db.query(ValidationLog).all()
print(f"\nTotal validations logged: {len(logs)}")

for log in logs[-5:]:  # Últimos 5
    print(f"- {log.email}: {log.deliverability_score}/100")

# Ver users
users = db.query(User).all()
print(f"\nTotal users: {len(users)}")

# Ver keys
keys = db.query(ApiKey).all()
print(f"Total API keys: {len(keys)}")
for key in keys:
    print(f"- {key.name}: {key.total_requests} requests")

db.close()
