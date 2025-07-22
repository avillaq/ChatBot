import asyncio
from nlp_pipeline.chatbot import chatbot as base_chatbot
from database.financial_db import FinancialDatabase
from nlp_pipeline.nltk_lib import tokenizer, stemming

class EnhancedChatbot:
    """Chatbot mejorado con capacidades financieras y P2P"""
    
    def __init__(self, db_path="financial.db"):
        self.db = FinancialDatabase(db_path)
        self.p2p_node = None
        
        # Mapeo de intents a funciones
        self.intent_handlers = {
            'balance_inquiry': self.handle_balance_inquiry,
            'transaction_history': self.handle_transaction_history,
            'critical_alerts': self.handle_critical_alerts,
            'account_info': self.handle_account_info
        }
    
    def set_p2p_node(self, p2p_node):
        """Configurar nodo P2P para compartir información"""
        self.p2p_node = p2p_node
    
    async def process_query(self, user_input, user_name=None):
        """Procesar consulta del usuario con capacidades financieras"""
        
        # Clasificar intent usando el modelo base
        intent = self.classify_intent(user_input)
        
        # Si es un intent financiero, usar handler específico
        if intent in self.intent_handlers:
            response = await self.handle_financial_query(intent, user_input, user_name)
        else:
            # Usar chatbot base para conversación general
            response = base_chatbot(user_input)
        
        # Compartir conversación con peers si está habilitado P2P
        if self.p2p_node and hasattr(self.p2p_node, 'share_chat'):
            try:
                await self.p2p_node.share_chat(user_input, response)
            except Exception as e:
                print(f"⚠️ Error compartiendo chat: {e}")
        
        return response
    
    def classify_intent(self, user_input):
        """Clasificar intent usando keywords (método simple pero efectivo)"""
        user_input_lower = user_input.lower()
        
        # Keywords para cada intent financiero
        intent_keywords = {
            'balance_inquiry': ['balance', 'saldo', 'money', 'dinero', 'account', 'cuenta'],
            'transaction_history': ['transaction', 'transaccion', 'history', 'historial', 'payment', 'pago'],
            'critical_alerts': ['alert', 'alerta', 'critical', 'critico', 'warning', 'advertencia'],
            'account_info': ['account info', 'información', 'details', 'detalles', 'summary', 'resumen']
        }
        
        # Buscar coincidencias
        for intent, keywords in intent_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return intent
        
        return None
    
    async def handle_financial_query(self, intent, user_input, user_name):
        """Manejar consulta financiera específica"""
        
        if intent == 'balance_inquiry':
            return self.handle_balance_inquiry(user_input, user_name)
        elif intent == 'transaction_history':
            return self.handle_transaction_history(user_input, user_name)
        elif intent == 'critical_alerts':
            return await self.handle_critical_alerts(user_input)
        elif intent == 'account_info':
            return self.handle_account_info(user_input, user_name)
        else:
            return "No pude procesar tu consulta financiera. ¿Puedes ser más específico?"
    
    def handle_balance_inquiry(self, user_input, user_name):
        """Manejar consulta de saldo"""
        
        # Extraer nombre de usuario del input si no se proporciona
        if not user_name:
            user_name = self.extract_name_from_input(user_input)
        
        if user_name:
            result = self.db.get_account_balance(user_name)
            return f"💰 {result}"
        else:
            return "Para consultar tu saldo, necesito que me digas tu nombre. Por ejemplo: 'Saldo de Juan'"
    
    def handle_transaction_history(self, user_input, user_name):
        """Manejar consulta de historial de transacciones"""
        
        if not user_name:
            user_name = self.extract_name_from_input(user_input)
        
        if user_name:
            result = self.db.get_recent_transactions(user_name, 5)
            return f"📋 {result}"
        else:
            return "Para ver tu historial, necesito que me digas tu nombre. Por ejemplo: 'Transacciones de María'"
    
    async def handle_critical_alerts(self, user_input):
        """Manejar consulta de alertas críticas"""
        
        # Detectar condiciones críticas actuales
        alerts = self.db.detect_critical_conditions()
        
        if alerts:
            # Compartir alertas con red P2P
            if self.p2p_node:
                try:
                    await self.p2p_node.broadcast_alert(alerts)
                    print(f"📡 {len(alerts)} alertas compartidas con la red P2P")
                except Exception as e:
                    print(f"⚠️ Error enviando alertas: {e}")
            
            # Formatear respuesta
            response = "🚨 ALERTAS CRÍTICAS DETECTADAS:\n\n"
            for alert in alerts:
                response += f"• {alert['message']}\n"
            
            response += f"\n📡 Alertas enviadas a {len(self.p2p_node.peers) if self.p2p_node else 0} nodos conectados"
            return response
        else:
            return "✅ No hay alertas críticas en este momento. Todos los sistemas funcionan normalmente."
    
    def handle_account_info(self, user_input, user_name):
        """Manejar consulta de información de cuenta"""
        
        if not user_name:
            user_name = self.extract_name_from_input(user_input)
        
        if user_name:
            balance_info = self.db.get_account_balance(user_name)
            transaction_info = self.db.get_recent_transactions(user_name, 3)
            
            return f"👤 INFORMACIÓN DE CUENTA:\n\n💰 {balance_info}\n\n📋 Últimas transacciones:\n{transaction_info}"
        else:
            return "Para ver tu información de cuenta, necesito que me digas tu nombre."
    
    def extract_name_from_input(self, user_input):
        """Extraer nombre del usuario del input usando palabras clave"""
        
        # Patrones comunes para extraer nombres
        import re
        
        # Buscar patrones como "saldo de Juan", "transacciones de María", etc.
        patterns = [
            r'(?:de|for|para)\s+([A-Za-záéíóúñÑ\s]+)',
            r'(?:usuario|user)\s+([A-Za-záéíóúñÑ\s]+)',
            r'([A-Za-záéíóúñÑ]+)\s*(?:account|cuenta)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Filtrar palabras comunes que no son nombres
                if name.lower() not in ['mi', 'my', 'el', 'la', 'los', 'las', 'account', 'cuenta']:
                    return name
        
        return None
    
    async def check_and_broadcast_alerts(self):
        """Verificar condiciones críticas y enviar a red P2P"""
        alerts = self.db.detect_critical_conditions()
        
        if alerts and self.p2p_node:
            try:
                await self.p2p_node.broadcast_alert(alerts)
                print(f"🔄 Monitoreo automático: {len(alerts)} alertas enviadas a la red")
                return alerts
            except Exception as e:
                print(f"❌ Error en monitoreo automático: {e}")
        
        return alerts

# Función de compatibilidad con el chatbot original
async def enhanced_chatbot(user_input, user_name=None, db_path="financial.db"):
    """Función wrapper para mantener compatibilidad"""
    chatbot_instance = EnhancedChatbot(db_path)
    return await chatbot_instance.process_query(user_input, user_name)