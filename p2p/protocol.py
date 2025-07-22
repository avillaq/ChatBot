import json
import time
from datetime import datetime

class P2PProtocol:
    """Protocolo de comunicación para red P2P"""
    
    MESSAGE_TYPES = {
        'CHAT': 'chat_request',
        'ALERT': 'critical_alert',
        'QUERY': 'db_query',
        'DISCOVERY': 'node_discovery',
        'RESPONSE': 'response',
        'HEARTBEAT': 'heartbeat'
    }
    
    @staticmethod
    def create_message(msg_type, content, sender_id, target_id=None):
        """Crear mensaje estructurado para P2P"""
        message = {
            'type': msg_type,
            'sender_id': sender_id,
            'target_id': target_id,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'message_id': f"{sender_id}_{int(time.time() * 1000)}"
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_message(raw_message):
        """Parsear mensaje recibido"""
        try:
            message = json.loads(raw_message)
            required_fields = ['type', 'sender_id', 'content', 'timestamp']
            
            if all(field in message for field in required_fields):
                return message
            else:
                return None
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def create_alert_message(alert_data, sender_id):
        """Crear mensaje de alerta crítica"""
        return P2PProtocol.create_message(
            P2PProtocol.MESSAGE_TYPES['ALERT'],
            alert_data,
            sender_id
        )
    
    @staticmethod
    def create_chat_message(user_input, response, sender_id):
        """Crear mensaje de chat para compartir"""
        content = {
            'user_input': user_input,
            'bot_response': response,
            'context': 'financial_chat'
        }
        return P2PProtocol.create_message(
            P2PProtocol.MESSAGE_TYPES['CHAT'],
            content,
            sender_id
        )