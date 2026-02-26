import pdfplumber
import re
from docx import Document

class PDFExtractor:
    def __init__(self):
        pass
    
    def extraer_informacion(self, pdf_path):
        if not pdf_path or pdf_path == "":
            return self._datos_vacios()
        
        if pdf_path.endswith('.crdownload'):
            return self._datos_vacios()
        
        if pdf_path.endswith('.zip'):
            return self._datos_zip_rar()
        
        if pdf_path.endswith('.rar'):
            return self._datos_zip_rar()
        
        try:
            texto_completo = ""
            
            if pdf_path.endswith('.pdf'):
                with pdfplumber.open(pdf_path) as pdf:
                    for pagina in pdf.pages:
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            texto_completo += texto_pagina + "\n"
            
            elif pdf_path.endswith('.docx'):
                doc = Document(pdf_path)
                for para in doc.paragraphs:
                    texto_completo += para.text + "\n"
            
            else:
                return self._datos_vacios()
            
            if len(texto_completo.strip()) < 50:
                return self._datos_vacios()
            
            return {
                'Estado': self._extraer_estado(texto_completo),
                'Duracion_dias': self._extraer_duracion(texto_completo),
                'Ciudad': self._extraer_ciudad(texto_completo),
                'Modalidad_trabajo': self._extraer_modalidad(texto_completo),
                'Experiencia_requerida': self._extraer_experiencia(texto_completo),
                'Experiencia_minima_mype': self._extraer_experiencia_mype(texto_completo),
                'Servicios_similares': self._extraer_servicios_similares(texto_completo)
            }
        except Exception as e:
            return self._datos_vacios()
    
    def _datos_vacios(self):
        return {
            'Estado': '-',
            'Duracion_dias': '-',
            'Ciudad': '-',
            'Modalidad_trabajo': '-',
            'Experiencia_requerida': '-',
            'Experiencia_minima_mype': '-',
            'Servicios_similares': '-'
        }
    
    def _datos_zip_rar(self):
        return {
            'Estado': 'Archivo comprimido',
            'Duracion_dias': '-',
            'Ciudad': '-',
            'Modalidad_trabajo': '-',
            'Experiencia_requerida': '-',
            'Experiencia_minima_mype': '-',
            'Servicios_similares': '-'
        }
    
    def _extraer_estado(self, texto):
        texto_lower = texto.lower()
        
        if 'vigente' in texto_lower:
            return 'Vigente'
        
        patrones_estado = [
            r'estado\s*[:\-]?\s*(\w+)',
            r'situaci[oó]n\s*[:\-]?\s*(\w+)'
        ]
        
        for patron in patrones_estado:
            match = re.search(patron, texto_lower)
            if match:
                estado = match.group(1).strip().capitalize()
                if estado:
                    return estado
        
        return 'Vigente'
    
    def _extraer_duracion(self, texto):
        patrones = [
            r'plazo.*?(\d+)\s*d[íi]as?\s+calendario',
            r'plazo.*?(\d+)\s*d[íi]as?\s+h[aá]biles',
            r'duraci[óo]n.*?(\d+)\s*d[íi]as?\s+calendario',
            r'duraci[óo]n.*?(\d+)\s*d[íi]as?\s+h[aá]biles',
            r'(\d+)\s*d[íi]as?\s+calendario',
            r'plazo\s*[:\-]?\s*(\d+)\s*d[íi]as?',
            r'duraci[óo]n\s*[:\-]?\s*(\d+)\s*d[íi]as?',
            r'(\d+)\s*d[íi]as?\s+h[aá]biles',
        ]
        
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)
            if matches:
                numeros = []
                for m in matches:
                    try:
                        num = int(m)
                        if 1 <= num <= 3650:
                            numeros.append(num)
                    except:
                        continue
                if numeros:
                    return str(max(numeros))
        
        return '-'
    
    def _extraer_ciudad(self, texto):
        ciudades_peru = [
            'Lima', 'Arequipa', 'Trujillo', 'Chiclayo', 'Piura', 'Iquitos', 
            'Cusco', 'Huancayo', 'Tacna', 'Ica', 'Pucallpa', 'Chimbote',
            'Huánuco', 'Tarapoto', 'Juliaca', 'Ayacucho', 'Cajamarca',
            'Puno', 'Tumbes', 'Talara', 'Huaraz', 'Moquegua', 'Cerro de Pasco',
            'Abancay', 'Jaén', 'Sullana', 'Chincha', 'Barranca', 'Huacho',
            'Callao', 'Lambayeque', 'Ancash', 'Ucayali', 'San Martín'
        ]
        
        patrones_contexto = [
            r'(?:ciudad|lugar|ubicaci[óo]n|sede)\s*[:\-]?\s*([a-záéíóúñ\s]+)',
            r'(?:departamento|provincia)\s*[:\-]?\s*([a-záéíóúñ\s]+)',
        ]
        
        for patron in patrones_contexto:
            matches = re.findall(patron, texto, re.IGNORECASE)
            for match in matches:
                match_clean = match.strip()
                for ciudad in ciudades_peru:
                    if ciudad.lower() in match_clean.lower():
                        return ciudad
        
        texto_lines = texto.split('\n')
        for line in texto_lines[:150]:
            for ciudad in ciudades_peru:
                if ciudad.lower() in line.lower():
                    return ciudad
        
        for ciudad in ciudades_peru:
            if ciudad.lower() in texto.lower():
                return ciudad
        
        return '-'
    
    def _extraer_modalidad(self, texto):
        texto_lower = texto.lower()
        
        patron_modalidad = r'modalidad\s*(?:de\s*)?(?:trabajo|servicio|prestaci[óo]n)\s*[:\-]?\s*([a-záéíóúñ\s]+?)(?:\n|\.|\,)'
        match = re.search(patron_modalidad, texto_lower)
        if match:
            modalidad_texto = match.group(1).strip()
            if 'remoto' in modalidad_texto or 'virtual' in modalidad_texto:
                return 'Remoto'
            if 'presencial' in modalidad_texto:
                return 'Presencial'
            if 'hibrido' in modalidad_texto or 'híbrido' in modalidad_texto or 'mixto' in modalidad_texto:
                return 'Híbrido'
        
        conteo_remoto = len(re.findall(r'remoto|virtual|teletrabajo', texto_lower))
        conteo_presencial = len(re.findall(r'presencial|oficina|instalaciones', texto_lower))
        
        if conteo_remoto > 0 and conteo_presencial > 0:
            return 'Híbrido'
        elif conteo_remoto > conteo_presencial and conteo_remoto >= 2:
            return 'Remoto'
        elif conteo_presencial >= 2:
            return 'Presencial'
        
        return '-'
    
    def _extraer_experiencia(self, texto):
        patrones = [
            r'monto\s*(?:m[íi]nimo|total|acumulado)?\s*(?:de\s*)?(?:facturaci[óo]n|experiencia)\s*[:\-]?\s*S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'experiencia.*?(?:m[íi]nimo|igual|mayor)\s*(?:a|de)?\s*S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'facturaci[óo]n.*?S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'valor\s+referencial\s*[:\-]?\s*S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'S/?\.?\s*([\d,]+(?:\.\d{2})?)\s*(?:nuevos\s*)?soles',
            r'US\$\s*([\d,]+(?:\.\d{2})?)',
        ]
        
        montos_encontrados = []
        
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)
            for match in matches:
                monto_limpio = match.replace(',', '').replace(' ', '')
                try:
                    valor = float(monto_limpio)
                    if 1000 <= valor <= 100000000:
                        montos_encontrados.append((valor, match))
                except:
                    continue
        
        if montos_encontrados:
            monto_mayor = max(montos_encontrados, key=lambda x: x[0])
            return f"S/ {monto_mayor[1]}"
        
        return '-'
    
    def _extraer_experiencia_mype(self, texto):
        patrones = [
            r'mype.*?(?:m[íi]nimo|monto).*?S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'micro\s+y\s+peque[ñn]a\s+empresa.*?S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'experiencia.*?mype.*?S/?\.?\s*([\d,]+(?:\.\d{2})?)',
            r'facturaci[óo]n.*?mype.*?S/?\.?\s*([\d,]+(?:\.\d{2})?)',
        ]
        
        montos_encontrados = []
        
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)
            for match in matches:
                monto_limpio = match.replace(',', '').replace(' ', '')
                try:
                    valor = float(monto_limpio)
                    if 100 <= valor <= 100000000:
                        montos_encontrados.append((valor, match))
                except:
                    continue
        
        if montos_encontrados:
            monto_mayor = max(montos_encontrados, key=lambda x: x[0])
            return f"S/ {monto_mayor[1]}"
        
        return '-'
    
    def _extraer_servicios_similares(self, texto):
        """
        Extrae la sección completa de servicios similares incluyendo:
        - Título: "De la Experiencia del Postor en la Especialidad"
        - Monto requerido
        - Lista de servicios similares
        """
        
        # Paso 1: Buscar la sección de experiencia del postor
        patron_seccion = r'(?:De\s+la\s+)?Experiencia\s+del\s+[Pp]ostor\s+en\s+la\s+[Ee]specialidad(.*?)(?=\n\s*(?:[IVX]+\.|[0-9]+\.|CAP[ÍI]TULO|SECCI[ÓO]N|ANEXO|^\s*$)|$)'
        
        match_seccion = re.search(patron_seccion, texto, re.IGNORECASE | re.DOTALL)
        
        if match_seccion:
            texto_seccion = match_seccion.group(0)
        else:
            # Intento alternativo: buscar por "servicios similares"
            patron_alt = r'(?:Se\s+consideran?\s+)?[Ss]ervicios?\s+(?:iguales?\s+o\s+)?similares?(?:\s+a)?[:\s]+(.*?)(?=\n\s*(?:[IVX]+\.|[0-9]+\.|CAP[ÍI]TULO|SECCI[ÓO]N|ANEXO)|$)'
            match_alt = re.search(patron_alt, texto, re.IGNORECASE | re.DOTALL)
            
            if match_alt:
                # Incluir contexto anterior
                inicio = max(0, match_alt.start() - 500)
                texto_seccion = texto[inicio:match_alt.end()]
            else:
                return '-'
        
        resultado = []
        
        if 'Experiencia del Postor' in texto_seccion or 'experiencia del postor' in texto_seccion.lower():
            resultado.append("De la Experiencia del Postor en la Especialidad")
            resultado.append("")
        
        patron_monto = r'(?:debe\s+acreditar.*?monto\s+facturado\s+acumulado.*?(?:equivalente\s+a|de)\s*)?S/?\.?\s*([\d,]+(?:\.\d{2})?)'
        match_monto = re.search(patron_monto, texto_seccion, re.IGNORECASE | re.DOTALL)
        
        if match_monto:
            # Buscar el párrafo completo que contiene el monto
            lineas = texto_seccion.split('\n')
            for i, linea in enumerate(lineas):
                if match_monto.group(1) in linea or 'facturado' in linea.lower() or 'acreditar' in linea.lower():
                    # Tomar la línea y las siguientes si es necesario
                    parrafo_monto = linea.strip()
                    j = i + 1
                    while j < len(lineas) and j < i + 3:
                        siguiente = lineas[j].strip()
                        if siguiente and not siguiente.startswith('*') and not siguiente.startswith('-'):
                            parrafo_monto += " " + siguiente
                        else:
                            break
                        j += 1
                    
                    if parrafo_monto and len(parrafo_monto) > 20:
                        resultado.append(parrafo_monto)
                        resultado.append("")
                        break
        
        patron_inicio_lista = r'(?:[Ss]e\s+consideran?\s+servicios?\s+similares?|servicios?\s+similares?\s+a\s+los\s+siguientes)[:\s]*'
        match_inicio = re.search(patron_inicio_lista, texto_seccion, re.IGNORECASE)
        
        if match_inicio:
            resultado.append("Se consideran servicios similares a los siguientes:")
            resultado.append("")
            
            texto_lista = texto_seccion[match_inicio.end():]
            
            lineas = texto_lista.split('\n')
            servicios = []
            
            for linea in lineas:
                linea_limpia = linea.strip()
                
                if re.match(r'^[\*\-\•]\s+', linea_limpia) or re.match(r'^\d+[\.\)]\s+', linea_limpia):
                    linea_limpia = re.sub(r'^[\*\-\•\d\.\)]+\s*', '', linea_limpia)
                    if linea_limpia and len(linea_limpia) > 10:
                        servicios.append(f"* {linea_limpia}")
                elif linea_limpia and not linea_limpia[0].isupper() and servicios:
                    servicios[-1] += " " + linea_limpia
                elif 'servicio' in linea_limpia.lower() and len(linea_limpia) > 15:
                    servicios.append(f"* {linea_limpia}")
            
            resultado.extend(servicios)
        
        if len(resultado) > 1:
            return '\n'.join(resultado)
        
        return '-'