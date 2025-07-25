from flask import Flask, render_template, request, jsonify
import asyncio
import threading
import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_pipeline.enhanced_chatbot import EnhancedChatbot
from p2p.node import P2PNode
from monitoring.alert_monitor import AlertMonitor

app = Flask(__name__)

class DockerChatbotManager:
    """Gestor de chatbot simplificado para un solo nodo Docker"""
    
    def __init__(self):
        self.chatbot = None
        self.p2p_node = None
        self.alert_monitor = None
        self.is_running = False
        self.config = None
        self.node_logs = []
        
    def load_config(self):
        """Cargar configuración desde archivo JSON"""
        try:
            config_file = os.getenv('CONFIG_FILE', '/app/config.json')
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            print(f"✅ Configuración cargada desde {config_file}")
            return True
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return False
    
    def initialize_from_config(self):
        """Inicializar sistema usando configuración cargada"""
        if not self.config:
            if not self.load_config():
                return False, "Error cargando configuración"
        
        try:
            # Crear directorio de datos si no existe
            os.makedirs('/app/data', exist_ok=True)
            
            # Configurar nodo P2P
            node_id = self.config['node_id']
            port = self.config['port']
            host = self.config.get('host', '0.0.0.0')
            
            self.p2p_node = P2PNode(host, port, node_id)
            self.add_log(f"Nodo P2P creado: {node_id} en puerto {port}", "system")
            
            # Configurar chatbot
            db_path = self.config['database']
            self.chatbot = EnhancedChatbot(db_path)
            self.chatbot.set_p2p_node(self.p2p_node)
            self.add_log(f"Chatbot inicializado con BD: {db_path}", "system")
            
            # Configurar monitor de alertas
            monitor_config = self.config.get('monitoring', {})
            if monitor_config.get('enabled', True):
                interval = monitor_config.get('interval', 30)
                self.alert_monitor = AlertMonitor(self.chatbot, check_interval=interval)
                self.add_log(f"Monitor de alertas configurado (intervalo: {interval}s)", "system")
            
            # Iniciar servidor P2P en thread separado
            def run_p2p_server():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.p2p_node.start_server())
                except Exception as e:
                    print(f"Error en servidor P2P: {e}")
                    self.add_log(f"Error en servidor P2P: {e}", "error")
            
            p2p_thread = threading.Thread(target=run_p2p_server, daemon=True)
            p2p_thread.start()
            self.add_log("Servidor P2P iniciado", "success")
            
            # Esperar que el servidor se inicie
            time.sleep(2)
            
            # Auto-conectar a otros nodos si está configurado
            if self.config.get('auto_connect'):
                self.auto_connect_peers()
            
            # Iniciar monitor si está configurado
            if self.alert_monitor:
                self.alert_monitor.start_monitoring()
                self.add_log("Monitor de alertas iniciado", "success")
            
            self.is_running = True
            self.add_log(f"Sistema {node_id} completamente inicializado", "success")
            
            return True, f"Nodo {node_id} iniciado exitosamente"
            
        except Exception as e:
            error_msg = f"Error inicializando sistema: {str(e)}"
            self.add_log(error_msg, "error")
            return False, error_msg
    
    def auto_connect_peers(self):
        """Conectar automáticamente a peers configurados"""
        def connect_to_peers():
            time.sleep(3)  # Esperar que otros nodos se inicien
            
            auto_connect = self.config.get('auto_connect', [])
            for peer_config in auto_connect:
                try:
                    host = peer_config['host']
                    port = peer_config['port']
                    peer_id = peer_config.get('node_id', f'peer_{port}')
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.p2p_node.connect_to_peer(host, port, peer_id)
                    )
                    
                    self.add_log(f"Auto-conexión exitosa a {peer_id} ({host}:{port})", "success")
                    time.sleep(1)
                    
                except Exception as e:
                    self.add_log(f"Error auto-conectando a {host}:{port} - {e}", "error")
        
        # Ejecutar conexiones en thread separado
        connect_thread = threading.Thread(target=connect_to_peers, daemon=True)
        connect_thread.start()
    
    def add_log(self, message, log_type="info"):
        """Agregar entrada al log del nodo"""
        log_entry = {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': message,
            'type': log_type
        }
        
        self.node_logs.append(log_entry)
        
        # Mantener solo los últimos 100 logs
        if len(self.node_logs) > 100:
            self.node_logs = self.node_logs[-100:]
        
        print(f"[{log_entry['timestamp']}] {message}")
    
    async def process_message(self, message, user_name=None):
        """Procesar mensaje de chat"""
        if not self.chatbot:
            return "Sistema no inicializado"
        
        try:
            self.add_log(f"Usuario: {message}", "user")
            response = await self.chatbot.process_query(message, user_name)
            self.add_log(f"Bot: {response[:100]}{'...' if len(response) > 100 else ''}", "bot")
            
            # Agregar logs P2P recientes
            if self.p2p_node:
                p2p_logs = self.p2p_node.get_p2p_logs()
                for p2p_log in p2p_logs[-3:]:  # Últimos 3 logs P2P
                    self.add_log(f"P2P: {p2p_log['message']}", "system")
            
            return response
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {str(e)}"
            self.add_log(error_msg, "error")
            return error_msg
    
    def get_node_status(self):
        """Obtener estado actual del nodo"""
        if not self.p2p_node or not self.is_running:
            return {
                'status': 'inactive',
                'node_id': 'N/A',
                'peers_count': 0,
                'peers': []
            }
        
        peers = self.p2p_node.get_connected_peers()
        return {
            'status': 'active',
            'node_id': self.p2p_node.node_id,
            'port': self.p2p_node.port,
            'peers_count': len(peers),
            'peers': peers,
            'config': self.config
        }
    
    def get_logs(self):
        """Obtener logs del nodo"""
        # Combinar logs del manager con logs P2P
        combined_logs = list(self.node_logs)
        
        if self.p2p_node:
            p2p_logs = self.p2p_node.get_p2p_logs()
            for p2p_log in p2p_logs[-10:]:
                combined_logs.append({
                    'timestamp': p2p_log['timestamp'],
                    'message': f"P2P: {p2p_log['message']}",
                    'type': 'system'
                })
        
        # Ordenar por timestamp y devolver los últimos 50
        combined_logs.sort(key=lambda x: x['timestamp'])
        return combined_logs[-50:]

# Instancia global del manager
chat_manager = DockerChatbotManager()

# Rutas de la API
@app.route('/')
def index():
    """Página principal con interfaz del nodo actual"""
    return render_template('node_interface.html')

@app.route('/api/health')
def health_check():
    """Health check para Docker"""
    try:
        status = chat_manager.get_node_status()
        return jsonify({
            'status': 'healthy' if status['status'] == 'active' else 'unhealthy',
            'node_id': status.get('node_id', 'unknown'),
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Obtener estado del nodo"""
    try:
        return jsonify({
            'success': True,
            'node_status': chat_manager.get_node_status(),
            'system_running': chat_manager.is_running
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint de chat"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_name = data.get('user_name', None)
        
        # Procesar mensaje de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            chat_manager.process_message(message, user_name)
        )
        
        return jsonify({
            'success': True,
            'response': response.replace('Â', '') if response else '',
            'node_status': chat_manager.get_node_status()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/logs')
def get_logs():
    """Obtener logs del nodo"""
    try:
        return jsonify({
            'success': True,
            'logs': chat_manager.get_logs()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/connect', methods=['POST'])
def connect_to_peer():
    """Conectar manualmente a otro nodo"""
    try:
        data = request.get_json()
        host = data.get('host', 'localhost')
        port = data.get('port')
        peer_id = data.get('peer_id', f'manual_peer_{port}')
        
        if not port:
            return jsonify({'success': False, 'message': 'Puerto requerido'})
        
        if not chat_manager.p2p_node:
            return jsonify({'success': False, 'message': 'Sistema no inicializado'})
        
        # Conectar de forma asíncrona
        def connect_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                chat_manager.p2p_node.connect_to_peer(host, port, peer_id)
            )
        
        connect_thread = threading.Thread(target=connect_async, daemon=True)
        connect_thread.start()
        
        chat_manager.add_log(f"Conectando manualmente a {host}:{port}", "system")
        
        return jsonify({
            'success': True,
            'message': f'Conectando a {host}:{port}...',
            'node_status': chat_manager.get_node_status()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/broadcast', methods=['POST'])
def broadcast_message():
    """Enviar mensaje a todos los peers"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not chat_manager.p2p_node:
            return jsonify({'success': False, 'message': 'Sistema no inicializado'})
        
        # Broadcast de forma asíncrona
        def broadcast_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                chat_manager.p2p_node.broadcast_message('CHAT', {'message': message})
            )
        
        broadcast_thread = threading.Thread(target=broadcast_async, daemon=True)
        broadcast_thread.start()
        
        chat_manager.add_log(f"Broadcast enviado: {message[:50]}...", "system")
        
        return jsonify({
            'success': True,
            'message': f'Mensaje enviado a {len(chat_manager.p2p_node.peers)} peers',
            'node_status': chat_manager.get_node_status()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("🐳 ChatBot P2P Financiero - Nodo Docker")
    print("=" * 50)
    
    # Intentar inicializar desde configuración
    success, message = chat_manager.initialize_from_config()
    print(f"📡 {message}")
    
    if success:
        config = chat_manager.config
        node_name = config.get('node_id', 'Nodo_Desconocido')
        web_port = config.get('web_port', 5000)
        
        print(f"🏦 Nodo: {node_name}")
        print(f"🌐 Interfaz web: http://localhost:{web_port}")
        print(f"🔗 Puerto P2P: {config.get('port', 'N/A')}")
        print("=" * 50)
        
        # Iniciar Flask
        app.run(debug=False, host='0.0.0.0', port=web_port)
    else:
        print("❌ Error inicializando nodo. Revisa la configuración.")
        exit(1)