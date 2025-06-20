# LLM Microservices Project

A complete microservices solution for local offline LLM processing with FastAPI, Docker, and Kubernetes deployment.

## 🚀 Overview

This project consists of two microservices:

1. **LLM Service** - A FastAPI microservice that processes LLM requests with configurable platforms and models
2. **Test Service** - A FastAPI microservice for testing the LLM service with a web interface

## 📋 Features

- **Generic LLM Interface**: Supports multiple platforms (HuggingFace, OpenAI, Local, Ollama) and models (Llama, DeepSeek, GPT, Mistral, Phi)
- **Artifact Processing**: Handles various input artifacts (documents, models, source code, etc.)
- **RESTful APIs**: Well-documented FastAPI endpoints with automatic OpenAPI documentation
- **Web Interface**: Simple web UI for testing the LLM service
- **Docker Support**: Complete containerization with optimized Dockerfiles
- **Kubernetes Ready**: Production-ready Kubernetes manifests
- **Automated Deployment**: Shell script for build, push, and deployment to Minikube

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Test Service  │ ──────────────► │   LLM Service   │
│   (Port 8001)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
        │                                   │
        │                                   │
        ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Web UI        │                 │ LLM Processing  │
│   /ui endpoint  │                 │ Engine          │
└─────────────────┘                 └─────────────────┘
```

## 📁 Project Structure

```
llm_microservices_project/
├── llm_service/
│   ├── main.py              # LLM service FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Docker configuration
├── test_service/
│   ├── main.py              # Test service FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Docker configuration
├── k8s/
│   ├── llm-service.yaml     # Kubernetes manifests for LLM service
│   └── test-service.yaml   # Kubernetes manifests for Test service
├── scripts/
│   └── deploy.sh           # Automated deployment script
└── README.md               # This file
```

## 🛠️ Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Python 3.11+ (for local development)
- DockerHub account (for pushing images)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd llm_microservices_project

# Make deployment script executable
chmod +x scripts/deploy.sh
```

### 2. Configure DockerHub Username

Edit the following files and replace `your-dockerhub-username` with your actual DockerHub username:

- `scripts/deploy.sh` (line 9)
- `k8s/llm-service.yaml` (line 18)
- `k8s/test-service.yaml` (line 18)

### 3. Deploy to Minikube

```bash
# Build and deploy locally (without pushing to DockerHub)
./scripts/deploy.sh

# Or build, push to DockerHub, and deploy
./scripts/deploy.sh --push
```

### 4. Access Services

After successful deployment, the script will display the service URLs:

- **LLM Service**: `http://<minikube-ip>:30000`
- **Test Service**: `http://<minikube-ip>:30001`
- **Web UI**: `http://<minikube-ip>:30001/ui`

## 📖 API Documentation

### LLM Service Endpoints

#### POST /process
Process an LLM request with the following parameters:

```json
{
  "artifacts": ["Document content", "Model description", "Source code"],
  "platform": "huggingface",
  "model": "llama",
  "prompt": "Your natural language prompt here"
}
```

**Response:**
```json
{
  "request_id": "req_1234567890",
  "status": "success",
  "response_text": "Generated LLM response...",
  "metadata": {
    "platform_used": "huggingface",
    "model_used": "llama",
    "artifacts_count": 3,
    "prompt_length": 50,
    "response_length": 200
  },
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 1500.0
}
```

#### GET /health
Health check endpoint

#### GET /models
Get supported models

#### GET /platforms
Get supported platforms

### Test Service Endpoints

#### POST /test
Test the LLM service with the same request format as `/process`

#### GET /ui
Web interface for testing

#### GET /health
Health check with LLM service status

## 🔧 Local Development

### Running Services Locally

#### LLM Service
```bash
cd llm_service
pip install -r requirements.txt
python main.py
# Service available at http://localhost:8000
```

#### Test Service
```bash
cd test_service
pip install -r requirements.txt
LLM_SERVICE_URL=http://localhost:8000 python main.py
# Service available at http://localhost:8001
```

### Building Docker Images

```bash
# Build LLM Service
cd llm_service
docker build -t your-dockerhub-username/llm-service:latest .

# Build Test Service
cd test_service
docker build -t your-dockerhub-username/test-service:latest .
```

## 🐳 Docker Compose (Alternative)

For local testing without Kubernetes:

```yaml
version: '3.8'
services:
  llm-service:
    build: ./llm_service
    ports:
      - "8000:8000"
    
  test-service:
    build: ./test_service
    ports:
      - "8001:8001"
    environment:
      - LLM_SERVICE_URL=http://llm-service:8000
    depends_on:
      - llm-service
```

## 🎯 Usage Examples

### Using the Web Interface

1. Navigate to `http://<minikube-ip>:30001/ui`
2. Fill in the form:
   - **Artifacts**: Enter one artifact per line (e.g., "Requirements document", "UML model")
   - **Platform**: Select from dropdown (huggingface, openai, local, ollama)
   - **Model**: Select from dropdown (llama, deepseek, gpt, mistral, phi)
   - **Prompt**: Enter your natural language prompt
3. Click "Test LLM" to see results

### Using cURL

```bash
# Test LLM Service directly
curl -X POST "http://<minikube-ip>:30000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "artifacts": ["System requirements", "Architecture diagram"],
    "platform": "huggingface",
    "model": "llama",
    "prompt": "Analyze the system requirements and suggest improvements"
  }'

# Test via Test Service
curl -X POST "http://<minikube-ip>:30001/test" \
  -H "Content-Type: application/json" \
  -d '{
    "artifacts": ["Code review checklist"],
    "platform": "local",
    "model": "mistral",
    "prompt": "Generate a comprehensive code review based on the checklist"
  }'
```

## 🔍 Monitoring and Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n llm-microservices
kubectl logs -f deployment/llm-service -n llm-microservices
kubectl logs -f deployment/test-service -n llm-microservices
```

### Check Service Status
```bash
kubectl get services -n llm-microservices
```

### Access Service URLs
```bash
minikube service llm-service -n llm-microservices --url
minikube service test-service -n llm-microservices --url
```

## 🧹 Cleanup

To remove the deployment:

```bash
./scripts/deploy.sh --cleanup
```

## 🔧 Configuration

### Environment Variables

#### LLM Service
- `PORT`: Service port (default: 8000)

#### Test Service
- `PORT`: Service port (default: 8001)
- `LLM_SERVICE_URL`: URL of the LLM service (default: http://llm-service:8000)

### Kubernetes Resources

Both services are configured with:
- **Resource Requests**: CPU and memory requests for scheduling
- **Resource Limits**: Maximum CPU and memory usage
- **Health Checks**: Liveness and readiness probes
- **NodePort Services**: External access via Minikube

## 🚀 Production Considerations

1. **Security**: Add authentication and authorization
2. **Scaling**: Configure horizontal pod autoscaling
3. **Monitoring**: Add Prometheus metrics and Grafana dashboards
4. **Logging**: Implement structured logging with ELK stack
5. **Storage**: Add persistent volumes for model caching
6. **Load Balancing**: Use Ingress controllers for production traffic
7. **Secrets Management**: Use Kubernetes secrets for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Kubernetes logs
3. Verify Docker and Minikube status
4. Open an issue with detailed error information

---

**Happy coding! 🎉**

