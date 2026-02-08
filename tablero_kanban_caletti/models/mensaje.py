# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#   
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

from odoo import models, fields, api
from datetime import date, datetime

class TableroTarea(models.Model):
    """
    Modelo principal para la gestión de tareas en Caletti Studio.
    Implementa lógica de seguimiento de progreso, estados de kanban y alertas automáticas.
    """
    _name = 'tablero.tarea'
    _description = 'Tareas de Caletti Studio'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Herencia para mensajería y actividades

    # --- CAMPOS BÁSICOS ---
    color = fields.Integer(string='ColorIndex') # Para la gestión de colores en la vista Kanban
    name = fields.Char(string='Tarea', required=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    
    # Definición de estados del flujo de trabajo con tracking activo para el Chatter
    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('proceso', 'En Proceso'),
        ('hecho', 'Finalizado')
    ], string='Estado', default='nuevo', tracking=True)

    description = fields.Text(string='Detalles')
    date_deadline = fields.Date(string='Fecha Límite', tracking=True)

    # --- NUEVOS CAMPOS V2 (NÚCLEO ROBUSTO) ---
    # Campo para medir el avance porcentual de cada tarea
    progress = fields.Float(string='Progreso (%)', default=0.0, tracking=True)
    # -----------------------------------------

    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
        ('4', 'Extra Urgente')
    ], string='Prioridad', default='1')
    
    # kanban_state: Controla el semáforo visual en el tablero (gris, rojo, amarillo, verde)
    kanban_state = fields.Selection([
        ('normal', 'A tiempo'),
        ('blocked', 'VENCIDA'),
        ('done', 'PRÓXIMA (2 días)'),
        ('completed', 'COMPLETADA') # Identificador para tareas finalizadas con éxito
    ], string='Estado Kanban', compute="_compute_kanban_state", store=True, default='normal')

    partner_id = fields.Many2one(
        'res.partner', 
        string='Cliente', 
        tracking=True,
        help="Cliente dueño de este proyecto o tarea"
    )

    # Campos técnicos para cálculos de BI y alertas
    is_overdue = fields.Boolean(string="Vencida", compute="_compute_kanban_state", store=True)
    date_started = fields.Datetime(string='Fecha de Inicio', readonly=True)
    date_finished = fields.Datetime(string='Fecha de Finalización', readonly=True)
    duration_days = fields.Float(string='Días de Ejecución', compute='_compute_duration', store=True)

    # --- LÓGICA DE SEMÁFORO MEJORADA V2 ---
    @api.depends('date_deadline', 'state', 'progress')
    def _compute_kanban_state(self):
        """
        Calcula dinámicamente el estado del semáforo y la bandera de vencimiento
        basándose en la fecha límite, el estado y el progreso actual.
        """
        today = fields.Date.today()
        for record in self:
            # Lógica prioritaria: Si está terminada o al 100%, se marca como completada
            if record.state == 'hecho' or record.progress >= 100.0:
                record.is_overdue = False
                record.kanban_state = 'completed'
            
            # Lógica de tiempos si la tarea sigue activa y tiene fecha límite
            elif record.date_deadline:
                overdue = record.date_deadline < today
                record.is_overdue = overdue
                
                if overdue:
                    record.kanban_state = 'blocked' # Color Rojo
                elif (record.date_deadline - today).days <= 2:
                    record.kanban_state = 'done' # Color Amarillo/Naranja
                else:
                    record.kanban_state = 'normal' # Color Gris/Verde
            else:
                record.is_overdue = False
                record.kanban_state = 'normal'

    @api.depends('date_started', 'date_finished')
    def _compute_duration(self):
        """
        Calcula la duración total de la tarea en días y fracciones
        restando la fecha de inicio de la fecha de finalización.
        """
        for record in self:
            if record.date_started and record.date_finished:
                diff = record.date_finished - record.date_started
                # Conversión de segundos a fracción de día (86400 seg = 1 día)
                record.duration_days = diff.days + (diff.seconds / 86400.0)
            else:
                record.duration_days = 0

    def action_finalizar_tarea(self):
        """ Acción manual para cerrar la tarea, forzando el progreso al 100% """
        return self.write({'state': 'hecho', 'progress': 100.0})

    def write(self, vals):
        """
        Sobrescritura del método write para capturar fechas de inicio/fin automáticamente
        y registrar mensajes de éxito en el Chatter.
        """
        if 'state' in vals:
            new_state = vals.get('state')
            # Si pasa a proceso, registramos el inicio
            if new_state == 'proceso' and not self.date_started:
                vals['date_started'] = fields.Datetime.now()
            # Si pasa a hecho, registramos fin, completamos progreso y cambiamos color a verde
            elif new_state == 'hecho':
                vals['date_finished'] = fields.Datetime.now()
                vals['progress'] = 100.0 
                vals['color'] = 10 # Código de color verde en Odoo
                for record in self:
                    record.message_post(body="✅ ¡Excelente! Esta tarea ha sido finalizada con éxito.")
        return super(TableroTarea, self).write(vals)

    # --- MOTOR DE ALERTAS MEJORADO ---
    def _cron_check_overdue_tasks(self):
        """
        Proceso automático (Cron) que se ejecuta diariamente para:
        1. Refrescar estados de vencimiento.
        2. Enviar notificaciones por correo electrónico a los responsables.
        """
        today = fields.Date.today()
        
        # 1. Identificar y actualizar tareas que acaban de vencer
        tasks_to_update = self.search([
            ('state', '!=', 'hecho'),
            ('date_deadline', '<', today),
            ('is_overdue', '=', False)
        ])
        if tasks_to_update:
            # Forzamos el re-cálculo de la lógica visual
            tasks_to_update._compute_kanban_state()

        # 2. Localizar la plantilla de correo definida en XML
        template = self.env.ref('tablero_kanban.email_template_tarea_vencida', raise_if_not_found=False)
        
        # 3. Filtrar tareas vencidas no finalizadas para envío de alertas
        overdue_tasks = self.search([
            ('is_overdue', '=', True),
            ('state', '!=', 'hecho'),
            ('progress', '<', 100.0)
        ])
        
        for task in overdue_tasks:
            # Registro en el historial y envío de correo electrónico automático
            task.message_post(body=f"⚠️ Alerta automática: Tarea vencida. Correo enviado a {task.user_id.name}.")
            if template:
                template.send_mail(task.id, force_send=True)