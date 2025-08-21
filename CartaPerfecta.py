import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import logging

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = None if not OPENROUTER_API_KEY else OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def get_example_content(name: str, position: str, skills: str, experience: str, style: str) -> tuple[str, str]:
    cv_content = f"""CV para {name}
=================
Experiencia Profesional:
- {experience}

Habilidades:
- {skills}"""

    cover_letter_content = f"""Estimado/a Responsable de Recursos Humanos,

Me dirijo a usted para expresar mi interés en la posición de {position}. Con una sólida experiencia en {experience}, y habilidades en {skills}, considero que puedo aportar valor significativo a su organización.

Mi estilo {style} y enfoque profesional se alinean perfectamente con los requisitos del puesto.

Agradezco su tiempo y consideración.

Atentamente,
{name}"""

    return cv_content, cover_letter_content

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(
    request: Request,
    name: str = Form(...),
    position: str = Form(...),
    skills: str = Form(...),
    experience: str = Form(...),
    style: str = Form(...)
):
    try:
        if client is None:
            generated_text = get_example_content(name, position, skills, experience, style)
        else:
            completion = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en redacción de CVs y cartas de presentación."
                    },
                    {
                        "role": "user",
                        "content": f"Genera un CV y una carta de presentación para {name}, que busca trabajo como {position}. Sus habilidades son: {skills}. Su experiencia incluye: {experience}. El estilo debe ser {style}."
                    }
                ]
            )
            generated_text = completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating content: {str(e)}")
        generated_text = get_example_content(name, position, skills, experience, style)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "name": name,
            "position": position,
            "generated_text": generated_text
        }
    )

@app.get("/download-pdf")
async def download_pdf():
    return FileResponse(
        "app/static/example.pdf",
        media_type="application/pdf",
        filename="cv_carta.pdf"
    )