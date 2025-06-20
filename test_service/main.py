from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import requests
import logging
import os
import json
from datetime import datetime
import uvicorn

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Test Service",
    description="Microserviço para testar o serviço LLM",
    version="1.0.0"
)

# Configuração de templates (para interface web simples)
templates = Jinja2Templates(directory="templates")

# URL do serviço LLM (configurável via variável de ambiente)
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8000")

# Modelos para requisições e respostas
class TestRequest(BaseModel):
    artifacts: List[str]
    platform: str
    model: str
    prompt: str

class TestResponse(BaseModel):
    test_id: str
    llm_request: TestRequest
    llm_response: Dict[str, Any]
    status: str
    timestamp: str
    test_duration_ms: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    llm_service_status: str

# Cliente para comunicação com o serviço LLM
class LLMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def check_health(self) -> bool:
        """Verifica se o serviço LLM está saudável"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do serviço LLM: {e}")
            return False
    
    def get_supported_models(self) -> List[str]:
        """Obtém os modelos suportados pelo serviço LLM"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                return response.json().get("supported_models", [])
            return []
        except Exception as e:
            logger.error(f"Erro ao obter modelos suportados: {e}")
            return []
    
    def get_supported_platforms(self) -> List[str]:
        """Obtém as plataformas suportadas pelo serviço LLM"""
        try:
            response = requests.get(f"{self.base_url}/platforms", timeout=5)
            if response.status_code == 200:
                return response.json().get("supported_platforms", [])
            return []
        except Exception as e:
            logger.error(f"Erro ao obter plataformas suportadas: {e}")
            return []
    
    def process_request(self, request: TestRequest) -> Dict[str, Any]:
        """Envia requisição para o serviço LLM"""
        try:
            payload = {
                "artifacts": request.artifacts,
                "platform": request.platform,
                "model": request.model,
                "prompt": request.prompt
            }
            
            response = requests.post(
                f"{self.base_url}/process",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro do serviço LLM: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de comunicação com serviço LLM: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Serviço LLM indisponível: {str(e)}"
            )

# Instância do cliente LLM
llm_client = LLMClient(LLM_SERVICE_URL)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check"""
    llm_healthy = llm_client.check_health()
    return HealthResponse(
        status="healthy" if llm_healthy else "degraded",
        timestamp=datetime.now().isoformat(),
        llm_service_status="healthy" if llm_healthy else "unhealthy"
    )

@app.get("/")
async def root():
    """Endpoint raiz com informações do serviço"""
    return {
        "service": "LLM Test Service",
        "version": "1.0.0",
        "description": "Microserviço para testar o serviço LLM",
        "llm_service_url": LLM_SERVICE_URL,
        "endpoints": {
            "health": "/health",
            "test": "/test",
            "models": "/models",
            "platforms": "/platforms",
            "ui": "/ui"
        }
    }

@app.get("/models")
async def get_supported_models():
    """Retorna os modelos suportados pelo serviço LLM"""
    models = llm_client.get_supported_models()
    return {
        "supported_models": models,
        "count": len(models),
        "source": "llm_service"
    }

@app.get("/platforms")
async def get_supported_platforms():
    """Retorna as plataformas suportadas pelo serviço LLM"""
    platforms = llm_client.get_supported_platforms()
    return {
        "supported_platforms": platforms,
        "count": len(platforms),
        "source": "llm_service"
    }

@app.post("/test", response_model=TestResponse)
async def test_llm_service(request: TestRequest):
    """Endpoint principal para testar o serviço LLM"""
    start_time = datetime.now()
    test_id = f"test_{int(start_time.timestamp() * 1000)}"
    
    try:
        logger.info(f"Iniciando teste {test_id}")
        
        # Enviar requisição para o serviço LLM
        llm_response = llm_client.process_request(request)
        
        # Calcular tempo de teste
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f"Teste {test_id} concluído com sucesso em {test_duration:.2f}ms")
        
        return TestResponse(
            test_id=test_id,
            llm_request=request,
            llm_response=llm_response,
            status="success",
            timestamp=end_time.isoformat(),
            test_duration_ms=test_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no teste {test_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/ui", response_class=HTMLResponse)
async def test_ui(request: Request):
    """Interface web simples para testar o serviço LLM"""
    models = llm_client.get_supported_models()
    platforms = llm_client.get_supported_platforms()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Test Service</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select, textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            textarea {{ height: 100px; }}
            button {{ background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background-color: #0056b3; }}
            .result {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }}
            .error {{ background-color: #f8d7da; color: #721c24; }}
            .success {{ background-color: #d4edda; color: #155724; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LLM Test Service</h1>
            <p>Interface para testar o microserviço LLM</p>
            
            <form id="testForm">
                <div class="form-group">
                    <label for="artifacts">Artefatos (um por linha):</label>
                    <textarea id="artifacts" placeholder="Documento de requisitos&#10;Modelo conceitual&#10;Código fonte"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="platform">Plataforma:</label>
                    <select id="platform">
                        {"".join(f'<option value="{p}">{p}</option>' for p in platforms)}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="model">Modelo:</label>
                    <select id="model">
                        {"".join(f'<option value="{m}">{m}</option>' for m in models)}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="prompt">Prompt:</label>
                    <textarea id="prompt" placeholder="Digite seu prompt em linguagem natural aqui..."></textarea>
                </div>
                
                <button type="submit">Testar LLM</button>
            </form>
            
            <div id="result"></div>
        </div>
        
        <script>
            document.getElementById('testForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const artifacts = document.getElementById('artifacts').value.split('\\n').filter(a => a.trim());
                const platform = document.getElementById('platform').value;
                const model = document.getElementById('model').value;
                const prompt = document.getElementById('prompt').value;
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>Processando...</p>';
                
                try {{
                    const response = await fetch('/test', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            artifacts: artifacts,
                            platform: platform,
                            model: model,
                            prompt: prompt
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>Resultado do Teste</h3>
                            <p><strong>Test ID:</strong> ${{data.test_id}}</p>
                            <p><strong>Status:</strong> ${{data.status}}</p>
                            <p><strong>Tempo de Processamento:</strong> ${{data.test_duration_ms.toFixed(2)}}ms</p>
                            <h4>Resposta da LLM:</h4>
                            <pre>${{data.llm_response.response_text}}</pre>
                            <h4>Metadados:</h4>
                            <pre>${{JSON.stringify(data.llm_response.metadata, null, 2)}}</pre>
                        `;
                    }} else {{
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<h3>Erro</h3><p>${{data.detail}}</p>`;
                    }}
                }} catch (error) {{
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<h3>Erro</h3><p>Erro de comunicação: ${{error.message}}</p>`;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

