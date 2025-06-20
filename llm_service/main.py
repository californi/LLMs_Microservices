from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import os
import json
from datetime import datetime
import uvicorn

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Microservice",
    description="Microserviço para processamento de LLM local offline",
    version="1.0.0"
)

# Modelos Pydantic para requisições e respostas
class LLMRequest(BaseModel):
    artifacts: List[str]  # Artefatos base (documentos, modelos, código fonte, etc.)
    platform: str  # Plataforma (huggingface, openai, etc.)
    model: str  # Modelo LLM (llama, deepseek, etc.)
    prompt: str  # Prompt em linguagem natural
    
class LLMResponse(BaseModel):
    request_id: str
    status: str
    response_text: str
    metadata: Dict[str, Any]
    timestamp: str
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Simulação de processamento LLM (substitua pela implementação real)
class LLMProcessor:
    def __init__(self):
        self.supported_platforms = ["huggingface", "openai", "local", "ollama"]
        self.supported_models = ["llama", "deepseek", "gpt", "mistral", "phi"]
        
    def validate_request(self, request: LLMRequest) -> bool:
        """Valida se a requisição está correta"""
        if request.platform.lower() not in self.supported_platforms:
            raise HTTPException(
                status_code=400, 
                detail=f"Plataforma '{request.platform}' não suportada. Plataformas suportadas: {self.supported_platforms}"
            )
        
        if not any(model in request.model.lower() for model in self.supported_models):
            raise HTTPException(
                status_code=400, 
                detail=f"Modelo '{request.model}' não suportado. Modelos suportados: {self.supported_models}"
            )
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt não pode estar vazio")
            
        return True
    
    def process_artifacts(self, artifacts: List[str]) -> str:
        """Processa os artefatos fornecidos"""
        if not artifacts:
            return "Nenhum artefato fornecido"
        
        artifact_summary = f"Processando {len(artifacts)} artefato(s): "
        for i, artifact in enumerate(artifacts[:3]):  # Limita a 3 para não ficar muito longo
            artifact_summary += f"\n- Artefato {i+1}: {artifact[:100]}..."
        
        if len(artifacts) > 3:
            artifact_summary += f"\n- ... e mais {len(artifacts) - 3} artefato(s)"
            
        return artifact_summary
    
    def generate_response(self, request: LLMRequest) -> str:
        """Simula a geração de resposta da LLM"""
        # Esta é uma simulação. Em uma implementação real, você integraria com:
        # - Hugging Face Transformers
        # - OpenAI API
        # - Ollama
        # - Modelos locais, etc.
        
        artifact_context = self.process_artifacts(request.artifacts)
        
        # Simulação de resposta baseada no prompt e contexto
        response = f"""
Resposta gerada pela LLM {request.model} na plataforma {request.platform}:

Contexto dos Artefatos:
{artifact_context}

Prompt Original: "{request.prompt}"

Resposta Simulada:
Com base nos artefatos fornecidos e no prompt "{request.prompt}", 
a análise indica que o sistema deve considerar os seguintes aspectos:

1. Análise dos artefatos fornecidos
2. Aplicação do modelo {request.model} para processamento
3. Geração de resposta contextualizada

Esta é uma resposta simulada. Em produção, seria gerada pelo modelo real {request.model}.
        """.strip()
        
        return response

# Instância do processador LLM
llm_processor = LLMProcessor()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Endpoint raiz com informações do serviço"""
    return {
        "service": "LLM Microservice",
        "version": "1.0.0",
        "description": "Microserviço para processamento de LLM local offline",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "models": "/models",
            "platforms": "/platforms"
        }
    }

@app.get("/models")
async def get_supported_models():
    """Retorna os modelos suportados"""
    return {
        "supported_models": llm_processor.supported_models,
        "count": len(llm_processor.supported_models)
    }

@app.get("/platforms")
async def get_supported_platforms():
    """Retorna as plataformas suportadas"""
    return {
        "supported_platforms": llm_processor.supported_platforms,
        "count": len(llm_processor.supported_platforms)
    }

@app.post("/process", response_model=LLMResponse)
async def process_llm_request(request: LLMRequest):
    """Endpoint principal para processamento de requisições LLM"""
    start_time = datetime.now()
    request_id = f"req_{int(start_time.timestamp() * 1000)}"
    
    try:
        logger.info(f"Processando requisição {request_id}")
        
        # Validar requisição
        llm_processor.validate_request(request)
        
        # Processar com LLM
        response_text = llm_processor.generate_response(request)
        
        # Calcular tempo de processamento
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        # Metadados da resposta
        metadata = {
            "platform_used": request.platform,
            "model_used": request.model,
            "artifacts_count": len(request.artifacts),
            "prompt_length": len(request.prompt),
            "response_length": len(response_text)
        }
        
        logger.info(f"Requisição {request_id} processada com sucesso em {processing_time:.2f}ms")
        
        return LLMResponse(
            request_id=request_id,
            status="success",
            response_text=response_text,
            metadata=metadata,
            timestamp=end_time.isoformat(),
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar requisição {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

