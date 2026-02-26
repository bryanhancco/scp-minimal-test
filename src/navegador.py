from selenium.webdriver.common.by import By
import time

class Navegador:
    def __init__(self, driver):
        self.driver = driver
    
    def _cerrar_recaptcha(self):
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                if "recaptcha" in iframe.get_attribute("src").lower():
                    self.driver.execute_script("""
                        var iframes = document.getElementsByTagName('iframe');
                        for(var i = 0; i < iframes.length; i++) {
                            if(iframes[i].src.toLowerCase().indexOf('recaptcha') !== -1) {
                                iframes[i].style.display = 'none';
                            }
                        }
                    """)
                    time.sleep(1)
                    return True
        except:
            pass
        return False
    
    def click_numero_pagina(self, numero):
        try:
            self._cerrar_recaptcha()
            time.sleep(2)
            
            paginas = self.driver.find_elements(By.CLASS_NAME, "ui-paginator-page")
            for pagina in paginas:
                if pagina.text == str(numero):
                    if "ui-state-active" not in pagina.get_attribute("class"):
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagina)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", pagina)
                        except:
                            pagina.click()
                        time.sleep(4)
                        return True
            return False
        except Exception as e:
            print(f"Error click_numero_pagina: {e}")
            return False
    
    def ir_siguiente_pagina(self):
        try:
            self._cerrar_recaptcha()
            time.sleep(2)
            
            boton = self.driver.find_element(By.CLASS_NAME, "ui-paginator-next")
            if "ui-state-disabled" in boton.get_attribute("class"):
                return False
            
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", boton)
            except:
                boton.click()
            
            time.sleep(4)
            return True
        except Exception as e:
            print(f"Error ir_siguiente_pagina: {e}")
            return False