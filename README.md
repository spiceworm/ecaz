```bash
cd ~/hdd1_cloud/programming/python/ecaz_xyz

# Run locally
docker compose up --build

# Flask shell
docker exec -it ecaz_xyz-app-1 flask shell

# Deploy
docker compose build \
  && docker tag ecaz_xyz-app:latest registry.digitalocean.com/ecaz-xyz/app:0.1.0 \
  && docker push registry.digitalocean.com/ecaz-xyz/app:0.1.0
```

```python
# API Example
import requests

jwt = ""  # Generate JWT through UI after logging in
resp = requests.get('http://127.0.0.1/api/v1/user', headers={'Authorization': f'Bearer {jwt}'})
resp.json()
```
