import os
import sys

# Ensure the 'src' directory is in PYTHONPATH so absolute imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import SEACEScraper
from extractor import Extractor
from navegador import Navegador
from navegador_ficha import NavegadorFicha
from extractor_ficha import ExtractorFicha
from exportador import Exportador
from filtro_entidad import FiltroEntidad
from config import (ANIOS, LIMITE_PAGINAS, REPO_PATH, 
                    LIMITE_REGISTROS_POR_PAGINA, FILTRO_ENTIDAD_HABILITADO, 
                    FILTRO_ENTIDAD_TIPO, FILTRO_ENTIDAD_SIGLA, FILTRO_ENTIDAD_RUC,
                    FILTRO_ENTIDAD_NOMBRE, FILTRO_PALABRAS_CLAVE_HABILITADO,
                    FILTRO_NOMENCLATURA_HABILITADO, FILTRO_NOMENCLATURA,
                    PALABRAS_CLAVE, HABILITAR_ESCANEO_PDF)
import shutil

def normalizar_nomenclatura(nomenclatura):
    return nomenclatura.strip().upper().replace(" ", "").replace("-", "").replace("/", "")

def main():
    download_dir = os.path.join(REPO_PATH, "documentos_descargados")
    
    print("\n" + "="*60)
    print("PREPARANDO ENTORNO")
    print("="*60)
    
    if os.path.exists(download_dir):
        print(f"Eliminando carpeta existente: {download_dir}")
        shutil.rmtree(download_dir)
        print("✓ Carpeta eliminada")
    
    os.makedirs(download_dir)
    print(f"✓ Carpeta creada: {download_dir}")
    
    if LIMITE_REGISTROS_POR_PAGINA:
        print(f"⚠ MODO PRUEBA: Procesando solo {LIMITE_REGISTROS_POR_PAGINA} registro(s) por página")
    
    if HABILITAR_ESCANEO_PDF:
        print(f"✓ Escaneo de PDF ACTIVADO")
    else:
        print(f"⚠ Escaneo de PDF DESACTIVADO")
    
    if FILTRO_PALABRAS_CLAVE_HABILITADO and not FILTRO_ENTIDAD_HABILITADO and not FILTRO_NOMENCLATURA_HABILITADO:
        print(f"✓ Filtro de palabras clave ACTIVO ({len(PALABRAS_CLAVE)} palabras)")
    elif FILTRO_PALABRAS_CLAVE_HABILITADO:
        print(f"⚠ Filtro de palabras clave DESACTIVADO (filtro de entidad/nomenclatura tiene prioridad)")
    else:
        print(f"⚠ Filtro de palabras clave DESACTIVADO")
    
    if FILTRO_ENTIDAD_HABILITADO:
        if FILTRO_ENTIDAD_TIPO == "sigla":
            print(f"✓ Filtro de entidad ACTIVO por SIGLA: {FILTRO_ENTIDAD_SIGLA}")
        elif FILTRO_ENTIDAD_TIPO == "ruc":
            print(f"✓ Filtro de entidad ACTIVO por RUC: {FILTRO_ENTIDAD_RUC}")
        elif FILTRO_ENTIDAD_TIPO == "nombre":
            print(f"✓ Filtro de entidad ACTIVO por NOMBRE: {FILTRO_ENTIDAD_NOMBRE}")
    
    if FILTRO_NOMENCLATURA_HABILITADO:
        print(f"✓ Filtro de nomenclatura ACTIVO: {FILTRO_NOMENCLATURA}")
    
    print("="*60 + "\n")
    
    scraper = SEACEScraper()
    
    try:
        scraper.abrir_pagina()
        scraper.click_tab_procedimientos()
        
        extractor = Extractor(scraper.driver)
        navegador = Navegador(scraper.driver)
        nav_ficha = NavegadorFicha(scraper.driver)
        ext_ficha = ExtractorFicha(scraper.driver)
        
        if FILTRO_ENTIDAD_HABILITADO:
            filtro_entidad = FiltroEntidad(scraper.driver)
            
            if FILTRO_ENTIDAD_TIPO == "sigla":
                valor = FILTRO_ENTIDAD_SIGLA
            elif FILTRO_ENTIDAD_TIPO == "ruc":
                valor = FILTRO_ENTIDAD_RUC
            elif FILTRO_ENTIDAD_TIPO == "nombre":
                valor = FILTRO_ENTIDAD_NOMBRE
            else:
                print(f"⚠ Tipo de filtro inválido: {FILTRO_ENTIDAD_TIPO}")
                valor = None
            
            if valor:
                if not filtro_entidad.aplicar_filtro(FILTRO_ENTIDAD_TIPO, valor):
                    print("⚠ No se pudo aplicar el filtro de entidad. Continuando sin filtro...")
        
        nav_ficha.guardar_ventana_principal()
        datos_totales = []
        nomenclaturas_procesadas = set()
        
        nomenclatura_buscada_normalizada = None
        if FILTRO_NOMENCLATURA_HABILITADO:
            nomenclatura_buscada_normalizada = normalizar_nomenclatura(FILTRO_NOMENCLATURA)
        
        if FILTRO_ENTIDAD_HABILITADO or FILTRO_NOMENCLATURA_HABILITADO:
            palabras_a_buscar = [""]
        elif FILTRO_PALABRAS_CLAVE_HABILITADO:
            palabras_a_buscar = PALABRAS_CLAVE
        else:
            palabras_a_buscar = [""]
        
        for palabra_idx, palabra_clave in enumerate(palabras_a_buscar, 1):
            
            if FILTRO_PALABRAS_CLAVE_HABILITADO and not FILTRO_NOMENCLATURA_HABILITADO and not FILTRO_ENTIDAD_HABILITADO:
                print(f"\n{'='*60}")
                print(f"PALABRA CLAVE {palabra_idx}/{len(palabras_a_buscar)}: {palabra_clave}")
                print(f"{'='*60}")
            
            for anio in ANIOS:
                print(f"\n{'='*60}")
                print(f"PROCESANDO AÑO {anio}")
                print(f"{'='*60}")
                
                scraper.seleccionar_objeto_contratacion()
                scraper.seleccionar_anio(anio)
                
                if FILTRO_PALABRAS_CLAVE_HABILITADO and palabra_clave and not FILTRO_NOMENCLATURA_HABILITADO and not FILTRO_ENTIDAD_HABILITADO:
                    scraper.aplicar_filtro_descripcion(palabra_clave)
                
                scraper.click_buscar()
                scraper.esperar_resultados()
                
                pagina_actual, total_paginas = extractor.obtener_info_paginacion()
                print(f"Total páginas: {total_paginas}")
                
                if FILTRO_NOMENCLATURA_HABILITADO:
                    print(f"Buscando nomenclatura en todas las páginas...")
                elif LIMITE_PAGINAS:
                    print(f"Procesando solo {LIMITE_PAGINAS} página(s) para prueba")
                    total_paginas = min(LIMITE_PAGINAS, total_paginas)
                
                for num_pagina in range(1, total_paginas + 1):
                    print(f"\n{'─'*60}")
                    print(f"Página {num_pagina}/{total_paginas}")
                    print(f"{'─'*60}")
                    
                    datos_pagina = extractor.extraer_datos_pagina()
                    
                    if FILTRO_NOMENCLATURA_HABILITADO:
                        datos_filtrados = []
                        for d in datos_pagina:
                            nomenclatura_dato = normalizar_nomenclatura(d.get('Nomenclatura', ''))
                            if nomenclatura_dato == nomenclatura_buscada_normalizada:
                                datos_filtrados.append(d)
                                print(f"✓ ENCONTRADO: {d.get('Nomenclatura')}")
                        print(f"Total: {len(datos_pagina)} | Filtrado por nomenclatura: {len(datos_filtrados)}")
                    else:
                        datos_filtrados = datos_pagina
                        print(f"Total: {len(datos_pagina)}")
                    
                    if LIMITE_REGISTROS_POR_PAGINA and not FILTRO_NOMENCLATURA_HABILITADO:
                        datos_filtrados = datos_filtrados[:LIMITE_REGISTROS_POR_PAGINA]
                        print(f"Procesando: {LIMITE_REGISTROS_POR_PAGINA}")
                    
                    for idx, dato in enumerate(datos_filtrados):
                        nomenclatura = dato['Nomenclatura']
                        
                        if nomenclatura in nomenclaturas_procesadas:
                            print(f"  [{idx+1}/{len(datos_filtrados)}] {nomenclatura} - ⚠ Ya procesado, omitiendo")
                            continue
                        
                        print(f"  [{idx+1}/{len(datos_filtrados)}] {nomenclatura}")
                        
                        if nav_ficha.click_ficha_seleccion(dato['Indice']):
                            info_ficha = ext_ficha.extraer_todo(nomenclatura)
                            dato.update(info_ficha)
                            nav_ficha.click_regresar()
                        
                        del dato['Indice']
                        datos_totales.append(dato)
                        nomenclaturas_procesadas.add(nomenclatura)
                    
                    print(f"✓ Página {num_pagina} completada ({len(datos_totales)} registros únicos acumulados)")
                    
                    if FILTRO_NOMENCLATURA_HABILITADO and len(datos_totales) > 0:
                        print(f"✓ Nomenclatura encontrada, deteniendo búsqueda")
                        break
                    
                    if num_pagina < total_paginas:
                        print(f"→ Navegando a página {num_pagina + 1}...")
                        if not navegador.click_numero_pagina(num_pagina + 1):
                            print("  Intento 1 falló, probando botón siguiente...")
                            if not navegador.ir_siguiente_pagina():
                                print("  ⚠ No se pudo navegar, deteniendo...")
                                break
                        else:
                            print(f"  ✓ En página {num_pagina + 1}")
                
                if FILTRO_NOMENCLATURA_HABILITADO and len(datos_totales) > 0:
                    break
            
            if FILTRO_NOMENCLATURA_HABILITADO and len(datos_totales) > 0:
                break
        
        if FILTRO_NOMENCLATURA_HABILITADO and len(datos_totales) == 0:
            print(f"\n⚠ No se encontró la nomenclatura: {FILTRO_NOMENCLATURA}")
            print(f"   Verifica que la nomenclatura sea correcta y esté en el año {ANIOS}")
        
        print(f"\n{'='*60}")
        print(f"RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Total registros únicos filtrados: {len(datos_totales)}")
        
        for dato in datos_totales:
            if dato.get('Documento_Path'):
                dato['Documento_URL'] = dato['Documento_Path']
        
        exportador = Exportador()
        ruta_excel = exportador.exportar_excel(datos_totales)
        print(f"✓ Excel generado exitosamente en: {ruta_excel}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCerrando navegador...")
        scraper.cerrar()

if __name__ == "__main__":
    main()