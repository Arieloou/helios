# 1. Introducción

El sistema fundamenta su motor de cálculo en la metodología MAGERIT y su catálogo de controles en la familia de normas ISO/IEC 27000. MAGERIT actúa como el diagnóstico que calcula el Riesgo Inherente, mientras que los controles ISO 27002 funcionan como las salvaguardas cuya eficacia (Madurez) reduce ese riesgo hasta llegar al Riesgo Residual.

Este documento especifica los requisitos funcionales (RF), los requisitos no funcionales (RNF) y los casos de uso (CU) del sistema, derivados de los fundamentos metodológicos y funcionales de Helios y de su estructura técnica actual.

## 1.1. Alcance y módulos del sistema

Helios agrupa sus funcionalidades en ocho módulos clave:

1.   Gestión de Evaluaciones (Aislamiento Contextual).
2.   Módulo de Inventario (Gestión de Activos).
3.   Módulo de Mapeo y Riesgo Inherente (el Motor MAGERIT).
4.   Módulo de Auditoría y Madurez (Cuestionarios ISO reactivos).
5.   Motor de Recálculo y Riesgo Residual (Backend).
6.   Copilot de IA Local (Módulo Ollama).
7.   Planes de Tratamiento (Gestor de Tareas).
8.   Dashboards Ejecutivos (la Matriz 5x5 Visual).

## 1.2. Actores del sistema

El sistema reconoce dos actores principales:

•     Administrador: gestiona usuarios, configuración del sistema y el ciclo de vida de las evaluaciones; puede consultar los dashboards y los resultados del análisis.
•     Agente de Seguridad de la Información: ejecuta el análisis de riesgos de extremo a extremo — inventario y valoración de activos, mapeo de amenazas y vulnerabilidades, cuestionarios de madurez, planes de tratamiento y consulta de dashboards.

## 1.3. Fundamento matemático del riesgo

Las funcionalidades de cálculo de Helios se apoyan en las siguientes ecuaciones universales del riesgo:

•     Valor total del activo: V_total = máx(Confidencialidad, Integridad, Disponibilidad).
•     Impacto: I = V_total × Degradación (D), donde D se captura como un porcentaje (0 a 1).
•     Riesgo Inherente: RI = I × Probabilidad (P), donde P se captura en una escala de 1 a 5.
•     Riesgo Residual: RR = RI × (1 − Madurez (M)), donde M se calcula dinámicamente a partir de los cuestionarios ISO.

Los resultados de Riesgo Inherente y Riesgo Residual constituyen las coordenadas que ubican los puntos de peligro dentro de la Matriz de Riesgo 5x5 de los dashboards.

## 1.4. Convenciones del documento

•     RF-XX: identifica un Requisito Funcional.
•     RNF-XX: identifica un Requisito No Funcional.
•     CU-XX: identifica un Caso de Uso.

# 2. Requisitos Funcionales

Los requisitos funcionales describen el comportamiento esperado del sistema. Se presentan agrupados por módulo y siguen el formato Descripción, Entradas, Proceso, Salidas y Reglas/Condiciones.

|**RF-01**|**Autenticación de usuarios**|
|---|---|
|**Módulo**|Seguridad / Acceso (transversal)|
|**Descripción**|Permite a los usuarios (Administrador y Agente de Seguridad de la Información) iniciar y cerrar sesión en Helios mediante credenciales válidas, habilitando las funcionalidades según su rol.|
|**Entradas**|Nombre de usuario o correo electrónico y contraseña.|
|**Proceso**|El sistema valida las credenciales contra la tabla de usuarios, verifica el rol asociado (Administrador / Agente) y establece una sesión segura. En el cierre de sesión, invalida la sesión activa.|
|**Salidas**|Sesión autenticada con rol asignado, o mensaje de error por credenciales inválidas.|
|**Reglas / Condiciones**|Las contraseñas se almacenan cifradas; tras múltiples intentos fallidos se restringe temporalmente el acceso; únicamente usuarios registrados pueden autenticarse.|

|**RF-02**|**Control de acceso basado en roles (RBAC)**|
|---|---|
|**Módulo**|Seguridad / Acceso (transversal)|
|**Descripción**|Restringe el acceso a los módulos y operaciones del sistema según el rol del usuario autenticado.|
|**Entradas**|Rol del usuario autenticado y recurso o acción solicitada.|
|**Proceso**|El sistema comprueba los permisos del rol antes de ejecutar cada operación o renderizar cada vista, concediendo o denegando el acceso correspondiente.|
|**Salidas**|Acceso concedido al recurso solicitado o mensaje de acceso denegado.|
|**Reglas / Condiciones**|El Administrador gestiona usuarios y configuración; el Agente de Seguridad ejecuta el análisis de riesgos; ninguna acción puede ejecutarse sin un rol válido asignado.|

|**RF-03**|**Creación de evaluaciones**|
|---|---|
|**Módulo**|1. Gestión de Evaluaciones (Aislamiento Contextual)|
|**Descripción**|Permite crear sesiones o campañas de evaluación independientes que actúan como contenedor contextual de todo el análisis.|
|**Entradas**|Nombre de la evaluación, descripción y período (ej. “Auditoría Financiera Q1 2026”).|
|**Proceso**|El sistema registra la nueva evaluación, le asigna un identificador único y la habilita como clave contextual para activos, mapeos, cuestionarios y dashboards.|
|**Salidas**|Evaluación creada y disponible para su selección.|
|**Reglas / Condiciones**|El nombre de la evaluación debe ser único; toda la información posterior queda asociada a esta evaluación, que opera como Foreign Key principal del sistema.|

|**RF-04**|**Selección y aislamiento contextual de la evaluación**|
|---|---|
|**Módulo**|1. Gestión de Evaluaciones (Aislamiento Contextual)|
|**Descripción**|Permite seleccionar una evaluación activa, de modo que todo el sistema filtre automáticamente la información perteneciente a ella.|
|**Entradas**|Evaluación seleccionada por el usuario.|
|**Proceso**|El sistema fija la evaluación como contexto activo y filtra activos, inventarios, cuestionarios y dashboards por ese identificador.|
|**Salidas**|Vistas y datos filtrados exclusivamente por la evaluación activa.|
|**Reglas / Condiciones**|No se deben mezclar datos de distintas evaluaciones; siempre debe existir una evaluación activa para operar los módulos dependientes.|

|**RF-05**|**Administración de evaluaciones**|
|---|---|
|**Módulo**|1. Gestión de Evaluaciones (Aislamiento Contextual)|
|**Descripción**|Permite editar, archivar o cerrar evaluaciones existentes para gestionar el ciclo de vida de las campañas.|
|**Entradas**|Evaluación seleccionada y datos a modificar, o acción a ejecutar (archivar / cerrar).|
|**Proceso**|El sistema actualiza los metadatos de la evaluación o cambia su estado, conservando el histórico de la campaña.|
|**Salidas**|Evaluación actualizada o archivada.|
|**Reglas / Condiciones**|Las evaluaciones archivadas se conservan como histórico y no deben perderse; solo roles autorizados pueden cerrarlas.|

|**RF-06**|**Registro y valoración CID de activos**|
|---|---|
|**Módulo**|2. Módulo de Inventario (Gestión de Activos)|
|**Descripción**|Permite registrar activos de información valorando su Confidencialidad, Integridad y Disponibilidad (tríada CID).|
|**Entradas**|Datos del activo (nombre, tipo, descripción) y valores de Confidencialidad, Integridad y Disponibilidad.|
|**Proceso**|El sistema almacena el activo asociado a la evaluación activa y guarda su valoración en la tríada CID.|
|**Salidas**|Activo registrado en el inventario de la evaluación.|
|**Reglas / Condiciones**|Cada activo debe ser valorado obligatoriamente en [C, I, D]; el activo queda asociado a la evaluación activa.|

|**RF-07**|**Gestión (CRUD) y consulta de activos**|
|---|---|
|**Módulo**|2. Módulo de Inventario (Gestión de Activos)|
|**Descripción**|Permite crear, leer, actualizar y eliminar activos, así como visualizarlos en tablas interactivas.|
|**Entradas**|Operación solicitada (crear / leer / actualizar / eliminar) y datos del activo.|
|**Proceso**|El sistema ejecuta la operación CRUD sobre el inventario y refleja los cambios en tablas interactivas con filtrado, ordenamiento y búsqueda.|
|**Salidas**|Inventario actualizado y visualizado.|
|**Reglas / Condiciones**|La eliminación de un activo debe considerar sus mapeos asociados; las operaciones se limitan a la evaluación activa.|

|**RF-08**|**Importación masiva de activos**|
|---|---|
|**Módulo**|2. Módulo de Inventario (Gestión de Activos)|
|**Descripción**|Permite cargar grandes volúmenes de activos mediante archivos de importación.|
|**Entradas**|Archivo de activos (ej. CSV u hoja de cálculo) con sus respectivas valoraciones.|
|**Proceso**|El sistema valida el formato, procesa los registros e inserta masivamente los activos válidos en el inventario de la evaluación activa.|
|**Salidas**|Activos importados y reporte de resultados (éxitos y errores).|
|**Reglas / Condiciones**|Los registros inválidos deben reportarse sin interrumpir la carga de los válidos; debe respetarse la obligatoriedad de la valoración CID por registro.|

|**RF-09**|**Cálculo del valor total del activo**|
|---|---|
|**Módulo**|2. Módulo de Inventario (Gestión de Activos)|
|**Descripción**|Calcula el valor total de cada activo a partir de su valoración CID.|
|**Entradas**|Valores de Confidencialidad, Integridad y Disponibilidad del activo.|
|**Proceso**|El sistema aplica V_total = máx(C, I, D), asumiendo que el activo queda comprometido si cae su dimensión más crítica.|
|**Salidas**|Valor total (V_total) del activo.|
|**Reglas / Condiciones**|Se utiliza el valor máximo de la tríada CID; el resultado alimenta el cálculo del Impacto.|

|**RF-10**|**Mapeo de activos con amenazas y vulnerabilidades**|
|---|---|
|**Módulo**|3. Módulo de Mapeo y Riesgo Inherente (Motor MAGERIT)|
|**Descripción**|Permite asociar a un activo una o varias amenazas y las vulnerabilidades que estas explotan, desde catálogos estandarizados.|
|**Entradas**|Activo seleccionado, amenaza(s) y vulnerabilidad(es) del catálogo.|
|**Proceso**|El sistema crea las relaciones de muchos a muchos (Activo → Amenaza → Vulnerabilidad) y prepara el cruce para el cálculo de riesgo.|
|**Salidas**|Cadena de mapeo registrada.|
|**Reglas / Condiciones**|Un activo puede mapearse a múltiples amenazas y vulnerabilidades; el mapeo es requisito previo para cualquier cálculo de riesgo.|

|**RF-11**|**Captura de variables de probabilidad y degradación**|
|---|---|
|**Módulo**|3. Módulo de Mapeo y Riesgo Inherente (Motor MAGERIT)|
|**Descripción**|Obliga a capturar la Probabilidad (P) y la Degradación (D) para cada cruce activo-amenaza.|
|**Entradas**|Probabilidad (escala de 1 a 5) y Degradación (porcentaje de 0 a 1).|
|**Proceso**|El sistema asocia las variables P y D al mapeo específico y dispara el cálculo de riesgo correspondiente.|
|**Salidas**|Variables P y D almacenadas para el mapeo.|
|**Reglas / Condiciones**|Las variables P y D son obligatorias al crear el mapeo; P se captura en escala 1–5 y D como porcentaje (0–1).|

|**RF-12**|**Cálculo automático del Riesgo Inherente**|
|---|---|
|**Módulo**|3. Módulo de Mapeo y Riesgo Inherente (Motor MAGERIT)|
|**Descripción**|Calcula automáticamente el Impacto y el Riesgo Inherente al guardar un mapeo.|
|**Entradas**|Valor total del activo (V_total), Degradación (D) y Probabilidad (P).|
|**Proceso**|El sistema calcula en el backend el Impacto (I = V_total × D) y el Riesgo Inherente (RI = I × P).|
|**Salidas**|Valores de Impacto y Riesgo Inherente del mapeo.|
|**Reglas / Condiciones**|El cálculo se dispara automáticamente al guardar el mapeo; sin mapeo no existen variables que calcular.|

|**RF-13**|**Generación reactiva de cuestionarios ISO**|
|---|---|
|**Módulo**|4. Módulo de Auditoría y Madurez (Cuestionarios ISO)|
|**Descripción**|Genera dinámicamente los cuestionarios de auditoría, desplegando únicamente los controles ISO aplicables según el mapeo.|
|**Entradas**|Mapeo de vulnerabilidades a controles ISO existentes.|
|**Proceso**|El sistema analiza el mapeo, deduce los controles aplicables y despliega solo las preguntas relevantes para esos controles.|
|**Salidas**|Cuestionario ISO contextualizado a los controles necesarios.|
|**Reglas / Condiciones**|Solo se muestran preguntas de los controles mapeados; el cuestionario depende del mapeo previo.|

|**RF-14**|**Registro de respuestas y guardado parcial**|
|---|---|
|**Módulo**|4. Módulo de Auditoría y Madurez (Cuestionarios ISO)|
|**Descripción**|Permite responder los cuestionarios ISO y guardar el progreso de forma parcial.|
|**Entradas**|Respuestas del auditor a las preguntas de control.|
|**Proceso**|El sistema almacena las respuestas, incluidos los estados parciales, asociándolas al control y a la evaluación.|
|**Salidas**|Respuestas guardadas y estado actualizado del cuestionario.|
|**Reglas / Condiciones**|Debe permitirse guardar avances incompletos; las respuestas se vinculan a los controles mapeados.|

|**RF-15**|**Cálculo automático de la Madurez de controles**|
|---|---|
|**Módulo**|4. Módulo de Auditoría y Madurez (Cuestionarios ISO)|
|**Descripción**|Calcula el porcentaje de Madurez de los controles a partir de las respuestas del cuestionario.|
|**Entradas**|Respuestas registradas en el cuestionario ISO.|
|**Proceso**|El sistema traduce las opciones de respuesta en un puntaje de eficacia y obtiene la Madurez (M) en un rango de 0 % a 100 %.|
|**Salidas**|Porcentaje de Madurez por control.|
|**Reglas / Condiciones**|La Madurez se expresa entre 0 y 1 (0 %–100 %); se recalcula cada vez que se modifican las respuestas.|

|**RF-16**|**Recálculo reactivo del Riesgo Residual**|
|---|---|
|**Módulo**|5. Motor de Recálculo y Riesgo Residual (Backend)|
|**Descripción**|Recalcula automáticamente el Riesgo Residual de todas las cadenas afectadas cuando cambia la Madurez de un control.|
|**Entradas**|Riesgo Inherente y Madurez actualizada de los controles.|
|**Proceso**|De forma reactiva, el sistema aplica RR = RI × (1 − M) a todas las cadenas activo-amenaza dependientes del control modificado, sin necesidad de refrescar la página.|
|**Salidas**|Riesgo Residual actualizado en tiempo casi real.|
|**Reglas / Condiciones**|El recálculo debe propagarse a todas las cadenas dependientes y reflejarse sin recarga manual de la página.|

|**RF-17**|**Análisis de coherencia y recomendaciones con IA local**|
|---|---|
|**Módulo**|6. Copilot de IA Local (Módulo Ollama)|
|**Descripción**|Permite analizar un activo con un copiloto de IA local (Ollama) para detectar incoherencias y sugerir controles omitidos.|
|**Entradas**|Información del activo (valor, mapeos, impactos y respuestas de controles) compilada en formato JSON.|
|**Proceso**|El sistema envía el JSON al modelo local Ollama, que evalúa la coherencia (ej. un activo vital con medidas básicas) y genera sugerencias.|
|**Salidas**|Observaciones de coherencia y recomendaciones de controles.|
|**Reglas / Condiciones**|El procesamiento debe ser local y offline para preservar la privacidad; el análisis se ejecuta a solicitud explícita del usuario.|

|**RF-18**|**Identificación de riesgos inaceptables**|
|---|---|
|**Módulo**|7. Planes de Tratamiento (Gestor de Tareas)|
|**Descripción**|Identifica los Riesgos Residuales que permanecen en “Zona Roja” o nivel inaceptable tras el cálculo.|
|**Entradas**|Riesgos Residuales calculados y umbrales de aceptación definidos.|
|**Proceso**|El sistema clasifica los riesgos según su nivel y marca aquellos que superan el umbral aceptable.|
|**Salidas**|Listado de riesgos inaceptables que requieren tratamiento.|
|**Reglas / Condiciones**|Los riesgos en zona roja obligan a generar un tratamiento; los umbrales dependen de la política de la organización.|

|**RF-19**|**Generación de tratamientos de riesgo**|
|---|---|
|**Módulo**|7. Planes de Tratamiento (Gestor de Tareas)|
|**Descripción**|Permite crear tickets de tratamiento para los riesgos inaceptables, decidiendo la estrategia a seguir (Mitigar, Aceptar o Transferir).|
|**Entradas**|Riesgo seleccionado y estrategia de tratamiento.|
|**Proceso**|El sistema registra el tratamiento con la estrategia elegida y lo asocia al riesgo correspondiente.|
|**Salidas**|Ticket de tratamiento creado.|
|**Reglas / Condiciones**|Cada riesgo inaceptable debe tener una estrategia definida; las opciones válidas son Mitigar, Aceptar o Transferir.|

|**RF-20**|**Asignación de responsables y seguimiento de plazos**|
|---|---|
|**Módulo**|7. Planes de Tratamiento (Gestor de Tareas)|
|**Descripción**|Permite asignar responsables y plazos de ejecución a cada tratamiento, habilitando su seguimiento.|
|**Entradas**|Responsable, fecha o plazo de ejecución y estado del tratamiento.|
|**Proceso**|El sistema registra y actualiza la asignación y el estado de avance de cada ticket de tratamiento.|
|**Salidas**|Tratamiento con responsable, plazo y estado de seguimiento.|
|**Reglas / Condiciones**|Todo tratamiento de mitigación debe tener responsable y plazo; el estado de avance debe poder actualizarse.|

|**RF-21**|**Visualización de la Matriz de Riesgo 5x5**|
|---|---|
|**Módulo**|8. Dashboards Ejecutivos (Matriz 5x5 Visual)|
|**Descripción**|Grafica de forma interactiva la Matriz de Calor 5x5 (Probabilidad vs. Impacto) con los riesgos de la evaluación.|
|**Entradas**|Coordenadas de riesgo (Impacto y Probabilidad; Riesgo Inherente y Riesgo Residual).|
|**Proceso**|El sistema ubica cada riesgo en la celda correspondiente de la matriz según sus coordenadas y nivel.|
|**Salidas**|Matriz de Calor 5x5 con los puntos de peligro representados.|
|**Reglas / Condiciones**|La matriz se filtra por la evaluación activa; el color de cada celda refleja el nivel de riesgo.|

|**RF-22**|**Visualización del “Viaje del Riesgo”**|
|---|---|
|**Módulo**|8. Dashboards Ejecutivos (Matriz 5x5 Visual)|
|**Descripción**|Muestra gráficamente cómo un riesgo se desplaza de su posición inherente (celda roja) a su posición residual (celda amarilla o verde) gracias a la madurez de los controles.|
|**Entradas**|Riesgo Inherente y Riesgo Residual de cada cadena de riesgo.|
|**Proceso**|El sistema representa el movimiento del riesgo entre celdas de la matriz, comparando el RI con el RR.|
|**Salidas**|Visualización del desplazamiento del riesgo (RI → RR).|
|**Reglas / Condiciones**|Requiere que existan calculados tanto el Riesgo Inherente como el Residual; ilustra el efecto de los controles aplicados.|

|**RF-23**|**Exportación e integración con herramientas externas**|
|---|---|
|**Módulo**|8. Dashboards Ejecutivos (Matriz 5x5 Visual)|
|**Descripción**|Permite integrar o exportar la información de los dashboards hacia herramientas externas como Power BI.|
|**Entradas**|Datos y métricas de la evaluación a exportar.|
|**Proceso**|El sistema expone o exporta la información en un formato compatible para su consumo por herramientas externas.|
|**Salidas**|Datos exportados o disponibles para integración externa.|
|**Reglas / Condiciones**|La exportación respeta el filtrado por evaluación; debe preservarse la seguridad de los datos sensibles.|

# 3. Requisitos No Funcionales

Los requisitos no funcionales describen las cualidades y restricciones del sistema (seguridad, privacidad, rendimiento, mantenibilidad, entre otras), derivadas de su arquitectura técnica y de las normativas de referencia.

|**RNF-01**|**Seguridad – Cifrado de datos sensibles**|
|---|---|
|**Módulo**|Seguridad|
|**Descripción**|El sistema debe proteger la información sensible mediante cifrado, apoyándose en un microservicio dedicado de cifrado.|
|**Entradas**|Datos sensibles a almacenar o transmitir (credenciales, información de activos).|
|**Proceso**|El microservicio de cifrado (FastAPI + Cryptography) cifra y descifra la información mediante el cliente de cifrado del núcleo de la aplicación.|
|**Salidas**|Datos cifrados en reposo y en tránsito.|
|**Reglas / Condiciones**|Las credenciales y datos críticos nunca se almacenan en texto plano; la comunicación entre servicios debe ser segura.|

|**RNF-02**|**Privacidad – Procesamiento de IA local y offline**|
|---|---|
|**Módulo**|Privacidad|
|**Descripción**|El análisis con inteligencia artificial debe ejecutarse de manera local y offline, sin enviar datos a servicios externos.|
|**Entradas**|Información del activo compilada para su análisis.|
|**Proceso**|El modelo Ollama procesa la información dentro de la infraestructura local del cliente.|
|**Salidas**|Resultados de IA generados localmente.|
|**Reglas / Condiciones**|Ningún dato sensible debe salir del entorno local; se preserva la confidencialidad de la organización auditada.|

|**RNF-03**|**Rendimiento – Recálculo reactivo en tiempo casi real**|
|---|---|
|**Módulo**|Rendimiento|
|**Descripción**|El recálculo de riesgos y la actualización de las vistas deben producirse de forma reactiva, sin recargas manuales perceptibles.|
|**Entradas**|Cambios en variables de riesgo o en respuestas de control.|
|**Proceso**|El motor de backend propaga los cálculos y actualiza la interfaz de forma eficiente.|
|**Salidas**|Resultados y dashboards actualizados en tiempo casi real.|
|**Reglas / Condiciones**|La latencia del recálculo debe ser mínima; la actualización no debe requerir refrescar la página manualmente.|

|**RNF-04**|**Usabilidad – Interfaces interactivas**|
|---|---|
|**Módulo**|Usabilidad|
|**Descripción**|El sistema debe ofrecer una experiencia clara mediante tablas interactivas y dashboards visuales comprensibles.|
|**Entradas**|Interacción del usuario (filtros, ordenamientos, selección de elementos).|
|**Proceso**|La interfaz responde a las acciones del usuario con visualizaciones interactivas (tablas, matriz de calor).|
|**Salidas**|Vistas navegables e intuitivas.|
|**Reglas / Condiciones**|Las visualizaciones deben facilitar la toma de decisiones tanto técnicas como gerenciales.|

|**RNF-05**|**Mantenibilidad – Arquitectura modular**|
|---|---|
|**Módulo**|Mantenibilidad|
|**Descripción**|El sistema debe mantener una arquitectura modular que separe responsabilidades (núcleo, cifrado, IA y capa de datos).|
|**Entradas**|No aplica (atributo arquitectónico del sistema).|
|**Proceso**|La organización en controladores, servicios, modelos y microservicios independientes facilita el mantenimiento y la evolución.|
|**Salidas**|Base de código mantenible y extensible.|
|**Reglas / Condiciones**|La separación de capas (MVC + servicios) y de microservicios debe conservarse en futuras evoluciones del producto.|

|**RNF-06**|**Escalabilidad**|
|---|---|
|**Módulo**|Escalabilidad|
|**Descripción**|El sistema debe soportar el crecimiento del volumen de activos, mapeos y evaluaciones sin degradación significativa del desempeño.|
|**Entradas**|Volumen creciente de datos e importaciones masivas.|
|**Proceso**|La base de datos relacional y los servicios deben manejar cargas crecientes de forma eficiente.|
|**Salidas**|Operación estable ante mayores volúmenes de información.|
|**Reglas / Condiciones**|Debe soportar importaciones masivas; el rendimiento no debe degradarse de forma abrupta al crecer los datos.|

|**RNF-07**|**Integridad y consistencia de datos**|
|---|---|
|**Módulo**|Integridad|
|**Descripción**|El sistema debe garantizar la consistencia de los cálculos y de las relaciones entre activos, amenazas, controles y riesgos.|
|**Entradas**|Operaciones que modifican datos y cálculos en cadena.|
|**Proceso**|La gestión transaccional (PostgreSQL / SQLAlchemy) y el recálculo en cadena mantienen la coherencia de los datos.|
|**Salidas**|Datos y cálculos consistentes en todo el sistema.|
|**Reglas / Condiciones**|Un cambio en una variable debe reflejarse coherentemente en todas las cadenas dependientes; no deben quedar cálculos desincronizados.|

|**RNF-08**|**Interoperabilidad**|
|---|---|
|**Módulo**|Interoperabilidad|
|**Descripción**|El sistema debe comunicarse eficientemente entre sus componentes internos y con herramientas externas.|
|**Entradas**|Solicitudes entre servicios y de herramientas externas.|
|**Proceso**|Se emplean interfaces estandarizadas: gRPC / Protobuf entre servicios, HTTP / REST e integración con Power BI.|
|**Salidas**|Comunicación e integración fiables entre componentes.|
|**Reglas / Condiciones**|Los contratos de comunicación (Protobuf / API) deben mantenerse versionados y compatibles.|

|**RNF-09**|**Trazabilidad y auditabilidad**|
|---|---|
|**Módulo**|Trazabilidad|
|**Descripción**|El sistema debe permitir el aislamiento histórico y la trazabilidad de los análisis por evaluación.|
|**Entradas**|Operaciones realizadas dentro de cada evaluación.|
|**Proceso**|Cada dato se asocia a su evaluación mediante la clave contextual, conservando el histórico de las campañas.|
|**Salidas**|Histórico auditable y separado por evaluación.|
|**Reglas / Condiciones**|No se deben mezclar datos entre evaluaciones; el histórico de campañas debe preservarse.|

|**RNF-10**|**Cumplimiento normativo**|
|---|---|
|**Módulo**|Cumplimiento|
|**Descripción**|El sistema debe alinear sus cálculos y controles con los estándares MAGERIT e ISO 27000 (ISO 27002:2022 e ISO 27005).|
|**Entradas**|Metodología MAGERIT y catálogo de controles ISO.|
|**Proceso**|Los motores de cálculo y los cuestionarios se basan en las fórmulas y dominios de control de dichos estándares.|
|**Salidas**|Resultados conformes a las normativas de referencia.|
|**Reglas / Condiciones**|Las fórmulas de riesgo y el catálogo de controles deben mantenerse fieles a MAGERIT e ISO 27002 / 27005.|

|**RNF-11**|**Portabilidad y compatibilidad**|
|---|---|
|**Módulo**|Portabilidad|
|**Descripción**|La aplicación web debe ser accesible desde navegadores modernos sin necesidad de instalación adicional en el cliente.|
|**Entradas**|Acceso del usuario a través de un navegador web.|
|**Proceso**|La interfaz web (Flask + frontend) se sirve de forma compatible con los navegadores estándar.|
|**Salidas**|Acceso multiplataforma vía navegador.|
|**Reglas / Condiciones**|Debe funcionar en los navegadores modernos más comunes y no requerir software adicional para su uso básico.|

|**RNF-12**|**Confiabilidad y configurabilidad por entorno**|
|---|---|
|**Módulo**|Confiabilidad|
|**Descripción**|El sistema debe operar de forma confiable y permitir configuraciones diferenciadas por entorno (desarrollo y producción).|
|**Entradas**|Variables de configuración y entorno (config.py, archivo .env).|
|**Proceso**|El sistema carga su configuración mediante Pydantic Settings y variables de entorno, separando desarrollo de producción.|
|**Salidas**|Operación estable y configurable según el entorno.|
|**Reglas / Condiciones**|Las credenciales y parámetros sensibles se gestionan mediante variables de entorno; los entornos deben mantenerse separados.|

# 4. Casos de Uso

Los casos de uso describen las interacciones entre los actores y el sistema para alcanzar un objetivo concreto. Cada caso detalla su secuencia normal, sus excepciones y sus atributos de frecuencia, importancia y urgencia.

|**CU-01**|**Iniciar sesión**|   |   |
|---|---|---|---|
|**Descripción**|El usuario inicia sesión en Helios para acceder a las funcionalidades del sistema según su rol.|   |   |
|**Actores**|Administrador, Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|El usuario está registrado en el sistema y dispone de credenciales válidas.|   |   |
|**Postcondiciones**|Se establece una sesión segura y se habilitan las funciones correspondientes al rol del usuario.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Ingresa al formulario de inicio de sesión.|Presenta el formulario de autenticación.|
|2|Introduce usuario y contraseña y los envía.|Valida las credenciales y el rol, y crea la sesión.|
|2.1|Si las credenciales son inválidas, el sistema muestra un mensaje de error y solicita reintentar.|   |
|3|Accede al sistema.|Redirige al dashboard correspondiente a su rol.|
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|En caso de múltiples intentos fallidos consecutivos, el sistema restringe temporalmente el acceso del usuario.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de varias veces al día.|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Inmediatamente|   |   |
|**Comentarios**|Aplica el control de acceso basado en roles (RBAC). Las contraseñas se gestionan cifradas.|   |   |

|**CU-02**|**Crear evaluación**|   |   |
|---|---|---|---|
|**Descripción**|El usuario crea una nueva campaña de evaluación que aislará contextualmente todo el análisis posterior.|   |   |
|**Actores**|Administrador, Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|El usuario está autenticado y cuenta con permisos para crear evaluaciones.|   |   |
|**Postcondiciones**|La evaluación queda creada y disponible como contexto activo del sistema.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Selecciona la opción “Nueva evaluación”.|Muestra el formulario de creación.|
|2|Ingresa el nombre y el período de la evaluación.|Valida que el nombre de la evaluación sea único.|
|2.1|Si el nombre ya existe, el sistema notifica el conflicto y solicita uno distinto.|   |
|3|Confirma la creación.|Registra la evaluación con un identificador único y la deja disponible.|
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|En caso de un error de persistencia, el sistema informa del fallo y no crea la evaluación.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de pocas veces al mes (una por campaña).|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|La evaluación es la clave contextual (Foreign Key) sobre la que se filtra todo el sistema.|   |   |

|**CU-03**|**Registrar activo con valoración CID**|   |   |
|---|---|---|---|
|**Descripción**|El Agente de Seguridad registra un activo de información valorando su Confidencialidad, Integridad y Disponibilidad.|   |   |
|**Actores**|Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existe una evaluación activa seleccionada y el usuario está autenticado.|   |   |
|**Postcondiciones**|El activo queda registrado en el inventario de la evaluación, con su valor total calculado.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Selecciona la opción “Nuevo activo”.|Muestra el formulario de activo.|
|2|Ingresa los datos del activo y sus valores de C, I y D.|Valida que la valoración CID esté completa.|
|2.1|Si falta alguna dimensión de la tríada CID, el sistema impide guardar y señala el campo faltante.|   |
|3|Guarda el activo.|Calcula V_total = máx(C, I, D) y registra el activo en la evaluación.|
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si no existe una evaluación activa, el sistema solicita seleccionar o crear una antes de continuar.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de muchas veces durante la fase de inventario.|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|La valoración en la tríada CID es obligatoria para todo activo.|   |   |

|**CU-04**|**Importar activos masivamente**|   |   |
|---|---|---|---|
|**Descripción**|El Agente de Seguridad carga múltiples activos en el inventario mediante un archivo de importación.|   |   |
|**Actores**|Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existe una evaluación activa y se dispone de un archivo con el formato esperado.|   |   |
|**Postcondiciones**|Los activos válidos quedan registrados y se entrega un reporte del resultado de la carga.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Selecciona “Importar activos” y carga el archivo.|Valida el formato del archivo.|
|2|Confirma la importación.|Procesa los registros e inserta los activos válidos.|
|2.1|Si existen registros inválidos, el sistema los omite y los incluye en el reporte de errores.|   |
|3|Revisa el resultado de la carga.|Muestra un reporte con los éxitos y los errores.|
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si el archivo presenta un formato no soportado, el sistema rechaza la carga e informa al usuario.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de ocasionalmente, al iniciar campañas.|   |   |
|**Importancia**|Importante|   |   |
|**Urgencia**|Puede esperar|   |   |
|**Comentarios**|Se mantiene la obligatoriedad de la valoración CID por cada registro importado.|   |   |

|**CU-05**|**Mapear activo con amenazas y vulnerabilidades**|   |   |
|---|---|---|---|
|**Descripción**|El Agente de Seguridad asocia un activo con amenazas y vulnerabilidades, capturando P y D para disparar el cálculo del Riesgo Inherente.|   |   |
|**Actores**|Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existe al menos un activo valorado dentro de la evaluación activa.|   |   |
|**Postcondiciones**|Queda registrada la cadena de mapeo y calculado el Riesgo Inherente de la asociación.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Selecciona un activo del inventario.|Presenta los catálogos de amenazas y vulnerabilidades.|
|2|Asocia una o varias amenazas y vulnerabilidades.|Solicita las variables P y D del cruce.|
|3|Ingresa la Probabilidad (1–5) y la Degradación (0–1).|Calcula I = V_total × D y RI = I × P.|
|3.1|Si faltan las variables P o D, el sistema impide guardar el mapeo.|   |
|4|Guarda el mapeo.|Almacena la cadena y el Riesgo Inherente calculado.|
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si el activo no tiene valoración CID, el sistema impide el mapeo y solicita completarla.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de muchas veces durante el análisis.|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|El mapeo es el detonante de todos los cálculos de riesgo del sistema.|   |   |

|**CU-06**|**Responder cuestionario ISO de madurez**|   |   |
|---|---|---|---|
|**Descripción**|El Agente de Seguridad responde el cuestionario ISO de los controles aplicables, lo que actualiza la Madurez y dispara el recálculo del Riesgo Residual.|   |   |
|**Actores**|Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existen mapeos que vinculan vulnerabilidades con controles ISO.|   |   |
|**Postcondiciones**|La Madurez queda registrada y el Riesgo Residual recalculado en las cadenas dependientes.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Abre el cuestionario de auditoría.|Despliega únicamente las preguntas de los controles mapeados.|
|2|Responde las preguntas del cuestionario.|Permite guardar estados parciales y calcula la Madurez.|
|3|Guarda las respuestas.|Recalcula de forma reactiva RR = RI × (1 − M) en las cadenas dependientes.|
|3.1|Si el actor modifica una respuesta posteriormente, el sistema recalcula nuevamente los riesgos afectados.|   |
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si no existen controles mapeados, el sistema indica que no hay preguntas aplicables.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de muchas veces durante la auditoría.|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|El recálculo del riesgo no requiere refrescar la página manualmente.|   |   |

|**CU-07**|**Analizar activo con Copilot de IA**|   |   |
|---|---|---|---|
|**Descripción**|El usuario solicita al copiloto de IA local analizar la coherencia de un activo y recibir sugerencias de controles.|   |   |
|**Actores**|Agente de Seguridad de la Información, Administrador.|   |   |
|**Precondiciones**|El activo cuenta con información de valor, mapeos y respuestas de control; el servicio Ollama está disponible localmente.|   |   |
|**Postcondiciones**|El usuario recibe observaciones de coherencia y recomendaciones de controles.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Pulsa “Analizar con IA” sobre un activo.|Compila la información del activo en un archivo JSON.|
|2|Espera el resultado del análisis.|Envía el JSON al modelo local Ollama y procesa la respuesta.|
|3|Revisa los resultados entregados.|Muestra las observaciones de coherencia y los controles sugeridos.|
|3.1|Si detecta incoherencias (ej. un activo vital con medidas básicas), el sistema lo advierte.|   |
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si el servicio de IA local no está disponible, el sistema informa y permite reintentar.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de ocasionalmente, bajo demanda.|   |   |
|**Importancia**|Importante|   |   |
|**Urgencia**|Puede esperar|   |   |
|**Comentarios**|El procesamiento es local y offline para preservar la privacidad de la información.|   |   |

|**CU-08**|**Generar plan de tratamiento**|   |   |
|---|---|---|---|
|**Descripción**|El Agente de Seguridad crea un tratamiento para un riesgo inaceptable, definiendo la estrategia, el responsable y el plazo.|   |   |
|**Actores**|Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existen riesgos residuales clasificados como inaceptables (Zona Roja).|   |   |
|**Postcondiciones**|Queda creado un ticket de tratamiento con su estrategia, responsable y plazo.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Selecciona un riesgo inaceptable.|Muestra el formulario de tratamiento.|
|2|Elige la estrategia (Mitigar / Aceptar / Transferir).|Registra la estrategia seleccionada.|
|3|Asigna responsable y plazo de ejecución.|Crea el ticket y habilita su seguimiento.|
|3.1|Si la estrategia es “Mitigar” y no se asigna responsable o plazo, el sistema impide guardar.|   |
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si el riesgo deja de ser inaceptable tras un recálculo, el sistema lo señala antes de continuar.|   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de muchas veces tras la fase de cálculo.|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|Los riesgos en Zona Roja obligan a generar un tratamiento.|   |   |

|**CU-09**|**Consultar dashboard y Matriz de Riesgo 5x5**|   |   |
|---|---|---|---|
|**Descripción**|El usuario consulta el dashboard ejecutivo para visualizar la Matriz 5x5 y el “Viaje del Riesgo” de la evaluación activa.|   |   |
|**Actores**|Administrador, Agente de Seguridad de la Información.|   |   |
|**Precondiciones**|Existen riesgos calculados (RI o RR) en la evaluación activa.|   |   |
|**Postcondiciones**|El usuario visualiza la posición y el movimiento de los riesgos.|   |   |
|**Secuencia Normal**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Abre el dashboard ejecutivo.|Filtra los datos por la evaluación activa.|   |
|2|Visualiza la matriz de riesgo.|Grafica la Matriz de Calor 5x5 con los riesgos posicionados.|   |
|3|Activa la vista de “Viaje del Riesgo”.|Muestra el desplazamiento de cada riesgo de RI a RR.|   |
|3.1|Si el actor solicita exportar, el sistema prepara los datos para herramientas externas (ej. Power BI).|   |   |
|**Excepciones**|**#**|**Acción (Actor)**|**Reacción (Sistema)**|
|1|Si no hay riesgos calculados en la evaluación, el sistema muestra un mensaje de matriz vacía.|   |   |
|**Frecuencia**|Este caso de uso se espera que se lleve a cabo una media de frecuentemente (consultas gerenciales).|   |   |
|**Importancia**|Vital|   |   |
|**Urgencia**|Hay presión|   |   |
|**Comentarios**|Integrable con Power BI; el “Viaje del Riesgo” evidencia el efecto de los controles aplicados.|   |   |