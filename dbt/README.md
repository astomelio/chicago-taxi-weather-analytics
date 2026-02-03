# dbt Models

Este directorio contiene los modelos de transformación de datos usando dbt.

## Estructura

```
dbt/
├── models/
│   ├── silver/          # Capa Silver (datos limpios)
│   │   ├── taxi_trips_silver.sql
│   │   ├── weather_silver.sql
│   │   └── schema.yml
│   └── gold/            # Capa Gold (datos analíticos)
│       ├── daily_summary.sql
│       ├── taxi_weather_analysis.sql
│       └── schema.yml
├── dbt_project.yml      # Configuración del proyecto
└── profiles.yml         # Configuración de conexión a BigQuery
```

## Capas de Datos

### Silver Layer

**Objetivo**: Limpiar y deduplicar datos raw

- `taxi_trips_silver`: Viajes de taxis limpios y deduplicados
- `weather_silver`: Datos del clima limpios y categorizados

**Características**:
- Eliminación de duplicados
- Validación de esquemas
- Enriquecimiento con campos calculados
- Particionamiento por fecha

### Gold Layer

**Objetivo**: Datos listos para análisis y dashboards

- `daily_summary`: Resumen diario agregado
- `taxi_weather_analysis`: Análisis detallado por hora y clima

**Características**:
- Agregaciones pre-calculadas
- Joins entre taxis y clima
- Métricas calculadas
- Optimizado para consultas de BI

## Uso

### Instalar dbt

```bash
pip install dbt-bigquery
```

### Configurar Credenciales

1. Crear service account en GCP
2. Descargar key JSON
3. Configurar variable de entorno:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
   export GCP_PROJECT_ID="your-project-id"
   ```

### Ejecutar Modelos

```bash
# Ejecutar todos los modelos
dbt run

# Ejecutar solo modelos Silver
dbt run --models silver

# Ejecutar solo modelos Gold
dbt run --models gold

# Ejecutar un modelo específico
dbt run --models taxi_trips_silver
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
dbt test

# Ejecutar tests de un modelo específico
dbt test --models taxi_trips_silver
```

### Generar Documentación

```bash
# Generar documentación
dbt docs generate

# Servir documentación localmente
dbt docs serve
```

### Compilar sin Ejecutar

```bash
# Compilar SQL sin ejecutar
dbt compile
```

## Tests Implementados

- **Uniqueness**: Verificar que las claves únicas no tengan duplicados
- **Not Null**: Verificar que campos requeridos no sean nulos
- **Accepted Values**: Validar valores permitidos (si aplica)

## Mejores Prácticas

1. **Versionado**: Todos los cambios en Git
2. **Tests**: Agregar tests para validaciones importantes
3. **Documentación**: Mantener schemas.yml actualizado
4. **Incremental**: Considerar modelos incrementales para grandes volúmenes
5. **Particionamiento**: Usar particionamiento para optimizar consultas

## Troubleshooting

### Error de Permisos

Asegúrate de que el service account tenga permisos:
- `BigQuery Data Editor`
- `BigQuery Job User`

### Error de Cuota

Si excedes la cuota gratuita, considera:
- Usar `maximum_bytes_billed` en profiles.yml
- Optimizar queries con filtros de fecha
- Usar particionamiento y clustering
