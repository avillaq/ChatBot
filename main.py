import asyncio
import speech_recognition as sr
import pyttsx3
import numpy as np
from nlp_pipeline.enhanced_chatbot import EnhancedChatbot
from p2p.node import P2PNode
from monitoring.alert_monitor import AlertMonitor

class P2PChatBot:
    """Chatbot P2P con capacidades financieras distribuidas"""
    
    def __init__(self, node_port=8000):
        print("----- Inicializando Chatbot P2P -----")
        
        # Configurar nodo P2P
        self.node_port = node_port
        self.p2p_node = P2PNode('localhost', node_port, f'bot_financiero_{node_port}')
        
        # Configurar chatbot mejorado
        self.enhanced_chatbot = EnhancedChatbot("financial.db")
        self.enhanced_chatbot.set_p2p_node(self.p2p_node)
        
        # Configurar monitor de alertas
        self.alert_monitor = AlertMonitor(self.enhanced_chatbot, check_interval=30)
        
        # Variables del chatbot original
        self.name = "AsistenteFinanciero"
    
    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def speech_to_text(self):
        """Convertir voz a texto"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as mic:
            print("🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(mic, duration=1)
            audio = recognizer.listen(mic, timeout=15)
            text = "Error"
        try:
            text = recognizer.recognize_google(audio, language='es-ES')
            print("Usuario -> ", text)
            return text
        except sr.RequestError as e:
            print("404 -> No se pudo procesar la solicitud: {0}".format(e))
            return text
        except sr.UnknownValueError:
            print("404 -> No se pudo entender el audio")
            return text
    
    def text_to_speech(self, text):
        """Convertir texto a voz"""
        print("Bot -> ", text)
        speaker = pyttsx3.init()
        voices = speaker.getProperty('voices')
        
        # Intentar configurar voz en español
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                speaker.setProperty('voice', voice.id)
                break
        
        speaker.setProperty('rate', 150)  # Velocidad mas lenta
        speaker.say(text)
        speaker.runAndWait()
    
    async def chat(self, text, user_name=None):
        """Procesar chat con capacidades financieras y P2P"""
        response = await self.enhanced_chatbot.process_query(text, user_name)
        return response
    
    async def start_p2p_mode(self):
        """Iniciar modo P2P"""
        print(f"🌐 Iniciando nodo P2P en puerto {self.node_port}...")
        
        # Iniciar servidor P2P en background
        server_task = asyncio.create_task(self.p2p_node.start_server())
        
        # Iniciar monitoreo de alertas
        self.alert_monitor.start_monitoring()
        
        # Esperar un poco para que el servidor se inicie
        await asyncio.sleep(2)
        
        print(f"✅ Sistema P2P activo!")
        print(f"📡 Para conectar otros nodos usar puerto: {self.node_port}")
        print(f"🔍 Monitoreo automatico de alertas activo")
        
        return server_task
    
    async def connect_to_peer(self, peer_host, peer_port):
        """Conectar a otro nodo"""
        await self.p2p_node.connect_to_peer(peer_host, peer_port)
    
    def get_network_status(self):
        """Obtener estado de la red P2P"""
        peers = self.p2p_node.get_connected_peers()
        return f"🌐 Red P2P: {len(peers)} nodos conectados: {peers}"

async def main():
    """Función principal del chatbot P2P"""
    
    # Configurar puerto del nodo
    print("🔧 Configuración del nodo P2P")
    try:
        port = int(input("Puerto para este nodo (por defecto 8000): ") or "8000")
    except ValueError:
        port = 8000
    
    # Crear chatbot P2P
    ai = P2PChatBot(port)
    
    # Iniciar sistema P2P
    server_task = await ai.start_p2p_mode()
    
    # Preguntar si conectar a otros nodos
    print("\n🔗 ¿Quieres conectarte a otros nodos?")
    connect_choice = input("(s/n): ").lower()
    
    if connect_choice == 's':
        try:
            peer_host = input("Host del nodo (por defecto localhost): ") or "localhost"
            peer_port = int(input("Puerto del nodo: "))
            await ai.connect_to_peer(peer_host, peer_port)
        except Exception as e:
            print(f"❌ Error conectando: {e}")
    
    # Mostrar estado de la red
    print(f"\n{ai.get_network_status()}")
    
    action = None
    try:
        # Interfaz de usuario
        ai.text_to_speech("Sistema P2P listo. ¿Quieres usar chat de texto o voz?")
        action = int(input("(1 para texto, 2 para voz): "))
        
        if action == 1:
            # Modo chat
            print("\n💬 Modo Chat P2P - Escribe 'salir' para terminar")
            print("💡 Prueba consultas como: 'saldo de Juan', 'alertas críticas', 'transacciones de María'")
            
            while True:
                user_input = input("\nUsuario -> ")
                
                if any(i in user_input.lower() for i in ["salir", "exit", "quit", "adiós"]):
                    break
                elif "estado de la red" in user_input.lower():
                    print(ai.get_network_status())
                elif "tu nombre" in user_input.lower() or "cómo te llamas" in user_input.lower():
                    print(f"Bot -> Soy {ai.get_name()}")
                else:
                    response = await ai.chat(user_input)
                    print(f"Bot -> {response}")
        
        elif action == 2:
            # Modo voz
            ai.text_to_speech("¿Cómo quieres que me llame?")
            while True:
                res = ai.speech_to_text()
                if res != "Error":
                    ai.set_name(res)
                    break
                ai.text_to_speech("Perdón, ¿puedes repetir?")
            
            ai.text_to_speech("¡Perfecto! ¿En qué puedo ayudarte?")
            
            while True:
                res = ai.speech_to_text()
                
                if isinstance(res, str) and any(i in res.lower() for i in ["gracias", "muchas gracias"]):
                    ai.text_to_speech("¡De nada!")
                elif isinstance(res, str) and any(i in res.lower() for i in ["tu nombre", "cómo te llamas"]):
                    ai.text_to_speech(f"Soy {ai.get_name()}")
                elif isinstance(res, str) and any(i in res.lower() for i in ["salir", "adiós", "hasta luego"]):
                    break
                else:
                    if res == "Error":
                        ai.text_to_speech("Perdón, ¿puedes repetir?")
                    else:
                        response = await ai.chat(res)
                        ai.text_to_speech(response)
    
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo sistema...")
    
    finally:
        # Cleanup
        ai.alert_monitor.stop_monitoring()
        ai.p2p_node.stop()
        
        farewell = np.random.choice([
            "¡Hasta luego!", 
            "¡Que tengas buen día!", 
            "¡Nos vemos!", 
            "¡Adiós!"
        ])
        if action == 2:
            ai.text_to_speech(farewell)
        else:
            print(f"Bot -> {farewell}")
        if not server_task.done():
            server_task.cancel()
            print(f"Bot -> {farewell}")

if __name__ == "__main__":
    print("🚀 ChatBot P2P Financiero")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta la vista!")