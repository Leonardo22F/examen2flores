# Calculadora Flask (CI/CD)

Aplicacion Flask con un servicio de calculadora que acepta expresiones matematicas y frases sencillas en lenguaje natural. Incluye pruebas con pytest, contenedor Docker y pipeline CI/CD para publicar la imagen en GHCR y desplegarla en un VPS mediante `docker stack deploy`.

## Uso local
1. Crea y activa un entorno virtual (opcional).
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la app:
   ```bash
   python app.py
   ```
4. Endpoints:
   - `GET /health` -> `{"status": "ok"}`
   - `POST /api/calc` con JSON `{"input": "suma 5 y 3"}` o `{"input": "2+2*2"}`

## Pruebas
```bash
pytest
```

## Contenedor
```bash
docker build -t ghcr.io/<owner>/almachi:1.0.6 .
docker run -p 5000:5000 ghcr.io/<owner>/almachi:1.0.6
```

## Pipeline CI/CD (GitHub Actions)
- Rama de trabajo: `almachi` (segundo apellido).
- Jobs:
  - `test`: instala dependencias y ejecuta `pytest`.
- `build_and_push`: construye la imagen y la publica en GHCR con tags `1.0.6` y `latest` (`ghcr.io/<owner>/almachi`).
  - `deploy`: copia `stack.yml` al VPS y despliega con `docker stack deploy` usando la imagen publicada.

### Secrets requeridos
- `GHCR_PAT`: token con permiso `packages:write`.
- `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD`, `VPS_SSH_PORT`: credenciales SSH al VPS.
- `STACK_NAME`: nombre del stack a desplegar en el servidor (ej. `almachi-stack`).

## Stack de despliegue
`stack.yml` usa variables de entorno `GH_OWNER` y `IMAGE_VERSION` (por defecto `1.0.6`). El job de deploy exporta estas variables antes de ejecutar:
```bash
docker stack deploy -c stack.yml <STACK_NAME>
```

## Subdominio
Asegura que el subdominio `almachi.byronrm.com` apunte al VPS donde se levanta el stack para completar la evidencia del despliegue.
