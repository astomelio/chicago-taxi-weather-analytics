#!/bin/bash
# Script para automatizar la creación del dashboard de Looker Studio
# Nota: Looker Studio no tiene API completa, pero podemos preparar todo

set -e

echo "🎨 Preparando creación automática de dashboard Looker Studio..."

# Verificar que las tablas existen
echo "📊 Verificando datos en BigQuery..."
python3 << 'PYEOF'
from google.cloud import bigquery
import os
import sys

project_id = os.environ.get('GCP_PROJECT_ID', 'brave-computer-454217-q4')
client = bigquery.Client(project=project_id)

# Verificar daily_summary
try:
    query = f"SELECT COUNT(*) as count FROM `{project_id}.chicago_taxi_gold.daily_summary`"
    result = client.query(query).result()
    count = next(result).count
    if count > 0:
        print(f"✅ daily_summary tiene {count:,} registros")
    else:
        print("⚠️  daily_summary está vacía")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error verificando daily_summary: {e}")
    sys.exit(1)
PYEOF

# Ejecutar script de creación
echo ""
echo "🔄 Ejecutando script de creación..."
python3 scripts/create_looker_dashboard.py

echo ""
echo "✅ Preparación completada"
echo ""
echo "📖 Próximos pasos:"
echo "   1. Revisa looker_dashboard_template.json"
echo "   2. Sigue LOOKER_DASHBOARD_INSTRUCTIONS.md"
echo "   3. O usa CREAR_DASHBOARD.md para guía detallada"
