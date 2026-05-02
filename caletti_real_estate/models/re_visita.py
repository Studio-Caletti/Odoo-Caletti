# caletti_real_estate/models/re_visita.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES
# =============================================================================

ESTADO_AGENDADA   = 'agendada'
ESTADO_REALIZADA  = 'realizada'
ESTADO_CANCELADA  = 'cancelada'
ESTADO_NO_SHOW    = 'no_show'

INTERES_MUY_ALTO  = 'muy_alto'
INTERES_ALTO      = 'alto'
INTERES_MEDIO     = 'medio'
INTERES_BAJO      = 'bajo'
INTERES_NULO      = 'sin_interes'


# =============================================================================
# MODELO PRINCIPAL: re.visita
# =============================================================================

class ReVisita(models.Model):
    """
    Visita a propiedad — Caletti Real Estate v1.1

    Complementa mail.activity sin reemplazarla.
    Las actividades de Odoo siguen para recordatorios y coordinación interna.
    re.visita agrega la capa analítica: métricas de conversión, tiempo
    promedio entre primera visita y cierre, y ranking por propiedad.

    Acceso dual:
    - Desde el Prospecto: tab Visitas + smart button
    - Desde el menú principal: Visitas (agenda del asesor)

    Métricas generadas:
    - tasa_conversion en re.propiedad
    - dias_primer_cierre en re.prospecto
    - visitas_count en ambos modelos
    """
    _name        = 're.visita'
    _description = 'Visita a Propiedad — Caletti Real Estate'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    _rec_name    = 'name'
    _order       = 'fecha_visita desc'

    # =========================================================================
    # SECCIÓN 1: IDENTIFICACIÓN
    # =========================================================================

    name = fields.Char(
        string='Referencia de Visita',
        readonly=True,
        copy=False,
        default=lambda self: _('Nueva Visita'),
        help="Referencia secuencial generada automáticamente al confirmar"
    )

    # =========================================================================
    # SECCIÓN 2: VINCULACIÓN
    # =========================================================================

    prospecto_id = fields.Many2one(
        're.prospecto',
        string='Prospecto',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
        help="Prospecto que realizará o realizó la visita"
    )

    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad Visitada',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
        help="Propiedad específica que se visitó o se visitará"
    )

    contrato_id = fields.Many2one(
        're.contrato',
        string='Contrato Generado',
        ondelete='set null',
        readonly=True,
        tracking=True,
        help="Contrato de renta o venta generado como resultado de esta visita. "
             "Se llena automáticamente cuando el prospecto cierra."
    )

    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor Responsable',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        index=True
    )

    # =========================================================================
    # SECCIÓN 3: AGENDA
    # =========================================================================

    fecha_visita = fields.Datetime(
        string='Fecha y Hora de Visita',
        required=True,
        tracking=True,
        help="Fecha y hora programada o realizada de la visita"
    )

    duracion_min = fields.Integer(
        string='Duración (min)',
        default=60,
        help="Duración estimada o real de la visita en minutos"
    )

    estado = fields.Selection([
        (ESTADO_AGENDADA,  '📅 Agendada'),
        (ESTADO_REALIZADA, '✅ Realizada'),
        (ESTADO_CANCELADA, '❌ Cancelada'),
        (ESTADO_NO_SHOW,   '👻 No Show'),
    ], string='Estado',
       default=ESTADO_AGENDADA,
       required=True,
       tracking=True,
       index=True
    )

    # =========================================================================
    # SECCIÓN 4: FEEDBACK DEL ASESOR
    # Visible y editable solo cuando estado = realizada
    # =========================================================================

    interes_prospecto = fields.Selection([
        (INTERES_MUY_ALTO, '🔥 Muy Alto — Listo para cerrar'),
        (INTERES_ALTO,     '⬆️ Alto — Muy interesado'),
        (INTERES_MEDIO,    '➡️ Medio — Evaluando opciones'),
        (INTERES_BAJO,     '⬇️ Bajo — Pocas posibilidades'),
        (INTERES_NULO,     '❌ Sin Interés — Descartada'),
    ], string='Nivel de Interés',
       tracking=True,
       help="Evaluación del asesor sobre el interés del prospecto "
            "tras la visita realizada"
    )

    probabilidad_cierre = fields.Float(
        string='Probabilidad de Cierre (%)',
        default=0.0,
        digits=(5, 1),
        tracking=True,
        help="Estimación del asesor sobre la probabilidad de que "
             "este prospecto cierre con esta propiedad. 0-100%"
    )

    objeciones = fields.Text(
        string='Objeciones del Prospecto',
        help="Objeciones, dudas o condiciones planteadas por el prospecto "
             "durante la visita. Base para la siguiente acción del asesor."
    )

    notas_asesor = fields.Text(
        string='Notas del Asesor',
        help="Observaciones generales del asesor sobre la visita: "
             "condiciones de la propiedad, comportamiento del prospecto, "
             "próximos pasos recomendados."
    )

    proxima_accion = fields.Selection([
        ('reagendar',        '📅 Reagendar visita'),
        ('segunda_visita',   '🏠 Segunda visita'),
        ('enviar_propuesta', '📄 Enviar propuesta económica'),
        ('negociar',         '🤝 Iniciar negociación'),
        ('esperar',          '⏳ Esperar decisión del prospecto'),
        ('cerrar',           '✅ Proceder al cierre'),
        ('descartar',        '❌ Descartar prospecto'),
    ], string='Próxima Acción',
       tracking=True,
       help="Acción recomendada por el asesor tras evaluar la visita"
    )

    # =========================================================================
    # SECCIÓN 5: CAMPOS COMPUTADOS — MÉTRICAS
    # =========================================================================

    es_primera_visita = fields.Boolean(
        string='Es Primera Visita',
        compute='_compute_es_primera_visita',
        store=True,
        help="True si esta es la primera visita del prospecto "
             "a esta propiedad específica"
    )

    convirtio = fields.Boolean(
        string='Convirtió',
        compute='_compute_convirtio',
        store=True,
        help="True si esta visita resultó en un contrato firmado"
    )

    dias_hasta_cierre = fields.Integer(
        string='Días hasta Cierre',
        compute='_compute_dias_hasta_cierre',
        store=True,
        help="Días transcurridos desde esta visita hasta la firma del contrato. "
             "0 si aún no hay contrato."
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

     # =========================================================================
    # SECCIÓN 10: CAMPOS TÉCNICOS Y UI
    # =========================================================================

    current_datetime = fields.Datetime(
        string='Fecha Actual',
        compute='_compute_current_datetime',
        help="Campo técnico para decoraciones de vista (overdue)"
    )

    color = fields.Integer(
        string='Color Index',
        help="Usado para la organización visual en el Kanban"
    )

    # =========================================================================
    # SECCIÓN 6: COMPUTES
    # =========================================================================


    @api.depends('prospecto_id', 'propiedad_id', 'fecha_visita',  'create_date')
    def _compute_es_primera_visita(self):
        for visita in self:
            if not visita.prospecto_id or not visita.propiedad_id:
               visita.es_primera_visita = False
            continue

        # Si el registro aún no está guardado (NewId), es primera visita
        # por definición — no hay con qué comparar en DB
            if not visita.id or isinstance(visita.id, models.NewId):
                visita.es_primera_visita = True
            continue

            visitas_anteriores = self.search([
                ('prospecto_id', '=', visita.prospecto_id.id),
                ('propiedad_id', '=', visita.propiedad_id.id),
                ('fecha_visita', '<', visita.fecha_visita),
                ('id', '!=', visita.id),
                ('estado', '!=', ESTADO_CANCELADA),
                ])
            visita.es_primera_visita = not bool(visitas_anteriores)


    @api.depends('contrato_id')
    def _compute_convirtio(self):
        """True si existe un contrato vinculado a esta visita."""
        for visita in self:
            visita.convirtio = bool(visita.contrato_id)

    @api.depends('contrato_id', 'fecha_visita')
    def _compute_dias_hasta_cierre(self):
        """
        Días desde la fecha de esta visita hasta la fecha de inicio
        del contrato generado. 0 si no hay contrato.
        """
        for visita in self:
            if visita.contrato_id and visita.fecha_visita:
                fecha_contrato = visita.contrato_id.fecha_inicio
                if fecha_contrato:
                    fecha_visita_date = visita.fecha_visita.date()
                    delta = fecha_contrato - fecha_visita_date
                    visita.dias_hasta_cierre = max(0, delta.days)
                else:
                    visita.dias_hasta_cierre = 0
            else:
                visita.dias_hasta_cierre = 0

    # =========================================================================
    # SECCIÓN 7: CONSTRAINS Y VALIDACIONES
    # =========================================================================

    @api.constrains('probabilidad_cierre')
    def _check_probabilidad(self):
        for visita in self:
            if not (0.0 <= visita.probabilidad_cierre <= 100.0):
                raise ValidationError(_(
                    "La probabilidad de cierre debe estar entre 0% y 100%."
                ))

#    @api.constrains('prospecto_id', 'propiedad_id')
#    def _check_propiedad_en_prospecto(self):
#        """
#        Validación suave: advierte si la propiedad no está en las
#        propiedades evaluadas del prospecto. No bloquea — el asesor
#        puede querer registrar visitas exploratorias.
#        """
#        for visita in self:
#            if (visita.prospecto_id
#                    and visita.propiedad_id
#                    and visita.propiedad_id not in
#                    visita.prospecto_id.propiedad_interes_ids):
#                _logger.warning(
#                    "⚠️ Visita %s: la propiedad '%s' no está en las "
#                    "propiedades evaluadas del prospecto '%s'. "
#                    "Considera agregarla al prospecto.",
#                    visita.name,
#                    visita.propiedad_id.name,
#                    visita.prospecto_id.name
#                )

    # =========================================================================
    # SECCIÓN 8: ORM OVERRIDES
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """Genera la referencia secuencial al crear."""
        for vals in vals_list:
            if vals.get('name', _('Nueva Visita')) == _('Nueva Visita'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    're.visita'
                ) or _('Nueva Visita')
        return super().create(vals_list)

    # =========================================================================
    # SECCIÓN 9: ACCIONES DE ESTADO
    # =========================================================================

    def action_marcar_realizada(self):
        """Marca la visita como realizada y solicita feedback al asesor."""
        self.ensure_one()
        if self.estado != ESTADO_AGENDADA:
            raise UserError(_(
                "Solo se puede marcar como realizada una visita agendada."
            ))

        self.write({'estado': ESTADO_REALIZADA})

        self.message_post(
            body=Markup(_(
                "✅ <strong>Visita realizada.</strong><br/>"
                "Propiedad: <strong>%(propiedad)s</strong><br/>"
                "Prospecto: <strong>%(prospecto)s</strong><br/>"
                "Completa el feedback para guiar la siguiente acción."
            )) % {
                'propiedad': self.propiedad_id.name,
                'prospecto': self.prospecto_id.name,
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        # Notificar también en el Chatter del prospecto
        self.prospecto_id.message_post(
            body=Markup(_(
                "🏠 <strong>Visita realizada.</strong><br/>"
                "Propiedad visitada: <strong>%(propiedad)s</strong><br/>"
                "Asesor: <strong>%(asesor)s</strong><br/>"
                "Ref. visita: <strong>%(ref)s</strong>"
            )) % {
                'propiedad': self.propiedad_id.name,
                'asesor':    self.asesor_id.name,
                'ref':       self.name,
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(
            "✅ Visita %s marcada como realizada — "
            "propiedad '%s' prospecto '%s'",
            self.name, self.propiedad_id.name, self.prospecto_id.name
        )

    def action_marcar_cancelada(self):
        """Cancela la visita agendada."""
        self.ensure_one()
        if self.estado not in [ESTADO_AGENDADA]:
            raise UserError(_(
                "Solo se puede cancelar una visita agendada."
            ))
        self.write({'estado': ESTADO_CANCELADA})
        self.message_post(
            body=Markup(_(
                "❌ <strong>Visita cancelada.</strong><br/>"
                "Propiedad: <strong>%(propiedad)s</strong>"
            )) % {'propiedad': self.propiedad_id.name},
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    def action_marcar_no_show(self):
        """Marca al prospecto como no presentado."""
        self.ensure_one()
        if self.estado != ESTADO_AGENDADA:
            raise UserError(_(
                "Solo se puede marcar No Show una visita agendada."
            ))
        self.write({'estado': ESTADO_NO_SHOW})
        self.message_post(
            body=Markup(_(
                "👻 <strong>No Show.</strong><br/>"
                "El prospecto <strong>%(prospecto)s</strong> "
                "no se presentó a la visita de "
                "<strong>%(propiedad)s</strong>.<br/>"
                "Considera reagendar o revisar el estado del prospecto."
            )) % {
                'prospecto': self.prospecto_id.name,
                'propiedad': self.propiedad_id.name,
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    def action_registrar_feedback(self):
        """
        Abre wizard de feedback inline (usa el mismo form).
        El botón en la vista abre el form en modo edición
        posicionado en la sección de feedback.
        """
        self.ensure_one()
        if self.estado != ESTADO_REALIZADA:
            raise UserError(_(
                "Solo se puede registrar feedback de una visita realizada."
            ))
        return {
            'type':      'ir.actions.act_window',
            'res_model': 're.visita',
            'res_id':    self.id,
            'view_mode': 'form',
            'target':    'current',
        }

    def action_vincular_contrato(self):
        """
        Abre selector de contratos para vincular el cierre
        a esta visita. Actualiza convirtio y dias_hasta_cierre.
        """
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Vincular Contrato'),
            'res_model': 're.contrato',
            'view_mode': 'list,form',
            'domain':    [
                ('propiedad_id', '=', self.propiedad_id.id),
                ('estado', 'not in', ['cancelado']),
            ],
            'target': 'new',
        }

    def _compute_current_datetime(self):
        """Asigna la fecha/hora actual para validaciones dinámicas en la UI."""
        now = fields.Datetime.now()
        for record in self:
            record.current_datetime = now

   

