# Odoo-Caletti: Advanced Kanban Framework & Strategic Portal 🚀

[Español](#español) | [English](#english) | [Italiano](#italiano)

---

## <a name="español"></a> 🇪🇸 Español

### 📄 Descripción
El **Tablero Kanban Caletti Core V2** no es solo un gestor de tareas; es un ecosistema de **Business Intelligence** y **Experiencia de Cliente** diseñado para Odoo 17. Este módulo constituye el pilar fundamental de nuestra arquitectura modular, integrando una lógica de estados robusta que no solo actualiza campos sino que **dispara eventos automáticos de seguimiento, comunicación y trazabilidad temporal**.

### 📌 Pilares de la Versión 2.0
- **Backend de Alto Rendimiento**: Interfaz Kanban evolucionada con **Header Dinámico** para filtrado rápido y **Visual Awareness** (cintas y bordes de color) que dictan el ritmo operativo.
- **Portal de Cliente 360°**: Transformamos el portal estándar en un centro de mando para el cliente, con barras de progreso animadas, acceso táctil optimizado y transparencia total vía Chatter.
- **Reporting & BI**: Salidas documentales en PDF (QWeb) con identidad visual dinámica y vistas de análisis (Pivote/Gráfico) para la toma de decisiones basada en datos reales (`duration_days`).
- **Comunicación Proactiva**: Integración total con el Chatter de Odoo, gestión de pestañas para una trazabilidad total de la comunicación, y sistema de notificaciones automáticas vía email para hitos críticos y tareas vencidas.

### 🛠️ Especificaciones Técnicas (Arquitectura)
- **Extensión del Core**: Herencia avanzada de `portal.portal_my_home` y controladores web especializados.
- **Lógica de Negocio**: Implementación robusta de métodos ORM, decoradores `@api.depends` y lógica de validación de fechas.
- **Seguridad (RBAC)🛡️**: Reglas de registro (Record Rules) que garantizan el aislamiento de datos por cliente y jerarquía interna (User, Manager, Admin, Client).


### ⚙️ Lógica de Estado Robusta
El núcleo del módulo implementa una automatización proactiva:
- **Cron de Vigilancia**: Revisión diaria de vencimientos y actualización de semáforos.
- **Tracking Temporal**: Captura automática de hitos (Inicio/Fin) al cambiar estados.
- **Comunicación**: Notificaciones por email integradas para hitos críticos y tareas vencidas.

---

## <a name="english"></a> 🇺🇸 English

### 📄 Description <img src="https://flagcdn.com/w20/us.png" width="20">
The **Caletti Core V2** Kanban Board is not just a task manager; it is a **Business Intelligence** and Customer Experience ecosystem designed for Odoo 17. This module forms the fundamental pillar of our modular architecture, integrating a robust state logic that not only updates fields but also **triggers automatic events for tracking, communication, and time traceability**.

### 📌 Version 2.0 Key Pillars
- **High-Performance Backend**: Evolved Kanban UI with **Dynamic Headers** for instant filtering and **Visual Awareness** (ribbons and color-coded borders) to drive operational pace.
- **360° Customer Portal**: We turn the standard portal into a client command center, featuring animated progress bars, touch-optimized UX, and full transparency through integrated Chatter.
- **Reporting & BI**: QWeb PDF reports with dynamic visual branding and native analytical views (Pivot/Graph) for data-driven decision-making based on lead times (`duration_days`).
- **Proactive Communication**: Full integration with Odoo's Chatter, tab management for complete communication traceability, and automatic email notification system for critical milestones and overdue tasks.
### 🛠️ Technical Specifications (Arquitecture)
- **Core Extension**: Advanced inheritance from portal.portal_my_home and specialized web controllers.
- **Business Logic**: Robust implementation of ORM methods, @api.depends decorators, and date validation logic.
- **Security (RBAC)🛡️**: Record Rules that ensure data isolation by client and internal hierarchy (User, Manager, Admin, Client).
### ⚙️ Robust State Logic

The core of the module implements proactive automation:

- **Monitoring Cron**: Daily review of due dates and updates to status indicators.
- **Time Tracking**: Automatic capture of milestones (Start/Finish) when statuses change.
- **Communication**: Integrated email notifications for critical milestones and overdue tasks.
---

## <a name="italiano"></a> 🇮🇹 Italiano

### 📄 Descrizione
**Caletti Core V2 Kanban Board** non è solo un task manager; è un ecosistema di **Business Intelligence e Customer Experience** progettato per Odoo 17. Questo modulo costituisce il pilastro fondamentale della nostra architettura modulare, integrando una logica di stato robusta che non solo aggiorna i campi, ma **attiva anche eventi automatici per il monitoraggio, la comunicazione e la tracciabilità temporale**.

### 📌 Pilastri della Versione 2.0
- **Backend ad Alte Prestazioni**: Interfaccia Kanban evoluta con **Header Dinamico** e **Visual Awareness** (ribbon e bordi colorati) per una gestione operativa immediata.
- **Portale Clienti 360°**: Un centro di controllo per il cliente con barre di progressione animate e trasparenza totale tramite l'integrazione del Chatter.
- **Reporting & BI**: Report PDF (QWeb) con identità visiva dinamica e viste analitiche (Pivot/Grafico) per decisioni basate su dati reali di esecuzione.
- **Comunicazione proattiva**: integrazione completa con Chatter di Odoo, gestione delle schede per una completa tracciabilità delle comunicazioni e sistema di notifica automatica via e-mail per traguardi critici e attività in ritardo.

### 🛠️ Specifiche tecniche (architettura)
- **Estensione Core**: Ereditarietà avanzata da portal.portal_my_home e controller web specializzati.
- **Logica di business**: Implementazione robusta di metodi ORM, decoratori @api.depends e logica di convalida delle date.
- **Sicurezza (RBAC)🛡️**: Regole di registrazione che garantiscono l'isolamento dei dati per client e gerarchia interna (Utente, Manager, Amministratore, Client).

### ⚙️ Logica di Stato Robusta
Il cuore del modulo implementa l'automazione proattiva:

- **Monitoraggio Cron**: revisione giornaliera delle scadenze e aggiornamenti semaforici.
- **Monitoraggio del tempo**: acquisizione automatica delle milestone (inizio/fine) al variare dello stato.
- **Comunicazione**: notifiche e-mail integrate per milestone critiche e attività in ritardo.
---

### 📊 Resumen de Componentes / Components Summary / Riepilogo dei componenti

| Componente | Widget / Clase | Impacto Visual |
| :--- | :--- | :--- |
| **Progreso** | `progressbar` | Visualización inmediata del avance del proyecto. |
| **Vencimiento** | `remaining_days` | Crea sentido de urgencia ("En 2 días", "Vencida"). |
| **Avatar** | `many2one_avatar_user` | Identificación rápida del responsable de la tarea. |
| **Semáforo** | `state_selection` | Estatus de salud (Punto verde/rojo/amarillo). |

---

### 🚀 Nota Estratégica: Expansión Modular
Este módulo ha sido concebido como una **Base Maestra (Core V2)**. Su arquitectura está preparada para una bifurcación estratégica en dos vertientes de crecimiento:
1. **Vertical Helpdesk**: Un sistema de tickets funcional y práctico con una curva de aprendizaje mínima.
2. **Vertical Project Tracking**: Gestión profunda de etapas, responsables, reportes de colaboradores y personal.

### 🚀 Strategic Note: Modular Expansion
This module has been designed as a Master Base (Core V2). Its architecture is prepared for strategic branching into two growth paths:
1.**Vertical Helpdesk**: A functional and practical ticketing system with a minimal learning curve.
2.**Vertical Project Tracking**: In-depth management of stages, responsible parties, and reports from collaborators and staff.

### 🚀 Nota strategica: Espansione modulare
Questo modulo è stato progettato come **Master Base (Core V2)**. La sua architettura è predisposta per la ramificazione strategica in due percorsi di crescita:
1.**Helpdesk verticale**: un sistema di ticketing funzionale e pratico con una curva di apprendimento minima.
2.**Monitoraggio verticale del progetto**: gestione approfondita di fasi, responsabili e report da parte di collaboratori e personale.

---

### 🛠️ Instalación / Installation / Installazione

### 🇪🇸 Español
1. **Descargar** el repositorio en tu carpeta de `custom_addons`.
2. **Dependencias**: Asegúrate de tener instalados los módulos base `mail` y `portal`.
3. **Actualizar**: Reinicia tu servidor Odoo y activa el modo desarrollador.
4. **Instalar**: Ve al menú de Aplicaciones, haz clic en "Actualizar lista de aplicaciones" y busca `Tablero Kanban Caletti`.

### 🇺🇸 English
1. **Clone/Download** the repository into your `custom_addons` directory.
2. **Dependencies**: Ensure Odoo's native `mail` and `portal` modules are installed.
3. **Update**: Restart your Odoo server and enable Developer Mode.
4. **Install**: Go to the Apps menu, click "Update Apps List", and search for `Tablero Kanban Caletti`.

### 🇮🇹 Italiano
1. **Scaricare** il repository nella cartella `custom_addons`.
2. **Dipendenze**: Assicurarsi che i moduli base `mail` e `portal` siano installati.
3. **Aggiornare**: Riavviare il server Odoo e attivare la Modalità Sviluppatore.
4. **Installare**: Vai al menu Applicazioni, clicca su "Aggiorna elenco applicazioni" e cerca `Tablero Kanban Caletti`.


##Check our data/ir_cron.xml to see how automated alerts are scheduled.

### 📂 Repository Structure
```text
tablero_kanban/
├── controllers/          # Portal routing & custom logic
├── data/                 # Cron jobs & automated alerts
├── models/               # Task definitions & Robust State Logic (ORM)
├── security/             # Groups & Record Rules (RBAC)
├── static/               # Assets, Icons & Screenshots
├── views/                # Kanban, Form, Graph, Pivot & Portal XML
├── report/               # QWeb PDF Templates & Branding
└── __manifest__.py       # Module metadata & dependencies
```
**Carlos Caletti** - ** *Lead Architect & Developer*
