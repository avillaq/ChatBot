#!/bin/bash
echo "🔗 Conectando nodos P2P..."

# Esperar que todos los nodos se inicien
echo "⏳ Esperando que los nodos se inicien..."
sleep 10

echo "✅ Nodos conectándose automáticamente según configuración..."
echo "🔍 Verificar logs con: docker-compose -f docker/docker-compose.yml logs"