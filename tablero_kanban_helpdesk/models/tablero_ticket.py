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
import logging

_logger = logging.getLogger(__name__)

class TableroTarea(models.Model):
    _inherit = 'tablero.tarea'
    
    # === CAMPOS DE HELPDESK ===
    es_ticket = fields.Boolean(
        string="Es Ticket de Soporte", 
        default=False,
        help="Marca esta tarea como un ticket de soporte técnico"
    )
    
    tipo_ticket = fields.Selection([
        ('soporte', 'Soporte Técnico'),
        ('facturacion', 'Facturación'),
        ('mejora', 'Solicitud de Mejora'),
        ('error', 'Reporte de Error'),
        ('consulta', 'Consulta General')
    ], string="Tipo de Ticket", tracking=True)

    prioridad_ticket = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Media'),
        ('2', 'Alta'),
        ('3', 'Crítica')
    ], string="Prioridad del Ticket", default='1', tracking=True)

    ticket_ref = fields.Char(
        string="Referencia Ticket", 
        readonly=True,
        copy=False,
        help="Número de referencia único del ticket"
    )
    
    ticket_email = fields.Char(
        string="Email del Solicitante",
        help="Email desde donde se creó el ticket"
    )
    
    date_first_response = fields.Datetime(
        string="Primera Respuesta",
        readonly=True,
        help="Fecha de la primera respuesta al ticket"
    )
    
    sla_hours = fields.Float(
        string="SLA (Horas)",
        compute="_compute_sla_hours",
        store=True,
        help="Horas transcurridas hasta la primera respuesta"
    )

    @api.depends('create_date', 'date_first_response')
    def _compute_sla_hours(self):
        """Calcula el tiempo de primera respuesta en horas"""
        for ticket in self:
            if ticket.create_date and ticket.date_first_response:
                diff = ticket.date_first_response - ticket.create_date
                ticket.sla_hours = diff.total_seconds() / 3600.0
            else:
                ticket.sla_hours = 0.0

    @api.model
    def create(self, vals):
        """
        Override para generar referencia de ticket automáticamente
        y enviar email de confirmación
        """
        # 🔥 GENERAR SECUENCIA SI ES TICKET
        if vals.get('es_ticket') and not vals.get('ticket_ref'):
            # Verificar que la secuencia exista
            sequence = self.env['ir.sequence'].search([('code', '=', 'tablero.ticket')], limit=1)
            if not sequence:
                # Crear secuencia si no existe (failsafe)
                sequence = self.env['ir.sequence'].create({
                    'name': 'Ticket Referencia',
                    'code': 'tablero.ticket',
                    'prefix': 'TK-',
                    'padding': 5,
                    'number_increment': 1,
                    'number_next': 1,
                })
                _logger.info("✅ Secuencia de tickets creada automáticamente")
            
            # Generar referencia única
            vals['ticket_ref'] = sequence.next_by_code('tablero.ticket')
            _logger.info("🎫 Ticket ref generada: %s", vals['ticket_ref'])
            
            # Si no tiene tipo, asignar 'consulta' por defecto
            if not vals.get('tipo_ticket'):
                vals['tipo_ticket'] = 'consulta'
        
        # Crear el ticket/tarea
        ticket = super(TableroTarea, self).create(vals)
        
        # ✉️ ENVIAR EMAIL DE CONFIRMACIÓN AUTOMÁTICAMENTE
        if ticket.es_ticket and ticket.ticket_ref and (ticket.partner_id or ticket.ticket_email):
            try:
                template = self.env.ref(
                    'tablero_kanban_helpdesk.email_template_ticket_confirmacion',
                    raise_if_not_found=False
                )
                if template:
                    template.send_mail(ticket.id, force_send=True)
                    _logger.info("✉️ Email de confirmación enviado para ticket %s a %s", 
                               ticket.ticket_ref, 
                               ticket.partner_id.email if ticket.partner_id else ticket.ticket_email)
                else:
                    _logger.warning("⚠️ Template de confirmación no encontrado")
            except Exception as e:
                _logger.error("❌ Error enviando email para ticket %s: %s", 
                             ticket.ticket_ref, str(e))
        else:
            # Logging para debugging
            if ticket.es_ticket and not ticket.ticket_ref:
                _logger.warning("⚠️ Ticket creado sin referencia: ID %s", ticket.id)
            if ticket.es_ticket and not (ticket.partner_id or ticket.ticket_email):
                _logger.info("ℹ️ Ticket %s sin cliente/email - no se envía confirmación", 
                           ticket.ticket_ref or ticket.id)
        
        return ticket

    def write(self, vals):
        """
        Override para manejar cuando se convierte una tarea en ticket
        y para capturar cambios importantes
        """
        # 🔄 SI SE MARCA COMO TICKET DESPUÉS DE CREAR
        if vals.get('es_ticket'):
            for record in self:
                if not record.ticket_ref:
                    # Generar referencia ahora
                    ticket_ref = self.env['ir.sequence'].next_by_code('tablero.ticket')
                    vals['ticket_ref'] = ticket_ref
                    _logger.info("🎫 Ticket ref generada al convertir tarea %s: %s", record.id, ticket_ref)
                    
                    # Si no tiene tipo, asignar consulta
                    if not vals.get('tipo_ticket') and not record.tipo_ticket:
                        vals['tipo_ticket'] = 'consulta'
        
        # Ejecutar el write original
        result = super(TableroTarea, self).write(vals)
        
        # ✉️ SI SE ACABA DE MARCAR COMO TICKET, ENVIAR EMAIL
        if vals.get('es_ticket'):
            for record in self:
                # Solo enviar si tiene referencia y cliente
                if record.ticket_ref and (record.partner_id or record.ticket_email):
                    try:
                        template = self.env.ref(
                            'tablero_kanban_helpdesk.email_template_ticket_confirmacion',
                            raise_if_not_found=False
                        )
                        if template:
                            template.send_mail(record.id, force_send=True)
                            _logger.info("✉️ Email enviado al convertir tarea en ticket: %s", 
                                       record.ticket_ref)
                    except Exception as e:
                        _logger.error("❌ Error enviando email al convertir: %s", str(e))
        
        return result

    def message_post(self, **kwargs):
        """
        Override para capturar la primera respuesta (SLA tracking)
        """
        result = super(TableroTarea, self).message_post(**kwargs)
        
        # 📊 TRACKING DE SLA - Primera respuesta del staff
        if self.es_ticket and not self.date_first_response:
            # Verificar si el mensaje viene de un usuario interno (no del portal/cliente)
            author_id = kwargs.get('author_id') or self.env.user.partner_id.id
            author = self.env['res.partner'].browse(author_id)
            
            # Si el autor NO es el partner del ticket = es respuesta del staff
            if author != self.partner_id:
                self.date_first_response = fields.Datetime.now()
                _logger.info("⏱️ Primera respuesta registrada para ticket %s. SLA: %.2f horas", 
                           self.ticket_ref, self.sla_hours)
        
        return result

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
        📧 CREACIÓN DE TICKETS DESDE EMAIL
        Este método se llama cuando llega un email al alias configurado.
        Crea automáticamente un ticket desde el correo electrónico.
        """
        if custom_values is None:
            custom_values = {}
        
        # Extraer información del correo
        email_from = msg_dict.get('email_from', '')
        subject = msg_dict.get('subject', 'Ticket sin asunto')
        body = msg_dict.get('body', '')
        
        # Buscar si el email corresponde a un partner existente
        partner = self.env['res.partner'].search([('email', '=ilike', email_from)], limit=1)
        
        # Valores por defecto para el nuevo ticket
        defaults = {
            'name': subject,
            'description': body,
            'es_ticket': True,
            'tipo_ticket': 'consulta',
            'state': 'nuevo',
            'ticket_email': email_from,
        }
        
        # Si encontramos un partner, asociarlo
        if partner:
            defaults['partner_id'] = partner.id
        
        # Merge con custom_values (permite override desde alias)
        defaults.update(custom_values)
        
        _logger.info("📧 Ticket creado desde email: %s - De: %s", subject, email_from)
        
        return super(TableroTarea, self).message_new(msg_dict, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """
        📨 ACTUALIZACIÓN DE TICKETS DESDE EMAIL
        Se llama cuando llega una respuesta a un ticket existente por email
        """
        _logger.info("📨 Actualización de ticket %s desde email", self.ticket_ref or self.name)
        return super(TableroTarea, self).message_update(msg_dict, update_vals=update_vals)


class HelpdeskTeam(models.Model):
    """
    🚀 MODELO PARA EQUIPOS DE SOPORTE (Escalabilidad Futura)
    
    Permite crear múltiples equipos de soporte con:
    - Miembros asignados
    - Alias de email propio por equipo
    - SLA específicos por equipo
    - Métricas y reportes por equipo
    
    Ejemplo de uso futuro:
    - Equipo "Soporte Técnico" → soporte-tecnico@caletti.com.mx
    - Equipo "Facturación" → facturacion@caletti.com.mx
    - Equipo "Mejoras" → mejoras@caletti.com.mx
    """
    _name = 'tablero.helpdesk.team'
    _description = 'Equipos de Soporte'
    _order = 'name'
    
    name = fields.Char(string="Nombre del Equipo", required=True)
    active = fields.Boolean(string="Activo", default=True)
    user_ids = fields.Many2many('res.users', string="Miembros del Equipo")
    
    alias_id = fields.Many2one(
        'mail.alias',
        string='Email Alias',
        ondelete="restrict",
        help="Email alias para este equipo de soporte"
    )
    
    # Campos para escalabilidad futura
    ticket_count = fields.Integer(
        string="Tickets Activos",
        compute="_compute_ticket_count"
    )
    
    sla_response_hours = fields.Float(
        string="SLA Respuesta (Horas)",
        default=24.0,
        help="Tiempo objetivo de primera respuesta en horas"
    )
    
    sla_resolution_hours = fields.Float(
        string="SLA Resolución (Horas)",
        default=72.0,
        help="Tiempo objetivo de resolución en horas"
    )
    
    def _compute_ticket_count(self):
        """Cuenta tickets activos del equipo (para implementar en futuro)"""
        for team in self:
            # TODO: Implementar cuando se agregue campo team_id a tickets
            team.ticket_count = 0
    
    @api.model
    def create(self, vals):
        """
        Crear alias automáticamente al crear el equipo
        Esto permite tener emails como:
        - soporte-tecnico@caletti.com.mx
        - soporte-facturacion@caletti.com.mx
        """
        team = super(HelpdeskTeam, self).create(vals)
        
        # Crear alias si no existe
        if not team.alias_id:
            alias_name = vals.get('name', '').lower().replace(' ', '-')
            
            # Verificar que el alias no exista ya
            existing_alias = self.env['mail.alias'].search([
                ('alias_name', '=', f'soporte-{alias_name}')
            ], limit=1)
            
            if not existing_alias:
                alias = self.env['mail.alias'].create({
                    'alias_name': f'soporte-{alias_name}',
                    'alias_model_id': self.env['ir.model'].search([
                        ('model', '=', 'tablero.tarea')
                    ], limit=1).id,
                    'alias_defaults': "{'es_ticket': True, 'tipo_ticket': 'consulta'}",
                    'alias_contact': 'everyone',
                })
                team.alias_id = alias.id
                _logger.info("✅ Alias creado para equipo %s: %s@%s", 
                           team.name, alias.alias_name, alias.alias_domain)
            else:
                team.alias_id = existing_alias.id
                _logger.info("ℹ️ Alias existente reutilizado para equipo %s", team.name)
        
        return team
    
    def unlink(self):
        """Eliminar alias al eliminar equipo (cleanup)"""
        for team in self:
            if team.alias_id:
                _logger.info("🗑️ Eliminando alias de equipo %s", team.name)
                team.alias_id.unlink()
        return super(HelpdeskTeam, self).unlink()