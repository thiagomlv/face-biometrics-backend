### Face biometrics system backend

1. Compilar imagem base

```bash
docker build -f Dockerfile_Base -t thiagomlv/faceid-backend-base-final:v1 .
```

2. Compilar a imagem principal

```bash
docker compose build
```