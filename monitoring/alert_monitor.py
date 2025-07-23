import asyncio
import threading
from datetime import datetime

class AlertMonitor:
    """Monitor automatico de alertas críticas para red P2P"""
    
    def __init__(self, enhanced_chatbot, check_interval=30):
        self.enhanced_chatbot = enhanced_chatbot
        self.check_interval = check_interval  # segundos
        self.monitoring = False
        self.monitor_task = None
    
    def start_monitoring(self):
        """Iniciar monitoreo automatico en hilo separado"""
        if self.monitoring:
            print("⚠️ El monitoreo ya esta activo")
            return
        
        self.monitoring = True
        
        # Crear hilo para monitoreo asíncrono
        def run_monitor():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._monitor_loop())
        
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()
        
        print(f" Monitoreo de alertas iniciado (cada {self.check_interval}s)")
    
    async def _monitor_loop(self):
        """Loop principal de monitoreo"""
        while self.monitoring:
            try:
                # Verificar condiciones críticas
                alerts = await self.enhanced_chatbot.check_and_broadcast_alerts()
                
                if alerts:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}]  Monitor: {len(alerts)} condiciones críticas detectadas")
                    
                    # Log de alertas para debug
                    for alert in alerts:
                        print(f"   - {alert.get('type', 'UNKNOWN')}: {alert.get('user_name', 'N/A')}")
                
                # Esperar antes del siguiente check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                await asyncio.sleep(5)  # Esperar menos tiempo en caso de error
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        print(" Monitoreo de alertas detenido")
    
    def set_check_interval(self, seconds):
        """Cambiar intervalo de verificación"""
        self.check_interval = seconds
        print(f" Intervalo de monitoreo cambiado a {seconds}s")