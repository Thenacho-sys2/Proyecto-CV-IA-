from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Solo crear el cliente si tenemos una API key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
) if OPENROUTER_API_KEY else None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Página inicial con el formulario"""
    return templates.TemplateResponse(request, "index.html", {"title": "CartaPerfecta"})

@app.get("/result", response_class=HTMLResponse)
def result_page(request: Request):
    """Página de resultado"""
    return templates.TemplateResponse(request, "result.html", {"title": "CartaPerfecta"})

@app.post("/generate", response_class=HTMLResponse)
async def generate_content(
    request: Request,
    name: str = Form(...),
    position: str = Form(...),
    skills: str = Form(...),
    experience: str = Form(...),
    style: str = Form(...)
):
    """Generar CV y carta de presentación"""
    try:
        # Validar datos de entrada
        if not name or not position or not skills or not experience or not style:
            raise HTTPException(status_code=422, detail="Todos los campos son requeridos")

        # Función para generar contenido de ejemplo
        def get_example_content():
            return f"""
            # CV para {name}
            
            ## Información Personal
            - Nombre: {name}
            - Posición: {position}
            
            ## Habilidades
            {skills}
            
            ## Experiencia
            {experience}
            
            # Carta de Presentación
            
            Estimado/a responsable de contratación,
            
            Me dirijo a usted para expresar mi interés en la posición de {position}. Con mis habilidades en {skills} y mi experiencia de {experience}, creo que puedo aportar valor significativo a su organización.
            
            Atentamente,
            {name}
            """

        # En modo prueba o si hay error de créditos, devolver contenido de ejemplo
        if not client:
            logger.info("Modo prueba: generando contenido de ejemplo")
            generated_text = get_example_content()
        else:
            try:
                logger.info("Modo producción: usando OpenAI para generar contenido")
                prompt = f"""
                Generar un CV y una carta de presentación para:
                
                Nombre: {name}
                Posición: {position}
                Habilidades: {skills}
                Experiencia: {experience}
                Estilo: {style}
                """

                completion = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "CartaPerfecta"
                    },
                    model="openai/gpt-4",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000
                )
                generated_text = completion.choices[0].message.content
            except Exception as api_error:
                # Si hay error de créditos (402) o cualquier error de API, usar contenido de ejemplo
                logger.warning(f"Error de API OpenAI, usando contenido de ejemplo: {str(api_error)}")
                generated_text = get_example_content()

        logger.info("Contenido generado exitosamente")
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "title": "CartaPerfecta",
                "generated_text": generated_text,
                "name": name,
                "position": position
            }
        )
    except HTTPException as he:
        logger.error(f"Error de validación: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-pdf")
async def download_pdf(request: Request):
    """Descargar CV como PDF"""
    try:
        # Aquí iría la lógica de generación del PDF
        # Por ahora, devolvemos un archivo de ejemplo
        pdf_path = os.path.join(os.path.dirname(__file__), "app", "static", "example.pdf")
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF no encontrado")
        return FileResponse(pdf_path, filename="cv.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
