# 🚀 Odoo-Caletti: Advanced Kanban Framework & Helpdesk System

**Framework Modular Extensible para Odoo 17 | Caletti Studio**

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-875A7B.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-brightgreen.svg)](https://github.com/Studio-Caletti/Odoo-Caletti)

[Español](#español) | [English](#english) | [Italiano](#italiano)

---

## <a name="español"></a> 🇪🇸 Español <img src="https://flagcdn.com/w20/es.png" width="20">

### 📄 Descripción
El **Tablero Kanban Caletti Core V3** no es solo un gestor de tareas; es un ecosistema de **Business Intelligence** y **Experiencia de Cliente** diseñado para Odoo 17. Este módulo constituye el pilar fundamental de nuestra arquitectura modular, integrando una lógica de estados robusta que no solo actualiza campos sino que **dispara eventos automáticos de seguimiento, comunicación y trazabilidad temporal**.

El **Core V3** marca la transición hacia una **Arquitectura Modular Escalable**, donde un núcleo robusto (Core) puede ser extendido mediante módulos especializados sin comprometer la integridad del sistema principal.

### 📌 Pilares de la Versión 3.0
- **Backend de Alto Rendimiento**: Interfaz Kanban evolucionada con **Header Dinámico** para filtrado rápido y **Visual Awareness** (cintas y bordes de color) que dictan el ritmo operativo.
- **Portal de Cliente 360°**: Transformamos el portal estándar en un centro de mando para el cliente, con barras de progreso animadas, acceso táctil optimizado y transparencia total vía Chatter.
- **Reporting & BI**: Salidas documentales en PDF (QWeb) con identidad visual dinámica y vistas de análisis (Pivote/Gráfico) para la toma de decisiones basada en datos reales (`duration_days`).
- **Comunicación Proactiva**: Integración total con el Chatter de Odoo, gestión de pestañas para una trazabilidad total de la comunicación, y sistema de notificaciones automáticas vía email para hitos críticos y tareas vencidas.
- **Ecosistema Extensible**: Implementación de una arquitectura de "Módulo Base + Extensiones" que permite inyectar funcionalidades de soporte técnico (Ticketing) sin sobrecargar el Core, manteniendo la base de datos limpia y eficiente.
- **Helpdesk Vertical**: Primera extensión oficial que integra un sistema de Ticketing avanzado con priorización y flujos de soporte técnico independientes.

### 🛠️ Especificaciones Técnicas (Arquitectura)
- **Extensión del Core**: Herencia avanzada de `portal.portal_my_home` y controladores web especializados.
- **Lógica de Negocio**: Implementación robusta de métodos ORM, decoradores `@api.depends` y lógica de validación de fechas.
- **Seguridad (RBAC)🛡️**: Reglas de registro (Record Rules) que garantizan el aislamiento de datos por cliente y jerarquía interna (User, Manager, Admin, Client).


### ⚙️ Lógica de Estado Robusta
El núcleo del módulo implementa una automatización proactiva:
- **Cron de Vigilancia**: Revisión diaria de vencimientos y actualización de semáforos.
- **Tracking Temporal**: Captura automática de hitos (Inicio/Fin) al cambiar estados.
- **Comunicación**: Notificaciones por email integradas para hitos críticos y tareas vencidas.

### 🎯 Casos de Uso
- **Agencias creativas**: Seguimiento de proyectos con clientes en tiempo real.
- **Equipos de soporte técnico**: HelpDesk con tickets aislados por cliente.
- **Consultorías**: Reportes BI para medir productividad y tiempos de entrega.

---

## <a name="english"></a> 🇺🇸 English <img src="https://flagcdn.com/w20/us.png" width="20">

### 📄 Description 
The **Caletti Core V3** Kanban Board is not just a task manager; it is a **Business Intelligence** and Customer Experience ecosystem designed for Odoo 17. This module forms the fundamental pillar of our modular architecture, integrating a robust state logic that not only updates fields but also **triggers automatic events for tracking, communication, and time traceability**.

The **Core V3** framework allows a high-performance Core that manages time-tracking and project logic, which can be seamlessly extended with specialized functional layers like our new **Helpdesk module**.

### 📌 Version 3.0 Key Pillars
- **High-Performance Backend**: Evolved Kanban UI with **Dynamic Headers** for instant filtering and **Visual Awareness** (ribbons and color-coded borders) to drive operational pace.
- **360° Customer Portal**: We turn the standard portal into a client command center, featuring animated progress bars, touch-optimized UX, and full transparency through integrated Chatter.
- **Reporting & BI**: QWeb PDF reports with dynamic visual branding and native analytical views (Pivot/Graph) for data-driven decision-making based on lead times (`duration_days`).
- **Proactive Communication**: Full integration with Odoo's Chatter, tab management for complete communication traceability, and automatic email notification system for critical milestones and overdue tasks.
- **Advanced Helpdesk**: Integrated ticketing extension with priority widgets and dedicated workflows for technical support.

### 🛠️ Technical Specifications (Arquitecture)
- **Core Extension**: Advanced inheritance from portal.portal_my_home and specialized web controllers.
- **Business Logic**: Robust implementation of ORM methods, @api.depends decorators, and date validation logic.
- **Security (RBAC)🛡️**: Record Rules that ensure data isolation by client and internal hierarchy (User, Manager, Admin, Client).
### ⚙️ Robust State Logic

The core of the module implements proactive automation:

- **Monitoring Cron**: Daily review of due dates and updates to status indicators.
- **Time Tracking**: Automatic capture of milestones (Start/Finish) when statuses change.
- **Communication**: Integrated email notifications for critical milestones and overdue tasks.

### 🎯 Use Cases

- **Creative agencies**: Real-time project tracking with clients.
- **Support teams**: HelpDesk with client-isolated tickets.
- **Consulting firms**: BI reports to measure productivity and delivery times.

---
### 🎫 Sistema Helpdesk Completo (Nuevo)

#### **Características Principales:**

1.  **🔢 Secuencia Automática de Tickets**
    
    -   Generación de referencias únicas:  `TK-00001`,  `TK-00002`, etc.
    -   Incremental y automático
2.  **📧 Creación de Tickets por Email**
    
    -   Los clientes envían emails a  `soporte@caletti.com.mx`
    -   Odoo crea tickets automáticamente
    -   Funciona para clientes registrados y no registrados
3.  **✉️ Emails de Confirmación Automáticos**
    
    -   Template profesional con branding
    -   Incluye número de ticket, tipo, prioridad y estado
    -   Personalizado con nombre del cliente
4.  **⏱️ Tracking de SLA**
    
    -   Mide tiempo de primera respuesta
    -   Campo  `sla_hours`  calculado automáticamente
5.  **👥 Equipos de Soporte (Escalabilidad)**
    
    -   Modelo  `HelpdeskTeam`  preparado para múltiples equipos
    -   Cada equipo puede tener su propio alias de email
    -   Métricas por equipo
    ---
## <a name="italiano"></a> 🇮🇹 Italiano <img src="https://flagcdn.com/w20/it.png" width="20">

### 📄 Descrizione
**Caletti Core V3 Kanban Board** non è solo un task manager; è un ecosistema di **Business Intelligence e Customer Experience** progettato per Odoo 17. Questo modulo costituisce il pilastro fondamentale della nostra architettura modulare, integrando una logica di stato robusta che non solo aggiorna i campi, ma **attiva anche eventi automatici per il monitoraggio, la comunicazione e la tracciabilità temporale**.

Il **Core V3** è ora un framework separa la logica principale di gestione dei tempi e dei progetti (Core) dalle estensioni funzionali specifiche, come il nuovo **modulo Helpdesk** per l'assistenza tecnica.

### 📌 Pilastri della Versione 3.0
- **Backend ad Alte Prestazioni**: Interfaccia Kanban evoluta con **Header Dinamico** e **Visual Awareness** (ribbon e bordi colorati) per una gestione operativa immediata.
- **Portale Clienti 360°**: Un centro di controllo per il cliente con barre di progressione animate e trasparenza totale tramite l'integrazione del Chatter.
- **Reporting & BI**: Report PDF (QWeb) con identità visiva dinamica e viste analitiche (Pivot/Grafico) per decisioni basate su dati reali di esecuzione.
- **Comunicazione proattiva**: integrazione completa con Chatter di Odoo, gestione delle schede per una completa tracciabilità delle comunicazioni e sistema di notifica automatica via e-mail per traguardi critici e attività in ritardo.
- **Helpdesk Integrato**: Estensione dedicata al supporto tecnico con gestione delle priorità e flussi di lavoro separati.

### 🛠️ Specifiche tecniche (architettura)
- **Estensione Core**: Ereditarietà avanzata da portal.portal_my_home e controller web specializzati.
- **Logica di business**: Implementazione robusta di metodi ORM, decoratori @api.depends e logica di convalida delle date.
- **Sicurezza (RBAC)🛡️**: Regole di registrazione che garantiscono l'isolamento dei dati per client e gerarchia interna (Utente, Manager, Amministratore, Client).

### ⚙️ Logica di Stato Robusta
Il cuore del modulo implementa l'automazione proattiva:

- **Monitoraggio Cron**: revisione giornaliera delle scadenze e aggiornamenti semaforici.
- **Monitoraggio del tempo**: acquisizione automatica delle milestone (inizio/fine) al variare dello stato.
- **Comunicazione**: notifiche e-mail integrate per milestone critiche e attività in ritardo.

### 🎯 Casi d’Uso
- **Agenzie creative**: Monitoraggio progetti in tempo reale con i clienti.
- **Team di supporto**: HelpDesk con ticket isolati per cliente.
- **Società di consulenza**: Report BI per misurare produttività e tempi di consegna.

---


### 📊 Resumen de Componentes / Components Summary / Riepilogo dei componenti

| Componente | Widget / Clase | Impacto Visual |
| :--- | :--- | :--- |
| **Progreso** | `progressbar` | Visualización inmediata del avance del proyecto. |
| **Vencimiento** | `remaining_days` | Crea sentido de urgencia ("En 2 días", "Vencida"). |
| **Avatar** | `many2one_avatar_user` | Identificación rápida del responsable de la tarea. |
| **Semáforo** | `state_selection` | Estatus de salud (Punto verde/rojo/amarillo). |

---

### 🚀 Evolución del Ecosistema: Expansión Modular Realizada
Este módulo ha sido concebido como una **Base Maestra (Core V3)**. Lo que antes era una visión estratégica, hoy es una realidad funcional. El sistema ha evolucionado de un módulo único a un ecosistema de dos vertientes:

1. **Helpdesk Extension** (tablero_kanban_helpdesk) 🆕: Un sistema de tickets totalmentefuncional y práctico con una curva de aprendizaje mínima.
- **Tiketing Especializado**: Inyecta campos de "Tipo de Ticket" y "Prioridad" (estrellas) mediante herencia de modelos.
- **Automatización de Flujo**:Acciones de ventana con context inteligente que marcan automáticamente los registros como tickets.
- **Vistas Dedicadas**:Menús y filtros exclusivos para que el equipo de soporte (como Ana) trabaje de forma independiente al área de proyectos.

2. **Vertical Project Tracking**: Gestión profunda de etapas, responsables, reportes de colaboradores y personal.

### 🚀 Strategic Note: Modular Expansion
This module has been designed as a Master Base (Core V3). Its architecture is prepared for strategic branching into two growth paths:
1. **Helpdesk Extension**: Adds a fully functional Ticketing layer. It includes priority widgets, specialized search filters, and dedicated menus, ensuring support teams have a streamlined workspace separate from project management with a minimal learning curve.
2. **Vertical Project Tracking**: In-depth management of stages, responsible parties, and reports from collaborators and staff.

### 🚀 Nota strategica: Espansione modulare
Questo modulo è stato progettato come **Master Base (Core V3)**. La sua architettura è predisposta per la ramificazione strategica in due percorsi di crescita:
1. **Helpdesk Extension 🆕**: Aggiunge un sistema di ticketing completo con widget di priorità, filtri di ricerca specializzati e menu dedicati per il supporto tecnico, pratico con una curva di apprendimento minima.
2. **Monitoraggio verticale del progetto**: gestione approfondita di fasi, responsabili e report da parte di collaboratori e personale.

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

---


## Check our data/ir_cron.xml to see how automated alerts are scheduled.

### 🗂️Repository Structure
```text
Odoo-Caletti/
├── tablero_kanban_caletti/          # MÓDULO BASE
│   ├── controllers/
│   │   └── main.py                   # Portal routes
│   ├── data/
│   │   ├── ir_cron.xml              # Cron de alertas
│   │   └── mail_template_data.xml   # Template de tareas vencidas
│   ├── models/
│   │   └── mensaje.py               # Modelo tablero.tarea
│   ├── security/
│   │   ├── security_groups.xml      # Grupos de seguridad
│   │   ├── ir.model.access.csv      # Permisos de acceso
│   │   ├── ir_rule.xml              # Record Rules (User, Manager)
│   │   └── tablero_rules.xml        # Record Rule Portal
│   ├── static/description/
│   │   ├── icon.png
│   │   └── screenshots/             # Capturas de pantalla
│   ├── views/
│   │   ├── views.xml                # Kanban, Form, List, Graph, Pivot
│   │   ├── portal_templates.xml     # Templates del portal
│   │   └── report_tarea.xml         # Reportes PDF
│   └── __manifest__.py
│
├── tablero_kanban_helpdesk/         # MÓDULO HELPDESK
│   ├── controllers/
│   │   └── helpdesk_portal.py       # Portal routes (tickets)
│   ├── data/
│   │   └── helpdesk_data.xml        # Sequence, Template confirmación
│   ├── models/
│   │   └── tablero_ticket.py        # Herencia + campos helpdesk
│   ├── views/
│   │   ├── helpdesk_views.xml       # Vistas backend
│   │   └── portal_helpdesk_views.xml # Vistas portal
│   └── __manifest__.py
│
└── README.md                         # Este archivo
```

**Carlos Caletti** - ** *Lead Architect & Developer* 2026
---
<p align="left">
  <a href="https://studio.caletti.com.mx">
    <img src="https://img.shields.io/badge/Visitanos-CALETII%20STUDIO-blue?style=for-the-badge&logo=odoo&logoColor=%23714B67&logoSize=auto&labelColor=lightgray&color=8A2BE2" />
  </a>
</p>