```bash
# Run locally
docker compose up --build

# Flask shell
docker exec -it ecaz_xyz-app-1 flask shell

# Deploy
# Bump TAG in deploy.sh and run it
./deploy.sh

# Run tests
./test.sh
```

```python
# API Example
import requests

jwt = ""  # Generate JWT through UI after logging in

local_instance = 'http://127.0.0.1'
production_instance = 'https://ecaz.xyz'

# Send API call to local or production instance
resp = requests.get(f'{production_instance}/api/v1/user', headers={'Authorization': f'Bearer {jwt}'})
resp.json()
```
