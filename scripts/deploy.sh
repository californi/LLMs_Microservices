#!/bin/bash

# Script para build, push e deploy dos microserviços LLM no Minikube
# Autor: Sistema LLM Microservices
# Data: $(date)

set -e  # Parar execução em caso de erro

# Configurações
DOCKER_REGISTRY="your-dockerhub-username"  # Substitua pelo seu username do DockerHub
LLM_SERVICE_IMAGE="llm-service"
TEST_SERVICE_IMAGE="test-service"
VERSION="latest"
NAMESPACE="llm-microservices"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se o Docker está rodando
check_docker() {
    log "Verificando se o Docker está rodando..."
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Por favor, inicie o Docker e tente novamente."
    fi
    success "Docker está rodando"
}

# Verificar se o Minikube está rodando
check_minikube() {
    log "Verificando se o Minikube está rodando..."
    if ! minikube status > /dev/null 2>&1; then
        warning "Minikube não está rodando. Tentando iniciar..."
        minikube start
    fi
    success "Minikube está rodando"
}

# Verificar se o kubectl está configurado
check_kubectl() {
    log "Verificando configuração do kubectl..."
    if ! kubectl cluster-info > /dev/null 2>&1; then
        error "kubectl não está configurado corretamente"
    fi
    success "kubectl está configurado"
}

# Configurar Docker para usar o registry do Minikube
configure_docker_minikube() {
    log "Configurando Docker para usar o registry do Minikube..."
    eval $(minikube docker-env)
    success "Docker configurado para Minikube"
}

# Build das imagens Docker
build_images() {
    log "Iniciando build das imagens Docker..."
    
    # Build da imagem do serviço LLM
    log "Building LLM Service..."
    cd llm_service
    docker build -t ${DOCKER_REGISTRY}/${LLM_SERVICE_IMAGE}:${VERSION} .
    success "LLM Service image built successfully"
    cd ..
    
    # Build da imagem do serviço de teste
    log "Building Test Service..."
    cd test_service
    docker build -t ${DOCKER_REGISTRY}/${TEST_SERVICE_IMAGE}:${VERSION} .
    success "Test Service image built successfully"
    cd ..
    
    success "Todas as imagens foram construídas com sucesso"
}

# Push das imagens para o DockerHub (opcional)
push_images() {
    if [ "$1" = "--push" ]; then
        log "Fazendo push das imagens para o DockerHub..."
        
        # Login no DockerHub (se necessário)
        log "Fazendo login no DockerHub..."
        docker login
        
        # Push das imagens
        docker push ${DOCKER_REGISTRY}/${LLM_SERVICE_IMAGE}:${VERSION}
        docker push ${DOCKER_REGISTRY}/${TEST_SERVICE_IMAGE}:${VERSION}
        
        success "Imagens enviadas para o DockerHub"
    else
        log "Pulando push para DockerHub (use --push para enviar)"
    fi
}

# Criar namespace
create_namespace() {
    log "Criando namespace ${NAMESPACE}..."
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    success "Namespace ${NAMESPACE} criado/atualizado"
}

# Deploy no Kubernetes
deploy_to_kubernetes() {
    log "Iniciando deploy no Kubernetes..."
    
    # Aplicar manifestos
    kubectl apply -f k8s/ -n ${NAMESPACE}
    
    success "Deploy realizado com sucesso"
}

# Aguardar pods ficarem prontos
wait_for_pods() {
    log "Aguardando pods ficarem prontos..."
    
    kubectl wait --for=condition=ready pod -l app=llm-service -n ${NAMESPACE} --timeout=300s
    kubectl wait --for=condition=ready pod -l app=test-service -n ${NAMESPACE} --timeout=300s
    
    success "Todos os pods estão prontos"
}

# Mostrar status do deployment
show_status() {
    log "Status do deployment:"
    echo ""
    kubectl get pods -n ${NAMESPACE}
    echo ""
    kubectl get services -n ${NAMESPACE}
    echo ""
    
    # Obter URLs dos serviços
    LLM_SERVICE_URL=$(minikube service llm-service -n ${NAMESPACE} --url)
    TEST_SERVICE_URL=$(minikube service test-service -n ${NAMESPACE} --url)
    
    echo -e "${GREEN}Serviços disponíveis:${NC}"
    echo -e "LLM Service: ${BLUE}${LLM_SERVICE_URL}${NC}"
    echo -e "Test Service: ${BLUE}${TEST_SERVICE_URL}${NC}"
    echo -e "Test Service UI: ${BLUE}${TEST_SERVICE_URL}/ui${NC}"
}

# Função para limpeza
cleanup() {
    if [ "$1" = "--cleanup" ]; then
        log "Removendo deployment..."
        kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
        success "Deployment removido"
        exit 0
    fi
}

# Função de ajuda
show_help() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --push      Faz push das imagens para o DockerHub"
    echo "  --cleanup   Remove o deployment do Kubernetes"
    echo "  --help      Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                    # Build e deploy local"
    echo "  $0 --push           # Build, push e deploy"
    echo "  $0 --cleanup        # Remove deployment"
}

# Função principal
main() {
    log "Iniciando script de deploy dos microserviços LLM..."
    
    # Verificar argumentos
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --cleanup)
            cleanup --cleanup
            ;;
    esac
    
    # Verificações iniciais
    check_docker
    check_minikube
    check_kubectl
    
    # Configurar Docker para Minikube (se não estiver fazendo push)
    if [ "$1" != "--push" ]; then
        configure_docker_minikube
    fi
    
    # Build das imagens
    build_images
    
    # Push das imagens (se solicitado)
    push_images $1
    
    # Deploy no Kubernetes
    create_namespace
    deploy_to_kubernetes
    wait_for_pods
    show_status
    
    success "Deploy concluído com sucesso!"
    echo ""
    echo -e "${YELLOW}Para acessar os serviços, use os URLs mostrados acima.${NC}"
    echo -e "${YELLOW}Para remover o deployment, execute: $0 --cleanup${NC}"
}

# Executar função principal com todos os argumentos
main "$@"

