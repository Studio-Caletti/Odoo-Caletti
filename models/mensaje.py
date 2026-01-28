from odoo import models, fields, api
from datetime import date, datetime

class TableroTarea(models.Model):
    _name = 'tablero.tarea'
    _description = 'Tareas de Caletti Studio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    color = fields.Integer(string='ColorIndex')
    name = fields.Char(string='Tarea', required=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    
    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('proceso', 'En Proceso'),
        ('hecho', 'Finalizado')
    ], string='Estado', default='nuevo', tracking=True)

    description = fields.Text(string='Detalles')
    date_deadline = fields.Date(string='Fecha Límite', tracking=True)

    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
        ('4', 'Extra Urgente')
    ], string='Prioridad', default='1')
    
    # kanban_state: normal (gris/verde), blocked (rojo), done (amarillo)
    kanban_state = fields.Selection([
        ('normal', 'A tiempo'),
        ('blocked', 'VENCIDA'),
        ('done', 'PRÓXIMA (2 días)')
    ], string='Estado Kanban', compute="_compute_kanban_state", store=True, default='normal')

    partner_id = fields.Many2one(
        'res.partner', 
        string='Cliente', 
        tracking=True,
        help="Cliente dueño de este proyecto o tarea"
    )

    is_overdue = fields.Boolean(string="Vencida", compute="_compute_kanban_state", store=True)
    date_started = fields.Datetime(string='Fecha de Inicio', readonly=True)
    date_finished = fields.Datetime(string='Fecha de Finalización', readonly=True)
    duration_days = fields.Float(string='Días de Ejecución', compute='_compute_duration', store=True)

    @api.depends('date_deadline', 'state')
    def _compute_kanban_state(self):
        # Usamos fields.Date.today() que es la forma nativa de Odoo
        today = fields.Date.today()
        for record in self:
            if record.date_deadline and record.state != 'hecho':
                overdue = record.date_deadline < today
                record.is_overdue = overdue
                
                if overdue:
                    record.kanban_state = 'blocked'
                elif (record.date_deadline - today).days <= 2:
                    record.kanban_state = 'done'
                else:
                    record.kanban_state = 'normal'
            else:
                record.is_overdue = False
                record.kanban_state = 'normal'

    @api.depends('date_started', 'date_finished')
    def _compute_duration(self):
        for record in self:
            if record.date_started and record.date_finished:
                diff = record.date_finished - record.date_started
                record.duration_days = diff.days + (diff.seconds / 86400.0)
            else:
                record.duration_days = 0

    def action_finalizar_tarea(self):
        return self.write({'state': 'hecho'})

    def write(self, vals):
        if 'state' in vals:
            new_state = vals.get('state')
            if new_state == 'proceso' and not self.date_started:
                vals['date_started'] = fields.Datetime.now()
            elif new_state == 'hecho':
                vals['date_finished'] = fields.Datetime.now()
                vals['color'] = 10 # Verde Caletti
                for record in self:
                    record.message_post(body="✅ ¡Excelente! Esta tarea ha sido finalizada con éxito.")
        return super(TableroTarea, self).write(vals)

    # --- MOTOR DE ALERTAS MEJORADO ---
    def _cron_check_overdue_tasks(self):
        """Función que ejecuta el ir.cron diariamente"""
        today = fields.Date.today()
        
        # 1. Forzamos la actualización de is_overdue para las tareas que acaban de vencer
        # Esto soluciona el problema de que el campo está 'stale' (viejo) en la DB
        tasks_to_update = self.search([
            ('state', '!=', 'hecho'),
            ('date_deadline', '<', today),
            ('is_overdue', '=', False)
        ])
        if tasks_to_update:
            tasks_to_update._compute_kanban_state()

        # 2. Buscamos la plantilla
        template = self.env.ref('tablero_kanban.email_template_tarea_vencida', raise_if_not_found=False)
        
        # 3. Buscamos tareas que ESTÉN vencidas (ahora sí actualizado) y no finalizadas
        overdue_tasks = self.search([
            ('is_overdue', '=', True),
            ('state', '!=', 'hecho')
        ])
        
        for task in overdue_tasks:
            # Dejamos evidencia en el chatter
            task.message_post(body=f"⚠️ Alerta automática: Tarea vencida. Correo enviado a {task.user_id.name}.")
            # Enviamos el correo corporativo
            if template:
                template.send_mail(task.id, force_send=True)