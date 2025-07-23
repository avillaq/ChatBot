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

class WebChatbotManager:
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
        self.p2p_node = P2PNode('localhost', port, f'main_node_{port}')
        self.chatbot = EnhancedChatbot("financial.db")
        self.chatbot.set_p2p_node(self.p2p_node)
        self.alert_monitor = AlertMonitor(self.chatbot, check_interval=20)
        
        # Inicializar logs del nodo principal
        self.node_logs[port] = []
        self.add_node_log(port, f"Nodo principal inicializado en puerto {port}", "system")
        
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
        """Crear red de demostración con nodos P2P REALES"""
        if not self.is_running:
            return False, "Sistema principal no inicializado"
            
        demo_ports = [8001, 8002, 8003]
        node_names = ['Banco_Nacional', 'Banco_Central', 'Banco_Regional']
        
        for port, name in zip(demo_ports, node_names):
            try:
                print(f"🔧 Creando nodo demo real: {name} en puerto {port}")
                
                # Inicializar logs para este nodo
                self.node_logs[port] = []
                self.add_node_log(port, f"Iniciando {name} en puerto {port}", "system")
                
                # Crear nodo P2P real
                demo_node = P2PNode('localhost', port, name)
                demo_chatbot = EnhancedChatbot("financial.db")
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
                        self.p2p_node.connect_to_peer('localhost', port, f'demo_bank_{port}')
                    )
                    print(f"✅ Nodo principal conectado a demo {port}")
                    self.add_node_log(8000, f"Conectado al nodo {port}", "success")
                    self.add_node_log(port, f"Conectado al nodo principal (8000)", "success")
                    time.sleep(0.5)
                    
                # Iniciar monitores de demo
                for port in demo_ports:
                    self.demo_monitors[port].start_monitoring()
                    self.add_node_log(port, "Monitor de alertas iniciado", "info")
                    
            except Exception as e:
                print(f"Error conectando nodos demo: {e}")
        
        connect_thread = threading.Thread(target=connect_demo_nodes, daemon=True)
        connect_thread.start()
        
        return True, "Red de demostración creada exitosamente"
    
    def add_node_log(self, port, message, log_type="info"):
        """Agregar log a un nodo específico"""
        if port not in self.node_logs:
            self.node_logs[port] = []
        
        log_entry = {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': message,
            'type': log_type
        }
        
        self.node_logs[port].append(log_entry)
        
        # Mantener solo los últimos 50 logs
        if len(self.node_logs[port]) > 50:
            self.node_logs[port] = self.node_logs[port][-50:]
    
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
        if self.chatbot:
            return await self.chatbot.process_query(message, user_name)
        return "Sistema no inicializado"
        
    def get_network_status(self):
        """Obtener estado de la red con información detallada"""
        if self.p2p_node:
            peers = self.p2p_node.get_connected_peers()
            return {
                'peers_count': len(peers),
                'peers': peers,
                'node_id': self.p2p_node.node_id,
                'status': 'active' if self.is_running else 'inactive',
                'demo_nodes_count': len(self.demo_nodes),
                'total_nodes': 1 + len(peers),
                'demo_running': len(self.demo_nodes) > 0
            }
        return {'status': 'not_initialized'}
    
    def get_network_topology(self):
        """Obtener topología de red REAL para visualización"""
        if not self.p2p_node:
            return {'nodes': [], 'connections': []}
            
        nodes = []
        connections = []
        
        # Nodo principal
        main_node = {
            'id': self.p2p_node.node_id,
            'label': f'Principal ({self.p2p_node.port})',
            'type': 'main',
            'active': self.is_running,
            'port': self.p2p_node.port
        }
        nodes.append(main_node)
        
        # Peers conectados (nodos demo)
        peers = self.p2p_node.get_connected_peers()
        for i, peer in enumerate(peers):
            # Extraer puerto del peer ID si es posible
            peer_port = None
            if 'demo_bank_' in peer:
                try:
                    peer_port = peer.split('_')[-1]
                except:
                    peer_port = 8000 + i + 1
            
            peer_node = {
                'id': peer,
                'label': f'Demo Bank {i+1}',
                'type': 'demo',
                'active': True,
                'port': peer_port
            }
            nodes.append(peer_node)
            
            # Conexión bidireccional con el nodo principal
            connections.append({
                'from': self.p2p_node.node_id,
                'to': peer,
                'type': 'p2p',
                'bidirectional': True
            })
        
        return {
            'nodes': nodes,
            'connections': connections,
            'timestamp': time.time()
        }

# Instancia global del manager
chat_manager = WebChatbotManager()

# ... (rutas anteriores)

@app.route('/')
def index():
    """Página principal"""
    return render_template('complete_demo.html')

# Nuevas rutas para manejo de nodos específicos
@app.route('/api/nodes')
def get_nodes():
    """Obtener lista de todos los nodos"""
    try:
        return jsonify({
            'success': True,
            'nodes': chat_manager.get_all_nodes()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/nodes/<int:port>')
def get_node_info(port):
    """Obtener información de un nodo específico"""
    try:
        node_info = chat_manager.get_node_info(port)
        if node_info:
            return jsonify({
                'success': True,
                'node': node_info
            })
        else:
            return jsonify({'success': False, 'message': 'Nodo no encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/nodes/<int:port>/chat', methods=['POST'])
def chat_with_node(port):
    """Chat con un nodo específico"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_name = data.get('user_name', None)
        
        # Ejecutar consulta asíncrona en el nodo específico
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            chat_manager.process_message_for_node(port, message, user_name)
        )
        response = (response or "").replace('Â', '')
        
        return jsonify({
            'success': True, 
            'response': response,
            'node_port': port
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/nodes/<int:port>/logs')
def get_node_logs(port):
    """Obtener logs de un nodo específico"""
    try:
        logs = chat_manager.node_logs.get(port, [])
        return jsonify({
            'success': True,
            'logs': logs[-20:]  # Últimos 20 logs
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Rutas anteriores mantienen compatibilidad
@app.route('/api/init', methods=['POST'])
def init_system():
    """Inicializar sistema P2P"""
    try:
        data = request.get_json()
        port = data.get('port', 8000)
        
        if not chat_manager.is_running:
            chat_manager.initialize(port)
            return jsonify({
                'success': True, 
                'message': f'Sistema P2P iniciado en puerto {port}',
                'node_id': chat_manager.p2p_node.node_id if chat_manager.p2p_node else None
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Sistema ya está activo'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/demo-network', methods=['POST'])
def create_demo_network():
    """Crear red de demostración REAL"""
    try:
        success, message = chat_manager.create_real_demo_network()
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/topology')
def get_topology():
    """Obtener topología de red REAL para visualización"""
    try:
        return jsonify({
            'success': True,
            'topology': chat_manager.get_network_topology()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test-scenarios', methods=['POST'])
def test_scenarios():
    """Ejecutar escenarios de prueba automáticos"""
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'alerts')
        
        if not chat_manager.is_running:
            return jsonify({'success': False, 'message': 'Sistema no inicializado'})
        
        results = []
        
        if scenario == 'alerts':
            # Probar las 3 condiciones críticas
            alerts = chat_manager.chatbot.db.detect_critical_conditions()
            critical_types = list(set(alert['type'] for alert in alerts))
            
            results.append({
                'test': 'Detección de 3 condiciones críticas',
                'result': f'{len(critical_types)} tipos detectados: {critical_types}',
                'success': len(critical_types) >= 3
            })
            
        elif scenario == 'queries':
            # Probar las 3 consultas requeridas
            test_queries = [
                "Saldo de Juan",
                "Transacciones de María", 
                "Alertas críticas"
            ]
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for query in test_queries:
                response = loop.run_until_complete(
                    chat_manager.process_message(query)
                )
                results.append({
                    'test': f'Consulta: {query}',
                    'result': response[:100] + '...' if len(response) > 100 else response,
                    'success': len(response) > 0 and 'error' not in response.lower()
                })
        
        return jsonify({
            'success': True,
            'scenario': scenario,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("🚀 ChatBot P2P Financiero - Demostración Completa")
    print("📡 Accede a: http://localhost:5000")
    print("🔗 Red P2P con nodos reales y funcionalidad completa")
    app.run(debug=True, host='0.0.0.0', port=5000)