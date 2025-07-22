import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p2p.node import P2PNode
from nlp_pipeline.enhanced_chatbot import EnhancedChatbot
from monitoring.alert_monitor import AlertMonitor

async def test_p2p_nodes():
    """Probar sistema P2P con múltiples nodos"""
    
    print("🔧 Iniciando prueba del sistema P2P...")
    
    # Crear 3 nodos P2P
    node1 = P2PNode('localhost', 8001, 'financial_node_1')
    node2 = P2PNode('localhost', 8002, 'financial_node_2')
    node3 = P2PNode('localhost', 8003, 'financial_node_3')
    
    # Crear chatbots mejorados para cada nodo
    chatbot1 = EnhancedChatbot("test_financial.db")
    chatbot2 = EnhancedChatbot("test_financial.db")
    chatbot3 = EnhancedChatbot("test_financial.db")
    
    # Vincular nodos P2P con chatbots
    chatbot1.set_p2p_node(node1)
    chatbot2.set_p2p_node(node2)
    chatbot3.set_p2p_node(node3)
    
    try:
        # Iniciar servidores
        print("\n📡 Iniciando servidores P2P...")
        await asyncio.gather(
            node1.start_server(),
            node2.start_server(),
            node3.start_server(),
            test_interactions(node1, node2, node3, chatbot1, chatbot2, chatbot3)
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo prueba...")
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

async def test_interactions(node1, node2, node3, chatbot1, chatbot2, chatbot3):
    """Probar interacciones entre nodos"""
    
    # Esperar a que los servidores se inicien
    await asyncio.sleep(2)
    
    # Conectar nodos entre sí
    print("\n🔗 Conectando nodos...")
    await node2.connect_to_peer('localhost', 8001, 'financial_node_1')
    await node3.connect_to_peer('localhost', 8001, 'financial_node_1')
    await node3.connect_to_peer('localhost', 8002, 'financial_node_2')
    
    await asyncio.sleep(1)
    
    # Probar consultas financieras distribuidas
    print("\n💬 Probando consultas financieras...")
    
    # Consulta de saldo desde nodo 1
    response1 = await chatbot1.process_query("Saldo de Juan")
    print(f"Node 1 response: {response1}")
    
    await asyncio.sleep(1)
    
    # Consulta de transacciones desde nodo 2
    response2 = await chatbot2.process_query("Transacciones de María")
    print(f"Node 2 response: {response2}")
    
    await asyncio.sleep(1)
    
    # Verificar alertas críticas desde nodo 3
    print("\n🚨 Probando detección de alertas críticas...")
    response3 = await chatbot3.process_query("Check critical alerts")
    print(f"Node 3 response: {response3}")
    
    await asyncio.sleep(2)
    
    # Probar monitoreo automatico
    print("\n🔄 Iniciando monitoreo automatico desde nodo 1...")
    monitor = AlertMonitor(chatbot1, check_interval=5)
    monitor.start_monitoring()
    
    # Mantener sistema activo por 30 segundos para ver el monitoreo
    print("⏰ Sistema activo por 30 segundos para demostrar monitoreo...")
    await asyncio.sleep(30)
    
    monitor.stop_monitoring()
    print("\n✅ Prueba completada exitosamente!")

if __name__ == "__main__":
    print("🚀 Iniciando prueba del sistema P2P financiero...")
    print("💡 Presiona Ctrl+C para detener\n")
    
    try:
        asyncio.run(test_p2p_nodes())
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")