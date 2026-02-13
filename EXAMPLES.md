# 📖 API Usage Examples

Ejemplos completos de cómo usar la Email Deliverability Checker API en diferentes lenguajes y escenarios.

---

## 🐍 Python

### Validar un solo email

```python
import requests

# Configuración
API_URL = "http://localhost:8000/api/v1"

# Validar email
response = requests.post(
    f"{API_URL}/validate",
    json={
        "email": "john.doe@gmail.com",
        "check_smtp": True
    }
)

result = response.json()

# Mostrar resultados
print(f"Email: {result['email']}")
print(f"Válido: {result['is_valid']}")
print(f"Score: {result['deliverability_score']}/100")
print(f"Es desechable: {result['is_disposable']}")

if result['has_mx_records']:
    print(f"Servidores MX: {len(result['mx_records'])}")
    for mx in result['mx_records']:
        print(f"  - {mx['host']} (prioridad: {mx['priority']})")
```

### Validación en lote

```python
import requests

emails_to_validate = [
    "user1@gmail.com",
    "user2@yahoo.com",
    "fake@tempmail.com",
    "invalid@nonexistentdomain123456.com"
]

response = requests.post(
    f"{API_URL}/validate/bulk",
    json={
        "emails": emails_to_validate,
        "check_smtp": False  # Más rápido sin SMTP
    }
)

result = response.json()

print(f"\nValidados: {result['total_checked']} emails")
print(f"Tiempo total: {result['processing_time_ms']:.2f}ms\n")

# Resultados detallados
for email_result in result['results']:
    status = "✅" if email_result['is_valid'] else "❌"
    print(f"{status} {email_result['email']}: {email_result['deliverability_score']}/100")
    
    if email_result['is_disposable']:
        print(f"   ⚠️  Email desechable detectado")
```

### Validación con manejo de errores

```python
import requests
from typing import Dict, Optional

def validate_email_safe(email: str) -> Optional[Dict]:
    """
    Valida un email con manejo de errores
    """
    try:
        response = requests.post(
            f"{API_URL}/validate",
            json={"email": email, "check_smtp": False},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout validando {email}")
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e.response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None

# Uso
result = validate_email_safe("test@example.com")
if result:
    print(f"Score: {result['deliverability_score']}/100")
```

### Async con aiohttp

```python
import aiohttp
import asyncio

async def validate_email_async(session, email):
    """Validación asíncrona de email"""
    async with session.post(
        f"{API_URL}/validate",
        json={"email": email, "check_smtp": False}
    ) as response:
        return await response.json()

async def validate_multiple_emails(emails):
    """Valida múltiples emails concurrentemente"""
    async with aiohttp.ClientSession() as session:
        tasks = [validate_email_async(session, email) for email in emails]
        results = await asyncio.gather(*tasks)
        return results

# Uso
emails = ["user1@gmail.com", "user2@yahoo.com", "user3@outlook.com"]
results = asyncio.run(validate_multiple_emails(emails))

for result in results:
    print(f"{result['email']}: {result['deliverability_score']}/100")
```

---

## 🟨 JavaScript/Node.js

### Con fetch (Node.js 18+)

```javascript
const API_URL = "http://localhost:8000/api/v1";

// Validar un email
async function validateEmail(email) {
  try {
    const response = await fetch(`${API_URL}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        check_smtp: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    console.log(`Email: ${result.email}`);
    console.log(`Valid: ${result.is_valid}`);
    console.log(`Score: ${result.deliverability_score}/100`);
    console.log(`Processing time: ${result.processing_time_ms}ms`);
    
    return result;
    
  } catch (error) {
    console.error('Error validating email:', error);
    return null;
  }
}

// Uso
validateEmail('test@gmail.com');
```

### Con axios

```javascript
const axios = require('axios');

const API_URL = "http://localhost:8000/api/v1";

// Validación en lote
async function validateBulk(emails) {
  try {
    const response = await axios.post(`${API_URL}/validate/bulk`, {
      emails: emails,
      check_smtp: false
    });

    const { total_checked, results, processing_time_ms } = response.data;
    
    console.log(`\nValidated ${total_checked} emails in ${processing_time_ms}ms\n`);
    
    results.forEach(result => {
      const status = result.is_valid ? '✅' : '❌';
      console.log(`${status} ${result.email}: ${result.deliverability_score}/100`);
    });
    
    return results;
    
  } catch (error) {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else {
      console.error('Error:', error.message);
    }
    return null;
  }
}

// Uso
const emails = [
  'user1@gmail.com',
  'user2@yahoo.com',
  'fake@tempmail.com'
];

validateBulk(emails);
```

### TypeScript con tipos

```typescript
interface EmailValidationRequest {
  email: string;
  check_smtp: boolean;
}

interface MXRecord {
  host: string;
  priority: number;
}

interface EmailValidationResponse {
  email: string;
  is_valid: boolean;
  syntax_valid: boolean;
  domain: string;
  has_mx_records: boolean;
  mx_records: MXRecord[] | null;
  is_disposable: boolean;
  smtp_check_performed: boolean;
  mailbox_exists: boolean | null;
  smtp_response: string | null;
  deliverability_score: number;
  checked_at: string;
  processing_time_ms: number;
}

async function validateEmail(
  email: string,
  checkSmtp: boolean = false
): Promise<EmailValidationResponse | null> {
  const API_URL = "http://localhost:8000/api/v1";
  
  try {
    const response = await fetch(`${API_URL}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        check_smtp: checkSmtp
      } as EmailValidationRequest)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json() as EmailValidationResponse;
    
  } catch (error) {
    console.error('Validation error:', error);
    return null;
  }
}

// Uso
(async () => {
  const result = await validateEmail('test@example.com');
  if (result) {
    console.log(`Score: ${result.deliverability_score}/100`);
  }
})();
```

---

## 🔷 React Hook

```typescript
import { useState, useCallback } from 'react';

interface UseEmailValidation {
  validate: (email: string) => Promise<void>;
  result: EmailValidationResponse | null;
  loading: boolean;
  error: string | null;
}

export function useEmailValidation(): UseEmailValidation {
  const [result, setResult] = useState<EmailValidationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = useCallback(async (email: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          check_smtp: false
        })
      });

      if (!response.ok) {
        throw new Error('Validation failed');
      }

      const data = await response.json();
      setResult(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  return { validate, result, loading, error };
}

// Componente de ejemplo
function EmailValidator() {
  const { validate, result, loading, error } = useEmailValidation();
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    validate(email);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter email to validate"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Validating...' : 'Validate'}
      </button>

      {error && <p className="error">{error}</p>}
      
      {result && (
        <div className="result">
          <h3>Score: {result.deliverability_score}/100</h3>
          <p>Valid: {result.is_valid ? '✅' : '❌'}</p>
          <p>Disposable: {result.is_disposable ? 'Yes ⚠️' : 'No ✅'}</p>
        </div>
      )}
    </form>
  );
}
```

---

## 🌐 cURL

### Validación simple

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "check_smtp": false
  }'
```

### Validación en lote

```bash
curl -X POST "http://localhost:8000/api/v1/validate/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "user1@gmail.com",
      "user2@yahoo.com",
      "fake@tempmail.com"
    ],
    "check_smtp": false
  }'
```

### Health check

```bash
curl "http://localhost:8000/api/v1/health"
```

### Con pretty print (jq)

```bash
curl -s -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "check_smtp": false}' \
  | jq '.'
```

---

## 🔴 PHP

```php
<?php

function validateEmail($email, $checkSmtp = false) {
    $url = "http://localhost:8000/api/v1/validate";
    
    $data = [
        'email' => $email,
        'check_smtp' => $checkSmtp
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode !== 200) {
        return null;
    }
    
    return json_decode($response, true);
}

// Uso
$result = validateEmail('test@gmail.com');

if ($result) {
    echo "Email: " . $result['email'] . "\n";
    echo "Valid: " . ($result['is_valid'] ? 'Yes' : 'No') . "\n";
    echo "Score: " . $result['deliverability_score'] . "/100\n";
}
?>
```

---

## 🟦 Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type EmailValidationRequest struct {
    Email     string `json:"email"`
    CheckSMTP bool   `json:"check_smtp"`
}

type MXRecord struct {
    Host     string `json:"host"`
    Priority int    `json:"priority"`
}

type EmailValidationResponse struct {
    Email              string     `json:"email"`
    IsValid            bool       `json:"is_valid"`
    SyntaxValid        bool       `json:"syntax_valid"`
    Domain             string     `json:"domain"`
    HasMXRecords       bool       `json:"has_mx_records"`
    MXRecords          []MXRecord `json:"mx_records"`
    IsDisposable       bool       `json:"is_disposable"`
    DeliverabilityScore float64   `json:"deliverability_score"`
    ProcessingTimeMs   float64   `json:"processing_time_ms"`
}

func validateEmail(email string) (*EmailValidationResponse, error) {
    url := "http://localhost:8000/api/v1/validate"
    
    reqBody := EmailValidationRequest{
        Email:     email,
        CheckSMTP: false,
    }
    
    jsonData, err := json.Marshal(reqBody)
    if err != nil {
        return nil, err
    }
    
    resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result EmailValidationResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }
    
    return &result, nil
}

func main() {
    result, err := validateEmail("test@gmail.com")
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    
    fmt.Printf("Email: %s\n", result.Email)
    fmt.Printf("Valid: %v\n", result.IsValid)
    fmt.Printf("Score: %.2f/100\n", result.DeliverabilityScore)
}
```

---

## 📊 Casos de uso comunes

### 1. Validación en formulario de registro

```javascript
// Frontend validation on form submit
async function handleRegistration(formData) {
  const email = formData.get('email');
  
  // Validate email before creating account
  const validation = await validateEmail(email, false);
  
  if (!validation.is_valid) {
    return {
      error: 'Invalid email address',
      details: validation
    };
  }
  
  if (validation.is_disposable) {
    return {
      error: 'Temporary emails are not allowed',
      details: validation
    };
  }
  
  if (validation.deliverability_score < 70) {
    return {
      warning: 'This email may have delivery issues',
      details: validation
    };
  }
  
  // Proceed with registration
  return { success: true };
}
```

### 2. Limpieza de lista de emails

```python
import csv

def clean_email_list(input_file, output_file, min_score=50):
    """
    Lee una lista de emails, los valida y guarda solo los válidos
    """
    valid_emails = []
    
    with open(input_file, 'r') as f:
        emails = [line.strip() for line in f]
    
    # Validar en lotes de 100
    for i in range(0, len(emails), 100):
        batch = emails[i:i+100]
        
        response = requests.post(
            f"{API_URL}/validate/bulk",
            json={"emails": batch, "check_smtp": False}
        )
        
        results = response.json()['results']
        
        # Filtrar emails válidos
        for result in results:
            if (result['is_valid'] and 
                not result['is_disposable'] and 
                result['deliverability_score'] >= min_score):
                valid_emails.append(result['email'])
    
    # Guardar lista limpia
    with open(output_file, 'w') as f:
        for email in valid_emails:
            f.write(f"{email}\n")
    
    print(f"Procesados: {len(emails)}")
    print(f"Válidos: {len(valid_emails)}")
    print(f"Tasa de validez: {len(valid_emails)/len(emails)*100:.1f}%")
```

### 3. Webhook para procesamiento asíncrono

```python
# Webhook handler (FastAPI)
@app.post("/webhook/email-validated")
async def email_validation_webhook(data: dict):
    """
    Recibe notificaciones de validación completada
    """
    email = data['email']
    score = data['deliverability_score']
    
    # Actualizar base de datos
    await update_user_email_status(email, score)
    
    # Enviar notificación si es necesario
    if score < 50:
        await notify_admin_low_score(email)
    
    return {"status": "processed"}
```

---

## 🔧 Manejo de errores comunes

```python
def handle_validation_response(response):
    """Maneja diferentes códigos de respuesta"""
    
    if response.status_code == 200:
        return response.json()
    
    elif response.status_code == 400:
        print("Error: Email inválido o request mal formado")
        print(response.json())
        return None
    
    elif response.status_code == 429:
        print("Error: Límite de rate excedido")
        print("Espera antes de hacer más requests")
        return None
    
    elif response.status_code == 500:
        print("Error del servidor")
        print("Intenta de nuevo más tarde")
        return None
    
    else:
        print(f"Error inesperado: {response.status_code}")
        return None
```

---

## 📝 Notas importantes

1. **Rate Limiting**: Respeta los límites de tu plan
2. **SMTP Checks**: Son más lentos, úsalos solo cuando sea necesario
3. **Bulk Validation**: Máximo 100 emails por request
4. **Timeouts**: Configura timeouts apropiados (10-30s recomendado)
5. **Error Handling**: Siempre maneja errores de red y API

---

**Última actualización**: Febrero 2024
