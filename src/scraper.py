import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import platform
import os
import zipfile
from dotenv import load_dotenv

load_dotenv()

from config import URL, TIMEOUT, OBJETO_CONTRATACION, REPO_PATH, PALABRAS_CLAVE, FILTRO_PALABRAS_CLAVE_HABILITADO

class SEACEScraper:
    def __init__(self):
        download_dir = os.path.join(REPO_PATH, "documentos_descargados")
        download_dir = os.path.abspath(download_dir)
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        if platform.system() == "Linux":
            try:
                from pyvirtualdisplay import Display
                # Iniciar display virtual (Xvfb) para engañar al WAF en EC2
                self.display = Display(visible=0, size=(1920, 1080))
                self.display.start()
            except FileNotFoundError:
                print("❌ ERROR CRÍTICO EN EC2: Falta instalar Xvfb.")
                print("Ejecuta en tu terminal de AWS: sudo dnf install -y xorg-x11-server-Xvfb")
                raise
            except Exception as e:
                print(f"⚠ Advertencia con display virtual: {e}")
                self.display = None
        else:
            self.display = None
        
        options = uc.ChromeOptions()
        
        # Integración dinámica de Proxys con usuario y contraseña
        proxy_host = os.environ.get("PROXY_HOST")
        proxy_port = os.environ.get("PROXY_PORT")
        proxy_user = os.environ.get("PROXY_USER")
        proxy_pass = os.environ.get("PROXY_PASS")

        if proxy_host and proxy_port:
            print(f"✓ Proxy Autenticado configurado: {proxy_host}:{proxy_port}")
            manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""
            background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (proxy_host, proxy_port, proxy_user, proxy_pass)

            plugin_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'proxy_auth_plugin')
            os.makedirs(plugin_dir, exist_ok=True)
            
            with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
                f.write(manifest_json)
            with open(os.path.join(plugin_dir, "background.js"), "w") as f:
                f.write(background_js)
            
            options.add_argument(f'--load-extension={plugin_dir}')
            
        elif os.environ.get("PROXY_URL"):
            # Para proxies sin usuario y contraseña (vía IP authorization)
            proxy_url = os.environ.get("PROXY_URL")
            print(f"✓ Proxy (sin auth) configurado: {proxy_url}")
            options.add_argument(f'--proxy-server={proxy_url}')

        # En Windows siempre usamos headless=new para que no te moleste la ventana popup.
        # En Linux (EC2) NO USAMOS headless porque Xvfb ya lo hace invisible y Cloudflare detecta el bot si lo mandamos.
        if platform.system() == "Windows":
            options.add_argument("--headless=new")
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-setuid-sandbox")
        
        # Eliminar el user-agent de Windows en Linux y puertos de debug que WAFs de Cloudflare detectan
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing.disable_download_protection": True
        }
        options.add_experimental_option("prefs", prefs)

        # Forzamos la versión 145 del driver para que coincida con la versión instalada en EC2
        self.driver = uc.Chrome(options=options, version_main=145, use_subprocess=True)

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
                    print(self.driver.page_source[:1000])
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
        if hasattr(self, 'display') and self.display:
            self.display.stop()