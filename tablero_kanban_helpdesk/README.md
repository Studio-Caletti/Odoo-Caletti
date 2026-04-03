# 🎧 Odoo-Caletti: Vertical Helpdesk & Ticketing System

**Módulo de gestión de incidencias y soporte técnico para Odoo 17.**

---

## 📄 Descripción
Este módulo extiende el **Core V3** para proporcionar una solución completa de soporte post-venta. Transforma las tareas simples en **Tickets de Soporte** con trazabilidad de cumplimiento, métricas de respuesta y automatización de canales.

## 🚀 Funcionalidades Principales
* **🔢 Secuenciación Automática:** Generación de folios únicos (ej. `TK-00001`) para cada incidencia.
* **📧 Omnicanalidad (Alias):** Integración nativa con el alias `soporte@caletti.com.mx`. Los correos entrantes se convierten en tickets instantáneamente.
* **⏱️ Gestión de SLA:** Cálculo automático de tiempos de respuesta y resolución para garantizar el estándar de servicio.
* **✉️ Notificaciones de Marca:** Plantillas de correo profesionales que confirman al cliente la recepción y el estado de su solicitud.

## 🛠️ Especificaciones de Implementación
* **Modelo base:** Hereda de `tablero.tarea`.
* **Seguridad:** Implementa grupos de `Helpdesk User` y `Helpdesk Manager` para el control de acceso a tickets sensibles.
* **Portal:** El cliente puede consultar el historial de sus tickets y el estado de resolución en tiempo real desde su área personal.

---
[⬅️ Volver al Ecosistema Principal](../README.md)