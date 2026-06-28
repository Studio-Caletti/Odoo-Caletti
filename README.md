# 🚀 Odoo-Caletti: Advanced Kanban Framework,

# Helpdesk (ticket system)

# Creative Management System

# Real Estate Management

**Framework Modular Extensible para Odoo 17 | Caletti Studio**

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-875A7B.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-5.1.0-brightgreen.svg)](https://github.com/Studio-Caletti/Odoo-Caletti)

[Español](#español) | [English](#english) | [Italiano](#italiano)

---

## <a name="español"></a> 🇪🇸 Español <img src="https://flagcdn.com/w20/es.png" width="20">

### 1. 📄 Descripción del Ecosistema V5.1

**Odoo-Caletti V5** es una plataforma de gestión de alto rendimiento diseñada sobre **Odoo 17 Community**. Su esencia no es la de un software cerrado, sino la de un ecosistema vivo compuesto por un **Núcleo Core** de tarjetas dinámicas que orquesta el quehacer cotidiano empresarial.

A diferencia de las soluciones aisladas (hojas de cálculo o apps simples), este ecosistema ofrece el poder de un **ERP (Enterprise Resource Planning)**. Esto significa que mientras nuestras verticales resuelven nichos específicos como el **Auxiliar de Soporte (Helpdesk)** o el **Sistema de Gestión Creativa (SGC)**, el usuario mantiene la puerta abierta para integrar módulos nativos de Odoo como **CRM, Calendario, Pagos Electrónicos, Recursos Humanos o Facturación**, todo bajo una misma base de datos y una sola interfaz.

### Tabla de Módulos


| Vertical | Módulo | Versión | Estado |
|---|---|---|---|
| Core Kanban Engine | `tablero_kanban_caletti` | 17.0.5.0.0 | ✅ Producción |
| Helpdesk | `tablero_kanban_helpdesk` | 17.0.1.0.0 | ✅ Producción |
| Creative Management (SGC) | `caletti_creative` | 17.0.1.0.0 | ✅ Producción |
| Real Estate (CRE) | `caletti_real_estate` | 17.0.1.1.0 | ✅ Producción |

### 2. 📌 Pilares de la Arquitectura Caletti

- **Core Kanban V3 (La Columna Vertebral)**: Infraestructura de Business Intelligence que gestiona prioridades y tiempos. Es la base donde vive la operación administrativa general.

- **Helpdesk Vertical**: Sistema de ticketing que transforma las solicitudes de soporte en flujos de trabajo con tiempos de respuesta (SLA) garantizados.

- **Sistema de Gestión Creativa (SGC)**: Diseñado para **Despachos de Artes Gráficas**, agencias de medios y estudios digitales. Administra desde el Brief (directiva de diseño) hasta los entregables finales, asegurando rentabilidad y acuerdos claros.

- **Caletti Real Estate (CRE):** Diseñado para **Asesores Inmobiliarios Independientes** y pequeñas administradoras de propiedades. Gestiona el ciclo completo del negocio inmobiliario: cartera de propiedades (residencial, comercial y terrenos), pipeline de captación de prospectos, contratos unificados de renta y venta, seguimiento de pagos mensuales con métricas de puntualidad de inquilinos, y solicitudes de mantenimiento con control de costos y aprobación del propietario. Migra al asesor de las hojas de cálculo a la potencia de un ERP especializado.

- **El "Chatter" y la Comunicación Contextual**: Aprovechamos la potencia del motor de comunicación de Odoo para que cada tarea, ticket o brief tenga su propio muro de colaboración. Olvídese de correos dispersos; toda la historia, archivos adjuntos y decisiones quedan selladas en el historial (Chatter) del documento.

### 🛠️ Especificaciones Técnicas y Potencial ERP

- **Modularidad y Extensibilidad**: Las verticales heredan del Core, permitiendo una escalabilidad horizontal. Si el cliente necesita una tienda web (E-commerce) o control de inventarios, el ecosistema Caletti convive nativamente con estas herramientas.

- **Backend de Clase Empresarial**: Implementación en Python con lógica de validación senior, manejo de seguridad por grupos (Aislamiento de departamentos) y flujos automatizados de email.

- **Interacción en Portal**: Portales QWeb que permiten al cliente interactuar directamente con el equipo, aprobando presupuestos o revisando artes en tiempo real. 

- **Extensión del Core**: Herencia avanzada de `portal.portal_my_home` y controladores web especializados.

- **Lógica de Negocio**: Implementación robusta de métodos ORM, decoradores `@api.depends` y lógica de validación de fechas.

- **Seguridad (RBAC)🛡️**: Reglas de registro (Record Rules) que garantizan el aislamiento de datos por cliente y jerarquía interna (User, Manager, Admin, Client).

### ⚙️ Lógica de Estado Robusta

El núcleo del módulo implementa una automatización proactiva:

- **Cron de Vigilancia**: Revisión diaria de vencimientos y actualización de semáforos.

- **Tracking Temporal**: Captura automática de hitos (Inicio/Fin) al cambiar estados.

- **Comunicación**: Notificaciones por email integradas para hitos críticos y tareas vencidas.

- **Directivas y Acuerdos**: El SGC utiliza el **Brief Creativo** como documento rector. No hay producción sin aprobación, eliminando la ambigüedad en los proyectos de artes gráficas.

- **Versionamiento Inteligente**: Cada revisión genera una nueva iteración (v1, v2, v3...) vinculada al registro maestro, permitiendo auditar la evolución de una idea sin perder datos.

- **Alertas de Gestión**: Notificaciones automáticas de "Revisiones Excedidas" o "Presupuesto en Alerta", protegiendo el margen de utilidad del despacho.

- **Arquitectura Inmobiliaria:** Modelos propios `re.propiedad`, `re.prospecto`, `re.contrato`, `re.pago` y `re.mantenimiento`. El modelo `re.operacion` extiende `tablero.tarea` del Core mediante `_inherit`, aplicando el patrón de aislamiento Opción B con el campo discriminador `es_operacion_re`.
- **Pipeline de Prospectos:** Flujo de 8 etapas (Nuevo → Contactado → Visita Agendada → Visita Realizada → Investigación → Negociación → Cerrado / Descartado) con Kanban drag-and-drop, calificación de temperatura (Caliente / Tibio / Frío) y trazabilidad de fuente de captación para análisis de ROI de canales de marketing.
- **Contratos Unificados:** Un solo modelo `re.contrato` maneja renta Y venta, diferenciados por `tipo_operacion`. Al activar un contrato de renta, genera automáticamente todos los registros `re.pago` mensuales por el plazo acordado. Métricas de puntualidad del inquilino con alerta automática de riesgo al superar el umbral de pagos atrasados.
- **Motor de Mantenimiento:** Ciclo completo solicitado → evaluando → aprobado → en proceso → resuelto → cerrado. Aprobación automática del propietario obligatoria cuando el costo estimado supera el umbral configurado. Referencia de ticket secuencial `MANT-YYYY-NNNNN`. Soporte para asesor directo y proveedor externo con datos de contacto.
- **Alertas Automatizadas:** Cron diario de vencimientos de contratos que actualiza estados a `por_vencer` (60 días antes) y `vencido`, con notificación automática en el Chatter del asesor responsable.


### 🎯 Casos de Uso y próximos horizontes

- **Agencias creativas**: Seguimiento de proyectos con clientes en tiempo real.

- **Equipos de soporte técnico**: HelpDesk con tickets aislados por cliente.

- **Consultorías**: Reportes BI para medir productividad y tiempos de entrega.

- **Despachos de Artes Gráficas y Agencias**: Gestión de campañas, impresos y medios digitales con validación del cliente.

- **Soporte Técnico**: Resolución de incidencias con métricas de desempeño.

- **Asesores Inmobiliarios:** Gestión integral de cartera con pipeline de prospectos, contratos, pagos y mantenimiento — todo en un solo ERP. Desde la captación del lead hasta el cobro de la comisión.

### 

---

## <a name="english"></a> 🇺🇸 English <img src="https://flagcdn.com/w20/us.png" width="20">

### 1. 📄 Ecosystem V4 Description

**Odoo-Caletti V5**, designed under Odoo 17 Community, is a high-performance management ecosystem featuring an advanced Core Nucleus task-card board. It orchestrates daily business operations with a data structure optimized for operational agility. Unlike standalone apps, this ecosystem provides the full power of an ERP (Enterprise Resource Planning), enabling seamless integration with native modules like CRM, Calendar, Payments, HR, and Invoicing under a single interface.

### 📌Strategic Pillars

- **Core Kanban V5 (The Nucleus)**: Provides BI infrastructure, time traceability, and priority management. It is the engine for overall organizational visibility.

- **Vertical Helpdesk**: Specialized in post-sale support, ensuring every ticket is a met commitment through automated workflows and response SLAs.

- **Creative Management (CMS)**: Designed for Graphic Arts Studios and digital agencies. It manages campaign complexity—from traditional print to social media—ensuring clear agreements and profitability.

- **Caletti Real Estate (CRE):** Designed for **Independent Real Estate Agents** and small property management firms. Manages the complete real estate business cycle: property portfolio (residential, commercial, and land), prospect acquisition pipeline, unified rental and sale contracts, monthly payment tracking with tenant punctuality metrics, and maintenance requests with cost control and owner approval workflows. Moves agents from spreadsheets to the power of a specialized ERP.


### 🛠️ Technical Specifications (Architecture)
- **Multilevel Inheritance**: Verticals extend the tablero.tarea model, ensuring Core improvements reflect instantly across the ecosystem.

- **Chatter Power**: All communications, files, and decisions are sealed within the document’s contextual history, eliminating scattered emails.

- **Isolated Securit**y: Implementation of record rules (ir.rule) for total isolation between creative and support departments.

### ⚙️ State Logic and Traceability
- **Design Directives (Briefing)**: A governing document with version control. Production does not start without approval, protecting the studio legally and operationally.

- **Smart Versioning**: Each change request triggers a new iteration (v1, v2, v3...) linked to the original record for full auditability.

- **Management Alert**s: Automatic "Exceeded Revisions" notifications to protect profit margins.

Designed to move businesses away from fragmented spreadsheets into a unified environment. Start with creative project management today and scale to full enterprise resource planning tomorrow.

- **Real Estate Architecture:** Dedicated models `re.propiedad`, `re.prospecto`, `re.contrato`, `re.pago` and `re.mantenimiento`. The `re.operacion` model extends the Core's `tablero.tarea` via `_inherit`, applying the Option B isolation pattern with the `es_operacion_re` discriminator field.
- **Prospect Pipeline:** 8-stage flow (New → Contacted → Visit Scheduled → Visit Done → Investigation → Negotiation → Closed / Discarded) with Kanban drag-and-drop, lead temperature scoring (Hot / Warm / Cold), and acquisition source tracking for marketing ROI analysis.
- **Unified Contracts:** A single `re.contrato` model handles both rental AND sale contracts, differentiated by `tipo_operacion`. Activating a rental contract automatically generates all monthly `re.pago` records for the agreed term. Tenant punctuality metrics with automatic risk alert when the overdue payments threshold is exceeded.
- **Maintenance Engine:** Complete cycle: requested → evaluating → approved → in progress → resolved → closed. Mandatory owner approval when estimated cost exceeds the configured threshold. Sequential ticket reference `MANT-YYYY-NNNNN`. Support for direct agent execution and external provider with contact details.
- **Automated Alerts:** Daily contract expiration cron that updates states to `por_vencer` (60 days ahead) and `vencido`, with automatic Chatter notification to the responsible agent.


## 🎯 Use Cases and Horizons
- Graphic Arts & Agencies: Management of complex campaigns with client approval via the portal.

- Technical Support: Incident management with real-time resolution metrics.

- **Real Estate Agents:** Full portfolio management with prospect pipeline, contracts, payments and maintenance — all in one ERP. From lead capture to commission collection.

---

## <a name="italiano"></a> 🇮🇹 Italiano <img src="https://flagcdn.com/w20/it.png" width="20">

### 📄 Descrizione dell'Ecosistema V5

**Odoo-Caletti V4**, progettato su Odoo 17 Community, è un ecosistema di gestione ad alte prestazioni composto da un Nucleo Core avanzato basato su un sistema di schede attività. Questo nucleo permette di orchestrare le operazioni aziendali quotidiane con una struttura dati ottimizzata per l'agilità operativa. A differenza delle soluzioni isolate, questo ecosistema offre la potenza di un **ERP (Enterprise Resource Planning**), consentendo l'integrazione di moduli nativi come **CRM, Calendario, Pagamenti, Risorse Umane e Fatturazione** in un'unica interfaccia.

### 📌 Pilastri Strategici

- **Core Kanban V5 (Il Nucleo)**: Fornisce l'infrastruttura di BI, la tracciabilità temporale e la gestione delle priorità. È il motore della visibilità dell'intera organizzazione.

- **Helpdesk Verticale**: Specializzato nell'assistenza post-vendita, garantisce che ogni ticket sia un impegno rispettato attraverso flussi automatizzati e SLA di risposta.

- **Gestione Creativa (SGC)**: Progettato per Studi di Arti Grafiche e agenzie digitali. Gestisce la complessità delle campagne, dalla stampa tradizionale ai social media, garantendo accordi chiari e redditività.

- **Caletti Real Estate (CRE):** Progettato per **Agenti Immobiliari Indipendenti** e piccole società di gestione immobiliare. Gestisce l'intero ciclo del business immobiliare: portafoglio immobili (residenziale, commerciale e terreni), pipeline di acquisizione prospect, contratti unificati di affitto e vendita, monitoraggio dei pagamenti mensili con metriche di puntualità degli inquilini, e richieste di manutenzione con controllo dei costi e approvazione del proprietario. Migra l'agente dai fogli di calcolo alla potenza di un ERP specializzato.

### 🛠️ Specifiche tecniche (architettura)

- **Ereditarietà Multilivello**: Le verticali estendono il modello tablero.tarea, garantendo che i miglioramenti del Core si riflettano istantaneamente in tutto il sistema.

- **Potenza del Chatter**: Tutte le comunicazioni, i file e le decisioni sono sigillati nella cronologia contestuale del documento, eliminando le email disperse.

- **Sicurezza Isolata**: Implementazione di regole di record (ir.rule) per un isolamento totale tra i reparti creativi e di supporto.

- **Sicurezza (RBAC)🛡️**: Regole di registrazione che garantiscono l'isolamento dei dati per client e gerarchia interna (Utente, Manager, Amministratore, Client).

- **Architettura Immobiliare:** Modelli dedicati `re.propiedad`, `re.prospecto`, `re.contrato`, `re.pago` e `re.mantenimiento`. Il modello `re.operacion` estende il `tablero.tarea` del Core tramite `_inherit`, applicando il pattern di isolamento Opzione B con il campo discriminatore `es_operacion_re`.
- **Pipeline Prospect:** Flusso a 8 fasi (Nuovo → Contattato → Visita Programmata → Visita Effettuata → Indagine → Negoziazione → Chiuso / Scartato) con Kanban drag-and-drop, scoring della temperatura del lead (Caldo / Tiepido / Freddo) e tracciabilità della fonte di acquisizione per l'analisi del ROI dei canali marketing.
- **Contratti Unificati:** Un unico modello `re.contrato` gestisce sia i contratti di affitto CHE di vendita, differenziati da `tipo_operacion`. L'attivazione di un contratto di affitto genera automaticamente tutti i record `re.pago` mensili per la durata concordata. Metriche di puntualità dell'inquilino con alert automatico di rischio al superamento della soglia di pagamenti in ritardo.
- **Motore di Manutenzione:** Ciclo completo: richiesto → in valutazione → approvato → in corso → risolto → chiuso. Approvazione obbligatoria del proprietario quando il costo stimato supera la soglia configurata. Riferimento ticket sequenziale `MANT-YYYY-NNNNN`. Supporto per esecuzione diretta dell'agente e fornitore esterno con dati di contatto.
- **Alert Automatizzati:** Cron giornaliero di scadenza contratti che aggiorna gli stati a `por_vencer` (60 giorni prima) e `vencido`, con notifica automatica nella Chatter dell'agente responsabile.

### ⚙️ Logica di Stato Robusta

- **Direttive di Design (Briefing)**: Documento d'indirizzo con controllo di versione. La produzione non inizia senza approvazione, proteggendo lo studio legalmente e operativamente.

- **Versionamento Intelligente**: Ogni richiesta di modifica genera una nuova iterazione (v1, v2, v3...) collegata al record originale per un'audit completa.

- **Avvisi di Gestione**: Notifiche automatiche di "Revisioni Eccedute" per proteggere i margini di profitto.

### 🎯 Casi d’Uso

- **Arti Grafiche e Agenzie**: Gestione di campagne complesse con approvazione del cliente tramite portale.

- **Supporto Tecnico**: Gestione degli incidenti con metriche di risoluzione in tempo reale.

- **Agenti Immobiliari:** Gestione completa del portafoglio con pipeline prospect, contratti, pagamenti e manutenzione — tutto in un unico ERP. Dalla cattura del lead alla riscossione della commissione.

---

### 📈 Evolución del Ecosistema: Expansión Modular Realizada

La V4 marca el nacimiento de una arquitectura que no compite con Odoo, sino que lo potencia para sectores específicos:

1. **Core**: El cimiento operativo.

2. **Helpdesk**: Excelencia en atención al cliente.

3. **Creative**: El estándar para Artes Gráficas y Agencias.

4. **Real Estate (CRE) v1.1**: Gestión inmobiliaria integral — portal propietario/inquilino, integración contable, analítica y modelo de visitas.
   
5. **Próximamente v6.0**: Nuevo vertical a definir según roadmap estratégico Caletti Studio.
 

---

### 🛠️ Instalación / Installation / Installazione

### 🇪🇸 Español

1. **Descargar** el repositorio en tu carpeta de `custom_addons`.
2. **Dependencias**: Asegúrate de tener instalados los módulos base `mail` y `portal`.
3. **Actualizar**: Reinicia tu servidor Odoo y activa el modo desarrollador.
4. **Instalar**: Ve al menú de Aplicaciones, haz clic en "Actualizar lista de aplicaciones" y busca `Tablero Kanban Caletti`(Core) y luego `tablero_kanban_helpdesk`.

### 🇺🇸 English

1. **Clone/Download** the repository into your `custom_addons` directory.
2. **Dependencies**: Ensure Odoo's native `mail` and `portal` modules are installed.
3. **Update**: Restart your Odoo server and enable Developer Mode.
4. **Install**: Go to the Apps menu, click "Update Apps List", and search for `Tablero Kanban Caletti`(Core) first, followed by `tablero_kanban_helpdesk`.

### 🇮🇹 Italiano

1. **Scaricare** il repository nella cartella `custom_addons`.
2. **Dipendenze**: Assicurarsi che i moduli base `mail` e `portal` siano installati.
3. **Aggiornare**: Riavviare il server Odoo e attivare la Modalità Sviluppatore.
4. **Installare**: Vai al menu Applicazioni, clicca su "Aggiorna elenco applicazioni" e cerca `Tablero Kanban Caletti` (Core) e poi ` tablero_kanban_helpdesk`.

## ⚙️ Instalación y Configuración del Ecosistema

La implementación de Odoo-Caletti V4 requiere una configuración precisa para habilitar su máxima potencia (Automatización y ERP). 

1. **Dependencias**: Asegúrese de tener instalado Odoo 17 Community.
2. **Orden de Instalación**: 
   - Primero: `tablero_kanban_caletti` (Core).
   - Segundo: Verticales de su elección (`helpdesk` / `creative`).
3. **Configuración Crítica**: Para el correcto funcionamiento de los Alias (`creativos@`, `soporte@`) y las notificaciones automáticas, es indispensable configurar el servidor de salida (SMTP) y los registros DNS correspondientes.

📘 **Guía Detallada de Instalación**: Para un paso a paso sobre configuración de servidores de correo, gestión de logotipos en plantillas y parámetros del sistema, consulte nuestro archivo: [INSTALL.md](./docs/INSTALL.md)

## 🛠️ Para Desarrolladores (Technical Stack)

Si eres desarrollador y deseas contribuir o entender la lógica profunda de este framework (Herencia multinivel, decoradores avanzados, seguridad Record Rules y gestión de contexto), hemos preparado una documentación técnica exhaustiva.

- **Arquitectura de Datos**: Relación entre el Core y las Verticales.
- **Flujos de API**: Cómo extendemos el Chatter y las notificaciones.
- **Seguridad**: Implementación de grupos y reglas de aislamiento (Opción B).

💻 **Notas Técnicas**: Consulta los detalles de ingeniería en: [TECHNICAL_NOTES.md](./docs/TECHNICAL_NOTES.md)

---

### 🗂️Repository Structure

```text
Odoo-Caletti/
├── tablero_kanban_caletti/                 # 🧠 MÓDULO BASE
│   ├── controllers/
│   │   └── main.py                         # Portal routes
│   ├── data/
│   │   ├── ir_cron.xml                     # Cron de alertas
│   │   └── mail_template_data.xml          # Template de tareas vencidas
│   ├── models/
│   │   └── mensaje.py                      # Modelo tablero.tarea
│   ├── security/
│   │   ├── security_groups.xml             # Grupos de seguridad
│   │   ├── ir.model.access.csv             # Permisos de acceso
│   │   ├── ir_rule.xml                     # Record Rules (User, Manager)
│   │   └── tablero_rules.xml               # Record Rule Portal
│   ├── static/description/
│   │   ├── icon.png
│   │   └── screenshots/                    # Capturas de pantalla
│   ├── views/
│   │   ├── views.xml                       # Kanban, Form, List, Graph, Pivot
│   │   ├── portal_templates.xml            # Templates del portal
│   │   └── report_tarea.xml                # Reportes PDF
│   ├── __init__.py
│   └── __manifest__.py
│
├── tablero_kanban_helpdesk/                # 🎧 VERTICAL HELPDESK
│   ├── controllers/
│   │   └── helpdesk_portal.py              # Portal routes (tickets)
│   ├── data/
│   │   └── helpdesk_data.xml               # Sequence, Template confirmación
│   ├── models/
│   │   └── tablero_ticket.py               # Herencia + campos helpdesk
│   ├── views/
│   │   ├── helpdesk_views.xml              # Vistas backend
│   │   └── portal_helpdesk_views.xml       # Vistas portal
│   ├── __init__.py
│   └── __manifest__.py
│
├── caletti_creative/                        #🎨 VERTICAL CREATIVA
│   ├── models/
│   │   ├── __init__.py
│   │   ├── creative_project.py              # _inherit tablero.tarea
│   │   ├── creative_brief.py                # Gestión de estrategia y versiones
│   │   ├── creative_deliverable.py          # Control de producción y revisiones
│   │   └── creative_team_member.py          # Colaboradores y roles
│   ├── views/                               # Vistas Backend
│   │   ├── creative_project_views.xml       # Vista proyecto Creativo
│   │   ├── creative_brief_views.xml         # Vista Brief Creativo
│   │   ├── creative_deliverable_views.xml   # Vista entregables
│   │   └── portal_creative_templates.xml    # Frontend del cliente
│   ├── security/
│   │   ├── security_groups.xml              # Grupos de seguridad
│   │   ├── ir.model.access.csv              # Permisos de acceso
│   │   └── ir_rule.xml                      # Record Rules (User, Manager)
│   ├── data/
│   │   └── creative_data.xml                # Sequence, Template confirmación
│   ├── __init__.py
│   └── __manifest__.py
│ 
├── caletti_real_estate/                     # 🏠 VERTICAL INMOBILIARIO v1.0
│   ├── models/
│   │   ├── re_propiedad.py                  # Cartera de propiedades + submodelo re.propiedad.foto
│   │   ├── re_prospecto.py                  # Pipeline de captación (8 etapas)
│   │   ├── re_operacion.py                  # _inherit tablero.tarea — operación activa
│   │   ├── re_contrato.py                   # Contratos renta/venta + submodelo re.pago
│   │   └── re_mantenimiento.py              # Solicitudes de mantenimiento con ticket
│   ├── views/
│   │   ├── re_propiedad_views.xml           # Kanban, Form, Tree, Search
│   │   ├── re_prospecto_views.xml           # Pipeline Kanban por etapa
│   │   ├── re_operacion_views.xml           # Vista propia sobre tablero.tarea
│   │   ├── re_contrato_views.xml            # Contratos + pagos inline + cron
│   │   └── re_mantenimiento_views.xml       # Kanban mantenimiento + secuencia
│   ├── security/
│   │   ├── security_groups.xml              # group_re_asesor, coordinador, admin
│   │   ├── ir.model.access.csv              # Permisos por rol y modelo
│   │   └── ir_rule.xml                      # Record Rules: asesor ve solo sus registros
│   ├── controllers/
│   │   └── __init__.py                      # Portal v1.1 — pendiente
│   ├── __init__.py
│   └── __manifest__.py
│
├── docs/
│   ├── INSTALL.md
│   └── TECHNICAL_NOTES.md
│
└── README.md                                # Este archivo
```

**Carlos Caletti** - ** *Lead Architect & Developer* 2026
---

<p align="left">
  <a href="https://studio.caletti.com.mx">
    <img src="https://img.shields.io/badge/Visitanos-CALETII%20STUDIO-blue?style=for-the-badge&logo=odoo&logoColor=%23714B67&logoSize=auto&labelColor=lightgray&color=8A2BE2" />
  </a>
</p>