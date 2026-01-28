# Odoo-Caletti: Advanced Kanban Framework & Customer Portal 🚀

[Español](#español) | [English](#english) | [Italiano](#italiano)

---

## <a name="español"></a> 🇪🇸 Español

### 📄 Descripción

Originalente diseñado para la gestión visual de tareas y coordinación de flujos de trabajo internos de Caletti Studio.

Este módulo de alto rendimiento para **Odoo 17** está diseñado para transformar la gestión de tareas en una experiencia de Business Intelligence. Concevido como un framework extensible para agencias creativas, integra una comunicación impecable entre el Backend administrativo y un Portal de Cliente personalizado de alta gama.

### 📌 Características de Vanguardia
- **Sistema "Visual Awareness"**: Implementación de Ribbons dinámicos y bordes de color (Semáforos) basados en el estado de urgencia y campos computados (`is_overdue`).
- **Portal de Cliente Premium**: Interfaz dedicada en `/my/tareas` con barras de progreso animadas, validación de acceso de seguridad (Record Rules) y feedback de retrasos en tiempo real.
- **Business Intelligence (BI)**: Vistas de Gráfico (Graph) y Pivote integradas nativamente para el análisis de carga de trabajo por colaborador y métricas de ejecución (`duration_days`).
- **Comunicación Proactiva**: Integración total con el Chatter de Odoo, gestión de pestañas para una trazabilidad total de la comunicación, y sistema de notificaciones automáticas vía email para hitos críticos y tareas vencidas.

### 🛠️ Especificaciones Técnicas (Arquitectura)
- **Extensión del Core**: Herencia avanzada de `portal.portal_my_home` y controladores web especializados.
- **Lógica de Negocio**: Implementación robusta de métodos ORM, decoradores `@api.depends` y lógica de validación de fechas.
- **Seguridad (RBAC)**: Reglas de registro (Record Rules) que garantizan el aislamiento de datos por cliente y jerarquía interna (User, Manager, Admin, Client).

---

## <a name="english"></a> 🇺🇸 English

### 📄 Description
Originally designed for the visual management of tasks and coordination of internal workflows at Caletti Studio.

This high-performance module for **Odoo 17** is designed to transform task management into a Business Intelligence experience. Conceived as an extensible framework for creative agencies, it integrates seamless communication between the administrative backend and a customized, high-end Client Portal.

### 📌 Cutting-Edge Features
- **Visual Awareness System**: Implementation of dynamic Ribbons and color-coded borders (Traffic Light system) based on urgency and computed fields (`is_overdue`).
- **Premium Customer Portal**: Dedicated UI at `/my/tasks` featuring animated progress bars, security access validation, and real-time delay feedback.
- **Business Intelligence (BI)**: Native Graph and Pivot views for workload analysis per collaborator and execution lead times (`duration_days`).
- **Proactive Communication**: Full integration with Odoo Chatter and automated email notification system for critical milestones and overdue tasks.

### 🛠️ Technical Specifications
- **Core Extension**: Advanced inheritance of `portal.portal_my_home` and specialized web controllers.
- **Business Logic**: Robust ORM methods, `@api.depends` decorators, and date validation logic.
- **Security (RBAC)**: Strict Record Rules ensuring data isolation per client and internal hierarchy (User, Manager, Admin).


---

## <a name="italiano"></a> 🇮🇹 Italiano

### 📄 Descrizione

Originariamente progettato per la gestione visiva delle attività e il coordinamento dei flussi di lavoro interni presso Caletti Studio.

Questo modulo ad alte prestazioni per **Odoo 17** è progettato per trasformare la gestione delle attività in un'esperienza di Business Intelligence. Concepito come un framework estensibile per le agenzie creative, integra una comunicazione fluida tra il backend amministrativo e un portale clienti personalizzato e di fascia alta.

### 📌 Caratteristiche Principali
- **Visual Awareness System**: Uso di Ribbon dinamici e bordi colorati (sistema a semaforo) basati sull'urgenza e campi calcolati (`is_overdue`).
- **Portale Clienti Premium**: Interfaccia dedicata su `/my/tasks` con barre di progresso animate, validazione degli accessi e feedback sui ritardi in tempo reale.
- **Business Intelligence (BI)**: Viste Grafico e Pivot integrate nativamente per l'analisi del carico di lavoro per collaboratore e tempi di esecuzione (`duration_days`).
- **Comunicazione Proattiva**: Integrazione totale con l'Odoo Chatter e sistema di notifiche email automatiche per le scadenze critiche.

### 🛠️ Specifiche Tecniche
- **Estensione del Core**: Ereditarietà avanzata di `portal.portal_my_home` e controller web specializzati.
- **Logica di Business**: Metodi ORM robusti, decoratori `@api.depends` e logica di convalida delle date.
- **Sicurezza (RBAC)**: Record Rules rigorose che garantiscono l'isolamento dei dati per cliente e gerarchia interna (User, Manager, Admin, Client).

---
## 🛠️ Instalación / Installation / Installazione

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

"Check our data/ir_cron.xml to see how automated alerts are scheduled."
---

### 📂 Repository Structure
```text
tablero_kanban/
├── controllers/          # Portal routing & custom logic
├── models/               # Task & Project definitions (ORM)
├── security/             # Groups & Record Rules (RBAC)
├── static/               # Assets (Icons, Description, Screenshots)
├── views/                # Kanban, Form, Tree, Graph, Pivot & Portal XML
└── __manifest__.py       # Module metadata & dependencies

```
**Carlos Caletti** - *Lead Architect & Developer*

