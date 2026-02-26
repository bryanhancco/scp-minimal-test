from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
from config import URL, TIMEOUT, OBJETO_CONTRATACION, REPO_PATH, PALABRAS_CLAVE, FILTRO_PALABRAS_CLAVE_HABILITADO

class SEACEScraper:
    def __init__(self):
        download_dir = os.path.join(REPO_PATH, "documentos_descargados")
        download_dir = os.path.abspath(download_dir)
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--remote-debugging-port=9222")

        # User-agent real para evitar bloqueos
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0,
            "plugins.always_open_pdf_externally": True,
            "download.extensions_to_open": "",
            "safebrowsing.disable_download_protection": True
        }
        options.add_experimental_option("prefs", prefs)

        # webdriver-manager instala automáticamente el ChromeDriver correcto
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": download_dir
        })
        
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.url = URL
        
    def abrir_pagina(self):
        print("Abriendo página de SEACE...")
        self.driver.get(self.url)
        time.sleep(8)  # más tiempo en CI para que cargue completamente
        
    def click_tab_procedimientos(self):
        print("Navegando a pestaña de Procedimientos de Selección...")
        try:
            tab = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '#tbBuscador:tab1')]")
            ))
            tab.click()
        except:
            try:
                # Intentar por texto si el href cambia
                tab = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Procedimientos')]")
                ))
                tab.click()
            except Exception as e:
                screenshot_path = os.path.join(os.path.abspath("."), "error_ec2_pantalla.png")
                try:
                    self.driver.save_screenshot(screenshot_path)
                    print(f"\n❌ ERROR de Timeout: El elemento no se pudo clickear.")
                    print(f"⚠ SE HA GUARDADO UNA CAPTURA DE PANTALLA EN: {screenshot_path}")
                    print("Por favor, revisa ese archivo para ver si el sitio está bloqueando tu IP (Cloudflare/Captcha) o si no ha terminado de cargar.")
                except:
                    pass
                raise e
        time.sleep(4)
        print("✓ Pestaña activa")
    
    def seleccionar_objeto_contratacion(self):
        print(f"Seleccionando Objeto de Contratación: {OBJETO_CONTRATACION}")
        try:
            time.sleep(2)
            select_element = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:j_idt188_input")
            ))
            Select(select_element).select_by_visible_text(OBJETO_CONTRATACION)
            time.sleep(1)
            print(f"✓ {OBJETO_CONTRATACION} seleccionado")
        except:
            script = f"""
            var select = document.getElementById('tbBuscador:idFormBuscarProceso:j_idt188_input');
            select.value = '65';
            select.dispatchEvent(new Event('change'));
            """
            self.driver.execute_script(script)
            time.sleep(1)
            print(f"✓ {OBJETO_CONTRATACION} seleccionado (método alternativo)")
    
    def seleccionar_anio(self, anio):
        print(f"Seleccionando año {anio}...")
        try:
            time.sleep(2)
            select_element = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:anioConvocatoria_input")
            ))
            Select(select_element).select_by_value(str(anio))
            time.sleep(1)
            print(f"✓ Año {anio} seleccionado")
        except:
            script = f"""
            var select = document.getElementById('tbBuscador:idFormBuscarProceso:anioConvocatoria_input');
            select.value = '{anio}';
            select.dispatchEvent(new Event('change'));
            """
            self.driver.execute_script(script)
            time.sleep(1)
            print(f"✓ Año {anio} seleccionado (método alternativo)")
    
    def aplicar_filtro_descripcion(self, palabra_clave):
        print(f"Aplicando filtro: {palabra_clave}")
        try:
            campo_descripcion = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:descripcionObjeto")
            ))
            campo_descripcion.clear()
            campo_descripcion.send_keys(palabra_clave)
            time.sleep(1)
            print(f"✓ Filtro aplicado: {palabra_clave}")
        except Exception as e:
            print(f"⚠ Error al aplicar filtro de descripción: {e}")
    
    def click_buscar(self):
        print("Ejecutando búsqueda...")
        boton = self.wait.until(EC.element_to_be_clickable(
            (By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarSelToken")
        ))
        boton.click()
        time.sleep(4)
        print("✓ Búsqueda ejecutada")
    
    def esperar_resultados(self):
        self.wait.until(EC.presence_of_element_located(
            (By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
        ))
        time.sleep(2)
    
    def cerrar(self):
        self.driver.quit()