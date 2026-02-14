"""
Setup completo: Usuario + API Key
"""
from app.core.database import SessionLocal
from app.models.database import User, ApiKey
from app.core.security import api_key_manager

db = SessionLocal()

# 1. Verificar si ya existe usuario
existing_user = db.query(User).filter(User.email == "demo@example.com").first()

if existing_user:
    print(f"✅ Usuario ya existe: ID {existing_user.id}")
    user_id = existing_user.id
else:
    # Crear usuario
    user = User(
        email="demo@example.com",
        username="demouser",
        plan="free",
        monthly_quota=100,
        validations_used=0,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    print(f"✅ Usuario creado: ID {user_id}")

# 2. Crear API key
api_key_obj, plain_key = api_key_manager.create_api_key(
    db=db,
    user_id=user_id,
    name="Demo Key"
)

print(f"\n🔑 API Key creada exitosamente!")
print(f"Key: {plain_key}")
print(f"User ID: {user_id}")
print(f"\n💾 Guarda esta key, no se mostrará de nuevo!\n")

# 3. Verificar que se guardó
verify = db.query(ApiKey).filter(ApiKey.key == plain_key).first()
if verify:
    print(f"✅ Verificado en DB: Key ID {verify.id}")
else:
    print(f"❌ Error: Key no encontrada en DB")

db.close()
