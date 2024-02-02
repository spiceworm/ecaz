# Run Locally
```bash
# Run locally
docker compose up --build

# Flask shell
docker exec -it ecaz_xyz-app-1 flask shell

# Flask CLI commands
docker exec -it ecaz_xyz-app-1 flask shell
```

# Helper Scripts
## Database
### Connect to postgres database
```bash
docker exec -it ecaz-app-1 ./db.sh
```

### Execute query in postgres database
```bash
docker exec -it ecaz-app-1 ./db.sh "SELECT * FROM public.user;"
```

## Debugging
### Stop all gunicorn workers in and start a single worker in the foreground
```bash
# This makes it easy to see tracebacks or drop into ipython
docker exec -it ecaz-app-1 ./debug.sh
```

## Deploy to production
```bash
./deploy.py [--push] [--tag TAG]
```

## Run tests
```bash
./test.sh
# or
./test.sh 'application/tests/test_some_file.py::test_some_function'
```

# API
```python
import requests

jwt = ""  # Generate JWT through UI after logging in
url = 'http://localhost'  # or 'https://ecaz.xyz'
resp = requests.get(f'{url}/api/v1/comment/<comment-id>', headers={'Authorization': f'Bearer {jwt}'})
resp.json()
```
