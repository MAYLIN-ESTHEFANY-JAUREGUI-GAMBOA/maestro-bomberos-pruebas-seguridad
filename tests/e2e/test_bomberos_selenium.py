
import os
import threading
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from app import create_app, db


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_SELENIUM") != "1",
    reason="Configura RUN_SELENIUM=1 para ejecutar las pruebas de navegador.",
)


@pytest.fixture()
def browser_app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'selenium.db'}",
            "SECRET_KEY": "selenium-test-key",
        }
    )

    with app.app_context():
        db.create_all()

    server = make_server("127.0.0.1", 0, app)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"

    finally:
        server.shutdown()
        thread.join(timeout=5)

        with app.app_context():
            db.drop_all()


def test_register_bombero_from_directory(browser_app):

    options = webdriver.ChromeOptions()

    # Mostrar Chrome normalmente, sin modo oculto
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    evidencia = Path(__file__).resolve().parents[1] / "evidencias"
    evidencia.mkdir(parents=True, exist_ok=True)

    try:
        print("\nAbriendo aplicación Flask...")
        driver.get(browser_app)

        wait = WebDriverWait(driver, 15)

        # Esperar formulario de registro
        wait.until(
            EC.presence_of_element_located(
                (By.ID, "formBombero")
            )
        )

        print("Formulario encontrado.")

        # Captura antes del registro
        driver.save_screenshot(
            str(evidencia / "01_selenium_antes_registro.png")
        )

        # Datos del nuevo bombero
        print("Ingresando datos del bombero...")

        driver.find_element(By.ID, "dni").send_keys("87654321")
        driver.find_element(By.ID, "nombres").send_keys("Elena")
        driver.find_element(By.ID, "apellidos").send_keys("Vargas")
        driver.find_element(By.ID, "especialidad").send_keys("Rescate")

        # Guardar registro
        print("Guardando bombero...")
        driver.find_element(By.ID, "btnGuardar").click()

        # Esperar que aparezca en el listado
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "listaBomberos"),
                "Elena Vargas"
            )
        )

        # Verificar DNI
        lista = driver.find_element(By.ID, "listaBomberos")

        assert "87654321" in lista.text

        print("\nREGISTRO EXITOSO")
        print("Bombero: Elena Vargas")
        print("DNI: 87654321")
        print("Especialidad: Rescate")

        # Captura después del registro
        driver.save_screenshot(
            str(evidencia / "02_despues_registro.png")
        )

        print(f"\nCapturas guardadas en: {evidencia}")

        assert "Elena Vargas" in lista.text

    except Exception:
        # Guardar captura si ocurre algún error
        driver.save_screenshot(
            str(evidencia / "error_selenium.png")
        )
        raise

    finally:
        # Mantener Chrome abierto hasta presionar ENTER
        try:
            input("\nPresiona ENTER en PowerShell para cerrar Chrome...")
        except EOFError:
            pass

        driver.quit()
