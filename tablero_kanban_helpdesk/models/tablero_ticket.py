# -*- coding: utf-8 -*-
# Archivo: tablero_kanban_helpdesk/models/tablero_ticket.py
from odoo import models, fields, api

class TableroTarea(models.Model):
    _inherit = 'tablero.tarea' # Mantenemos la herencia al modelo base

    es_ticket = fields.Boolean(string="Es Ticket", default=False)
    tipo_ticket = fields.Selection([
        ('soporte', 'Soporte Técnico'),
        ('facturacion', 'Facturación'),
        ('mejora', 'Solicitud de Mejora'),
        ('error', 'Reporte de Error')
    ], string="Tipo de Ticket")

    prioridad_ticket = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Media'),
        ('2', 'Alta'),
        ('3', 'Crítica')
    ], string="Prioridad del Ticket", default='1')

    ticket_ref = fields.Char(string="Ref. Ticket", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('es_ticket'):
            vals['ticket_ref'] = "TK-" + fields.Datetime.now().strftime('%Y%m%d%H%M')
        return super(TableroTarea, self).create(vals)