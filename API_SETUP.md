# Configuración de Datos del Clima

## Fuente Principal: BigQuery Público (NOAA)

**El sistema usa el dataset público de NOAA en BigQuery** (`bigquery-public-data.noaa_gsod`).

- ✅ **No requiere API key**
- ✅ **Datos históricos disponibles desde 1929**
- ✅ **Gratis** (dentro del tier gratuito de GCP)
- ✅ **Datos oficiales** de estaciones meteorológicas

**Estación usada**: Chicago O'Hare International Airport (USW00094846)

### Conversiones Automáticas

El código convierte automáticamente:
- Temperatura: Fahrenheit → Celsius
- Precipitación: Pulgadas → Milímetros
- Viento: Nudos → m/s

---

## Fallback: API Externa (Opcional)

Si BigQuery público no tiene datos para alguna fecha específica, el sistema puede usar una API externa como fallback.

### Visual Crossing Weather API (Ejemplo)

1. Registrarse en: https://www.visualcrossing.com/weather-api
2. Obtener API key desde el dashboard
3. Configurar (opcional):
   ```bash
   export OPENWEATHER_API_KEY="tu-api-key"
   ```

**Nota**: Solo se usa si BigQuery no tiene datos. Para el período 2023, BigQuery público debería tener todos los datos necesarios.

---

## Verificar Datos en BigQuery Público

Puedes verificar que los datos existen con:

```sql
SELECT 
  date,
  temp,
  prcp,
  wdsp
FROM `bigquery-public-data.noaa_gsod.gsod2023`
WHERE stn = '725300'  -- Chicago O'Hare
  AND date >= '2023-06-01'
  AND date <= '2023-12-31'
ORDER BY date
LIMIT 10;
```

---

## Ventajas de Usar BigQuery Público

1. **No requiere API externa** - Todo está en Google Cloud
2. **Datos oficiales** - NOAA es la fuente oficial de datos climáticos de EE.UU.
3. **Gratis** - Dentro del tier gratuito de GCP
4. **Consistente** - Misma fuente que otros proyectos de Google Cloud
5. **Históricos completos** - Datos desde 1929 disponibles
