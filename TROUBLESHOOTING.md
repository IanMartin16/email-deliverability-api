# 🔧 Troubleshooting - Errores Comunes

## ❌ Error: "validation error for Settings database_url"

### Causa
La aplicación está buscando la variable `DATABASE_URL` pero no está configurada.

### ✅ Solución Rápida

La base de datos NO es necesaria en Fase 1. Ya está solucionado en la última versión, pero si persiste:

**Opción 1: Usar el archivo .env incluido**
```bash
# El archivo .env ya está creado en el proyecto
# Solo asegúrate de que existe
ls -la .env

# Si no existe, créalo:
cp .env.example .env
```

**Opción 2: Ejecutar sin base de datos**
El código ya está actualizado para que `DATABASE_URL` sea opcional.

---

## ❌ Error: "ModuleNotFoundError: No module named 'X'"

### Causa
Falta instalar dependencias o no estás en el entorno virtual.

### ✅ Solución

```bash
# 1. Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
pip list | grep fastapi
pip list | grep dnspython
```

---

## ❌ Error: "Address already in use" o "Port 8000 is already allocated"

### Causa
Ya hay un proceso usando el puerto 8000.

### ✅ Solución

**Opción 1: Usar otro puerto**
```bash
uvicorn app.main:app --reload --port 8001
```

**Opción 2: Matar el proceso**
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

## ❌ Error: "Cannot import name 'app' from 'app.main'"

### Causa
Python no encuentra el módulo porque no estás en el directorio correcto.

### ✅ Solución

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd email-validator-api

# Verifica que exista app/main.py
ls app/main.py

# Ejecuta desde aquí
uvicorn app.main:app --reload
```

---

## ❌ Error: DNS resolution failed / "dns.resolver.NXDOMAIN"

### Causa
No hay conexión a internet o el dominio no existe.

### ✅ Solución

```bash
# 1. Verifica tu conexión a internet
ping google.com

# 2. Prueba con dominios conocidos
# En vez de: test@fakeemail123.com
# Usa: test@gmail.com, test@yahoo.com
```

---

## ❌ Error: "pydantic_core._pydantic_core.ValidationError"

### Causa
Datos inválidos en el request.

### ✅ Solución

Asegúrate de enviar el formato correcto:

```json
{
  "email": "test@example.com",
  "check_smtp": false
}
```

**NO envíes:**
```json
{
  "mail": "test@example.com"  ❌ (campo incorrecto)
}
```

---

## 🧪 Testing Rápido

### Verificar que todo funciona:

```bash
# 1. Iniciar servidor
uvicorn app.main:app --reload

# 2. En otra terminal, probar el health check
curl http://localhost:8000/api/v1/health

# 3. Probar validación simple
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "check_smtp": false}'

# 4. O usar el script de prueba
python test_validation.py
```

### Usando el navegador:

1. Inicia el servidor: `uvicorn app.main:app --reload`
2. Abre: http://localhost:8000/docs
3. Prueba el endpoint `/validate` desde Swagger UI

---

## 📋 Checklist de Verificación

Antes de reportar un error, verifica:

- [ ] Estás en el directorio correcto (`email-validator-api/`)
- [ ] El entorno virtual está activado (verás `(venv)` en el prompt)
- [ ] Las dependencias están instaladas (`pip list`)
- [ ] El archivo `.env` existe
- [ ] No hay otro proceso en el puerto 8000
- [ ] Tienes conexión a internet (para DNS lookups)
- [ ] Python version >= 3.11 (`python --version`)

---

## 🐍 Verificar versión de Python

```bash
# Ver versión
python --version
# o
python3 --version

# Debe ser Python 3.11 o superior
# Si no, instala Python 3.11+
```

---

## 🔍 Debug Mode

Si necesitas más información sobre errores:

```bash
# Modo debug con más logs
uvicorn app.main:app --reload --log-level debug

# Ver todos los requests
uvicorn app.main:app --reload --access-log
```

---

## 🆘 Si Nada Funciona

### Reinstalación limpia:

```bash
# 1. Eliminar entorno virtual
rm -rf venv

# 2. Crear nuevo
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

# 3. Actualizar pip
pip install --upgrade pip

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
pip list

# 6. Iniciar servidor
uvicorn app.main:app --reload
```

---

## 💡 Tips para Desarrollo

### 1. Auto-reload funcionando
Si cambias código y no se refresca:
```bash
# Usa --reload
uvicorn app.main:app --reload
```

### 2. Ver requests en tiempo real
```bash
uvicorn app.main:app --reload --log-level info
```

### 3. Cambiar puerto fácilmente
```bash
# Agrega al final de tu comando
--port 8001
```

### 4. Ver errores de Pydantic
Los errores de validación son muy descriptivos, léelos completos:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 📞 Comandos Útiles

```bash
# Ver procesos de Python
ps aux | grep python

# Ver qué está usando el puerto 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Reiniciar servidor rápido (Ctrl+C y luego)
uvicorn app.main:app --reload

# Ver logs del servidor
# Los logs aparecen directamente en la terminal donde ejecutaste uvicorn
```

---

## ✅ Solución Funcionando

Si todo está bien, deberías ver:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
🚀 Email Deliverability Checker API v1.0.0 starting...
📍 API Documentation: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/api/v1/health
INFO:     Application startup complete.
```

---

**Última actualización**: Febrero 2024

Si encuentras un error que no está aquí, crea un issue en GitHub o consulta los logs completos.
