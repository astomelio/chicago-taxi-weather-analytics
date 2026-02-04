# Alternativa Simplificada: Ingesta de Datos

## Opción 1: Solo Airbyte (Recomendado para el diseño)

**Airbyte** es una plataforma ETL open-source moderna que puede manejar tanto batch como streaming, y es mucho más simple de entender y explicar.

### Ventajas:
- ✅ **Una sola herramienta** para todas las fuentes
- ✅ Soporta batch y streaming
- ✅ Interfaz visual fácil de usar
- ✅ Conectores pre-construidos para todas las fuentes necesarias:
  - PostgreSQL, MySQL, MongoDB
  - SAP, Salesforce, SurveyMonkey
- ✅ Open-source
- ✅ Fácil de explicar en el diagrama

### Flujo Simplificado:
```
Fuentes → Airbyte → Cloud Storage (Bronze) → BigQuery
```

### En el Diagrama:
- **Una sola caja:** "Airbyte (ETL Platform)"
- **Flechas directas** desde cada fuente a Airbyte
- **Más simple y claro**

---

## Opción 2: Debezium + Airbyte (Más técnico)

### ¿Qué es Debezium?

**Debezium** es una plataforma de **Change Data Capture (CDC)** open-source.

**¿Qué hace?**
- Se conecta a bases de datos (PostgreSQL, MySQL, MongoDB)
- Detecta cambios en tiempo real (INSERT, UPDATE, DELETE)
- Convierte esos cambios en eventos de streaming
- Los envía a Pub/Sub o Kafka

**Ejemplo práctico:**
```
1. Un cliente actualiza su email en PostgreSQL
2. Debezium detecta el cambio
3. Genera un evento: "customer_123 email changed to new@email.com"
4. Lo envía a Pub/Sub
5. Dataflow procesa el evento y actualiza BigQuery
```

**¿Cuándo usarlo?**
- Cuando necesitas datos **en tiempo real** (segundos/minutos)
- Para mantener sincronización continua entre sistemas
- Para evitar hacer queries pesadas a la BD origen

**¿Cuándo NO usarlo?**
- Si batch diario es suficiente (caso más común)
- Si quieres mantener el diseño simple
- Si las fuentes no soportan CDC (como APIs REST)

### Flujo con Debezium:
```
PostgreSQL/MySQL → Debezium → Pub/Sub → Dataflow → BigQuery
```

---

## Recomendación para el Diagrama

### Opción A: Simple (Recomendado)
**Usar solo Airbyte** para todo:
- Más fácil de explicar
- Cubre todos los casos de uso
- Menos componentes en el diagrama
- Más claro para el evaluador

### Opción B: Completo
**Usar Airbyte + Debezium**:
- Airbyte para batch y APIs
- Debezium para streaming de bases de datos
- Muestra conocimiento técnico más avanzado
- Más complejo de explicar

---

## Cómo Explicarlo en el Diagrama

### Si usas solo Airbyte:
```
┌─────────────┐
│  Airbyte    │  ← Plataforma ETL open-source
│  (ETL)      │     Extrae datos de todas las fuentes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Cloud Storage│
│  (Bronze)   │
└─────────────┘
```

### Si usas Airbyte + Debezium:
```
┌─────────────┐     ┌─────────────┐
│  Airbyte    │     │  Debezium   │  ← CDC para streaming
│  (Batch)    │     │   (CDC)     │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
         ┌─────────────┐
         │Cloud Storage │
         │  (Bronze)    │
         └─────────────┘
```

---

## Mi Recomendación Final

**Para el diseño del desafío, usa solo Airbyte** porque:

1. ✅ Es más simple y fácil de entender
2. ✅ Cumple todos los requisitos (open-source, Google Cloud)
3. ✅ Puede manejar todas las fuentes necesarias
4. ✅ El diagrama será más limpio
5. ✅ Es más fácil de explicar en la presentación

**Puedes mencionar Debezium como "opcional para streaming en tiempo real"** si quieres mostrar conocimiento técnico, pero no es necesario para cumplir el desafío.
