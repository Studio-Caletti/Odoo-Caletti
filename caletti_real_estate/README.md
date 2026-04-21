# 🏠 Caletti Real Estate v1.0.0 — Release Notes

**Fecha de Release:** Abril 2026
**Módulo:** `caletti_real_estate`
**Versión Odoo:** 17.0 Community
**Dependencias:** `tablero_kanban_caletti` (Core), `account`

---

## 🇪🇸 Español

### Caletti Real Estate v1.0.0 — Primer Release Estable

Este release marca el lanzamiento oficial del vertical inmobiliario del ecosistema Odoo-Caletti. Diseñado específicamente para asesores inmobiliarios independientes que gestionan propiedades de terceros, el módulo cubre el ciclo completo del negocio: desde la captación del prospecto hasta el cobro de la comisión, pasando por la gestión de contratos, pagos y mantenimiento.

---

#### ✨ Funcionalidades Incluidas

**🏠 Cartera de Propiedades (`re.propiedad`)**
- Soporte para tres tipos desde v1.0: Residencial, Comercial y Terrenos con subtipos específicos por categoría (casa, departamento, townhouse, penthouse, local, oficina, bodega, nave industrial, terreno urbano, agrícola, etc.)
- Galería de fotos integrada con submodelo `re.propiedad.foto` — hasta 10 imágenes por propiedad, ordenables por secuencia, con foto de portada designada
- Ciclo de estados: Disponible → En Negociación → Ocupada → Vendida → Vacante → En Mantenimiento → Suspendida, con notificaciones automáticas en Chatter por cada transición
- Campos económicos: precio de renta, precio de venta, depósito, porcentaje de comisión con cálculo estimado informativo
- Dirección compuesta calculada automáticamente para reportes y portal
- Regla de negocio: el asesor gestiona exclusivamente propiedades de terceros — `propietario_id` es campo obligatorio

**👤 Pipeline de Prospectos (`re.prospecto`)**
- 8 etapas de pipeline con Kanban drag-and-drop: Nuevo Lead → Contactado → Visita Agendada → Visita Realizada → En Investigación → En Negociación → Cerrado / Descartado
- Calificación de temperatura: Caliente (listo para cerrar), Tibio (evaluando) y Frío (explorando)
- 9 fuentes de captación para análisis de ROI: referido, portal web, redes sociales, Lamudi, Inmuebles24, Vivanuncios, WhatsApp, llamada directa, cartel en propiedad
- Relación Many2many con propiedades: un prospecto puede evaluar múltiples propiedades simultáneamente
- Investigación socioeconómica integrada con resultado (Aprobado / Aprobado con Observaciones / Rechazado / Pendiente)
- Visitas registradas como `mail.activity` con tipo personalizado "Visita a Propiedad" — `re.visita` reservado para v2.0
- Chatter automático en cada cambio de etapa con contexto del proceso

**📋 Operaciones Inmobiliarias (`re.operacion` — extiende `tablero.tarea`)**
- Pipeline visual de 7 etapas: Captación → Difusión → Con Prospecto → Negociación → Documentación → Cierre → Cerrada
- Regla fundamental: una propiedad solo puede tener una operación activa simultáneamente — validado por `@api.constrains`
- Sincronización automática del estado de la propiedad al avanzar etapas
- Aislamiento completo de vistas mediante `view_ids` explícitos en la acción — sin contaminación cruzada con el vertical Creative
- Campo discriminador `es_operacion_re` para separación limpia del Core

**📄 Contratos Unificados (`re.contrato` + `re.pago`)**
- Un solo modelo maneja renta Y venta, diferenciados por `tipo_operacion`
- **Renta:** fecha de fin calculada automáticamente (fecha inicio + plazo en meses), depósito en garantía con control de devolución, incremento anual configurable, día de pago por mes
- **Venta:** precio final, enganche, saldo a escrituración calculado, tipo de financiamiento (contado, hipotecario, INFONAVIT, FOVISSSTE)
- Generación automática de todos los pagos mensuales al activar un contrato de renta (`_generar_pagos_renta`)
- Métricas de calidad del inquilino: porcentaje de puntualidad, conteo de pagos atrasados, flag `inquilino_riesgo` con alerta en Chatter
- Acción de renovación con incremento automático de renta según porcentaje pactado
- Comisión capturada manualmente con flag de cobrado y fecha
- Cron diario de alertas de vencimiento: actualiza a `por_vencer` 60 días antes y a `vencido` al superar la fecha fin

**🔧 Mantenimiento (`re.mantenimiento`)**
- 16 categorías: fontanería, electricidad, pintura, carpintería, herrería, impermeabilización, climatización, fumigación, limpieza profunda, albañilería, vidriería, jardinería, cerrajería, electrodoméstico, remodelación, otro
- 4 niveles de prioridad: Urgente (riesgo para propiedad/inquilino), Alta, Normal, Baja
- Flujo de 7 estados: Solicitado → Evaluando → Aprobado → En Proceso → Resuelto → Cerrado / Cancelado
- Aprobación automáticamente requerida cuando `costo_estimado > $2,000 MXN` — bloquea avance sin autorización del propietario
- Dos tipos de ejecutor: asesor directo o proveedor externo con nombre y teléfono
- 4 orígenes de solicitud: asesor, propietario, inquilino (portal v1.1), inspección
- Referencia de ticket secuencial `MANT-YYYY-NNNNN` generada automáticamente al crear
- Control de costos: estimado vs real con diferencia calculada y flag de quién paga (propietario / inquilino / asesor)

**🛡️ Seguridad (Opción B — Aislamiento Total)**
- Tres grupos propios: `group_re_asesor`, `group_re_coordinador`, `group_re_admin`
- Record Rules: el asesor ve exclusivamente sus propias propiedades, prospectos, contratos, pagos y mantenimientos
- El coordinador tiene visibilidad total del vertical
- Portal: el propietario ve solo sus propiedades (read-only) — base para portal v1.1

---

#### 🏗️ Decisiones de Arquitectura

- **`re.visita` reservado para v2.0:** Las visitas se registran como `mail.activity` en v1.0. El modelo propio `re.visita` se implementará en v2.0 para administradoras con cartera activa mayor a 50 propiedades que requieran métricas de conversión por visita.
- **`account.move` evaluado para v1.1:** La integración con facturación se revisará en el siguiente ciclo arquitectónico para no introducir dependencias prematuras.
- **Contrato unificado:** La decisión de usar un solo modelo para renta y venta simplifica la gestión del asesor independiente que opera ambos tipos en su cartera diaria.

---

#### 🐛 Bugs Corregidos Durante QA

- Herencia colateral de vistas Creative sobre el modelo `tablero.tarea` — resuelto con `view_ids` explícitos y `priority=25` en vistas RE
- Campos del Core (`Es Ticket de Soporte`, `Estado Kanban`) visibles en form de Operación — resuelto con `xpath` + `invisible="es_operacion_re"`
- Error OWL en Kanban de Mantenimiento por uso de `not` en expresiones QWeb y ternarios Python en `t-attf-class` — resuelto con `!` y sintaxis ternaria JS
- `NaN` en campos Float del Kanban de Propiedades — resuelto con `t-if="raw_value > 0"`

---

#### 📌 Pendientes para v1.1

- Portal del propietario e inquilino (`re_portal.py`)
- Integración `account.move` para facturas automáticas de renta
- Cron automático de marcado de pagos atrasados
- `re.visita` como modelo propio para administradoras de cartera grande
- Demo data para App Store

---

---

## 🇺🇸 English

### Caletti Real Estate v1.0.0 — First Stable Release

This release marks the official launch of the real estate vertical within the Odoo-Caletti ecosystem. Designed specifically for independent real estate agents managing third-party properties, the module covers the complete business cycle: from prospect acquisition to commission collection, including contract management, payment tracking, and maintenance requests.

---

#### ✨ Features Included

**🏠 Property Portfolio (`re.propiedad`)**
- Three property types supported from v1.0: Residential, Commercial, and Land with specific subtypes per category (house, apartment, townhouse, penthouse, retail unit, office, warehouse, industrial building, urban land, agricultural, etc.)
- Integrated photo gallery with `re.propiedad.foto` submodel — up to 10 images per property, sortable by sequence, with a designated cover photo
- State lifecycle: Available → In Negotiation → Occupied → Sold → Vacant → Under Maintenance → Suspended, with automatic Chatter notifications on each transition
- Economic fields: rental price, sale price, deposit, commission percentage with informative estimated calculation
- Auto-computed full address for reports and portal
- Business rule: the agent exclusively manages third-party properties — `propietario_id` is a required field

**👤 Prospect Pipeline (`re.prospecto`)**
- 8-stage pipeline with Kanban drag-and-drop: New Lead → Contacted → Visit Scheduled → Visit Done → Under Investigation → In Negotiation → Closed / Discarded
- Lead temperature scoring: Hot (ready to close), Warm (evaluating), Cold (exploring)
- 9 acquisition sources for ROI analysis: referral, web portal, social media, Lamudi, Inmuebles24, Vivanuncios, WhatsApp, direct call, property sign
- Many2many relationship with properties: a prospect can evaluate multiple properties simultaneously
- Integrated socioeconomic investigation with result (Approved / Approved with Observations / Rejected / Pending)
- Visits registered as `mail.activity` with custom "Property Visit" type — `re.visita` reserved for v2.0
- Automatic Chatter notes on every stage change with process context

**📋 Real Estate Operations (`re.operacion` — extends `tablero.tarea`)**
- 7-stage visual pipeline: Acquisition → Listing → With Prospect → Negotiation → Documentation → Close → Closed/Archived
- Core rule: one property can only have one active operation at a time — enforced by `@api.constrains`
- Automatic property state synchronization on stage advancement
- Full view isolation via explicit `view_ids` in the action — no cross-contamination with the Creative vertical
- `es_operacion_re` discriminator field for clean Core separation

**📄 Unified Contracts (`re.contrato` + `re.pago`)**
- A single model handles both rental AND sale contracts, differentiated by `tipo_operacion`
- **Rental:** end date auto-calculated (start date + term in months), security deposit with return tracking, configurable annual increase, payment day per month
- **Sale:** final price, down payment, balance to deed automatically calculated, financing type (cash, mortgage, INFONAVIT, FOVISSSTE)
- Automatic generation of all monthly payments upon rental contract activation (`_generar_pagos_renta`)
- Tenant quality metrics: punctuality percentage, overdue payment count, `inquilino_riesgo` flag with Chatter alert
- Renewal action with automatic rent increase based on agreed percentage
- Manually captured commission with paid flag and date
- Daily expiration alerts cron: updates to `por_vencer` 60 days ahead and `vencido` when end date is exceeded

**🔧 Maintenance (`re.mantenimiento`)**
- 16 categories: plumbing, electrical, painting, carpentry, ironwork, waterproofing, HVAC, fumigation, deep cleaning, masonry, glazing, landscaping, locksmithing, appliances, remodeling, other
- 4 priority levels: Urgent (risk to property/tenant), High, Normal, Low
- 7-state flow: Requested → Evaluating → Approved → In Progress → Resolved → Closed / Cancelled
- Owner approval automatically required when `costo_estimado > $2,000 MXN` — blocks advancement without authorization
- Two executor types: direct agent or external provider with name and phone
- 4 request origins: agent, owner, tenant (portal v1.1), inspection
- Sequential ticket reference `MANT-YYYY-NNNNN` auto-generated on creation
- Cost control: estimated vs actual with calculated difference and who-pays flag (owner / tenant / agent)

**🛡️ Security (Option B — Full Isolation)**
- Three dedicated groups: `group_re_asesor`, `group_re_coordinador`, `group_re_admin`
- Record Rules: agent sees exclusively their own properties, prospects, contracts, payments and maintenance records
- Coordinator has full vertical visibility
- Portal: owner sees only their properties (read-only) — base for portal v1.1

---

#### 🏗️ Architecture Decisions

- **`re.visita` reserved for v2.0:** Visits are registered as `mail.activity` in v1.0. The dedicated `re.visita` model will be implemented in v2.0 for property management firms with active portfolios exceeding 50 properties requiring per-visit conversion metrics.
- **`account.move` evaluated for v1.1:** Billing integration will be reviewed in the next architectural cycle to avoid premature dependencies.
- **Unified contract:** The decision to use a single model for rental and sale simplifies management for the independent agent who handles both types in their daily portfolio.

---

#### 🐛 Bugs Fixed During QA

- Cross-inheritance of Creative views over `tablero.tarea` — resolved with explicit `view_ids` and `priority=25` on RE views
- Core fields (`Es Ticket de Soporte`, `Estado Kanban`) visible in Operations form — resolved with `xpath` + `invisible="es_operacion_re"`
- OWL error in Maintenance Kanban due to `not` in QWeb expressions and Python ternaries in `t-attf-class` — resolved with `!` and JS ternary syntax
- `NaN` in Float fields of Property Kanban — resolved with `t-if="raw_value > 0"`

---

#### 📌 Roadmap v1.1

- Owner and tenant portal (`re_portal.py`)
- `account.move` integration for automatic rental invoices
- Automatic overdue payment marking cron
- `re.visita` as dedicated model for large portfolio managers
- App Store demo data

---

---

## 🇮🇹 Italiano

### Caletti Real Estate v1.0.0 — Primo Release Stabile

Questo release segna il lancio ufficiale del vertical immobiliare nell'ecosistema Odoo-Caletti. Progettato specificamente per agenti immobiliari indipendenti che gestiscono immobili di terzi, il modulo copre l'intero ciclo del business: dall'acquisizione del prospect alla riscossione della commissione, passando per la gestione dei contratti, dei pagamenti e delle richieste di manutenzione.

---

#### ✨ Funzionalità Incluse

**🏠 Portafoglio Immobili (`re.propiedad`)**
- Tre tipologie di immobili supportate dalla v1.0: Residenziale, Commerciale e Terreni con sottotipi specifici per categoria (casa, appartamento, townhouse, penthouse, locale commerciale, ufficio, magazzino, capannone industriale, terreno urbano, agricolo, ecc.)
- Galleria fotografica integrata con sottomodello `re.propiedad.foto` — fino a 10 immagini per immobile, ordinabili per sequenza, con foto di copertina designata
- Ciclo di stati: Disponibile → In Trattativa → Occupato → Venduto → Libero → In Manutenzione → Sospeso, con notifiche automatiche nella Chatter ad ogni transizione
- Campi economici: prezzo di affitto, prezzo di vendita, deposito, percentuale di commissione con calcolo stimato informativo
- Indirizzo completo calcolato automaticamente per report e portale
- Regola di business: l'agente gestisce esclusivamente immobili di terzi — `propietario_id` è campo obbligatorio

**👤 Pipeline Prospect (`re.prospecto`)**
- Pipeline a 8 fasi con Kanban drag-and-drop: Nuovo Lead → Contattato → Visita Programmata → Visita Effettuata → In Indagine → In Trattativa → Chiuso / Scartato
- Scoring temperatura lead: Caldo (pronto a chiudere), Tiepido (in valutazione), Freddo (in esplorazione)
- 9 fonti di acquisizione per analisi ROI: referral, portale web, social media, Lamudi, Inmuebles24, Vivanuncios, WhatsApp, chiamata diretta, cartello sull'immobile
- Relazione Many2many con gli immobili: un prospect può valutare più immobili contemporaneamente
- Indagine socioeconomica integrata con risultato (Approvato / Approvato con Osservazioni / Rifiutato / In Attesa)
- Visite registrate come `mail.activity` con tipo personalizzato "Visita Immobile" — `re.visita` riservato alla v2.0
- Note automatiche nella Chatter ad ogni cambio di fase con contesto del processo

**📋 Operazioni Immobiliari (`re.operacion` — estende `tablero.tarea`)**
- Pipeline visuale a 7 fasi: Acquisizione → Pubblicazione → Con Prospect → Trattativa → Documentazione → Chiusura → Chiuso/Archiviato
- Regola fondamentale: un immobile può avere una sola operazione attiva contemporaneamente — validata da `@api.constrains`
- Sincronizzazione automatica dello stato dell'immobile all'avanzamento delle fasi
- Isolamento completo delle viste tramite `view_ids` espliciti nell'azione — nessuna contaminazione incrociata con il vertical Creative
- Campo discriminatore `es_operacion_re` per una separazione pulita dal Core

**📄 Contratti Unificati (`re.contrato` + `re.pago`)**
- Un unico modello gestisce sia contratti di affitto CHE di vendita, differenziati da `tipo_operacion`
- **Affitto:** data di fine calcolata automaticamente (data inizio + durata in mesi), deposito cauzionale con tracciamento della restituzione, aumento annuale configurabile, giorno di pagamento mensile
- **Vendita:** prezzo finale, acconto, saldo all'atto calcolato automaticamente, tipo di finanziamento (contanti, mutuo, INFONAVIT, FOVISSSTE)
- Generazione automatica di tutti i pagamenti mensili all'attivazione di un contratto d'affitto (`_generar_pagos_renta`)
- Metriche di qualità dell'inquilino: percentuale di puntualità, conteggio pagamenti in ritardo, flag `inquilino_riesgo` con alert nella Chatter
- Azione di rinnovo con aumento automatico del canone in base alla percentuale concordata
- Commissione catturata manualmente con flag di incassato e data
- Cron giornaliero di alert scadenze: aggiorna a `por_vencer` 60 giorni prima e a `vencido` al superamento della data di fine

**🔧 Manutenzione (`re.mantenimiento`)**
- 16 categorie: idraulica, elettricità, pittura, falegnameria, fabbri, impermeabilizzazione, climatizzazione, disinfestazione, pulizie profonde, muratura, vetreria, giardinaggio, serrature, elettrodomestici, ristrutturazione, altro
- 4 livelli di priorità: Urgente (rischio per immobile/inquilino), Alta, Normale, Bassa
- Flusso a 7 stati: Richiesto → In Valutazione → Approvato → In Corso → Risolto → Chiuso / Annullato
- Approvazione del proprietario automaticamente richiesta quando `costo_estimado > $2.000 MXN` — blocca l'avanzamento senza autorizzazione
- Due tipi di esecutore: agente diretto o fornitore esterno con nome e telefono
- 4 origini della richiesta: agente, proprietario, inquilino (portale v1.1), ispezione
- Riferimento ticket sequenziale `MANT-YYYY-NNNNN` generato automaticamente alla creazione
- Controllo costi: stimato vs reale con differenza calcolata e flag su chi paga (proprietario / inquilino / agente)

**🛡️ Sicurezza (Opzione B — Isolamento Totale)**
- Tre gruppi dedicati: `group_re_asesor`, `group_re_coordinador`, `group_re_admin`
- Record Rules: l'agente vede esclusivamente le proprie proprietà, prospect, contratti, pagamenti e manutenzioni
- Il coordinatore ha visibilità totale sul vertical
- Portale: il proprietario vede solo i propri immobili (sola lettura) — base per portale v1.1

---

#### 🏗️ Decisioni Architetturali

- **`re.visita` riservato alla v2.0:** Le visite sono registrate come `mail.activity` nella v1.0. Il modello dedicato `re.visita` sarà implementato nella v2.0 per società di gestione immobiliare con portafogli attivi superiori a 50 immobili che richiedono metriche di conversione per visita.
- **`account.move` valutato per v1.1:** L'integrazione con la fatturazione sarà rivista nel prossimo ciclo architetturale per evitare dipendenze premature.
- **Contratto unificato:** La decisione di usare un unico modello per affitto e vendita semplifica la gestione dell'agente indipendente che opera entrambe le tipologie nel proprio portafoglio quotidiano.

---

#### 🐛 Bug Corretti Durante QA

- Ereditarietà incrociata delle viste Creative sul modello `tablero.tarea` — risolto con `view_ids` espliciti e `priority=25` sulle viste RE
- Campi del Core (`Es Ticket de Soporte`, `Estado Kanban`) visibili nel form Operazione — risolto con `xpath` + `invisible="es_operacion_re"`
- Errore OWL nel Kanban Manutenzione per uso di `not` nelle espressioni QWeb e ternari Python in `t-attf-class` — risolto con `!` e sintassi ternaria JS
- `NaN` nei campi Float del Kanban Immobili — risolto con `t-if="raw_value > 0"`

---

#### 📌 Roadmap v1.1

- Portale proprietario e inquilino (`re_portal.py`)
- Integrazione `account.move` per fatture automatiche di affitto
- Cron automatico per marcatura pagamenti in ritardo
- `re.visita` come modello dedicato per gestori di portafogli grandi
- Dati demo per App Store

---

**Carlos Caletti** — *Lead Architect & Developer 2026*
**Caletti Studio / MÉXICO — BUENOS AIRES — ROMA**
