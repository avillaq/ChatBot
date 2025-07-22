import asyncio
from nlp_pipeline.enhanced_chatbot import EnhancedChatbot
from p2p.node import P2PNode
from monitoring.alert_monitor import AlertMonitor

class LiveDemo:
    """Demostración en vivo del sistema P2P"""
    
    def __init__(self):
        self.nodes = {}
        self.chatbots = {}
        self.monitors = {}
        
    async def setup_network(self):
        """Configurar red de 3 nodos"""
        print("🔧 Configurando red de demostración con 3 nodos...")
        
        # Crear 3 nodos
        ports = [8201, 8202, 8203]
        node_names = ['Banco_Central', 'Sucursal_A', 'Sucursal_B']
        
        for i, (port, name) in enumerate(zip(ports, node_names)):
            # Crear nodo P2P
            node = P2PNode('localhost', port, name)
            self.nodes[name] = node
            
            # Crear chatbot
            chatbot = EnhancedChatbot("financial.db")
            chatbot.set_p2p_node(node)
            self.chatbots[name] = chatbot
            
            # Crear monitor
            monitor = AlertMonitor(chatbot, check_interval=15)
            self.monitors[name] = monitor
            
            # Iniciar servidor
            asyncio.create_task(node.start_server())
            print(f"  ✅ {name} iniciado en puerto {port}")
        
        # Esperar que todos los servidores se inicien
        await asyncio.sleep(2)
        
        # Conectar nodos en topología de malla
        print("\n🔗 Conectando nodos...")
        await self.nodes['Sucursal_A'].connect_to_peer('localhost', 8201, 'Banco_Central')
        await self.nodes['Sucursal_B'].connect_to_peer('localhost', 8201, 'Banco_Central')
        await self.nodes['Sucursal_B'].connect_to_peer('localhost', 8202, 'Sucursal_A')
        
        await asyncio.sleep(1)
        
        # Iniciar monitoreo en todos los nodos
        for name, monitor in self.monitors.items():
            monitor.start_monitoring()
            print(f"  📡 Monitor activo en {name}")
        
        print("✅ Red P2P configurada y operativa!")
        
    def show_network_status(self):
        """Mostrar estado de la red"""
        print("\n📊 ESTADO DE LA RED P2P:")
        print("=" * 50)
        
        for name, node in self.nodes.items():
            peers = node.get_connected_peers()
            print(f"🏦 {name}:")
            print(f"  - Puerto: {node.port}")
            print(f"  - Peers: {len(peers)} conectados {peers}")
            print()
    
    async def demonstrate_financial_queries(self):
        """Demostrar consultas financieras"""
        print("💰 DEMOSTRANDO CONSULTAS FINANCIERAS:")
        print("=" * 50)
        
        demo_queries = [
            ("Saldo de Juan", "Banco_Central"),
            ("Transacciones de María", "Sucursal_A"),
            ("Critical alerts", "Sucursal_B"),
            ("Account info de Carlos", "Banco_Central")
        ]
        
        for query, node_name in demo_queries:
            print(f"\n🔍 Consulta desde {node_name}: '{query}'")
            
            chatbot = self.chatbots[node_name]
            response = await chatbot.process_query(query)
            
            print(f"📤 Respuesta: {response[:100]}...")
            await asyncio.sleep(2)
    
    async def demonstrate_alert_propagation(self):
        """Demostrar propagación de alertas"""
        print("\n🚨 DEMOSTRANDO PROPAGACIÓN DE ALERTAS:")
        print("=" * 50)
        
        print("Forzando detección de alertas críticas...")
        
        # Detectar alertas desde Banco_Central
        chatbot = self.chatbots['Banco_Central']
        alerts = await chatbot.check_and_broadcast_alerts()
        
        if alerts:
            print(f"📡 {len(alerts)} alertas detectadas y enviadas a la red:")
            for alert in alerts:
                print(f"  - {alert['type']}: {alert['user_name']}")
        else:
            print("ℹ️ No hay alertas críticas en este momento")
        
        await asyncio.sleep(3)
    
    async def interactive_demo(self):
        """Demostración interactiva"""
        print("\n💬 MODO INTERACTIVO:")
        print("=" * 50)
        print("Escribe consultas para probar el sistema distribuido")
        print("Comandos especiales:")
        print("  - 'status' - Ver estado de la red")
        print("  - 'alerts' - Forzar verificación de alertas")
        print("  - 'switch <nodo>' - Cambiar nodo activo")
        print("  - 'quit' - Salir")
        print()
        
        current_node = 'Banco_Central'
        
        while True:
            try:
                user_input = input(f"\n[{current_node}] > ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'status':
                    self.show_network_status()
                elif user_input.lower() == 'alerts':
                    chatbot = self.chatbots[current_node]
                    alerts = await chatbot.check_and_broadcast_alerts()
                    print(f"🔍 {len(alerts) if alerts else 0} alertas detectadas")
                elif user_input.lower().startswith('switch '):
                    new_node = user_input[7:].strip()
                    if new_node in self.nodes:
                        current_node = new_node
                        print(f"✅ Cambiado a {current_node}")
                    else:
                        print(f"❌ Nodo '{new_node}' no encontrado")
                        print(f"Nodos disponibles: {list(self.nodes.keys())}")
                elif user_input:
                    chatbot = self.chatbots[current_node]
                    response = await chatbot.process_query(user_input)
                    print(f"🤖 {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        print("\n🧹 Limpiando recursos...")
        
        # Detener monitores
        for monitor in self.monitors.values():
            monitor.stop_monitoring()
        
        # Detener nodos
        for node in self.nodes.values():
            node.stop()
        
        print("✅ Recursos liberados")

async def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN EN VIVO - CHATBOT P2P FINANCIERO")
    print("=" * 60)
    
    demo = LiveDemo()
    
    try:
        # Configurar red
        await demo.setup_network()
        
        # Mostrar estado inicial
        demo.show_network_status()
        
        # Demostrar funcionalidades automáticas
        await demo.demonstrate_financial_queries()
        await demo.demonstrate_alert_propagation()
        
        # Modo interactivo
        await demo.interactive_demo()
        
    except KeyboardInterrupt:
        print("\n⏹️ Demostración interrumpida")
    except Exception as e:
        print(f"❌ Error en demostración: {e}")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    print("💡 Presiona Ctrl+C para detener la demostración\n")
    asyncio.run(main())