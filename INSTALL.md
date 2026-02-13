# 📦 INSTALACIÓN - Email Deliverability Checker API

## 🚀 Setup en 3 Minutos

### Paso 1: Descargar el Proyecto

Descarga la carpeta `email-validator-api` completa desde Claude.

### Paso 2: Copiar a tu Directorio de Trabajo

```bash
# Windows
# 1. Extrae el zip descargado
# 2. Copia la carpeta email-validator-api a:
C:\Users\imart\Desktop\myApps\email-validator-api
```

### Paso 3: Crear Entorno Virtual e Instalar

```powershell
# Abre PowerShell o CMD en la carpeta del proyecto
cd C:\Users\imart\Desktop\myApps\email-validator-api

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 4: Iniciar el Servidor

```powershell
uvicorn app.main:app --reload
```

### Paso 5: Probar

Abre tu navegador en: **http://localhost:8000/docs**

---

## ✅ Verificación Rápida

Si todo está bien, deberías ver en la terminal:

```
🚀 Email Deliverability Checker API v1.0.0 starting...
📍 API Documentation: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/api/v1/health
INFO:     Application startup complete.
```

---

## 📁 Archivos Incluidos

### Código:
- ✅ `app/main.py` - Aplicación principal
- ✅ `app/api/routes.py` - Endpoints
- ✅ `app/core/config.py` - Configuración
- ✅ `app/models/schemas.py` - Modelos Pydantic
- ✅ `app/services/validator.py` - Lógica de validación

### Configuración:
- ✅ `.env` - Variables de entorno (ya configurado)
- ✅ `requirements.txt` - Dependencias Python
- ✅ `Dockerfile` - Para deploy
- ✅ `.gitignore` - Para Git

### Documentación:
- ✅ `README.md` - Documentación principal
- ✅ `QUICKSTART.md` - Guía rápida
- ✅ `ROADMAP.md` - Plan de desarrollo
- ✅ `EXAMPLES.md` - Ejemplos de uso
- ✅ `TROUBLESHOOTING.md` - Solución de problemas
- ✅ `GIT_SETUP.md` - Configurar Git/GitHub
- ✅ `NEXT_STEPS.md` - Próximos pasos
- ✅ `FIX_IMPORT_ERROR.md` - Fix errores de importación

### Testing:
- ✅ `test_validation.py` - Script de pruebas

---

## 🎯 Comandos Básicos

```powershell
# Iniciar servidor
uvicorn app.main:app --reload

# Cambiar puerto
uvicorn app.main:app --reload --port 8001

# Ver tests
python test_validation.py

# Verificar dependencias instaladas
pip list
```

---

## 🆘 Si Tienes Problemas

1. **Lee `TROUBLESHOOTING.md`** - Soluciones a errores comunes
2. **Lee `FIX_IMPORT_ERROR.md`** - Si tienes problemas de importación
3. **Verifica Python**: Debe ser Python 3.11+
   ```powershell
   python --version
   ```

---

## 📚 Siguiente Paso

Una vez que funcione localmente:

1. **Lee `NEXT_STEPS.md`** - Plan para continuar
2. **Lee `ROADMAP.md`** - Visión completa del proyecto
3. **Implementa SMTP verification** (Fase 2)

---

## ✨ Features Actuales

- ✅ Validación de sintaxis
- ✅ Verificación MX records
- ✅ Detección de emails desechables
- ✅ Scoring 0-100
- ✅ Bulk validation (hasta 100 emails)
- 🔄 SMTP verification (Fase 2 - próximamente)
- 🔄 Database integration (Fase 2 - próximamente)

---

¡Listo para empezar! 🚀
