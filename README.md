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
