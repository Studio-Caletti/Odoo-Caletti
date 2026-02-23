# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#   
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)

# === CONSTANTES PARA COLORES ===
COLOR_VERDE_COMPLETADO = 10
COLOR_ROJO_VENCIDA = 1
COLOR_AMARILLO_URGENTE = 3
COLOR_GRIS_NORMAL = 7

class TableroTarea(models.Model):
    """
    Modelo principal para la gestión de tareas en Caletti Studio.
    Implementa lógica de seguimiento de progreso, estados de kanban y alertas automáticas.
    """
    _name = 'tablero.tarea'
    _description = 'Tareas de Caletti Studio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_deadline desc, priority desc'

    # --- CAMPOS BÁSICOS ---
    color = fields.Integer(string='ColorIndex')
    name = fields.Char(string='Tarea', required=True, index=True, tracking=True)
    user_id = fields.Many2one(
        'res.users', 
        string='Responsable', 
        default=lambda self: self.env.user,
        index=True,
        tracking=True
    )
    
    # Definición de estados del flujo de trabajo con tracking activo para el Chatter
    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('proceso', 'En Proceso'),
        ('hecho', 'Finalizado')
    ], string='Estado', default='nuevo', tracking=True, required=True)

    description = fields.Text(string='Detalles')
    date_deadline = fields.Date(string='Fecha Límite', tracking=True)

    # --- CAMPOS DE PROGRESO ---
    progress = fields.Float(
        string='Progreso (%)', 
        default=0.0, 
        tracking=True,
        help="Porcentaje de avance de la tarea (0-100)"
    )

    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
        ('4', 'Extra Urgente')
    ], string='Prioridad', default='1')
    
    # completion_status: Indicador visual del semáforo (separado del estado de flujo)
    completion_status = fields.Selection([
        ('normal', 'A tiempo'),
        ('blocked', 'VENCIDA'),
        ('warning', 'PRÓXIMA (2 días)'),
        ('completed', 'COMPLETADA')
    ], string='Estado Visual', compute="_compute_completion_status", store=True, default='normal')

    # Mantener kanban_state para compatibilidad con vistas existentes
    kanban_state = fields.Selection([
        ('normal', 'A tiempo'),
        ('blocked', 'VENCIDA'),
        ('done', 'PRÓXIMA (2 días)'),
        ('completed', 'COMPLETADA')
    ], string='Estado Kanban', compute="_compute_completion_status", store=True, default='normal')

    partner_id = fields.Many2one(
        'res.partner', 
        string='Cliente', 
        tracking=True,
        index=True,
        help="Cliente dueño de este proyecto o tarea"
    )

    # Campos técnicos para cálculos de BI y alertas
    is_overdue = fields.Boolean(string="Vencida", compute="_compute_completion_status", store=True)
    date_started = fields.Datetime(string='Fecha de Inicio', readonly=True)
    date_finished = fields.Datetime(string='Fecha de Finalización', readonly=True)
    duration_days = fields.Float(string='Días de Ejecución', compute='_compute_duration', store=True)

    # --- VALIDACIONES ---
    @api.constrains('progress')
    def _check_progress_range(self):
        """Valida que el progreso esté entre 0 y 100"""
        for record in self:
            if not (0 <= record.progress <= 100):
                raise ValidationError(_("El progreso debe estar entre 0%% y 100%%. Valor actual: %.2f%%") % record.progress)

    @api.constrains('date_deadline')
    def _check_deadline_future(self):
        """Opcional: Advertir si la fecha límite está en el pasado al crear"""
        for record in self:
            if record.date_deadline and record.date_deadline < fields.Date.today():
                # Solo warning, no bloquear
                _logger.warning("Tarea '%s' creada con fecha límite en el pasado: %s", record.name, record.date_deadline)

    # --- LÓGICA DE SEMÁFORO MEJORADA ---
    @api.depends('date_deadline', 'state', 'progress')
    def _compute_completion_status(self):
        """
        Calcula dinámicamente el estado visual del semáforo y la bandera de vencimiento
        basándose en la fecha límite, el estado y el progreso actual.
        """
        today = fields.Date.today()
        for record in self:
            # Lógica prioritaria: Si está terminada o al 100%, se marca como completada
            if record.state == 'hecho' or record.progress >= 100.0:
                record.is_overdue = False
                record.completion_status = 'completed'
                record.kanban_state = 'completed'
            
            # Lógica de tiempos si la tarea sigue activa y tiene fecha límite
            elif record.date_deadline:
                overdue = record.date_deadline < today
                record.is_overdue = overdue
                
                if overdue:
                    record.completion_status = 'blocked'
                    record.kanban_state = 'blocked'
                elif (record.date_deadline - today).days <= 2:
                    record.completion_status = 'warning'
                    record.kanban_state = 'done'  # Para compatibilidad
                else:
                    record.completion_status = 'normal'
                    record.kanban_state = 'normal'
            else:
                record.is_overdue = False
                record.completion_status = 'normal'
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
        _logger.info("Finalizando tarea(s): %s", ', '.join(self.mapped('name')))
        return self.write({'state': 'hecho', 'progress': 100.0})

    def write(self, vals):
        """
        Sobrescritura del método write para capturar fechas de inicio/fin automáticamente
        y registrar mensajes de éxito en el Chatter.
        """
        if 'state' in vals:
            new_state = vals.get('state')
            for record in self:
                # Si pasa a proceso, registramos el inicio
                if new_state == 'proceso' and not record.date_started:
                    vals['date_started'] = fields.Datetime.now()
                    _logger.info("Tarea '%s' iniciada por %s", record.name, self.env.user.name)
                
                # Si pasa a hecho, registramos fin, completamos progreso y cambiamos color
                elif new_state == 'hecho':
                    vals['date_finished'] = fields.Datetime.now()
                    vals['progress'] = 100.0 
                    vals['color'] = COLOR_VERDE_COMPLETADO
                    record.message_post(
                        body=_("✅ ¡Excelente! Esta tarea ha sido finalizada con éxito."),
                        subject=_("Tarea Completada")
                    )
                    _logger.info("Tarea '%s' completada. Duración: %.2f días", record.name, record.duration_days)
        
        # Actualizar color según urgencia si se cambia la deadline
        if 'date_deadline' in vals and 'color' not in vals:
            for record in self:
                if record.state != 'hecho':
                    # Recalcular color según nueva fecha
                    if vals['date_deadline']:
                        days_to_deadline = (fields.Date.from_string(vals['date_deadline']) - fields.Date.today()).days
                        if days_to_deadline < 0:
                            vals['color'] = COLOR_ROJO_VENCIDA
                        elif days_to_deadline <= 2:
                            vals['color'] = COLOR_AMARILLO_URGENTE
                        else:
                            vals['color'] = COLOR_GRIS_NORMAL
        
        return super(TableroTarea, self).write(vals)

    # --- MOTOR DE ALERTAS MEJORADO ---
    def _cron_check_overdue_tasks(self):
        """
        Proceso automático (Cron) que se ejecuta diariamente para:
        1. Refrescar estados de vencimiento.
        2. Enviar notificaciones por correo electrónico a los responsables.
        """
        _logger.info("🔄 Iniciando revisión automática de tareas vencidas...")
        today = fields.Date.today()
        
        # 1. Identificar y actualizar tareas que acaban de vencer
        tasks_to_update = self.search([
            ('state', '!=', 'hecho'),
            ('date_deadline', '<', today),
            ('is_overdue', '=', False)
        ])
        
        if tasks_to_update:
            _logger.info("📋 Actualizando %d tareas que acaban de vencer", len(tasks_to_update))
            # Forzamos el re-cálculo de la lógica visual
            tasks_to_update._compute_completion_status()

        # 2. Localizar la plantilla de correo definida en XML
        template = self.env.ref('tablero_kanban_caletti.email_template_tarea_vencida', raise_if_not_found=False)
        
        if not template:
            _logger.warning("⚠️ Plantilla de correo 'email_template_tarea_vencida' no encontrada")
            return
        
        # 3. Filtrar tareas vencidas no finalizadas para envío de alertas
        overdue_tasks = self.search([
            ('is_overdue', '=', True),
            ('state', '!=', 'hecho'),
            ('progress', '<', 100.0)
        ])
        
        _logger.info("📧 Enviando alertas para %d tareas vencidas", len(overdue_tasks))
        
        for task in overdue_tasks:
            # Registro en el historial y envío de correo electrónico automático
            task.message_post(
                body=_("⚠️ Alerta automática: Tarea vencida. Correo enviado a %s.") % task.user_id.name,
                subject=_("Alerta de Tarea Vencida")
            )
            try:
                template.send_mail(task.id, force_send=True)
                _logger.debug("✉️ Correo enviado para tarea '%s' a %s", task.name, task.user_id.email)
            except Exception as e:
                _logger.error("❌ Error enviando correo para tarea '%s': %s", task.name, str(e))
        
        _logger.info("✅ Revisión de tareas completada")
