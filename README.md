# Speedtest Monitor con Supabase

Monitor de velocidad de internet que ejecuta tests automáticos cada 30 minutos, guarda los resultados en Supabase y los muestra en un dashboard web.

## Arquitectura

- **speedtest.py**: Script que ejecuta el test y guarda en Supabase (corre en Docker con cron)
- **dashboard.html**: Dashboard estático para visualizar los datos (deploy en Cloudflare Worker u otro)
- **Supabase**: Base de datos PostgreSQL para almacenar los resultados

## Requisitos

- Docker y Docker Compose
- Cuenta en [Supabase](https://supabase.com) (gratis)
- (Opcional) Bot de Telegram para alertas

## Setup

### 1. Configurar Supabase

1. Crear un proyecto en Supabase
2. Ir a SQL Editor y ejecutar el contenido de `supabase/schema.sql`
3. Copiar las credenciales desde Settings > API:
   - `Project URL` → SUPABASE_URL
   - `anon public` key → SUPABASE_ANON_KEY

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=eyJ...

# Opcional - Alertas por Telegram
TELEGRAM_TOKEN=tu-bot-token
TELEGRAM_CHAT_ID=tu-chat-id
ERROR_REPORTING=TRUE
SPEED_THRESHOLD_MBPS=50
```

### 3. Ejecutar con Docker

```bash
docker-compose up -d --build
```

El script se ejecutará cada 30 minutos (en el minuto 0 y 30 de cada hora).

### 4. Configurar Dashboard

Editar `dashboard.html` y reemplazar las credenciales:

```javascript
const SUPABASE_URL = 'https://tu-proyecto.supabase.co';
const SUPABASE_ANON_KEY = 'eyJ...';
const SPEED_THRESHOLD_MBPS = 50;
```

Luego subir el archivo a tu Cloudflare Worker o hosting estático.

## Comandos útiles

```bash
# Ver logs del cron
docker-compose logs -f

# Ejecutar test manualmente
docker-compose exec speedtest python /app/speedtest.py

# Ver logs del speedtest
docker-compose exec speedtest cat /var/log/cron.log

# Reiniciar
docker-compose restart

# Detener
docker-compose down
```

## Alertas

Si configuras `SPEED_THRESHOLD_MBPS`, recibirás una alerta por Telegram cuando la velocidad de descarga sea menor al umbral configurado.

## Estructura de archivos

```
speedtest/
├── speedtest.py          # Script principal
├── Dockerfile
├── docker-compose.yml
├── .env                  # Variables de entorno (no commitear)
├── .env.example          # Ejemplo de configuración
├── dashboard.html        # Dashboard para Cloudflare Worker
├── supabase/
│   └── schema.sql        # Schema de la base de datos
└── README.md
```

## Seguridad

- `SUPABASE_ANON_KEY` es una clave pública por diseño, segura para exponer en el cliente
- La seguridad está en las políticas RLS (Row Level Security) de Supabase
- Nunca expongas la `service_role` key
