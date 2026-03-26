# caletti_creative/models/creative_project.py
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

# === CONSTANTES: TIPOS DE PROYECTO ===
TIPO_BRANDING     = 'branding'
TIPO_CAMPANA      = 'campana'
TIPO_WEB          = 'web'
TIPO_SOCIAL_MEDIA = 'social_media'
TIPO_VIDEO        = 'video'
TIPO_FOTOGRAFIA   = 'fotografia'
TIPO_EDITORIAL    = 'editorial'
TIPO_OTRO         = 'otro'

# === CONSTANTES: ESTADOS DE PRESUPUESTO ===
PRESUPUESTO_OK        = 'ok'
PRESUPUESTO_ALERTA    = 'alerta'    # > 80% consumido
PRESUPUESTO_EXCEDIDO  = 'excedido'  # > 100% consumido

# Umbrales para alertas de presupuesto
UMBRAL_ALERTA_PRESUPUESTO   = 80.0
UMBRAL_EXCEDIDO_PRESUPUESTO = 100.0


class CreativeProject(models.Model):
    """
    Extensión del modelo tablero.tarea para proyectos de agencias creativas.
    
    Agrega sobre el Core:
    - Tipo de proyecto creativo
    - Brief creativo integrado (One2many → creative.brief)
    - Equipo creativo con roles (One2many → creative.team.member)
    - Entregables propios del vertical (One2many → creative.deliverable)
    - Presupuesto aprobado + seguimiento de costo real computed
    
    El Core provee: name, state, progress, partner_id, user_id,
    date_deadline, is_overdue, kanban_state, chatter, portal.
    Este modelo NO duplica ni modifica esa lógica.
    """
    _inherit = 'tablero.tarea'

    # --- IDENTIFICACIÓN DEL VERTICAL ---
    # Flag para distinguir proyectos creativos de tareas genéricas del Core
    es_proyecto_creativo = fields.Boolean(
        string='Es Proyecto Creativo',
        default=False,
        help="Marca esta tarea como un proyecto del vertical creativo"
    )

    tipo_proyecto = fields.Selection([
        (TIPO_BRANDING,     'Branding / Identidad'),
        (TIPO_CAMPANA,      'Campaña Publicitaria'),
        (TIPO_WEB,          'Sitio Web / Digital'),
        (TIPO_SOCIAL_MEDIA, 'Social Media'),
        (TIPO_VIDEO,        'Video / Animación'),
        (TIPO_FOTOGRAFIA,   'Fotografía'),
        (TIPO_EDITORIAL,    'Editorial / Impreso'),
        (TIPO_OTRO,         'Otro'),
    ], string='Tipo de Proyecto', tracking=True)

    # --- PRESUPUESTO ---
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    presupuesto_aprobado = fields.Monetary(
        string='Presupuesto Aprobado',
        currency_field='currency_id',
        tracking=True,
        help="Monto total aprobado por el cliente para este proyecto"
    )

    costo_real = fields.Monetary(
        string='Costo Real Acumulado',
        currency_field='currency_id',
        compute='_compute_costo_real',
        store=True,
        help="Suma de costos estimados de todos los entregables del proyecto"
    )

    presupuesto_consumido_pct = fields.Float(
        string='Presupuesto Consumido (%)',
        compute='_compute_presupuesto_consumido',
        store=True,
        help="Porcentaje del presupuesto aprobado que representa el costo real"
    )

    estado_presupuesto = fields.Selection([
        (PRESUPUESTO_OK,       '✅ En presupuesto'),
        (PRESUPUESTO_ALERTA,   '⚠️ Alerta (>80%)'),
        (PRESUPUESTO_EXCEDIDO, '🔴 Excedido'),
    ], string='Estado Presupuesto',
       compute='_compute_presupuesto_consumido',
       store=True)

    # --- RELACIONES CON MODELOS PROPIOS DEL VERTICAL ---
    brief_ids = fields.One2many(
        'creative.brief',
        'proyecto_id',
        string='Brief Creativo',
        help="Brief del proyecto. Se recomienda un brief por proyecto."
    )

    equipo_ids = fields.One2many(
        'creative.team.member',
        'proyecto_id',
        string='Equipo Creativo'
    )

    entregable_ids = fields.One2many(
        'creative.deliverable',
        'proyecto_id',
        string='Entregables'
    )

    # --- CAMPOS COMPUTED DE RESUMEN ---
    brief_count = fields.Integer(
        string='Briefs',
        compute='_compute_resumen_counts',
        store=True
    )

    entregable_count = fields.Integer(
        string='Entregables',
        compute='_compute_resumen_counts',
        store=True
    )

    entregable_aprobado_count = fields.Integer(
        string='Entregables Aprobados',
        compute='_compute_resumen_counts',
        store=True
    )

    brief_aprobado = fields.Boolean(
        string='Brief Aprobado',
        compute='_compute_brief_aprobado',
        store=True,
        help="True si existe al menos un brief en estado 'aprobado'"
    )

    # --- LÓGICA COMPUTED ---

    @api.depends('entregable_ids.costo_estimado')
    def _compute_costo_real(self):
        """Suma los costos estimados de todos los entregables del proyecto"""
        for project in self:
            project.costo_real = sum(
                project.entregable_ids.mapped('costo_estimado')
            )
            _logger.debug(
                "💰 Proyecto '%s': costo_real recalculado → %s",
                project.name, project.costo_real
            )

    @api.depends('costo_real', 'presupuesto_aprobado')
    def _compute_presupuesto_consumido(self):
        """
        Calcula el porcentaje de presupuesto consumido y
        determina el estado de alerta correspondiente.
        """
        for project in self:
            if project.presupuesto_aprobado > 0:
                pct = (project.costo_real / project.presupuesto_aprobado) * 100.0
                project.presupuesto_consumido_pct = pct

                if pct >= UMBRAL_EXCEDIDO_PRESUPUESTO:
                    project.estado_presupuesto = PRESUPUESTO_EXCEDIDO
                    _logger.warning(
                        "🔴 Proyecto '%s' EXCEDIÓ el presupuesto: %.1f%%",
                        project.name, pct
                    )
                elif pct >= UMBRAL_ALERTA_PRESUPUESTO:
                    project.estado_presupuesto = PRESUPUESTO_ALERTA
                    _logger.info(
                        "⚠️ Proyecto '%s' en alerta de presupuesto: %.1f%%",
                        project.name, pct
                    )
                else:
                    project.estado_presupuesto = PRESUPUESTO_OK
            else:
                project.presupuesto_consumido_pct = 0.0
                project.estado_presupuesto = PRESUPUESTO_OK

    @api.depends('brief_ids', 'entregable_ids', 'entregable_ids.estado')
    def _compute_resumen_counts(self):
        """Contadores de resumen para mostrar en la vista kanban y form"""
        for project in self:
            project.brief_count = len(project.brief_ids)
            project.entregable_count = len(project.entregable_ids)
            project.entregable_aprobado_count = len(
                project.entregable_ids.filtered(
                    lambda e: e.estado == 'aprobado'
                )
            )

    @api.depends('brief_ids.estado_brief')
    def _compute_brief_aprobado(self):
        """Verifica si existe al menos un brief aprobado por el cliente"""
        for project in self:
            project.brief_aprobado = any(
                b.estado_brief == 'aprobado'
                for b in project.brief_ids
            )

    # --- VALIDACIONES ---
    @api.constrains('presupuesto_aprobado')
    def _check_presupuesto_positivo(self):
        """El presupuesto no puede ser negativo"""
        for project in self:
            if project.presupuesto_aprobado < 0:
                raise ValidationError(
                    _("El presupuesto aprobado no puede ser negativo.")
                )

    # --- OVERRIDE write PARA ALERTAS AUTOMÁTICAS ---
    def write(self, vals):
        """
        Extiende el write del Core para emitir alertas en Chatter
        cuando el presupuesto entra en zona de riesgo.
        """
        result = super(CreativeProject, self).write(vals)

        # Revisar estado de presupuesto después de cualquier cambio
        # Solo para proyectos creativos con presupuesto definido
        if any(f in vals for f in ['presupuesto_aprobado', 'entregable_ids']):
            for project in self.filtered(
                lambda p: p.es_proyecto_creativo and p.presupuesto_aprobado > 0
            ):
                if project.estado_presupuesto == PRESUPUESTO_EXCEDIDO:
                    project.message_post(
                        body=_(
                            "🔴 <strong>Alerta de Presupuesto:</strong> "
                            "El costo real del proyecto ha excedido el "
                            "presupuesto aprobado (%(pct).1f%% consumido)."
                        ) % {'pct': project.presupuesto_consumido_pct},
                        subject=_("Presupuesto Excedido")
                    )
                elif project.estado_presupuesto == PRESUPUESTO_ALERTA:
                    project.message_post(
                        body=_(
                            "⚠️ <strong>Aviso:</strong> El proyecto ha "
                            "consumido el %(pct).1f%% del presupuesto aprobado."
                        ) % {'pct': project.presupuesto_consumido_pct},
                        subject=_("Alerta de Presupuesto")
                    )

        return result