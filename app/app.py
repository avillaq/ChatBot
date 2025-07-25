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
        self.demo_nodes = {}  # {port: node}
        self.demo_chatbots = {}  # {port: chatbot}
        self.demo_monitors = {}  # {port: monitor}
        self.node_logs = {}  # {port: [logs]}
        
    def initialize(self, port=8000):
        """Inicializar sistema P2P principal"""
        # Base de datos específica para nodo principal
        main_db_path = f"financial_main_{port}.db"
        
        self.p2p_node = P2PNode('localhost', port, f'Banco_Principal_{port}')
        self.chatbot = EnhancedChatbot(main_db_path, node_id=f'main_{port}')
        self.chatbot.set_p2p_node(self.p2p_node)
        self.alert_monitor = AlertMonitor(self.chatbot, check_interval=20)
        
        # Inicializar logs del nodo principal
        self.node_logs[port] = []
        self.add_node_log(port, f"Banco Principal inicializado en puerto {port}", "system")
        self.add_node_log(port, f"Base de datos: {main_db_path}", "info")
        
        # Iniciar servidor P2P en hilo separado
        def run_p2p():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.p2p_node.start_server())
            except Exception as e:
                print(f"Error en servidor P2P principal: {e}")
                self.add_node_log(port, f"Error en servidor: {e}", "error")
        
        p2p_thread = threading.Thread(target=run_p2p, daemon=True)
        p2p_thread.start()
        
        # Esperar que el servidor se inicie
        time.sleep(1)
        
        # Iniciar monitoreo
        self.alert_monitor.start_monitoring()
        self.is_running = True
        self.add_node_log(port, "Sistema P2P activo y funcionando", "success")
        
    def create_real_demo_network(self):
        """Crear red de demostración con nodos P2P REALES y BD independientes"""
        if not self.is_running:
            return False, "Sistema principal no inicializado"
            
        demo_ports = [8001, 8002, 8003]
        node_names = ['Banco_Nacional', 'Banco_Central', 'Banco_Regional']
        
        for port, name in zip(demo_ports, node_names):
            try:
                print(f"🔧 Creando nodo demo real: {name} en puerto {port}")
                
                # Base de datos específica para cada nodo demo
                demo_db_path = f"financial_{name.lower()}_{port}.db"
                
                # Inicializar logs para este nodo
                self.node_logs[port] = []
                self.add_node_log(port, f"Iniciando {name} en puerto {port}", "system")
                self.add_node_log(port, f"Base de datos: {demo_db_path}", "info")
                
                # Crear nodo P2P real con BD independiente
                demo_node = P2PNode('localhost', port, name)
                demo_chatbot = EnhancedChatbot(demo_db_path, node_id=name.lower())
                demo_chatbot.set_p2p_node(demo_node)
                demo_monitor = AlertMonitor(demo_chatbot, check_interval=30)
                
                # Guardar referencias
                self.demo_nodes[port] = demo_node
                self.demo_chatbots[port] = demo_chatbot
                self.demo_monitors[port] = demo_monitor
                
                # Iniciar servidor demo en hilo separado
                def run_demo_node(node, port_num, node_name):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(node.start_server())
                    except Exception as e:
                        print(f"Error en nodo demo {port_num}: {e}")
                        self.add_node_log(port_num, f"Error en servidor: {e}", "error")
                
                demo_thread = threading.Thread(
                    target=run_demo_node, 
                    args=(demo_node, port, name), 
                    daemon=True
                )
                demo_thread.start()
                
                self.add_node_log(port, f"Servidor {name} iniciado", "success")
                time.sleep(0.5)  # Esperar entre creaciones
                
            except Exception as e:
                print(f"Error creando nodo demo {port}: {e}")
                self.add_node_log(port, f"Error de creación: {e}", "error")
                return False, f"Error creando nodo {port}: {str(e)}"
        
        # Esperar que todos los servidores demo se inicien
        time.sleep(2)
        
        # Conectar nodos demo al nodo principal
        def connect_demo_nodes():
            time.sleep(1)
            try:
                for port in demo_ports:
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
    
    def add_node_log(self, port, message, log_type="info"):
        """Agregar log a un nodo específico - MEJORADO para incluir logs P2P"""
        if port not in self.node_logs:
            self.node_logs[port] = []
        
        log_entry = {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': message,
            'type': log_type
        }
        
        self.node_logs.append(log_entry)
        
        # Mantener solo los últimos 100 logs
        if len(self.node_logs[port]) > 100:
            self.node_logs[port] = self.node_logs[port][-100:]
    
    async def process_message_for_node(self, port, message, user_name=None):
        """Procesar mensaje para un nodo específico"""
        if port == 8000 and self.chatbot:
            # Nodo principal
            self.add_node_log(port, f"Usuario: {message}", "user")
            response = await self.chatbot.process_query(message, user_name)
            self.add_node_log(port, f"Bot: {response[:100]}{'...' if len(response) > 100 else ''}", "bot")
            return response
        elif port in self.demo_chatbots:
            # Nodo demo
            chatbot = self.demo_chatbots[port]
            self.add_node_log(port, f"Usuario: {message}", "user")
            response = await chatbot.process_query(message, user_name)
            self.add_node_log(port, f"Bot: {response[:100]}{'...' if len(response) > 100 else ''}", "bot")
            return response
        else:
            return "Nodo no disponible"
    def get_node_logs_combined(self, port):
        """Obtener logs combinados del nodo (aplicación + P2P)"""
        app_logs = self.node_logs.get(port, [])
        
        # Obtener logs P2P del nodo
        p2p_logs = []
        if port == 8000 and self.p2p_node:
            p2p_logs = self.p2p_node.get_p2p_logs()
        elif port in self.demo_nodes:
            p2p_logs = self.demo_nodes[port].get_p2p_logs()
        
        # Combinar logs
        combined_logs = list(app_logs)
        for p2p_log in p2p_logs:
            combined_logs.append({
                'timestamp': p2p_log['timestamp'],
                'message': f"P2P: {p2p_log['message']}",
                'type': p2p_log['type']
            })
        
        # Ordenar por timestamp y devolver los últimos 50
        combined_logs.sort(key=lambda x: x['timestamp'])
        return combined_logs[-50:]
    
    def get_node_info(self, port):
        """Obtener información detallada de un nodo"""
        if port == 8000 and self.p2p_node:
            # Nodo principal
            return {
                'port': port,
                'node_id': self.p2p_node.node_id,
                'name': 'Banco Principal',
                'type': 'main',
                'status': 'active' if self.is_running else 'inactive',
                'peers': self.p2p_node.get_connected_peers(),
                'logs': self.node_logs.get(port, [])
            }
        elif port in self.demo_nodes:
            # Nodo demo
            node = self.demo_nodes[port]
            names = {8001: 'Banco Nacional', 8002: 'Banco Central', 8003: 'Banco Regional'}
            return {
                'port': port,
                'node_id': node.node_id,
                'name': names.get(port, f'Banco Demo {port}'),
                'type': 'demo',
                'status': 'active',
                'peers': node.get_connected_peers(),
                'logs': self.node_logs.get(port, [])
            }
        else:
            return None
    
    def get_all_nodes(self):
        """Obtener lista de todos los nodos disponibles"""
        nodes = []
        
        # Nodo principal
        if self.p2p_node:
            nodes.append({
                'port': 8000,
                'name': 'Banco Principal',
                'type': 'main',
                'status': 'active' if self.is_running else 'inactive'
            })
        
        # Nodos demo
        names = {8001: 'Banco Nacional', 8002: 'Banco Central', 8003: 'Banco Regional'}
        for port in self.demo_nodes.keys():
            nodes.append({
                'port': port,
                'name': names.get(port, f'Banco Demo {port}'),
                'type': 'demo',
                'status': 'active'
            })
        
        return nodes
    
    # ... (resto de métodos anteriores)
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

@app.route('/api/nodes/<int:port>/logs')
def get_node_logs(port):
    """Obtener logs combinados de un nodo específico"""
    try:
        logs = chat_manager.get_node_logs_combined(port)
        return jsonify({
            'success': True,
            'logs': logs,
            'node_port': port
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