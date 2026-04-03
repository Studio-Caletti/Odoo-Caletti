# 🛠️ Odoo-Caletti V4: Notas Técnicas de Arquitectura

Este documento detalla las decisiones de ingeniería, patrones de diseño y lógica de negocio avanzada implementada en el Ecosistema Caletti V4 sobre Odoo 17 Community.

---

## 1. Estrategia de Herencia (Multi-level Inheritance)
El ecosistema utiliza un patrón de **herencia de clase (`_inherit`)** para extender el modelo base `tablero.tarea`. 

* **Core (`tablero_kanban_caletti`):** Define el modelo abstracto funcional. Implementa `mail.thread` y `mail.activity.mixin` para centralizar la comunicación.
* **Verticales (`helpdesk`, `creative`):** Extienden el modelo base añadiendo campos específicos de dominio (`ticket_ref`, `brief_id`) sin romper la integridad del motor de BI del Core.
    * *Decisión Técnica:* Se evitó `_inherits` (delegación) para mantener una tabla única de base de datos, optimizando el rendimiento de las consultas SQL en tableros Kanban de alto volumen.

## 2. Motor de Estados y Business Intelligence (BI)
La criticidad y el seguimiento de tiempos se gestionan mediante campos calculados y decoradores:

* **Cálculo de SLAs:** Implementación de lógica en Python para determinar la diferencia entre `create_date` y `date_closed`, considerando el calendario laboral del equipo.
* **Decoradores `@api.depends`:** Se utilizan para la actualización en tiempo real de los colores del Kanban, basados en la proximidad del `date_deadline` y el `priority`.
* **Validaciones:** Uso de `@api.constrains` para asegurar que el progreso (`progress`) y los estados de los entregables mantengan coherencia lógica (ej. no finalizar tarea con entregables pendientes).

## 3. Gestión de Contexto y Seguridad (ORM)
Se han implementado Reglas de Registro (`ir.rule`) robustas para garantizar el aislamiento de datos entre verticales:

* **Aislamiento de Departamentos:** Los usuarios del grupo `Helpdesk` no tienen visibilidad sobre los objetos de `Creative` a menos que compartan el mismo `partner_id`.
* **Uso de `sudo()`:** En el portal de co-creación, se utiliza el escalado de privilegios controlado para permitir que clientes (usuarios portal) firmen Briefs y suban archivos adjuntos, manteniendo el principio de "mínimo privilegio".

## 4. Automatización de Canales (Email Ingestion)
El sistema utiliza el motor de `mail.gateway` de Odoo:
* **Message New:** Sobrecarga del método `message_new` en las verticales para asignar automáticamente el tipo de ticket o categoría creativa basándose en el alias de correo receptor (`soporte@` vs `creativos@`).
* **Thread ID:** Mantenimiento estricto del ID del hilo para asegurar que todas las respuestas de clientes se mantengan dentro del **Chatter** correspondiente, evitando la duplicidad de registros.

## 5. UI/UX Avanzado (QWeb & JavaScript)
* **Portal de Cliente:** Uso de plantillas QWeb con Bootstrap 5 para una interfaz responsive donde el cliente interactúa con el SGC.
* **Kanban Decorators:** Personalización de la vista Kanban mediante el atributo `decoration-info`, `decoration-danger`, etc., vinculado a campos técnicos del Core para una lectura rápida de la carga de trabajo.

---

## 🚀 Guía de Mantenimiento para Desarrolladores
1.  **Migraciones:** Siempre verificar la coherencia de los campos `selection` al añadir nuevos estados en las verticales.
2.  **Logs:** Utilizar el logger integrado (`_logger`) para trazar errores en el procesamiento de correos entrantes.
3.  **Tests:** Se recomienda ejecutar `odoo-bin` con el flag `-t` para validar los flujos de aprobación del portal tras cada actualización del Core.

---

**Carlos Caletti** -  *Lead Architect & Developer* 2026
---
<p align="left">
  <a href="https://studio.caletti.com.mx">
    <img src="https://img.shields.io/badge/Visitanos-CALETII%20STUDIO-blue?style=for-the-badge&logo=odoo&logoColor=%23714B67&logoSize=auto&labelColor=lightgray&color=8A2BE2" />
  </a>
</p>