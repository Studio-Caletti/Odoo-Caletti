from odoo import models, fields

class HolaMundoMensaje(models.Model):
    _name = 'hola.mundo.mensaje'
    _description = 'Tabla de Mensajes de Carlos'

    name = fields.Char(string='Título', required=True)
    contenido = fields.Text(string='Mensaje')
    fecha = fields.Date(string='Fecha de Creación', default=fields.Date.today)
