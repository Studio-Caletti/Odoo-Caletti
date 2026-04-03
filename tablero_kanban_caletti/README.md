# 🧠 Odoo-Caletti: Core Kanban Engine (V3)

**El motor de Business Intelligence y gestión de estados para el ecosistema Caletti.**

---

## 📄 Descripción
El **Core Engine** es el pilar fundamental de nuestra arquitectura modular en Odoo 17. No es simplemente un tablero de tareas; es una infraestructura diseñada para centralizar la lógica de **SLA, estados dinámicos y comunicación contextual (Chatter)**. 

Al ser un "Core", este módulo define el modelo base `tablero.tarea`, el cual es heredado y extendido por todas nuestras verticales (Helpdesk, Creative, Real Estate), garantizando una integridad de datos total en todo el ERP.

## 🚀 Funcionalidades del Motor (Engine)
* **⚡ Gestión de Estados Robusta:** Lógica de transiciones que dispara eventos automáticos de seguimiento y trazabilidad temporal.
* **📊 Business Intelligence Nativo:** Campos calculados para medir la eficiencia, prioridades y tiempos de respuesta directamente en la base del modelo.
* **🛡️ Arquitectura de Seguridad:** Definición de grupos jerárquicos (User, Manager, Admin) y reglas de registro (`ir.rule`) que las verticales heredan automáticamente.
* **🎨 UI/UX Kanban Avanzada:** Vistas extendidas con headers dinámicos y decoradores de colores basados en la criticidad de la tarea.

## 🛠️ Especificaciones Técnicas (Senior Level)
* **Clase Maestra:** `tablero.tarea` (Hereda de `mail.thread` y `mail.activity.mixin`).
* **Lógica de Herencia:** Diseñado para ser extendido mediante `_inherit`. Proporciona los "ganchos" (hooks) necesarios para que las verticales añadan campos sin romper el flujo base.
* **Optimización:** Uso intensivo de `api.depends` no almacenados para cálculos de tiempo real sin penalizar el rendimiento de la base de datos.
* **Portal Base:** Define la estructura de rutas `/my/tareas` que sirve como plantilla para los portales especializados.

---
[⬅️ Volver al Ecosistema Principal](../README.md)