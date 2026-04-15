# caletti_real_estate/models/re_operacion.py
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
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES: TIPO DE OPERACIÓN
# =============================================================================
OP_RENTA = 'renta'
OP_VENTA = 'venta'

# =============================================================================
# CONSTANTES: ETAPAS DEL FLUJO OPERATIVO
# Mapean el pipeline visual del Kanban del vertical
# =============================================================================
ETAPA_CAPTACION    = 'captacion'     # propiedad ingresada a cartera
ETAPA_DIFUSION     = 'difusion'      # publicada y en búsqueda de prospecto
ETAPA_PROSPECTO    = 'con_prospecto' # hay prospecto activo evaluando
ETAPA_NEGOCIACION  = 'negociacion'   # en proceso de cierre
ETAPA_DOCUMENTACION = 'documentacion' # papeles y trámites en curso
ETAPA_CIERRE       = 'cierre'        # contrato firmado / escriturado
ETAPA_CERRADA      = 'cerrada'       # operación concluida (archivada)


class ReOperacion(models.Model):
    """
    Operación inmobiliaria — extiende tablero.tarea del Core.

    Representa la gestión activa de una propiedad en el pipeline
    del asesor: desde que ingresa a su cartera hasta el cierre
    del contrato de renta o venta.

    REGLA FUNDAMENTAL: Una propiedad tiene exactamente UNA operación
    activa simultáneamente. El @api.constrains valida esto al crear
    o reactivar una operación.

    El Kanban del vertical filtra por:
    - es_operacion_re = True
    - etapa_re != 'cerrada'

    Así el tablero muestra solo las operaciones activas.
    Las cerradas permanecen como historial y son accesibles
    desde la vista lista con el filtro 'Historial'.

    Herencia del Core (tablero.tarea):
    - Chatter + actividades
    - Portal base
    - Alertas de fecha límite (is_overdue, date_deadline)
    - Prioridad y estado kanban
    - Seguridad base (group_tablero_user heredado por group_re_asesor)

    Campos propios del vertical:
    - propiedad_id: la propiedad gestionada
    - tipo_operacion_re: renta o venta
    - etapa_re: pipeline visual del vertical
    - prospecto_activo_id: el prospecto del pipeline vinculado
    - contrato_id: el contrato generado al cerrar
    """
    _inherit = 'tablero.tarea'

    # =========================================================================
    # CAMPO DISCRIMINADOR
    # Separa las operaciones RE del resto de tareas del Core
    # Mismo patrón que es_proyecto_creativo en caletti_creative
    # =========================================================================

    es_operacion_re = fields.Boolean(
        string='Es Operación Inmobiliaria',
        default=False,
        index=True,
        help="Marca esta tarea del Core como una operación del "
             "vertical inmobiliario Caletti Real Estate."
    )

    # =========================================================================
    # CAMPOS PROPIOS DEL VERTICAL
    # =========================================================================

    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad',
        index=True,
        tracking=True,
        help="Inmueble que se está gestionando en esta operación. "
             "Solo puede haber una operación activa por propiedad."
    )

    # Campos relacionados de la propiedad — evitan ir al modelo padre
    # en vistas y filtros frecuentes
    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        related='propiedad_id.propietario_id',
        store=True,
        readonly=True
    )

    tipo_propiedad_re = fields.Selection(
        related='propiedad_id.tipo_propiedad',
        string='Tipo de Propiedad',
        store=True,
        readonly=True
    )

    estado_propiedad = fields.Selection(
        related='propiedad_id.estado',
        string='Estado de la Propiedad',
        store=True,
        readonly=True
    )

    tipo_operacion_re = fields.Selection([
        (OP_RENTA, '🔑 Renta'),
        (OP_VENTA, '💰 Venta'),
    ], string='Tipo de Operación',
       tracking=True,
       index=True,
       help="Define si esta operación es de arrendamiento o compraventa"
    )

    etapa_re = fields.Selection([
        (ETAPA_CAPTACION,     '📋 Captación — Propiedad en cartera'),
        (ETAPA_DIFUSION,      '📢 Difusión — Buscando prospecto'),
        (ETAPA_PROSPECTO,     '👤 Con Prospecto — Evaluando'),
        (ETAPA_NEGOCIACION,   '🤝 Negociación — En cierre'),
        (ETAPA_DOCUMENTACION, '📄 Documentación — Trámites'),
        (ETAPA_CIERRE,        '✅ Cierre — Contrato firmado'),
        (ETAPA_CERRADA,       '📦 Cerrada — Archivada'),
    ], string='Etapa de la Operación',
       default=ETAPA_CAPTACION,
       tracking=True,
       index=True,
       help="Pipeline visual del Kanban inmobiliario. "
            "Las operaciones en etapa 'Cerrada' se archivan "
            "y no aparecen en el Kanban activo."
    )

    # Vínculos con el pipeline y el contrato
    prospecto_activo_id = fields.Many2one(
        're.prospecto',
        string='Prospecto Activo',
        tracking=True,
        help="Prospecto del pipeline que está evaluando esta propiedad actualmente"
    )

    contrato_id = fields.Many2one(
        're.contrato',
        string='Contrato Generado',
        readonly=True,
        tracking=True,
        help="Contrato de renta o compraventa generado al cerrar la operación"
    )

    # Precio objetivo — campo rápido sin ir a re.propiedad
    precio_objetivo = fields.Monetary(
        string='Precio Objetivo',
        currency_field='currency_id',
        tracking=True,
        help="Precio de cierre objetivo para esta operación. "
             "Referencia para el asesor durante la negociación."
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='propiedad_id.currency_id',
        readonly=True
    )

    # Días en el pipeline — computed desde fecha de inicio de la tarea
    dias_en_operacion = fields.Integer(
        string='Días en Operación',
        compute='_compute_dias_operacion',
        help="Días desde que la operación fue creada"
    )

    color = fields.Integer(string='Color Index', default=0)

    # =========================================================================
    # COMPUTED
    # =========================================================================

    @api.depends('date_started', 'state', 'etapa_re')
    def _compute_dias_operacion(self):
        """
        Días transcurridos desde el inicio de la operación.
        Usa date_started del Core si existe, si no create_date.
        """
        today = fields.Date.today()
        for op in self:
            if op.date_started:
                inicio = op.date_started.date()
            elif op.create_date:
                inicio = op.create_date.date()
            else:
                inicio = today
            op.dias_en_operacion = (today - inicio).days

    # =========================================================================
    # VALIDACIONES
    # =========================================================================

    @api.constrains('propiedad_id', 'es_operacion_re', 'etapa_re')
    def _check_una_operacion_activa(self):
        """
        REGLA FUNDAMENTAL: Una propiedad solo puede tener
        una operación activa simultáneamente.

        Una operación es 'activa' cuando etapa_re != 'cerrada'.
        Al cerrar una operación queda archivada y la propiedad
        puede recibir una nueva.
        """
        for op in self:
            if (op.es_operacion_re
                    and op.propiedad_id
                    and op.etapa_re != ETAPA_CERRADA):

                otras_activas = self.search([
                    ('es_operacion_re', '=', True),
                    ('propiedad_id', '=', op.propiedad_id.id),
                    ('etapa_re', '!=', ETAPA_CERRADA),
                    ('id', '!=', op.id),
                ])

                if otras_activas:
                    raise ValidationError(_(
                        "La propiedad '%(prop)s' ya tiene una operación "
                        "activa: '%(op)s'.\n\n"
                        "Cierra la operación actual antes de crear una nueva. "
                        "Una propiedad solo puede tener una operación activa "
                        "a la vez."
                    ) % {
                        'prop': op.propiedad_id.name,
                        'op':   otras_activas[0].name,
                    })

    @api.constrains('contrato_id', 'propiedad_id')
    def _check_contrato_de_propiedad(self):
        """El contrato vinculado debe ser de la misma propiedad."""
        for op in self:
            if (op.contrato_id
                    and op.propiedad_id
                    and op.contrato_id.propiedad_id != op.propiedad_id):
                raise ValidationError(_(
                    "El contrato '%(contrato)s' no pertenece a la "
                    "propiedad '%(propiedad)s'."
                ) % {
                    'contrato':  op.contrato_id.name,
                    'propiedad': op.propiedad_id.name,
                })

    # =========================================================================
    # ACCIONES DE WORKFLOW
    # =========================================================================

    def action_avanzar_etapa_re(self):
        """
        Avanza la operación a la siguiente etapa del pipeline.
        Registra el cambio en el Chatter con contexto inmobiliario.
        """
        self.ensure_one()

        flujo = [
            ETAPA_CAPTACION,
            ETAPA_DIFUSION,
            ETAPA_PROSPECTO,
            ETAPA_NEGOCIACION,
            ETAPA_DOCUMENTACION,
            ETAPA_CIERRE,
        ]

        if self.etapa_re == ETAPA_CERRADA:
            raise ValidationError(_(
                "La operación ya está cerrada y archivada."
            ))

        if self.etapa_re not in flujo:
            return

        idx = flujo.index(self.etapa_re)

        # Validación especial: para llegar a Cierre necesita contrato
        if flujo[idx + 1] == ETAPA_CIERRE and not self.contrato_id:
            raise ValidationError(_(
                "Vincula el contrato generado antes de pasar a Cierre.\n"
                "Genera el contrato desde Caletti Real Estate → Contratos."
            ))

        self.write({'etapa_re': flujo[idx + 1]})

    def action_cerrar_operacion(self):
        """
        Archiva la operación. Solo desde etapa Cierre.
        Registra el resumen final en el Chatter.
        """
        self.ensure_one()
        if self.etapa_re != ETAPA_CIERRE:
            raise ValidationError(_(
                "Solo se puede cerrar una operación que está en "
                "etapa Cierre. Avanza el pipeline primero."
            ))
        self.write({
            'etapa_re': ETAPA_CERRADA,
            'state':    'hecho',
        })
        _logger.info(
            "📦 Operación RE '%s' cerrada. Propiedad: '%s'. "
            "Días: %d",
            self.name,
            self.propiedad_id.name if self.propiedad_id else '—',
            self.dias_en_operacion
        )

    # =========================================================================
    # OVERRIDE write — CHATTER Y SINCRONIZACIÓN CON RE.PROPIEDAD
    # =========================================================================

    def write(self, vals):
        """
        Sincroniza el estado de re.propiedad cuando cambia la etapa.
        Registra cambios de etapa en el Chatter con contexto inmobiliario.
        Patrón idéntico al resto de modelos del vertical.
        """
        resultado = super(ReOperacion, self).write(vals)

        if 'etapa_re' in vals:
            nueva_etapa = vals['etapa_re']
            etiquetas   = dict(self._fields['etapa_re'].selection)

            for op in self:
                if not op.es_operacion_re:
                    continue

                etiqueta = etiquetas.get(nueva_etapa, nueva_etapa)

                # Sincronizar estado de la propiedad según etapa
                if op.propiedad_id:
                    mapa_estado = {
                        ETAPA_CAPTACION:    'disponible',
                        ETAPA_DIFUSION:     'disponible',
                        ETAPA_PROSPECTO:    'disponible',
                        ETAPA_NEGOCIACION:  'en_negociacion',
                        ETAPA_DOCUMENTACION:'en_negociacion',
                        ETAPA_CIERRE:       'en_negociacion',
                        ETAPA_CERRADA:      None,  # re.contrato gestiona el estado final
                    }
                    nuevo_estado_prop = mapa_estado.get(nueva_etapa)
                    if nuevo_estado_prop:
                        op.propiedad_id.write({'estado': nuevo_estado_prop})
                        _logger.info(
                            "🏠 Propiedad '%s' → %s (etapa operación: %s)",
                            op.propiedad_id.name,
                            nuevo_estado_prop,
                            nueva_etapa
                        )

                # Mensaje en Chatter
                op.message_post(
                    body=Markup(_(
                        "📊 <strong>Etapa actualizada: %(etapa)s</strong><br/>"
                        "Propiedad: <em>%(prop)s</em><br/>"
                        "%(extra)s"
                    )) % {
                        'etapa': etiqueta,
                        'prop':  op.propiedad_id.name
                                 if op.propiedad_id else '—',
                        'extra': (
                            _("Contrato: <strong>%(c)s</strong>") % {
                                'c': op.contrato_id.name
                            }
                            if op.contrato_id
                            and nueva_etapa in [ETAPA_CIERRE, ETAPA_CERRADA]
                            else ''
                        ),
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        return resultado

    # =========================================================================
    # OVERRIDE create — MARCAR COMO OPERACIÓN RE Y LOG INICIAL
    # =========================================================================

    @api.model
    def create(self, vals):
        """
        Fuerza es_operacion_re = True cuando se crea desde el contexto
        del vertical. Registra la captación en el Chatter.
        """
        # El contexto default_es_operacion_re=True viene de la acción de ventana
        if vals.get('es_operacion_re') and vals.get('propiedad_id'):
            propiedad = self.env['re.propiedad'].browse(
                vals['propiedad_id']
            )
            _logger.info(
                "📋 Nueva operación RE creada para propiedad '%s'",
                propiedad.name
            )

        op = super(ReOperacion, self).create(vals)

        if op.es_operacion_re:
            op.message_post(
                body=Markup(_(
                    "📋 <strong>Operación inmobiliaria iniciada.</strong><br/>"
                    "Propiedad: <strong>%(prop)s</strong><br/>"
                    "Tipo: <em>%(tipo)s</em><br/>"
                    "Asesor: <strong>%(asesor)s</strong>"
                )) % {
                    'prop':  op.propiedad_id.name
                             if op.propiedad_id else '—',
                    'tipo':  dict(
                        self._fields['tipo_operacion_re'].selection
                    ).get(op.tipo_operacion_re, _("Sin definir")),
                    'asesor': op.user_id.name if op.user_id else '—',
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        return op
