import pytest
from fastapi.testclient import TestClient
from CartaPerfecta import app
import os

client = TestClient(app)

def test_home_page():
    """Probar que la página inicial carga correctamente"""
    response = client.get("/")
    assert response.status_code == 200
    assert "CartaPerfecta" in response.text

def test_generate_cv():
    """Probar la generación de CV con datos válidos"""
    data = {
        "name": "Test User",
        "position": "Software Developer",
        "skills": "Python, FastAPI",
        "experience": "5 years of development",
        "style": "Professional"
    }
    response = client.post("/generate", data=data)
    assert response.status_code == 200
    assert "Test User" in response.text
    assert "Software Developer" in response.text

def test_invalid_data():
    """Probar el manejo de datos inválidos"""
    data = {
        "name": "",  # Campo requerido vacío
        "position": "Software Developer",
        "skills": "Python, FastAPI",
        "experience": "5 years of development",
        "style": "Professional"
    }
    response = client.post("/generate", data=data)
    assert response.status_code == 422  # Validación fallida

def test_required_files():
    """Verificar que existen los archivos necesarios"""
    # Verificar archivos estáticos
    assert os.path.exists("app/static/style.css")
    assert os.path.exists("app/static/example.pdf")
    
    # Verificar plantillas
    assert os.path.exists("app/templates/index.html")
    assert os.path.exists("app/templates/result.html")

def test_result_page():
    """Probar la página de resultados"""
    response = client.get("/result")
    assert response.status_code == 200

def test_pdf_generation():
    """Probar la descarga del PDF"""
    response = client.get("/download-pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_static_files():
    """Probar que los archivos estáticos se sirven correctamente"""
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/css; charset=utf-8"