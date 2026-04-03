# 🚀 Odoo-Caletti: Advanced Kanban Framework,

# Helpdesk (ticket system)

# Creative Management System

**Framework Modular Extensible para Odoo 17 | Caletti Studio**

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-875A7B.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.0.0-brightgreen.svg)](https://github.com/Studio-Caletti/Odoo-Caletti)

[Español](#español) | [English](#english) | [Italiano](#italiano)

---

## <a name="español"></a> 🇪🇸 Español <img src="https://flagcdn.com/w20/es.png" width="20">

### 1. 📄 Descripción del Ecosistema V4

**Odoo-Caletti V4** es una plataforma de gestión de alto rendimiento diseñada sobre **Odoo 17 Community**. Su esencia no es la de un software cerrado, sino la de un ecosistema vivo compuesto por un **Núcleo Core** de tarjetas dinámicas que orquesta el quehacer cotidiano empresarial.

A diferencia de las soluciones aisladas (hojas de cálculo o apps simples), este ecosistema ofrece el poder de un **ERP (Enterprise Resource Planning)**. Esto significa que mientras nuestras verticales resuelven nichos específicos como el **Auxiliar de Soporte (Helpdesk)** o el **Sistema de Gestión Creativa (SGC)**, el usuario mantiene la puerta abierta para integrar módulos nativos de Odoo como **CRM, Calendario, Pagos Electrónicos, Recursos Humanos o Facturación**, todo bajo una misma base de datos y una sola interfaz.

### 2. 📌 Pilares de la Arquitectura Caletti

- **Core Kanban V3 (La Columna Vertebral)**: Infraestructura de Business Intelligence que gestiona prioridades y tiempos. Es la base donde vive la operación administrativa general.

- **Helpdesk Vertical**: Sistema de ticketing que transforma las solicitudes de soporte en flujos de trabajo con tiempos de respuesta (SLA) garantizados.

- **Sistema de Gestión Creativa (SGC)**: Diseñado para **Despachos de Artes Gráficas**, agencias de medios y estudios digitales. Administra desde el Brief (directiva de diseño) hasta los entregables finales, asegurando rentabilidad y acuerdos claros.

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

### 🎯 Casos de Uso y próximos horizontes

- **Agencias creativas**: Seguimiento de proyectos con clientes en tiempo real.

- **Equipos de soporte técnico**: HelpDesk con tickets aislados por cliente.

- **Consultorías**: Reportes BI para medir productividad y tiempos de entrega.

- **Despachos de Artes Gráficas y Agencias**: Gestión de campañas, impresos y medios digitales con validación del cliente.

- **Soporte Técnico**: Resolución de incidencias con métricas de desempeño.

- **Futuro: Vertical Bienes Raíces**: Próximamente, un sistema para Venta, Renta y Administración de propiedades, migrando a los profesionales del sector de las hojas de cálculo hacia la potencia de un ERP especializado.

### 

---

## <a name="english"></a> 🇺🇸 English <img src="https://flagcdn.com/w20/us.png" width="20">

### 1. 📄 Ecosystem V4 Description

**Odoo-Caletti V4** is a high-performance management ecosystem built on **Odoo 17 Community**. More than just specialized modules, it provides the full power of an **ERP**. While our verticals solve specific niches like **Helpdesk** or **Creative Management (CMS)**, users can seamlessly integrate Odoo native apps such as **CRM, Accounting, Web Design, and HR**.

### 2. 📌Strategic Pillars

- **Core Engine**: The foundation for general business tasks and BI.

- **Creative Vertical**: Tailored for **Graphic Arts Studios** and Digital Agencies. Handles Briefs, deliverables, and revision rounds.

- **The Chatter Advantage**: All communications, files, and logs are centralized within each record, eliminating scattered emails and ensuring total transparency.

### 3. 🛠️Scalability

Designed to move businesses away from fragmented spreadsheets into a unified environment. Start with creative project management today and scale to full enterprise resource planning tomorrow.

---

## <a name="italiano"></a> 🇮🇹 Italiano <img src="https://flagcdn.com/w20/it.png" width="20">

### 📄 Descrizione dell'Ecosistema V4

**Odoo-Caletti V4** è una piattaforma di gestione avanzata basata su **Odoo 17 Community**. Offre la potenza di un **ERP** completo, permettendo di integrare moduli di **CRM, Contabilità e Risorse Umane** con le nostre verticali specializzate in **Helpdesk** e **Gestione Creativa**.

### 📌 Pilastri Strategici

- **Nucleo Core**: Gestione amministrativa e BI.

- **SGC (Sistema di Gestione Creativa)**: Ideale per **Studi di Arti Grafiche**, gestisce Brief, revisioni e deliverable.

- **Potenza del Chatter**: Comunicazione centralizzata e contestuale per ogni attività, garantendo che nessuna decisione venga persa.

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

### 📈 Evolución del Ecosistema: Expansión Modular Realizada

La V4 marca el nacimiento de una arquitectura que no compite con Odoo, sino que lo potencia para sectores específicos:

1. **Core**: El cimiento operativo.

2. **Helpdesk**: Excelencia en atención al cliente.

3. **Creative**: El estándar para Artes Gráficas y Agencias.

4. **Próximamente**: Real Estate (Bienes Raíces).

# 

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
├── tablero_kanban_caletti/          # 🧠 MÓDULO BASE
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
│   ├── __init__.py
│   └── __manifest__.py
│
├── tablero_kanban_helpdesk/         # 🎧 VERTICAL HELPDESK
│   ├── controllers/
│   │   └── helpdesk_portal.py       # Portal routes (tickets)
│   ├── data/
│   │   └── helpdesk_data.xml        # Sequence, Template confirmación
│   ├── models/
│   │   └── tablero_ticket.py        # Herencia + campos helpdesk
│   ├── views/
│   │   ├── helpdesk_views.xml       # Vistas backend
│   │   └── portal_helpdesk_views.xml # Vistas portal
│   ├── __init__.py
│   └── __manifest__.py
│
├── caletti_creative/                        #🎨 VERTICAL CREATIVA
│   ├── models/
│   │   ├── init__.py
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
│   │   ├── creative_data.xml                # Sequence, Template confirmación
│   ├── init__.py
│   └── manifest__.py
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