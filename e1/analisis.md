# P4 — Comparativa de proveedores
Nicolás González del Río

## Método

He enviado cinco correos a cada uno de los tres modelos utilizando
el mismo mensaje de sistema y un límite de 1024 tokens de salida.
He registrado el tiempo, los tokens, el coste estimado y la respuesta.

Los modelos utilizados son:
- OpenAI: openai/gpt-5.4-mini.
- Claude: anthropic/claude-haiku-4.5.
- Gemini: google/gemini-3.8-flash.

## Criterio de calidad

La puntuación valora la utilidad, la claridad, el cumplimiento de la
instrucción de brevedad y que la respuesta no invente información.

- 5: útil, pertinente y sin afirmaciones importantes no justificadas.
- 4: buena respuesta, con algún detalle mejorable.
- 3: parcialmente útil, pero con suposiciones o compromisos no comprobados.
- 2: poco concreta o afirma información importante sin respaldo.
- 1: inventa varios detalles importantes que podrían confundir al cliente.

Las puntuaciones son subjetivas y se aplican a esta muestra.

## Resultados medios

| Proveedor | Tiempo medio | Tokens de salida medios | Coste medio por correo (USD) | Calidad media sobre 5 | Coste estimado de 2000 correos (USD) |
|---|---:|---:|---:|---:|---:|
| OpenAI | 2,31 s | 60,2 | 0,00031140 | 3,4 | 0,6228 |
| Claude | 1,86 s | 74,6 | 0,00044000 | 3,2 | 0,8800 |
| Gemini | 5,24 s | 520,2 | 0,00198315 | 2,6 | 3,9663 |

El coste mensual se calcula multiplicando el coste medio por correo
por 2000. Es una estimación basada en estos cinco ejemplos por modelo
y en los precios configurados, sin ajustes por caché, reintentos,
comisiones u otros gastos.

## Justificación de las puntuaciones

### OpenAI

- Entregas, 2/5: afirma que hay reparto los sábados sin conocer la política.
- Cafetera, 4/5: plantea posibles causas y pide datos útiles para aclararlas.
- Pedido, 3/5: recoge las cantidades y pide la dirección, pero promete
  prepararlo para el jueves sin comprobar disponibilidad.
- Factura, 3/5: presenta posibilidades y ofrece revisar el detalle,
  aunque los ajustes de lecturas parecen propios de otros suministros.
- Hotel, 5/5: recomienda perfiles de café de forma general y pide
  información sobre volumen y maquinaria sin inventar un producto concreto.

### Claude

- Entregas, 2/5: confirma el reparto sin respaldo, aunque después
  recomienda consultar los horarios.
- Cafetera, 3/5: ofrece posibles causas y derivación técnica, pero
  recomienda revisar piezas sin conocer la máquina ni pedir más datos.
- Pedido, 4/5: recoge correctamente las cantidades y solicita la dirección;
  podría dejar más clara la necesidad de confirmar la fecha.
- Factura, 5/5: reconoce que no puede ver las facturas, plantea causas
  posibles y propone revisar el desglose.
- Hotel, 2/5: ofrece una respuesta comercial poco concreta e inventa
  características del producto y servicios de degustación.

### Gemini

- Entregas, 1/5: inventa el reparto en sábado, sus condiciones y la
  posibilidad de seleccionar una franja en la web.
- Cafetera, 3/5: solicita identificación, pero plantea enviar un técnico
  sin comprobar el procedimiento ni la disponibilidad.
- Pedido, 4/5: recoge el pedido y solicita datos para tramitarlo;
  falta aclarar que la entrega está pendiente de confirmación.
- Factura, 4/5: plantea posibles causas y solicita la identificación
  de la factura, aunque presupone un patrón de consumo estacional.
- Hotel, 1/5: inventa un producto llamado Blend Especial Hostelería,
  su composición y la disponibilidad de una visita con cata.

## ¿Por qué Gemini registra muchos más tokens de salida?

Los tokens de salida pueden incluir razonamiento interno además del
texto visible. Por eso una respuesta breve puede consumir muchos tokens.

Gemini registra una media de 520,2 tokens frente a 60,2 de OpenAI
y 74,6 de Claude, aunque sus respuestas visibles son también cortas.
Esto es compatible con un mayor consumo de razonamiento interno.
El CSV no incluye el desglose necesario para determinar su cantidad exacta.

Las diferencias entre tokenizadores también influyen en el recuento,
pero no debe confundirse el total de tokens con la longitud visible.

## ¿Qué modelo elegiría para contestar 2000 correos al mes?

Elegiría OpenAI como punto de partida para generar borradores:
tiene el menor coste estimado, unos 0,62 USD para 2000 correos,
la mejor calidad media según esta valoración, 3,4 sobre 5,
y una latencia media de 2,31 segundos.

Claude es más rápido, con 1,86 segundos, y su coste mensual estimado
también es bajo, unos 0,88 USD. Sería una alternativa interesante
si se priorizara la rapidez.

Gemini resulta más lento y caro en esta muestra y obtiene una
puntuación inferior por inventar detalles concretos del negocio.

Antes de enviar respuestas automáticamente, conectaría el sistema
con información real de pedidos, productos, facturación y reparto.
También indicaría que no confirme acciones ni condiciones desconocidas.

## Limitaciones

Solo he probado cinco correos por modelo en una ejecución.
Los tiempos y las respuestas pueden variar y las diferencias de calidad
son pequeñas y subjetivas. Harían falta más ejemplos y repeticiones
para tomar una decisión de producción.