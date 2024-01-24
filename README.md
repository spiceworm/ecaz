# Run Locally
```bash
# Run locally
docker compose up --build

# Flask shell
docker exec -it ecaz_xyz-app-1 flask shell
```

# Helper Scripts
## Database
### Connect to postgres database
```bash
./db.sh
```

### Execute query in postgres database
```bash
./db.sh "SELECT * FROM public.user;"
```

## Debugging
### Stop all gunicorn workers in and start a single worker in the foreground
```bash
# This makes it easy to see tracebacks or drop into ipython
./debug.sh
```

## Deploy to production
```bash
# Make sure to bump TAG in deploy.sh
./deploy.sh
```

## Run test suite
```bash
./test.sh
```

# API
```python
import requests

jwt = ""  # Generate JWT through UI after logging in
url = 'http://127.0.0.1'  # or 'https://ecaz.xyz'
resp = requests.get(f'{url}/api/v1/user', headers={'Authorization': f'Bearer {jwt}'})
resp.json()
```
