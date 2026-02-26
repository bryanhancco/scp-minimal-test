from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class FiltroEntidad:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
    
    def aplicar_filtro(self, tipo, valor):
        if tipo == "sigla":
            return self._filtrar_por_sigla(valor)
        elif tipo == "ruc":
            return self._filtrar_por_ruc(valor)
        elif tipo == "nombre":
            return self._filtrar_por_nombre(valor)
        return False
    
    def _filtrar_por_sigla(self, sigla):
        try:
            print(f"\n{'='*60}")
            print(f"FILTRO DE ENTIDAD POR SIGLA: {sigla}")
            print(f"{'='*60}")
            
            boton_lupa = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "tbBuscador:idFormBuscarProceso:ajax")
            ))
            boton_lupa.click()
            time.sleep(2)
            
            campo_sigla = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:txtsigla")
            ))
            campo_sigla.clear()
            campo_sigla.send_keys(sigla)
            time.sleep(1)
            
            boton_buscar = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarEntidad")
            boton_buscar.click()
            time.sleep(3)
            
            return self._seleccionar_entidad()
            
        except Exception as e:
            print(f"Error al filtrar por sigla: {e}")
            return False
    
    def _filtrar_por_ruc(self, ruc):
        try:
            print(f"\n{'='*60}")
            print(f"FILTRO DE ENTIDAD POR RUC: {ruc}")
            print(f"{'='*60}")
            
            boton_lupa = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "tbBuscador:idFormBuscarProceso:ajax")
            ))
            boton_lupa.click()
            time.sleep(2)
            
            campo_ruc = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:txtRucEntidad")
            ))
            campo_ruc.clear()
            campo_ruc.send_keys(ruc)
            time.sleep(1)
            
            boton_buscar = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarEntidad")
            boton_buscar.click()
            time.sleep(3)
            
            return self._seleccionar_entidad()
            
        except Exception as e:
            print(f"Error al filtrar por RUC: {e}")
            return False
    
    def _filtrar_por_nombre(self, nombre):
        try:
            print(f"\n{'='*60}")
            print(f"FILTRO DE ENTIDAD POR NOMBRE: {nombre}")
            print(f"{'='*60}")
            
            boton_lupa = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "tbBuscador:idFormBuscarProceso:ajax")
            ))
            boton_lupa.click()
            time.sleep(2)
            
            campo_nombre = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:txtNombreEntidad")
            ))
            campo_nombre.clear()
            campo_nombre.send_keys(nombre)
            time.sleep(1)
            
            boton_buscar = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarEntidad")
            boton_buscar.click()
            time.sleep(3)
            
            return self._seleccionar_entidad()
            
        except Exception as e:
            print(f"Error al filtrar por nombre: {e}")
            return False
    
    def _seleccionar_entidad(self):
        try:
            tabla = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:dataTable_data")
            ))
            
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            
            if not filas:
                print("⚠ No se encontraron entidades")
                return False
            
            opciones = []
            for i, fila in enumerate(filas):
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 4:
                    numero = celdas[0].text.strip()
                    ruc = celdas[1].text.strip()
                    entidad = celdas[3].text.strip()
                    opciones.append({
                        'numero': numero,
                        'ruc': ruc,
                        'entidad': entidad,
                        'indice': i
                    })
            
            if len(opciones) == 0:
                print("⚠ No se encontraron entidades")
                return False
            
            if len(opciones) == 1:
                print(f"\n✓ Se encontró 1 entidad:")
                print(f"  {opciones[0]['numero']}. {opciones[0]['entidad']} (RUC: {opciones[0]['ruc']})")
                print(f"  Seleccionando automáticamente...")
                seleccion = 0
            else:
                print(f"\n✓ Se encontraron {len(opciones)} entidades:")
                for opcion in opciones:
                    print(f"  {opcion['numero']}. {opcion['entidad']} (RUC: {opcion['ruc']})")
                
                print(f"\n{'─'*60}")
                while True:
                    try:
                        respuesta = input(f"Selecciona el número de entidad (1-{len(opciones)}): ")
                        seleccion = int(respuesta) - 1
                        if 0 <= seleccion < len(opciones):
                            break
                        else:
                            print(f"⚠ Número fuera de rango. Ingresa un valor entre 1 y {len(opciones)}")
                    except ValueError:
                        print("⚠ Ingresa un número válido")
                print(f"{'─'*60}\n")
            
            entidad_seleccionada = opciones[seleccion]
            print(f"✓ Seleccionada: {entidad_seleccionada['entidad']}")
            
            boton_seleccionar = self.driver.find_element(
                By.ID, 
                f"tbBuscador:idFormBuscarProceso:dataTable:{entidad_seleccionada['indice']}:ajax"
            )
            boton_seleccionar.click()
            time.sleep(2)
            
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"Error al seleccionar entidad: {e}")
            return False