from flask import Flask, render_template, request, jsonify
import asyncio
import threading
import sys
import os

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
        
    def initialize(self, port=8000):
        """Inicializar sistema P2P"""
        self.p2p_node = P2PNode('localhost', port, f'web_node_{port}')
        self.chatbot = EnhancedChatbot("financial.db")
        self.chatbot.set_p2p_node(self.p2p_node)
        self.alert_monitor = AlertMonitor(self.chatbot, check_interval=20)
        
        # Iniciar servidor P2P en hilo separado
        def run_p2p():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if self.p2p_node:
                loop.run_until_complete(self.p2p_node.start_server())
        
        p2p_thread = threading.Thread(target=run_p2p, daemon=True)
        p2p_thread.start()
        
        # Iniciar monitoreo
        self.alert_monitor.start_monitoring()
        self.is_running = True
        
    async def process_message(self, message, user_name=None):
        """Procesar mensaje de chat"""
        if self.chatbot:
            return await self.chatbot.process_query(message, user_name)
        return "Sistema no inicializado"
        
    def get_network_status(self):
        """Obtener estado de la red"""
        if self.p2p_node:
            peers = self.p2p_node.get_connected_peers()
            return {
                'peers_count': len(peers),
                'peers': peers,
                'node_id': self.p2p_node.node_id,
                'status': 'active' if self.is_running else 'inactive'
            }
        return {'status': 'not_initialized'}

# Instancia global del manager
chat_manager = WebChatbotManager()

@app.route('/')
def index():
    """Pagina principal"""
    return render_template('index.html')

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
                'message': 'Sistema ya esta activo'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Procesar mensaje de chat"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_name = data.get('user_name', None)
        
        if not chat_manager.is_running:
            return jsonify({
                'success': False, 
                'message': 'Sistema no inicializado. Presiona "Iniciar Sistema" primero.'
            })
        
        # Ejecutar consulta asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            chat_manager.process_message(message, user_name)
        )
        
        return jsonify({
            'success': True, 
            'response': response,
            'network_status': chat_manager.get_network_status()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/connect', methods=['POST'])
def connect_peer():
    """Conectar a otro nodo"""
    try:
        data = request.get_json()
        host = data.get('host', 'localhost')
        port = int(data.get('port'))
        
        if not chat_manager.is_running or chat_manager.p2p_node is None:
            return jsonify({'success': False, 'message': 'Sistema no inicializado'})
        
        # Conectar de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            chat_manager.p2p_node.connect_to_peer(host, port)
        )
        
        return jsonify({
            'success': True, 
            'message': f'Conectado a {host}:{port}',
            'network_status': chat_manager.get_network_status()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/status')
def get_status():
    """Obtener estado del sistema"""
    try:
        return jsonify({
            'success': True,
            'network_status': chat_manager.get_network_status(),
            'system_running': chat_manager.is_running
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/alerts')
def get_alerts():
    """Obtener alertas críticas"""
    try:
        if not chat_manager.is_running or chat_manager.chatbot is None:
            return jsonify({'success': False, 'message': 'Sistema no inicializado'})
            
        alerts = chat_manager.chatbot.db.detect_critical_conditions()
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)