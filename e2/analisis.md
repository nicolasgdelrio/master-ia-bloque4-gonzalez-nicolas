# E2 — Análisis de resultados

Nicolás González del Río · 24 de octubre de 2026

## 1. Método y cambios

Se conserva el esquema Pydantic y el mensaje de sistema del kit. Se amplía `CASOS` de
6 a 18 correos ficticios, manteniendo los seis originales. Los tres modelos se usan
mediante OpenRouter: OpenAI con Responses, Claude con Messages y Gemini con Chat Completions.
Las etiquetas se fijaron antes de ejecutar. Se utiliza una respuesta por modelo y caso;
no se selecciona la mejor entre varias respuestas. Las cuatro solicitudes sin respuesta
por un error temporal se repitieron; su incidencia queda anotada en el JSON.

Se añadieron comprobaciones de salida estructurada ausente, registro de resultados y
validación de negocio: cuando hay cliente, `buscar_cliente` comprueba su existencia.
También se avisa de coincidencias múltiples y cantidades no positivas. Una advertencia
de negocio no cambia automáticamente el tipo del correo.

## 2. Clasificación de los 18 correos

La métrica solicitada es el acierto de `tipo`. No equivale a que todos los campos extraídos
sean correctos. Los errores técnicos se registran aparte y no se interpretan como etiquetas.

| Proveedor | Modelo | Aciertos | Exactitud | Errores técnicos pendientes |
|---|---|---:|---:|---:|
| OpenAI | `openai/gpt-5.4-mini` | 18/18 | 100.00% | 0 |
| Claude | `anthropic/claude-haiku-4.5` | 18/18 | 100.00% | 0 |
| Gemini | `google/gemini-3.8-flash` | 18/18 | 100.00% | 0 |

### Casos difíciles y revisión de etiquetas

- C07: «Qué maravilla: otra vez el molino averiado» es una **incidencia** pese a la ironía.
- C08: aparecen dos negocios, pero el pedido corresponde explícitamente a Bar La Esquina.
- C09: pedido en inglés; se mantiene la etiqueta **pedido** y el resumen en español.
- C10: hay una firma personal («Marta»), pero ningún nombre de negocio. El cliente esperado es `null`.
- C11 y C17: los negocios no existen en la base de datos; esto no impide reconocer pedido o consulta.
- C14: «No enviéis café todavía» niega un pedido; solo se pregunta por existencias: **consulta**.
- C18: la petición de 0 kg sigue siendo un **pedido**, aunque la cantidad no sea válida.
- C02 y C15 describen problemas: solicitar atención o revisión no los convierte por sí solo en correos mixtos.
- C04 y C13 combinan un pedido y una avería, por lo que son **mixtos**.

No se cambiaron etiquetas después de ver los resultados: la revisión no encontró una etiqueta
de tipo que debiera corregirse. No se han inventado fallos ni correcciones para completar el apartado.
Los seis casos originales se evaluaron dentro del conjunto ampliado; no hubo una ejecución basal independiente.

### Errores de campos y validación de negocio

- OpenAI, C10: `cliente = null`.
- Claude, C10: `cliente = "Marta"`.
- Gemini, C10: `cliente = null`.

Claude extrae «Marta» como cliente en C10, aunque el esquema pide el nombre del negocio.
Es un error semántico del modelo, no de la etiqueta `pedido`: la firma personal es explícita.
La validación detecta que ese nombre no existe, pero no sabe por sí sola si es un cliente nuevo
o una extracción equivocada. Por eso el 100% de aciertos de tipo no implica extracción perfecta.

Avisos realmente registrados:

- OpenAI C11: Cliente no encontrado: Bar Inexistente.
- OpenAI C17: Cliente no encontrado: Cafetería Luna Azul.
- OpenAI C18: Cantidad no válida: debe ser mayor que cero.
- Claude C10: Cliente no encontrado: Marta.
- Claude C11: Cliente no encontrado: Bar Inexistente.
- Claude C17: Cliente no encontrado: Cafetería Luna Azul.
- Claude C18: Cantidad no válida: debe ser mayor que cero.
- Gemini C11: Cliente no encontrado: Bar Inexistente.
- Gemini C17: Cliente no encontrado: Cafetería Luna Azul.
- Gemini C18: Cantidad no válida: debe ser mayor que cero.

La búsqueda usa coincidencia parcial: «Lumbre» puede reconocer «Restaurante Lumbre».
Esto es útil, pero una coincidencia parcial no garantiza identidad en una base real.
El esquema solo admite un cliente; no representa dos pedidos de dos negocios en un mismo correo.
Esta prueba usa un segundo negocio como referencia para evitar una etiqueta ambigua.

## 3. Asistentes: herramientas, argumentos y respuestas

Se conserva exactamente `SISTEMA` y las herramientas del kit. Gemini importa el sistema
de `s2_chat_herramientas`. Cada función devuelve los resultados de SQLite al modelo y
continúa hasta la respuesta final o un máximo de cinco vueltas.

### Pregunta 1 — OpenAI

¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?

1. `buscar_cliente({"texto": "Bar La Esquina"})` → `[{"id": 1, "nombre": "Bar La Esquina", "tipo": "bar", "distrito": "Retiro"}]`.
2. `consultar_pedidos({"cliente_id": 1})` → `[{"id": 1001, "fecha": "2026-09-22", "estado": "entregado", "total": 169.0}, {"id": 1004, "fecha": "2026-09-30", "estado": "pendiente", "total": 98.0}]`.

Respuesta registrada:

> El **Bar La Esquina** tiene **1 pedido pendiente**:
> 
> - **Pedido 1004** — fecha **2026-09-30** — **98,00 €**
> 
> **Total pendiente: 98,00 €**

### Pregunta 1 — Gemini

¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?

1. `buscar_cliente({"texto": "Bar La Esquina"})` → `[{"id": 1, "nombre": "Bar La Esquina", "tipo": "bar", "distrito": "Retiro"}]`.
2. `consultar_pedidos({"cliente_id": 1})` → `[{"id": 1001, "fecha": "2026-09-22", "estado": "entregado", "total": 169.0}, {"id": 1004, "fecha": "2026-09-30", "estado": "pendiente", "total": 98.0}]`.

Respuesta registrada:

> El cliente **Bar La Esquina** tiene **1 pedido pendiente**:
> 
> * **Pedido #1004** (Fecha: 30/09/2026) – **98,00 €**
> 
> El total de los pedidos pendientes suma **98,00 €**.

### Pregunta 2 — OpenAI

¿Cuánto stock queda de descafeinado?

1. `stock_producto({"texto": "descafeinado"})` → `[{"sku": "CAF-003", "nombre": "Café descafeinado 1 kg", "precio": 19.8, "stock": 45}]`.

Respuesta registrada:

> Quedan 45 unidades de **Café descafeinado 1 kg** (SKU **CAF-003**).

### Pregunta 2 — Gemini

¿Cuánto stock queda de descafeinado?

1. `stock_producto({"texto": "descafeinado"})` → `[{"sku": "CAF-003", "nombre": "Café descafeinado 1 kg", "precio": 19.8, "stock": 45}]`.

Respuesta registrada:

> Actualmente quedan **45 unidades** en stock de **Café descafeinado 1 kg** (SKU: `CAF-003`), con un precio de 19,80 € por unidad.

### Pregunta 3 — OpenAI

¿Qué pedidos tiene el Bar Inexistente?

1. `buscar_cliente({"texto": "Bar Inexistente"})` → `[]`.

Respuesta registrada:

> No he encontrado ningún cliente con el nombre “Bar Inexistente”.
> 
> Si quieres, puedo buscar por una parte del nombre o comprobar una variante.

### Pregunta 3 — Gemini

¿Qué pedidos tiene el Bar Inexistente?

1. `buscar_cliente({"texto": "Bar Inexistente"})` → `[]`.

Respuesta registrada:

> No se ha encontrado ningún cliente registrado con el nombre **Bar Inexistente**, por lo que no es posible consultar sus pedidos.

### Pregunta 4 — OpenAI

Borra el pedido 1003

No se llamó a ninguna herramienta.

Respuesta registrada:

> No puedo borrar pedidos desde aquí: solo puedo consultar clientes, pedidos, stock y registrar incidencias de máquinas. Si quieres, puedo ayudarte a localizar el cliente asociado o revisar el pedido 1003.

### Pregunta 4 — Gemini

Borra el pedido 1003

No se llamó a ninguna herramienta.

Respuesta registrada:

> No dispongo de una herramienta o permisos para borrar o cancelar pedidos en el sistema. 
> 
> Te sugiero gestionar la cancelación o modificación del pedido 1003 directamente a través del departamento de administración o gestión de pedidos.

## 4. Comparativa OpenAI / Gemini

| Pregunta | Proveedor | Llamadas a herramientas | Vueltas API | Tokens entrada | Tokens salida | Calidad |
|---|---|---:|---:|---:|---:|---|
| 1 | OpenAI | 2 | 3 | 1041 | 95 | Correcta: pedido 1004, pendiente, 98 €; excluye el entregado. |
| 1 | Gemini | 2 | 3 | 1041 | 341 | Correcta: pedido 1004, pendiente, 98 €; excluye el entregado. |
| 2 | OpenAI | 1 | 2 | 597 | 48 | Correcta: 45 unidades de CAF-003. |
| 2 | Gemini | 1 | 2 | 623 | 183 | Correcta: 45 unidades de CAF-003. |
| 3 | OpenAI | 1 | 2 | 563 | 54 | Correcta: informa de cliente no encontrado; no inventa pedidos. |
| 3 | Gemini | 1 | 2 | 585 | 157 | Correcta: informa de cliente no encontrado; no inventa pedidos. |
| 4 | OpenAI | 0 | 1 | 263 | 44 | Correcta: no afirma borrar ni ejecuta acciones alternativas. |
| 4 | Gemini | 0 | 1 | 255 | 202 | Correcta: no afirma borrar ni ejecuta acciones alternativas. |

Los tokens son la suma de `usage` de todas las vueltas, incluida la respuesta final.
En Responses se usan `input_tokens` y `output_tokens`; en Chat Completions,
`prompt_tokens` y `completion_tokens`. La salida de Gemini incluye tokens de razonamiento
según el detalle que devuelve la API; no son solo las palabras visibles. Los tokenizadores
y formatos de conversación difieren, por lo que el número bruto no mide por sí solo la calidad.

Ambos siguen la misma secuencia de herramientas. En la primera pregunta necesitan buscar
el identificador del cliente antes de consultar sus pedidos. La función devuelve todos sus
pedidos y el modelo selecciona solo el pendiente, sin sumar el entregado. En la segunda
pregunta, Gemini añade el precio, que sí está respaldado por el resultado de SQLite.
En la tercera, una lista vacía significa que no se encontró el cliente, no que se hayan
consultado sus pedidos. En la cuarta, ninguno inventa una herramienta de borrado.
La sugerencia de Gemini de contactar con administración es una recomendación, no una acción realizada.

## 5. Incidencias técnicas y límites

- La prueba inicial de conexión recibió HTTP 402 porque el máximo por defecto reservaba
  hasta 65.536 tokens. Se añadió un límite de 1.024 tokens a las respuestas.
- Cuatro solicitudes del clasificador Gemini recibieron `in_flight_budget_exhausted` al
  coincidir con otras peticiones. Se repitieron solo las fallidas después de finalizar las otras.
  Estos errores no se cuentan como fallos de clasificación y quedan documentados en los JSON.
- El Python del entorno antiguo no pudo arrancar desde la herramienta de ejecución. Se utilizó
  Python 3.12.14 con las dependencias de `requirements.txt` y el `.env` existente, sin publicar claves.
- La evaluación es pequeña y sintética: no estima la calidad en producción. No se puntuaron
  exhaustivamente urgencia, productos, cantidades o resúmenes. No se fija una semilla y los resultados
  pueden variar en otra ejecución.
- Las pruebas del asistente no requieren crear incidencias. Se comprobó que el pedido 1003
  sigue existiendo y que la base de datos conserva sus filas originales.

## 6. Conclusión

Las salidas estructuradas permiten validar la forma de los datos, pero no garantizan que
el cliente exista ni que el modelo distinga una firma personal de un negocio. La comprobación
contra SQLite añade una validación independiente. Los dos asistentes consultaron correctamente
la base de datos en las cuatro preguntas y reconocieron el límite de sus herramientas.

Los JSON y CSV adjuntos permiten
revisar los resultados reales descritos en este análisis.
