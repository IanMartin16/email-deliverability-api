# 🚀 Quick Start Guide

## Setup en 5 minutos

### 1. Instalación

```bash
# Clonar el proyecto
cd email-validator-api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env si es necesario (opcional para desarrollo local)
```

### 3. Ejecutar

```bash
# Iniciar el servidor
uvicorn app.main:app --reload
```

La API estará disponible en: http://localhost:8000

### 4. Probar

#### Opción A: Swagger UI (Recomendado)
Abre tu navegador en: http://localhost:8000/docs

#### Opción B: cURL
```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "check_smtp": false}'
```

#### Opción C: Python Script
```bash
python test_validation.py
```

## 📚 Ejemplos de Uso

### Validar un solo email

```python
import requests

url = "http://localhost:8000/api/v1/validate"
data = {
    "email": "john.doe@example.com",
    "check_smtp": True
}

response = requests.post(url, json=data)
result = response.json()

print(f"Valid: {result['is_valid']}")
print(f"Score: {result['deliverability_score']}/100")
```

### Validación en lote

```python
import requests

url = "http://localhost:8000/api/v1/validate/bulk"
data = {
    "emails": [
        "user1@gmail.com",
        "user2@yahoo.com",
        "fake@tempmail.com"
    ],
    "check_smtp": False
}

response = requests.post(url, json=data)
result = response.json()

print(f"Total validados: {result['total_checked']}")
for email_result in result['results']:
    print(f"{email_result['email']}: {email_result['deliverability_score']}/100")
```

### JavaScript/TypeScript

```javascript
const validateEmail = async (email) => {
  const response = await fetch('http://localhost:8000/api/v1/validate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      check_smtp: false
    })
  });
  
  const result = await response.json();
  return result;
};

// Uso
validateEmail('test@example.com')
  .then(result => console.log(result));
```

## 🔍 Entendiendo los Resultados

### Campos de la respuesta

```json
{
  "email": "user@example.com",           // Email normalizado
  "is_valid": true,                      // ¿Es válido en general?
  "syntax_valid": true,                  // ¿Sintaxis correcta?
  "domain": "example.com",               // Dominio extraído
  "has_mx_records": true,                // ¿Tiene registros MX?
  "mx_records": [...],                   // Lista de servidores MX
  "is_disposable": false,                // ¿Es email temporal?
  "smtp_check_performed": true,          // ¿Se verificó SMTP?
  "mailbox_exists": true,                // ¿Existe el buzón?
  "deliverability_score": 95.0,          // Puntuación 0-100
  "processing_time_ms": 1234.56          // Tiempo de proceso
}
```

### Interpretación del Score

- **90-100**: ✅ Excelente - Email altamente confiable
- **70-89**: 🟢 Bueno - Email probablemente válido
- **50-69**: 🟡 Regular - Algunos problemas detectados
- **0-49**: 🔴 Malo - Alto riesgo de rebote

## ⚙️ Configuración Avanzada

### Variables de entorno importantes

```env
# Performance
SMTP_TIMEOUT=10                # Timeout para verificación SMTP (segundos)

# Validación
SMTP_FROM_EMAIL=verify@yourdomain.com  # Email usado para verificación SMTP
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de activar el entorno virtual
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Address already in use"
```bash
# El puerto 8000 está ocupado, usa otro puerto
uvicorn app.main:app --reload --port 8001
```

### MX records no encontrados
- Algunos dominios pueden tener configuraciones especiales
- Verifica que tengas conexión a internet
- El dominio podría no existir o no tener email configurado

## 📈 Próximos Pasos

1. ✅ Has completado el setup básico
2. 🔄 Próximo: Implementar verificación SMTP
3. 💾 Después: Integrar PostgreSQL
4. 🔑 Luego: Añadir autenticación API
5. 🚀 Finalmente: Deploy a Render + RapidAPI

## 💡 Tips

- Para desarrollo, mantén `check_smtp=False` (más rápido)
- Usa el endpoint `/bulk` para validar múltiples emails
- Revisa los logs en la consola para debugging
- La documentación interactiva está en `/docs`

¿Necesitas ayuda? Revisa el README.md principal o crea un issue en GitHub.
