# Deployment Guide - Soul Astro Engine

This guide covers deploying the Soul Astro Engine to Docker Hub using GitHub Actions.

## Prerequisites

1. **Docker Hub Account**: Create an account at [hub.docker.com](https://hub.docker.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **GitHub Secrets**: Configure the required secrets in your repository

## Setup Instructions

### 1. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

> **Note**: For better security, use a Docker Hub access token instead of your password.

### 2. Repository Structure

Ensure your repository has this structure:
```
soul-astro-engine/
├── .github/
│   └── workflows/
│       └── docker-deploy.yml
├── app/
│   ├── astro/
│   ├── core/
│   └── main.py
├── ephe/
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

### 3. Automatic Deployment

The GitHub Actions workflow will automatically:

- **Build** the Docker image on every push to `main` or `develop` branches
- **Push** to Docker Hub with appropriate tags
- **Scan** for security vulnerabilities
- **Support** multi-architecture builds (AMD64 and ARM64)

#### Trigger Events:
- Push to `main` or `develop` branches
- Create tags (e.g., `v1.0.0`)
- Pull requests (build only, no push)

## Manual Deployment

If you prefer to build and push manually:

### 1. Build the Image
```bash
# Build locally
docker build -t your-username/soul-astro-engine:latest .

# Test locally
docker run -p 8000:8000 your-username/soul-astro-engine:latest
```

### 2. Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Push the image
docker push your-username/soul-astro-engine:latest
```

## Using the Deployed Image

### Pull and Run
```bash
# Pull the latest image
docker pull your-username/soul-astro-engine:latest

# Run the container
docker run -p 8000:8000 your-username/soul-astro-engine:latest
```

### Environment Variables
```bash
# Run with custom environment variables
docker run -p 8000:8000 \
  -e APP_VERSION=1.0.0 \
  -e SWE_EPHE_PATH=/app/ephe \
  your-username/soul-astro-engine:latest
```

### Health Check
The container includes a health check endpoint:
```bash
# Check container health
curl http://localhost:8000/health

# Expected response: {"status": "ok"}
```

## Image Tags

The workflow creates multiple tags for different scenarios:

- `latest`: Latest version from main branch
- `develop`: Latest version from develop branch
- `v1.0.0`: Specific version tags
- `v1.0`: Major.minor version
- `v1`: Major version only

## Monitoring and Logs

### View Container Logs
```bash
# Get container ID
docker ps

# View logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>
```

### Container Health
```bash
# Check container status
docker ps

# Inspect container health
docker inspect <container-id> | grep -A 10 "Health"
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check GitHub Actions logs for specific error messages
   - Ensure all dependencies are in `requirements.txt`
   - Verify Dockerfile syntax

2. **Push Failures**
   - Verify Docker Hub credentials in GitHub Secrets
   - Check if the repository name matches your Docker Hub username

3. **Runtime Issues**
   - Check container logs: `docker logs <container-id>`
   - Verify environment variables are set correctly
   - Ensure the `ephe/` directory is properly included

### Debug Mode

To run in debug mode:
```bash
docker run -p 8000:8000 \
  -e DEBUG=true \
  your-username/soul-astro-engine:latest
```

## Security Features

The deployment includes:
- **Multi-stage builds** for smaller production images
- **Non-root user** execution
- **Security scanning** with Trivy
- **Minimal base image** (Python slim)
- **Health checks** for container monitoring

## Production Considerations

1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Restart Policy**: Use `unless-stopped` restart policy
3. **Logging**: Configure log rotation and monitoring
4. **Updates**: Use specific version tags in production
5. **Backup**: Ensure ephemeris data is backed up

## Support

For deployment issues:
1. Check GitHub Actions workflow logs
2. Review container logs
3. Verify Docker Hub repository permissions
4. Open an issue in the repository
