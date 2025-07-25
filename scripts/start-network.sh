#!/bin/bash

echo "🐳 Iniciando Red P2P con Docker..."

# Limpiar contenedores existentes
echo "🧹 Limpiando contenedores existentes..."
docker-compose -f docker/docker-compose.yml down --volumes

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose -f docker/docker-compose.yml build

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose -f docker/docker-compose.yml up -d

# Mostrar estado
echo "📊 Estado de los servicios:"
docker-compose -f docker/docker-compose.yml ps

echo "✅ Red P2P iniciada!"
echo ""
echo "🌐 Interfaces web disponibles:"
echo "   • Banco Principal: http://localhost:5000"
echo "   • Banco Nacional:  http://localhost:5001"
echo "   • Banco Central:   http://localhost:5002"
echo "   • Banco Regional:  http://localhost:5003"
echo ""
echo "📝 Ver logs con: docker-compose -f docker/docker-compose.yml logs -f"
echo "⏹️  Detener con: docker-compose -f docker/docker-compose.yml down"