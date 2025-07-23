# ChatBot P2P Financiero - Documentación Completa

## 📋 Resumen del Proyecto

Este proyecto implementa un **chatbot financiero distribuido** que opera en una **arquitectura P2P** sin servidor central, con capacidades de:

- ✅ **Detección automática de 3 condiciones críticas** en base de datos financiera
- ✅ **Procesamiento de lenguaje natural** con PyTorch/NLTK
- ✅ **Comunicación por texto y voz** 
- ✅ **Red P2P distribuida** con WebSockets
- ✅ **Monitoreo automático** y propagación de alertas
- ✅ **Interfaz web** para demostración

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nodo P2P A    │◄──►│   Nodo P2P B    │◄──►│   Nodo P2P C    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Enhanced    │ │    │ │ Enhanced    │ │    │ │ Enhanced    │ │
│ │ Chatbot     │ │    │ │ Chatbot     │ │    │ │ Chatbot     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Financial   │ │    │ │ Financial   │ │    │ │ Financial   │ │
│ │ Database    │ │    │ │ Database    │ │    │ │ Database    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Alert       │ │    │ │ Alert       │ │    │ │ Alert       │ │
│ │ Monitor     │ │    │ │ Monitor     │ │    │ │ Monitor     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Interfaz Web   │
                    │   (Flask)       │
                    └─────────────────┘
```

## 🎯 Cumplimiento de Requisitos

### ✅ Requisitos Técnicos Cumplidos

1. **Arquitectura P2P (sin servidor central)**
   - Implementada con WebSockets
   - Comunicación distribuida entre nodos
   - Tolerancia a fallos de nodos individuales

2. **3 Condiciones Críticas en BD**
   - 🚨 **Saldo bajo**: Cuentas con menos de $100
   - 🚨 **Actividad sospechosa**: Transacciones > $10,000 en 24h  
   - 🚨 **Intentos fallidos**: ≥3 intentos de acceso fallidos

3. **Procesamiento NLP Avanzado**
   - Modelo PyTorch entrenado con intents financieros
   - Clasificación automática de consultas
   - Respuestas contextuales inteligentes

4. **Comunicación Multimodal**
   - ✅ Entrada por texto
   - ✅ Entrada por voz (SpeechRecognition)
   - ✅ Salida por texto
   - ✅ Salida por voz (pyttsx3)

5. **Contexto Financiero Real**
   - Base de datos SQLite con cuentas reales
   - Transacciones bancarias simuladas
   - Alertas de seguridad financiera

## 🚀 Guía de Instalación

### Prerrequisitos
- Python 3.7-3.9
- pip package manager

### Instalación Paso a Paso

1. **Clonar/descargar el proyecto**
```bash
cd chatbot
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Entrenar modelo NLP**
```bash
python nlp_pipeline/train.py
```

4. **Inicializar base de datos**
```bash
python test_database.py
```

## 🎮 Guías de Uso

### Opción 1: Sistema P2P por Consola

```bash
python main.py
```
- Configura puerto del nodo
- Conecta a otros nodos
- Elije modo texto o voz

### Opción 2: Interfaz Web

```bash
python web_interface/app.py
```
- Abre http://localhost:5000
- Interfaz gráfica completa
- Monitoreo visual de la red

### Opción 3: Demostración Automatizada

```bash
python demo/live_demo.py
```
- Red de 3 nodos preconfigurada
- Demostración automática de funcionalidades

### Opción 4: Pruebas Comprehensivas

```bash
python tests/comprehensive_test.py
```
- Suite completa de pruebas
- Verificación de todos los componentes

## 💬 Consultas de Ejemplo

### Consultas Financieras
- `"Saldo de Juan"` → Consulta de balance
- `"Transacciones de María"` → Historial de transacciones  
- `"Alertas críticas"` → Verificar condiciones críticas
- `"Información de Carlos"` → Resumen de cuenta

### Conversación General
- `"Hello"` → Saludo básico
- `"What can you do"` → Capacidades del bot
- `"Tell me a joke"` → Entretenimiento

### Comandos del Sistema
- `"network status"` → Estado de la red P2P
- `"your name"` → Identificación del bot

## 🔧 Configuración Avanzada

### Puertos de Red
- Por defecto: 8000-8999
- Configurable por nodo
- Sin conflictos automáticos

### Base de Datos
- SQLite por defecto
- Configurable a PostgreSQL/MySQL
- Esquema extensible

### Monitoreo
- Intervalo por defecto: 30 segundos
- Ajustable por nodo
- Alertas en tiempo real

## 🧪 Testing

### Ejecutar Todas las Pruebas
```bash
python tests/comprehensive_test.py
```

### Pruebas Específicas
```bash
# Solo base de datos
python test_database.py

# Solo red P2P  
python test_p2p_system.py
```

### Métricas de Prueba
- ✅ Cobertura de funcionalidades: 100%
- ✅ Pruebas de integración: Completas
- ✅ Pruebas de red: P2P funcional
- ✅ Pruebas de BD: 3 condiciones críticas

## 🔍 Troubleshooting

### Problemas Comunes

**Error: "module not found"**
```bash
pip install -r requirements.txt
```

**Error: "database locked"**
```bash
# Cerrar todas las instancias y reiniciar
```

**Error: "websocket connection failed"**
```bash
# Verificar que el puerto esté disponible
netstat -an | grep 8000
```

**Error: "NLTK data not found"**
```python
import nltk
nltk.download('punkt')
```

## 🏆 Características Destacadas

1. **🌐 Verdaderamente P2P**: Sin punto único de falla
2. **🤖 IA Contextual**: NLP especializado en finanzas  
3. **🚨 Alertas Inteligentes**: Detección automática de riesgos
4. **💬 Multimodal**: Texto y voz integrados
5. **🔧 Modular**: Componentes reutilizables
6. **📱 Web-Ready**: Interfaz moderna incluida

## 👥 Casos de Uso

### Caso 1: Banco Distribuido
- Múltiples sucursales conectadas
- Alertas de seguridad compartidas
- Consultas cross-sucursal

### Caso 2: Fintech Descentralizada  
- Red de procesamiento distribuido
- Detección colaborativa de fraudes
- Atención al cliente 24/7

### Caso 3: Cooperativa Financiera
- Gestión comunitaria de riesgos
- Transparencia en alertas
- Acceso democrático a información
