from odoo import models, fields, api

class TableroTarea(models.Model):
    _name = 'tablero.tarea'
    _description = 'Tareas del Tablero'
    _inherit = ['mail.thread']

    color = fields.Integer(string='ColorIndex')
    name = fields.Char(string='Tarea', required=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('proceso', 'En Proceso'),
        ('hecho', 'Finalizado')
    ], string='Estado', default='nuevo')


   # Función que se ejecutará al presionar el botón
    def action_finalizar_tarea(self):
        for record in self:
            record.write({
                'state': 'hecho',
                'color': 10
            })
        return True


    # FUNCIÓN DE AUTOMATIZACIÓN
    def write(self, vals):
        # Si el usuario está cambiando el estado ('state')
        if 'state' in vals:
            # Si el nuevo estado es 'hecho' (Finalizado)
            if vals.get('state') == 'hecho':
                vals['color'] = 10  # El color 10 es verde en Odoo
                
                # Publicar un mensaje automático en el Chatter
                for record in self:
                    record.message_post(body="¡Excelente! Esta tarea ha sido finalizada con éxito.")
        
        # Llamamos a la función original para que Odoo guarde los cambios
        return super(TableroTarea, self).write(vals)
