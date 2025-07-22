import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from p2p.protocol import P2PProtocol

class P2PNode:
    """Nodo P2P para comunicación distribuida"""
    
    def __init__(self, host='localhost', port=8000, node_id=None):
        self.host = host
        self.port = port
        self.node_id = node_id or f"node_{port}"
        self.peers = {}  # {node_id: websocket}
        self.message_handlers = {}
        self.running = False
        self.server = None
        
        # Configurar handlers por defecto
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """Configurar handlers de mensajes por defecto"""
        self.message_handlers = {
            P2PProtocol.MESSAGE_TYPES['DISCOVERY']: self.handle_discovery,
            P2PProtocol.MESSAGE_TYPES['HEARTBEAT']: self.handle_heartbeat,
            P2PProtocol.MESSAGE_TYPES['ALERT']: self.handle_alert,
            P2PProtocol.MESSAGE_TYPES['CHAT']: self.handle_chat_message
        }
    
    async def start_server(self):
        """Iniciar servidor WebSocket"""
        print(f"🔄 Iniciando servidor P2P en {self.host}:{self.port}")
        
        async def handle_client(websocket):
            try:
                await self.handle_new_connection(websocket)
                async for message in websocket:
                    await self.process_message(message, websocket)
            except websockets.exceptions.ConnectionClosed:
                await self.handle_disconnection(websocket)
            except Exception as e:
                print(f"❌ Error en conexión: {e}")
        
        self.server = await websockets.serve(handle_client, self.host, self.port)
        self.running = True
        print(f"✅ Servidor P2P activo en {self.host}:{self.port}")
        
        # Mantener servidor corriendo
        await self.server.wait_closed()
    
    async def connect_to_peer(self, peer_host, peer_port, peer_id=None):
        """Conectar a otro nodo"""
        try:
            uri = f"ws://{peer_host}:{peer_port}"
            websocket = await websockets.connect(uri)
            
            peer_id = peer_id or f"peer_{peer_port}"
            self.peers[peer_id] = websocket
            
            # Enviar mensaje de descubrimiento
            discovery_msg = P2PProtocol.create_message(
                P2PProtocol.MESSAGE_TYPES['DISCOVERY'],
                {'node_id': self.node_id, 'action': 'join'},
                self.node_id
            )
            await websocket.send(discovery_msg)
            
            print(f"✅ Conectado a peer {peer_id} en {uri}")
            
            # Escuchar mensajes del peer
            asyncio.create_task(self.listen_to_peer(websocket, peer_id))
            
        except Exception as e:
            print(f"❌ Error conectando a {peer_host}:{peer_port} - {e}")
    
    async def listen_to_peer(self, websocket, peer_id):
        """Escuchar mensajes de un peer específico"""
        try:
            async for message in websocket:
                await self.process_message(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            if peer_id in self.peers:
                del self.peers[peer_id]
                print(f"🔌 Peer {peer_id} desconectado")
    
    async def handle_new_connection(self, websocket):
        """Manejar nueva conexión entrante"""
        print("🔗 Nueva conexión entrante")
    
    async def handle_disconnection(self, websocket):
        """Manejar desconexión"""
        # Buscar y remover peer desconectado
        peer_to_remove = None
        for peer_id, peer_ws in self.peers.items():
            if peer_ws == websocket:
                peer_to_remove = peer_id
                break
        
        if peer_to_remove:
            del self.peers[peer_to_remove]
            print(f"🔌 Peer {peer_to_remove} desconectado")
    
    async def process_message(self, raw_message, sender_websocket):
        """Procesar mensaje recibido"""
        message = P2PProtocol.parse_message(raw_message)
        if not message:
            print("❌ Mensaje malformado recibido")
            return
        
        msg_type = message.get('type')
        handler = self.message_handlers.get(msg_type)
        
        if handler:
            await handler(message, sender_websocket)
        else:
            print(f"⚠️ No hay handler para tipo de mensaje: {msg_type}")
    
    async def handle_discovery(self, message, sender_websocket):
        """Manejar mensaje de descubrimiento"""
        content = message.get('content', {})
        sender_id = message.get('sender_id')
        action = content.get('action')
        
        if action == 'join' and sender_id:
            self.peers[sender_id] = sender_websocket
            print(f"🤝 Nuevo peer registrado: {sender_id}")
            
            # Responder con confirmación
            response = P2PProtocol.create_message(
                P2PProtocol.MESSAGE_TYPES['DISCOVERY'],
                {'node_id': self.node_id, 'action': 'welcome'},
                self.node_id,
                sender_id
            )
            await sender_websocket.send(response)
    
    async def handle_heartbeat(self, message, sender_websocket):
        """Manejar latido de corazón"""
        sender_id = message.get('sender_id')
        # Responder con heartbeat
        response = P2PProtocol.create_message(
            P2PProtocol.MESSAGE_TYPES['HEARTBEAT'],
            {'status': 'alive', 'timestamp': datetime.now().isoformat()},
            self.node_id,
            sender_id
        )
        await sender_websocket.send(response)
    
    async def handle_alert(self, message, sender_websocket):
        """Manejar alerta crítica recibida"""
        sender_id = message.get('sender_id')
        alert_content = message.get('content')
        
        print(f"\n🚨 ALERTA CRÍTICA RECIBIDA DE {sender_id}:")
        if isinstance(alert_content, list):
            for alert in alert_content:
                print(f"   {alert.get('message', 'Sin mensaje')}")
        else:
            print(f"   {alert_content}")
        print("=" * 50)
    
    async def handle_chat_message(self, message, sender_websocket):
        """Manejar mensaje de chat compartido"""
        sender_id = message.get('sender_id')
        content = message.get('content', {})
        
        print(f"\n💬 CHAT COMPARTIDO POR {sender_id}:")
        print(f"   Usuario: {content.get('user_input', 'N/A')}")
        print(f"   Bot: {content.get('bot_response', 'N/A')}")
        print("-" * 30)
    
    async def broadcast_message(self, message_type, content, target_id=None):
        """Enviar mensaje a todos los peers o a uno específico"""
        if not self.peers:
            print("⚠️ No hay peers conectados para enviar mensaje")
            return
        
        message = P2PProtocol.create_message(message_type, content, self.node_id, target_id)
        
        if target_id and target_id in self.peers:
            # Enviar a peer específico
            try:
                await self.peers[target_id].send(message)
                print(f"📤 Mensaje enviado a {target_id}")
            except Exception as e:
                print(f"❌ Error enviando a {target_id}: {e}")
        else:
            # Broadcast a todos los peers
            disconnected_peers = []
            for peer_id, websocket in self.peers.items():
                try:
                    await websocket.send(message)
                    print(f"📤 Mensaje enviado a {peer_id}")
                except Exception as e:
                    print(f"❌ Error enviando a {peer_id}: {e}")
                    disconnected_peers.append(peer_id)
            
            # Limpiar peers desconectados
            for peer_id in disconnected_peers:
                del self.peers[peer_id]
    
    async def broadcast_alert(self, alerts):
        """Enviar alerta crítica a todos los peers"""
        await self.broadcast_message(
            P2PProtocol.MESSAGE_TYPES['ALERT'],
            alerts
        )
    
    async def share_chat(self, user_input, bot_response):
        """Compartir conversación con peers"""
        content = {
            'user_input': user_input,
            'bot_response': bot_response,
            'context': 'financial_chat',
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_message(
            P2PProtocol.MESSAGE_TYPES['CHAT'],
            content
        )
    
    def get_connected_peers(self):
        """Obtener lista de peers conectados"""
        return list(self.peers.keys())
    
    def stop(self):
        """Detener el nodo"""
        self.running = False
        if self.server:
            self.server.close()