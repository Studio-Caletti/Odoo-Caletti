# caletti_creative/models/creative_deliverable.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------
from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

# === CONSTANTES: TIPOS DE ENTREGABLE ===
TIPO_DISENO_GRAFICO  = 'diseno_grafico'
TIPO_COPY            = 'copy'
TIPO_VIDEO           = 'video'
TIPO_FOTOGRAFIA      = 'fotografia'
TIPO_WEB             = 'web'
TIPO_ANIMACION       = 'animacion'
TIPO_ILUSTRACION     = 'ilustracion'
TIPO_PRESENTACION    = 'presentacion'
TIPO_SOCIAL_MEDIA    = 'social_media'
TIPO_IMPRESO         = 'impreso'
TIPO_OTRO            = 'otro'

# === CONSTANTES: ESTADOS DEL ENTREGABLE ===
ESTADO_PENDIENTE     = 'pendiente'
ESTADO_EN_PROCESO    = 'en_proceso'
ESTADO_EN_REVISION   = 'en_revision'
ESTADO_APROBADO      = 'aprobado'
ESTADO_RECHAZADO     = 'rechazado'
ESTADO_ENTREGADO     = 'entregado'

# === CONSTANTES: LÍMITES DE REVISIÓN ===
MAX_REVISIONES_DEFAULT  = 3   # Estándar de industria: 2-3 rondas
ALERTA_REVISIONES       = 2   # Alertar desde la ronda 2


class CreativeDeliverable(models.Model):
    """
    Entregable creativo — Unidad mínima de trabajo y seguimiento del proyecto.

    Cada entregable es un producto concreto que la agencia entregará al cliente:
    un logo, un video, una página web, un copy, etc.

    Ciclo de vida: pendiente → en_proceso → en_revision → aprobado → entregado
    Con posibilidad de rechazo y re-trabajo en cualquier fase pre-aprobación.

    El control de rondas de revisión es crítico para la rentabilidad:
    cada ronda extra no contemplada en el presupuesto reduce el margen.
    """
    _name = 'creative.deliverable'
    _description = 'Entregable Creativo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'fecha_limite asc, sequence asc'

    # --- IDENTIFICACIÓN Y ORDEN ---
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Orden de ejecución dentro del proyecto"
    )

    name = fields.Char(
        string='Nombre del Entregable',
        required=True,
        tracking=True,
        help="Ej: 'Logotipo principal', 'Banner para Facebook 1200x628', "
             "'Video institucional 60s'"
    )

    proyecto_id = fields.Many2one(
        'tablero.tarea',
        string='Proyecto',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True
    )

    # Cliente via related del proyecto — sin duplicar relación
    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='proyecto_id.partner_id',
        store=True,
        readonly=True
    )

    # --- CLASIFICACIÓN ---
    tipo_entregable = fields.Selection([
        (TIPO_DISENO_GRAFICO, '🎨 Diseño Gráfico'),
        (TIPO_COPY,           '✍️ Copy / Redacción'),
        (TIPO_VIDEO,          '🎬 Video / Producción'),
        (TIPO_FOTOGRAFIA,     '📷 Fotografía'),
        (TIPO_WEB,            '💻 Web / Digital'),
        (TIPO_ANIMACION,      '✨ Animación / Motion'),
        (TIPO_ILUSTRACION,    '🖌️ Ilustración'),
        (TIPO_PRESENTACION,   '📊 Presentación'),
        (TIPO_SOCIAL_MEDIA,   '📱 Social Media'),
        (TIPO_IMPRESO,        '🖨️ Impreso / Editorial'),
        (TIPO_OTRO,           '📦 Otro'),
    ], string='Tipo',
       required=True,
       tracking=True
    )

    descripcion = fields.Text(
        string='Descripción y Especificaciones',
        tracking=True,
        help="Especificaciones técnicas del entregable: dimensiones, formato, "
             "resolución, duración, número de variaciones, etc."
    )

    # --- RESPONSABLE ---
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        tracking=True,
        index=True,
        help="Miembro del equipo creativo asignado a este entregable"
    )

    # --- ESTADO Y WORKFLOW ---
    estado = fields.Selection([
        (ESTADO_PENDIENTE,   '⏳ Pendiente'),
        (ESTADO_EN_PROCESO,  '🔄 En Proceso'),
        (ESTADO_EN_REVISION, '🔍 En Revisión'),
        (ESTADO_APROBADO,    '✅ Aprobado'),
        (ESTADO_RECHAZADO,   '❌ Rechazado'),
        (ESTADO_ENTREGADO,   '🚀 Entregado'),
    ], string='Estado',
       default=ESTADO_PENDIENTE,
       required=True,
       tracking=True
    )

    # --- FECHAS ---
    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        tracking=True
    )

    fecha_limite = fields.Date(
        string='Fecha Límite',
        tracking=True,
        help="Fecha límite interna de entrega. Puede diferir de la fecha "
             "de entrega al cliente."
    )

    fecha_entrega_cliente = fields.Date(
        string='Fecha de Entrega al Cliente',
        tracking=True,
        help="Fecha comprometida con el cliente para este entregable"
    )

    fecha_aprobacion = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True
    )

    fecha_entrega_real = fields.Datetime(
        string='Fecha de Entrega Real',
        readonly=True,
        help="Fecha y hora en que se marcó como entregado al cliente"
    )

    # --- CONTROL DE REVISIONES (crítico para rentabilidad) ---
    max_revisiones = fields.Integer(
        string='Rondas de Revisión Incluidas',
        default=MAX_REVISIONES_DEFAULT,
        help="Número de rondas de revisión incluidas en el presupuesto. "
             "Estándar de industria: 2-3 rondas."
    )

    rondas_utilizadas = fields.Integer(
        string='Rondas Utilizadas',
        default=0,
        readonly=True,
        tracking=True,
        help="Contador de rondas de revisión utilizadas. "
             "Se incrementa automáticamente al rechazar."
    )

    revisiones_excedidas = fields.Boolean(
        string='Revisiones Excedidas',
        compute='_compute_estado_revisiones',
        store=True,
        help="True cuando se superaron las rondas incluidas en presupuesto"
    )

    revisiones_en_alerta = fields.Boolean(
        string='Revisiones en Alerta',
        compute='_compute_estado_revisiones',
        store=True,
        help="True cuando se alcanzó el umbral de alerta de revisiones"
    )

    # --- PRESUPUESTO DEL ENTREGABLE ---
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='proyecto_id.currency_id',
        readonly=True
    )

    costo_estimado = fields.Monetary(
        string='Costo Estimado',
        currency_field='currency_id',
        tracking=True,
        help="Costo estimado de producción de este entregable. "
             "Alimenta el costo real del proyecto."
    )

    costo_adicional_revisiones = fields.Monetary(
        string='Costo Adicional por Revisiones',
        currency_field='currency_id',
        compute='_compute_costo_adicional',
        store=True,
        help="Costo generado por rondas de revisión que exceden el presupuesto"
    )

    tarifa_revision_extra = fields.Monetary(
        string='Tarifa por Revisión Extra',
        currency_field='currency_id',
        help="Costo por cada ronda de revisión adicional fuera del presupuesto"
    )

    # --- COMPUTED ---

    @api.depends('rondas_utilizadas', 'max_revisiones')
    def _compute_estado_revisiones(self):
        """
        Evalúa el estado de las rondas de revisión para
        activar alertas visuales y notificaciones proactivas.
        """
        for entregable in self:
            entregable.revisiones_excedidas = (
                entregable.rondas_utilizadas > entregable.max_revisiones
            )
            entregable.revisiones_en_alerta = (
                entregable.rondas_utilizadas >= ALERTA_REVISIONES
                and not entregable.revisiones_excedidas
            )

    @api.depends('rondas_utilizadas', 'max_revisiones', 'tarifa_revision_extra')
    def _compute_costo_adicional(self):
        """
        Calcula el costo generado por revisiones que exceden
        las incluidas en el presupuesto original.
        """
        for entregable in self:
            rondas_extra = max(
                0,
                entregable.rondas_utilizadas - entregable.max_revisiones
            )
            entregable.costo_adicional_revisiones = (
                rondas_extra * entregable.tarifa_revision_extra
            )
            if rondas_extra > 0:
                _logger.info(
                    "💸 Entregable '%s': %d rondas extra → costo adicional %s",
                    entregable.name,
                    rondas_extra,
                    entregable.costo_adicional_revisiones
                )

    # --- VALIDACIONES ---

    @api.constrains('fecha_limite', 'fecha_entrega_cliente')
    def _check_fechas_coherentes(self):
        """
        La fecha límite interna debe ser anterior o igual
        a la fecha de entrega al cliente — nunca al revés.
        """
        for entregable in self:
            if (entregable.fecha_limite
                    and entregable.fecha_entrega_cliente
                    and entregable.fecha_limite > entregable.fecha_entrega_cliente):
                raise ValidationError(_(
                    "La fecha límite interna de '%(nombre)s' "
                    "no puede ser posterior a la fecha de entrega al cliente."
                ) % {'nombre': entregable.name})

    @api.constrains('max_revisiones')
    def _check_max_revisiones_positivo(self):
        for entregable in self:
            if entregable.max_revisiones < 1:
                raise ValidationError(_(
                    "El número mínimo de rondas de revisión es 1."
                ))

    # --- REGLA DE NEGOCIO: brief aprobado antes de iniciar ---

    def _validar_brief_aprobado(self):
        """
        Verifica que el proyecto tenga brief aprobado
        antes de permitir iniciar producción.
        Regla de negocio fundamental de agencias creativas.
        """
        self.ensure_one()
        if not self.proyecto_id.brief_aprobado:
            raise UserError(_(
                "No se puede iniciar '%(entregable)s' porque el proyecto "
                "'%(proyecto)s' no tiene un Brief aprobado.\n\n"
                "Aprueba el brief creativo antes de iniciar la producción."
            ) % {
                'entregable': self.name,
                'proyecto': self.proyecto_id.name,
            })

    # --- ACCIONES DE WORKFLOW ---

    def action_iniciar(self):
        """
        Inicia la producción del entregable.
        Requiere brief aprobado en el proyecto — regla no negociable.
        """
        self.ensure_one()
        if self.estado != ESTADO_PENDIENTE:
            raise UserError(_("Solo se puede iniciar un entregable Pendiente."))

        self._validar_brief_aprobado()

        self.write({
            'estado': ESTADO_EN_PROCESO,
            'fecha_inicio': fields.Date.today(),
        })
        self.message_post(
            body=_(
                "🔄 <strong>Producción iniciada.</strong><br/>"
                "Responsable: <strong>%(responsable)s</strong>"
            ) % {
                'responsable': self.responsable_id.name
                    if self.responsable_id else _("Sin asignar")
            },
            subject=_("Entregable en Producción")
        )
        _logger.info(
            "🔄 Entregable '%s' iniciado por %s",
            self.name, self.env.user.name
        )

    def action_enviar_a_revision(self):
        """
        Envía el entregable a revisión del cliente o dirección creativa.
        """
        self.ensure_one()
        if self.estado != ESTADO_EN_PROCESO:
            raise UserError(_(
                "Solo se puede enviar a revisión un entregable En Proceso."
            ))

        self.write({'estado': ESTADO_EN_REVISION})
        self.message_post(
            body=_(
                "🔍 <strong>Entregable enviado a revisión.</strong><br/>"
                "Ronda de revisión: <strong>%(ronda)d de %(max)d</strong>"
                "%(alerta)s"
            ) % {
                'ronda': self.rondas_utilizadas + 1,
                'max': self.max_revisiones,
                'alerta': _(
                    "<br/>⚠️ <em>Próxima a agotar las rondas incluidas.</em>"
                ) if (self.rondas_utilizadas + 1) >= ALERTA_REVISIONES else ''
            },
            subject=_("Entregable en Revisión")
        )
        _logger.info(
            "🔍 Entregable '%s' enviado a revisión (ronda %d/%d)",
            self.name,
            self.rondas_utilizadas + 1,
            self.max_revisiones
        )

    def action_aprobar(self):
        """
        Aprueba el entregable. Registra fecha de aprobación.
        """
        self.ensure_one()
        if self.estado != ESTADO_EN_REVISION:
            raise UserError(_(
                "Solo se puede aprobar un entregable En Revisión."
            ))

        ahora = fields.Datetime.now()
        self.write({
            'estado': ESTADO_APROBADO,
            'fecha_aprobacion': ahora,
        })
        self.message_post(
            body=_(
                "✅ <strong>¡Entregable Aprobado!</strong><br/>"
                "Aprobado por: <strong>%(usuario)s</strong><br/>"
                "Rondas utilizadas: <strong>%(rondas)d de %(max)d</strong>"
            ) % {
                'usuario': self.env.user.name,
                'rondas': self.rondas_utilizadas,
                'max': self.max_revisiones,
            },
            subject=_("Entregable Aprobado")
        )
        _logger.info(
            "✅ Entregable '%s' aprobado. Rondas: %d/%d",
            self.name, self.rondas_utilizadas, self.max_revisiones
        )

    def action_rechazar(self, motivo=''):
        """
        Rechaza el entregable e incrementa el contador de rondas.
        Emite alerta si se exceden las rondas del presupuesto.
        """
        self.ensure_one()
        if self.estado != ESTADO_EN_REVISION:
            raise UserError(_(
                "Solo se puede rechazar un entregable En Revisión."
            ))

        nuevas_rondas = self.rondas_utilizadas + 1
        self.write({
            'estado': ESTADO_EN_PROCESO,
            'rondas_utilizadas': nuevas_rondas,
        })

        # Construir mensaje con nivel de alerta adecuado
        if nuevas_rondas > self.max_revisiones:
            cuerpo = _(
                "❌ <strong>Entregable rechazado — RONDA EXTRA.</strong><br/>"
                "Motivo: %(motivo)s<br/>"
                "⚠️ <strong>Ronda %(ronda)d excede las %(max)d incluidas "
                "en presupuesto.</strong><br/>"
                "Aplica tarifa adicional de revisión."
            ) % {
                'motivo': motivo or _("Sin motivo especificado."),
                'ronda': nuevas_rondas,
                'max': self.max_revisiones,
            }
            _logger.warning(
                "⚠️ Entregable '%s': ronda extra %d (máx %d)",
                self.name, nuevas_rondas, self.max_revisiones
            )
        else:
            cuerpo = _(
                "❌ <strong>Entregable rechazado.</strong><br/>"
                "Motivo: %(motivo)s<br/>"
                "Rondas utilizadas: <strong>%(ronda)d de %(max)d</strong>"
            ) % {
                'motivo': motivo or _("Sin motivo especificado."),
                'ronda': nuevas_rondas,
                'max': self.max_revisiones,
            }

        self.message_post(
            body=cuerpo,
            subject=_("Entregable Rechazado — Requiere Ajustes")
        )

        # Email de alerta solo cuando se exceden las rondas
        if nuevas_rondas > self.max_revisiones:
            try:
                template = self.env.ref(
                    'caletti_creative.email_template_revisiones_excedidas',
                    raise_if_not_found=False
                )
                if template:
                    template.send_mail(self.id, force_send=True)
                    _logger.info(
                        "✉️ Alerta de revisiones excedidas enviada — '%s'",
                        self.name
                    )
            except Exception as e:
                _logger.error(
                    "❌ Error enviando alerta de revisiones '%s': %s",
                    self.name, str(e)
                )

    def action_marcar_entregado(self):
        """
        Marca el entregable como entregado al cliente.
        Solo es posible desde estado Aprobado.
        """
        self.ensure_one()
        if self.estado != ESTADO_APROBADO:
            raise UserError(_(
                "Solo se puede marcar como entregado un entregable Aprobado."
            ))

        ahora = fields.Datetime.now()
        self.write({
            'estado': ESTADO_ENTREGADO,
            'fecha_entrega_real': ahora,
        })
        self.message_post(
            body=_(
                "🚀 <strong>¡Entregable entregado al cliente!</strong><br/>"
                "Fecha de entrega: <strong>%(fecha)s</strong><br/>"
                "Rondas utilizadas: <strong>%(rondas)d de %(max)d</strong>"
                "%(extra)s"
            ) % {
                'fecha': ahora.strftime('%d/%m/%Y %H:%M'),
                'rondas': self.rondas_utilizadas,
                'max': self.max_revisiones,
                'extra': _(
                    "<br/>💸 Costo adicional por revisiones: %(costo)s"
                ) % {'costo': self.costo_adicional_revisiones}
                if self.costo_adicional_revisiones > 0 else ''
            },
            subject=_("Entregable Entregado al Cliente")
        )
        _logger.info(
            "🚀 Entregable '%s' entregado. Rondas: %d/%d. "
            "Costo adicional revisiones: %s",
            self.name,
            self.rondas_utilizadas,
            self.max_revisiones,
            self.costo_adicional_revisiones
        )