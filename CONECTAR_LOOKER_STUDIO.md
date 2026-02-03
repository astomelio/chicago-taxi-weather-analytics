# 🔗 Cómo Conectar Looker Studio a BigQuery - Guía Simple

## ¿Qué necesitas hacer?

Conectar Looker Studio a tus datos en BigQuery para crear el dashboard.

## 📋 Paso 1: Obtener la Información de Conexión

Terraform ya creó todo y generó una URL especial para conectar fácilmente.

### Opción A: Usar la URL Automática (MÁS FÁCIL) ⭐

1. **Abre tu terminal** y ejecuta:
   ```bash
   cd terraform
   terraform output looker_studio_connection_info
   ```

2. **Verás algo como esto**:
   ```
   {
     "connection_url" = "https://lookerstudio.google.com/datasources/create?connectorId=bigquery&projectId=..."
     "full_path" = "brave-computer-454217-q4.chicago_taxi_gold.daily_summary"
     ...
   }
   ```

3. **Copia la URL** que está en `connection_url` (la que empieza con `https://lookerstudio.google.com/...`)

4. **Pega la URL en tu navegador** y presiona Enter

5. **¡Listo!** Looker Studio se abrirá automáticamente con la conexión a BigQuery ya configurada

### Opción B: Conectar Manualmente (Si prefieres hacerlo paso a paso)

1. **Abre Looker Studio**:
   - Ve a: https://lookerstudio.google.com/
   - (Necesitas estar logueado con tu cuenta de Google)

2. **Crear un nuevo reporte**:
   - Click en el botón **"Create"** (arriba a la izquierda)
   - Selecciona **"Report"**

3. **Agregar fuente de datos**:
   - Te aparecerá una ventana "Add data to report"
   - Busca y click en **"BigQuery"** (está en la lista de conectores)

4. **Seleccionar tu proyecto y tabla**:
   - En "Select a BigQuery project", busca y selecciona: `brave-computer-454217-q4` (o tu proyecto)
   - En "Select a dataset", selecciona: `chicago_taxi_gold`
   - En "Select a table", selecciona: `daily_summary`
   - Click en **"Add"** (o "Connect")

5. **¡Listo!** Ya estás conectado a tus datos

## 🎯 ¿Cuál opción usar?

- **Opción A (URL automática)**: Más rápido, menos pasos, recomendado
- **Opción B (Manual)**: Si prefieres ver cada paso o si la URL no funciona

## ✅ Después de Conectar

Una vez conectado, verás tus datos en Looker Studio y podrás:
- Crear gráficos
- Agregar métricas
- Diseñar el dashboard

**Sigue el resto de `CREAR_DASHBOARD.md` para crear las visualizaciones.**

## 🔍 Verificar que Funcionó

Si todo está bien, deberías ver:
- Una tabla con columnas como: `date`, `total_trips`, `temperature`, `weather_category`, etc.
- Los datos de junio-diciembre 2023
- Un editor de reporte listo para crear visualizaciones

## ❓ Problemas Comunes

### "No puedo ver el proyecto en BigQuery"
- Verifica que estés logueado con la misma cuenta de Google que usaste para crear el proyecto
- Verifica que el proyecto tenga facturación habilitada

### "La tabla daily_summary no existe"
- Ejecuta primero los modelos dbt: `cd dbt && dbt run --models gold`
- O espera a que GitHub Actions complete el despliegue

### "No tengo permisos"
- Verifica que tu cuenta tenga acceso al proyecto de GCP
- Verifica que el dataset `chicago_taxi_gold` exista

## 📖 Siguiente Paso

Una vez conectado, sigue `CREAR_DASHBOARD.md` desde el **Paso 2** para crear las visualizaciones.
