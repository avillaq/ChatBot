import re
from nlp_pipeline.chatbot import chatbot as base_chatbot
from database.financial_db import FinancialDatabase

class EnhancedChatbot:
    """Chatbot mejorado con capacidades financieras y P2P"""
    
    def __init__(self, db_path="financial.db"):
        self.db = FinancialDatabase(db_path)
        self.p2p_node = None
        
        # Mapeo de intents a funciones
        self.intent_handlers = {
            'consulta_saldo': self.handle_balance_inquiry,
            'historial_transacciones': self.handle_transaction_history,
            'alertas_criticas': self.handle_critical_alerts,
            'informacion_cuenta': self.handle_account_info
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
            if response and ("I don't understand" in response or "dumb" in response):
                response = "No entiendo tu consulta. ¿Puedes ser mas específico? Puedo ayudarte con saldos, transacciones o alertas críticas."
        
        # Compartir conversación con peers si esta habilitado P2P
        if self.p2p_node and hasattr(self.p2p_node, 'share_chat'):
            try:
                await self.p2p_node.share_chat(user_input, response)
            except Exception as e:
                print(f"⚠️ Error compartiendo chat: {e}")
        
        return response
    
    def classify_intent(self, user_input):
        """Clasificar intent usando keywords - versión simplificada"""
        user_input_lower = user_input.lower()
                
        # Consulta de saldo
        saldo_keywords = ['saldo de', 'balance de', 'consultar saldo', 'ver saldo', 'mostrar saldo', 
                          'saldo', 'balance', 'dinero', 'cuanto tengo', 'cuánto tengo', 
                          'fondos', 'capital disponible']
        
        for keyword in saldo_keywords:
            if keyword in user_input_lower:
                return 'consulta_saldo'
        
        # Historial de transacciones
        transaccion_keywords = ['transacciones de', 'historial de', 'movimientos de', 
                               'transacciones', 'historial', 'movimientos', 'pagos', 
                               'transferencias', 'actividad', 'operaciones']
        
        for keyword in transaccion_keywords:
            if keyword in user_input_lower:
                return 'historial_transacciones'
        
        # Alertas críticas
        alerta_keywords = ['alertas criticas', 'alertas críticas', 'alertas', 'alerta', 
                           'advertencias', 'problemas', 'seguridad', 'emergencia']
        
        for keyword in alerta_keywords:
            if keyword in user_input_lower:
                return 'alertas_criticas'
        
        # Información de cuenta
        info_keywords = ['informacion de cuenta', 'información de cuenta', 'informacion de', 
                         'información de', 'información', 'detalles', 'resumen', 'perfil']
        
        for keyword in info_keywords:
            if keyword in user_input_lower:
                return 'informacion_cuenta'
        
        return None
    
    async def handle_financial_query(self, intent, user_input, user_name):
        """Manejar consulta financiera específica"""
        
        if intent == 'consulta_saldo':
            return self.handle_balance_inquiry(user_input, user_name)
        elif intent == 'historial_transacciones':
            return self.handle_transaction_history(user_input, user_name)
        elif intent == 'alertas_criticas':
            return await self.handle_critical_alerts(user_input)
        elif intent == 'informacion_cuenta':
            return self.handle_account_info(user_input, user_name)
        else:
            return "No pude procesar tu consulta financiera. ¿Puedes ser mas específico?"
    
    def handle_balance_inquiry(self, user_input, user_name):
        """Manejar consulta de saldo"""
        
        # Extraer nombre de usuario del input si no se proporciona
        if not user_name:
            user_name = self.extract_name_from_input(user_input)
        
        if user_name:
            result = self.db.get_account_balance(user_name)
            return f"💰 {result}"
        else:
            return "Para consultar el saldo, necesito que me digas el nombre. Por ejemplo: 'Saldo de Juan'"
    
    def handle_transaction_history(self, user_input, user_name):
        """Manejar consulta de historial de transacciones"""
        
        if not user_name:
            user_name = self.extract_name_from_input(user_input)
        
        if user_name:
            result = self.db.get_recent_transactions(user_name, 5)
            return f"📋 {result}"
        else:
            return "Para ver el historial, necesito que me digas el nombre. Por ejemplo: 'Transacciones de María'"
    
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
            
            peer_count = len(self.p2p_node.peers) if self.p2p_node else 0
            response += f"\n📡 Alertas enviadas a {peer_count} nodos conectados"
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
            return "Para ver la información de cuenta, necesito que me digas el nombre."
    
    def extract_name_from_input(self, user_input):
        """Extraer nombre del usuario del input usando palabras clave"""
        
        # Patrones comunes para extraer nombres en español
        import re
        
        # Buscar patrones como "saldo de Juan", "transacciones de María", etc.
        patterns = [
            r'(?:de|para|del|de la)\s+([A-Za-záéíóúñÑ\s]+)',
            r'(?:usuario|cuenta de)\s+([A-Za-záéíóúñÑ\s]+)',
            r'([A-Za-záéíóúñÑ]+)\s*(?:cuenta|saldo|transacciones)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Filtrar palabras comunes que no son nombres
                common_words = ['mi', 'mis', 'el', 'la', 'los', 'las', 'cuenta', 'saldo', 'transacciones']
                if name.lower() not in common_words and len(name) > 0:
                    return name
        
        return None
    
    async def check_and_broadcast_alerts(self):
        """Verificar condiciones críticas y enviar a red P2P"""
        alerts = self.db.detect_critical_conditions()
        
        if alerts and self.p2p_node:
            try:
                await self.p2p_node.broadcast_alert(alerts)
                print(f"🔄 Monitoreo automatico: {len(alerts)} alertas enviadas a la red")
                return alerts
            except Exception as e:
                print(f"❌ Error en monitoreo automatico: {e}")
        
        return alerts

# Función de compatibilidad con el chatbot original
async def enhanced_chatbot(user_input, user_name=None, db_path="financial.db"):
    """Función wrapper para mantener compatibilidad"""
    chatbot_instance = EnhancedChatbot(db_path)
    return await chatbot_instance.process_query(user_input, user_name)