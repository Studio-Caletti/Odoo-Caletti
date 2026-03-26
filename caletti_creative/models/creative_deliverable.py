# caletti_creative/models/creative_deliverable.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

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