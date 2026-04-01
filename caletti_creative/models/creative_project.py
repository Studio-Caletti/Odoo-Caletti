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
PRESUPUESTO_ALERTA    = 'alerta'
PRESUPUESTO_EXCEDIDO  = 'excedido'

UMBRAL_ALERTA_PRESUPUESTO   = 80.0
UMBRAL_EXCEDIDO_PRESUPUESTO = 100.0


class CreativeProject(models.Model):
    """
    Extensión del modelo tablero.tarea para proyectos de agencias creativas.
    """
    _inherit = 'tablero.tarea'

    # --- IDENTIFICACIÓN DEL VERTICAL ---
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
        string='Total Entregables',
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
    )

    # --- LÓGICA COMPUTED ---

    @api.depends('entregable_ids.costo_estimado')
    def _compute_costo_real(self):
        """Suma los costos estimados de todos los entregables del proyecto"""
        for project in self:
            project.costo_real = sum(
                project.entregable_ids.mapped('costo_estimado')
            )

    @api.depends('costo_real', 'presupuesto_aprobado')
    def _compute_presupuesto_consumido(self):
        """Calcula el porcentaje de presupuesto consumido."""
        for project in self:
            if project.presupuesto_aprobado > 0:
                pct = (project.costo_real / project.presupuesto_aprobado) * 100.0
                project.presupuesto_consumido_pct = pct
                if pct >= UMBRAL_EXCEDIDO_PRESUPUESTO:
                    project.estado_presupuesto = PRESUPUESTO_EXCEDIDO
                elif pct >= UMBRAL_ALERTA_PRESUPUESTO:
                    project.estado_presupuesto = PRESUPUESTO_ALERTA
                else:
                    project.estado_presupuesto = PRESUPUESTO_OK
            else:
                project.presupuesto_consumido_pct = 0.0
                project.estado_presupuesto = PRESUPUESTO_OK

    @api.depends('brief_ids', 'entregable_ids', 'entregable_ids.estado')
    def _compute_resumen_counts(self):
        """Contadores de resumen"""
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
        """Verifica si existe al menos un brief aprobado"""
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

    # --- OVERRIDE create PARA NOTIFICACIÓN AL CLIENTE ---

    @api.model
    def create(self, vals):
        """
        Notifica al cliente cuando se registra un nuevo proyecto creativo.
        Solo dispara si el proyecto tiene cliente asignado.
        """
        project = super(CreativeProject, self).create(vals)

        if project.es_proyecto_creativo and project.partner_id:
            _logger.info(
                "📧 Intentando enviar email de registro para '%s' a '%s'",
                project.name,
                project.partner_id.email or 'SIN EMAIL'
            )
            try:
                template = self.env.ref(
                    'caletti_creative.email_template_proyecto_registrado',
                    raise_if_not_found=False
                )
                if not template:
                    _logger.error(
                        "❌ Template no encontrado: "
                        "email_template_proyecto_registrado"
                    )
                    return project

                _logger.info(
                    "✅ Template encontrado: %s (ID: %s)",
                    template.name, template.id
                )

                if not project.partner_id.email:
                    _logger.warning(
                        "⚠️ Partner '%s' sin email — no se envía",
                        project.partner_id.name
                    )
                    return project

                template.send_mail(project.id, force_send=True)
                _logger.info(
                    "✉️ Email enviado exitosamente para '%s'",
                    project.name
                )

            except Exception as e:
                _logger.error(
                    "❌ Error DETALLADO enviando email para '%s': %s",
                    project.name, str(e),
                    exc_info=True
                )
        else:
            _logger.warning(
                "⚠️ No se envía email: es_creativo=%s, partner=%s",
                project.es_proyecto_creativo,
                project.partner_id.name if project.partner_id else 'NINGUNO'
            )

        return project

    # --- CREACIÓN DESDE EMAIL ENTRANTE ---

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
        Crea un proyecto creativo desde email entrante al alias
        creativos@caletti.com.mx — mismo patrón que helpdesk.
        """
        if custom_values is None:
            custom_values = {}

        email_from = msg_dict.get('email_from', '')
        subject    = msg_dict.get('subject', 'Proyecto sin asunto')

        partner = self.env['res.partner'].search(
            [('email', '=ilike', email_from)], limit=1
        )

        defaults = {
            'name': subject,
            'es_proyecto_creativo': True,
            'state': 'nuevo',
        }

        if partner:
            defaults['partner_id'] = partner.id

        defaults.update(custom_values)

        _logger.info(
            "📧 Proyecto creativo creado desde email: '%s' — De: %s",
            subject, email_from
        )

        return super(CreativeProject, self).message_new(
            msg_dict, custom_values=defaults
        )
        