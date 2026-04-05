# ⚙️ Guía de Instalación y Configuración: 
##  Odoo-Caletti V4

Esta guía detalla los pasos críticos para desplegar el Ecosistema Caletti V4 en un entorno de **Odoo 17 Community**. Siga el orden estricto para garantizar la integridad de las dependencias.

---

## 1. Requisitos Previos

* **Odoo 17.0 Community Edition** (Instalado y funcional).
* **Python 3.10+**.
* **Dependencias de Python adicionales:**

  ```bash
  pip install markupsafe  # Para el renderizado de HTML en el Chatter
  ````

## 2. 📦 Secuencia de Instalación de Módulos
Debido a la arquitectura de herencia, el orden de carga en la base de datos es mandatorio:

1  **tablero_kanban_caletti**: Instalar primero. Es el Core Engine que crea el modelo tablero.tarea.

2 **tablero_kanban_helpdesk**: (Opcional) Instalar para habilitar el flujo de soporte técnico.

3 **caletti_creative**: (Opcional) Instalar para habilitar el Sistema de Gestión Creativa (SGC).

  
## 3. ✉️ Configuración de Canales de Correo (Crítico)

Para que la creación automática de Tickets y Proyectos funcione, debe configurar los Alias de Correo:

1. **Vaya a Ajustes > Técnico > Canales de Correo > Alias**.

2. Configure los siguientes alias vinculados a sus respectivos modelos:

- **Alias**: soporte -> Modelo: tablero.tarea (Filtrado por es_ticket=True).

- **Alias**: creativos -> Modelo: tablero.tarea (Filtrado por es_proyecto_creativo=True).

3. Asegúrese de tener un Servidor de Correo Entrante **(IMAP/POP)** configurado y activo.

## 4. 🏢 Personalización de Branding y Salida (SMTP)
Para que los correos de confirmación tengan la identidad de **LOGOTIPO**:

1. **Logotipo de Correo**: Cargue el logotipo de la empresa en Ajustes > Compañías. Este logo se inyectará automáticamente en los QWeb Templates de las verticales.

2. **Servidor de Salida**: Configure su servidor SMTP en Ajustes > Técnico > Servidores de Correo Saliente.

3. **Firma del Chatter**: Configure la firma de los usuarios en su perfil para que la comunicación en el Chatter sea profesional.

## 5. 🔒 Permisos y Seguridad
El ecosistema incluye grupos de seguridad predefinidos. Asigne los roles correctamente en la ficha del usuario:

- Caletti Core / Usuario: Acceso a tareas generales.

- Helpdesk / Manager: Gestión total de tickets y SLAs.

- Creative / Director: Acceso a Briefs, presupuestos y entregables del SGC.

- Portal: Asegúrese de que sus clientes tengan el tipo de usuario "Portal" para acceder a las vistas externas.

## 6.  🛠️ Troubleshooting Común

¿Los correos no crean tareas? Verifique que el remitente no esté en la lista negra (Blacklist) y que el Alias tenga permisos para "Todos" (Policy: everyone).


¿No se ven los colores en el Kanban? Actualice la lista de módulos y asegúrese de que el campo color no esté oculto por algún otro módulo de terceros.

---

**Carlos Caletti** -  *Lead Architect & Developer* 2026
---
<p align="left">
  <a href="https://studio.caletti.com.mx">
    <img src="https://img.shields.io/badge/Visitanos-CALETII%20STUDIO-blue?style=for-the-badge&logo=odoo&logoColor=%23714B67&logoSize=auto&labelColor=lightgray&color=8A2BE2" />
  </a>
</p>
