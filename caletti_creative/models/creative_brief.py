# caletti_creative/models/creative_brief.py
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

# === CONSTANTES: ESTADOS DEL BRIEF ===
ESTADO_BORRADOR    = 'borrador'
ESTADO_EN_REVISION = 'en_revision'
ESTADO_APROBADO    = 'aprobado'
ESTADO_RECHAZADO   = 'rechazado'

# === CONSTANTES: TONO DE COMUNICACIÓN ===
TONO_FORMAL        = 'formal'
TONO_CASUAL        = 'casual'
TONO_INSPIRACIONAL = 'inspiracional'
TONO_TECNICO       = 'tecnico'
TONO_HUMORISTICO   = 'humoristico'
TONO_EMOCIONAL     = 'emocional'
TONO_DIRECTO       = 'directo'
TONO_OTRO          = 'otro'

# === CONSTANTES: CANALES DE DISTRIBUCIÓN ===
CANAL_DIGITAL      = 'digital'
CANAL_IMPRESO      = 'impreso'
CANAL_REDES        = 'redes_sociales'
CANAL_VIDEO        = 'video'
CANAL_OOH          = 'ooh'          # Out of Home (espectaculares, vallas)
CANAL_EMAIL        = 'email'
CANAL_MIXTO        = 'mixto'


class CreativeBrief(models.Model):
    """
    Brief Creativo — Documento contractual y rector del proyecto creativo.

    Es el documento al que todo el equipo recurre durante la ejecución.
    Define: contexto del cliente, objetivos medibles, audiencia objetivo,
    mensaje clave, tono, canales de distribución, restricciones de marca
    y criterios de éxito.

    Lifecycle: borrador → en_revision → aprobado / rechazado

    Un proyecto puede tener un solo brief activo (aprobado).
    Se permiten múltiples versiones (rechazado → nuevo borrador).
    """
    _name = 'creative.brief'
    _description = 'Brief Creativo del Proyecto'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    # --- IDENTIFICACIÓN ---
    name = fields.Char(
        string='Título del Brief',
        required=True,
        tracking=True,
        help="Nombre corto que identifica este brief. Ej: 'Brief Campaña Verano 2026'"
    )

    proyecto_id = fields.Many2one(
        'tablero.tarea',
        string='Proyecto',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
        help="Proyecto creativo al que pertenece este brief"
    )

    # Cliente disponible desde el proyecto vía related — solo lectura
    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='proyecto_id.partner_id',
        store=True,
        readonly=True
    )

    version = fields.Integer(
        string='Versión',
        default=1,
        readonly=True,
        help="Número de versión del brief. Se incrementa automáticamente al rechazar y crear uno nuevo."
    )

    estado_brief = fields.Selection([
        (ESTADO_BORRADOR,    '📝 Borrador'),
        (ESTADO_EN_REVISION, '🔍 En Revisión'),
        (ESTADO_APROBADO,    '✅ Aprobado'),
        (ESTADO_RECHAZADO,   '❌ Rechazado'),
    ], string='Estado',
       default=ESTADO_BORRADOR,
       required=True,
       tracking=True
    )

    fecha_entrega_brief = fields.Date(
        string='Fecha Límite de Aprobación',
        tracking=True,
        help="Fecha límite para que el cliente apruebe o rechace este brief"
    )

    fecha_aprobacion = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True,
        help="Fecha y hora exacta en que el cliente aprobó el brief"
    )

    aprobado_por_id = fields.Many2one(
        'res.users',
        string='Aprobado por',
        readonly=True,
        help="Usuario que registró la aprobación del brief"
    )

    # --- SECCIÓN 1: CONTEXTO Y ANTECEDENTES ---
    antecedentes = fields.Text(
        string='Antecedentes del Cliente / Marca',
        tracking=True,
        help="Información sobre la marca, su historia, posicionamiento actual "
             "y contexto del mercado. ¿Qué sabemos del cliente?"
    )

    problema_oportunidad = fields.Text(
        string='Problema u Oportunidad',
        required=True,
        tracking=True,
        help="¿Qué problema resuelve este proyecto o qué oportunidad aprovecha? "
             "Es la razón de ser del trabajo creativo."
    )

    competencia = fields.Text(
        string='Contexto Competitivo',
        tracking=True,
        help="Análisis breve de la competencia. ¿Cómo se diferencia el cliente? "
             "¿Qué hace la competencia que debemos considerar o evitar?"
    )

    # --- SECCIÓN 2: OBJETIVOS ---
    objetivo_principal = fields.Text(
        string='Objetivo Principal',
        required=True,
        tracking=True,
        help="Objetivo SMART del proyecto. ¿Qué queremos lograr, para quién y cuándo? "
             "Debe ser medible al finalizar el proyecto."
    )

    objetivos_secundarios = fields.Text(
        string='Objetivos Secundarios',
        tracking=True,
        help="Objetivos de apoyo que contribuyen al objetivo principal."
    )

    criterios_exito = fields.Text(
        string='Criterios de Éxito / KPIs',
        tracking=True,
        help="¿Cómo sabremos que el proyecto fue exitoso? "
             "Define métricas concretas: impresiones, conversiones, alcance, etc."
    )

    # --- SECCIÓN 3: AUDIENCIA OBJETIVO ---
    audiencia_primaria = fields.Text(
        string='Audiencia Primaria',
        required=True,
        tracking=True,
        help="Perfil detallado del público principal: datos demográficos, "
             "comportamientos, intereses, necesidades y pain points."
    )

    audiencia_secundaria = fields.Text(
        string='Audiencia Secundaria',
        tracking=True,
        help="Público secundario o influenciadores de la decisión de compra."
    )

    # --- SECCIÓN 4: MENSAJE Y DIRECCIÓN CREATIVA ---
    mensaje_clave = fields.Text(
        string='Mensaje Clave',
        required=True,
        tracking=True,
        help="La idea central que debe comunicar todo el trabajo creativo. "
             "Una sola idea, clara y memorable."
    )

    propuesta_valor = fields.Text(
        string='Propuesta de Valor',
        tracking=True,
        help="¿Qué beneficio único ofrece el cliente a su audiencia? "
             "La razón por la que deben elegirlo."
    )

    tono_comunicacion = fields.Selection([
        (TONO_FORMAL,        'Formal / Profesional'),
        (TONO_CASUAL,        'Casual / Cercano'),
        (TONO_INSPIRACIONAL, 'Inspiracional / Aspiracional'),
        (TONO_TECNICO,       'Técnico / Especializado'),
        (TONO_HUMORISTICO,   'Humorístico / Divertido'),
        (TONO_EMOCIONAL,     'Emocional / Empático'),
        (TONO_DIRECTO,       'Directo / Informativo'),
        (TONO_OTRO,          'Otro (ver notas)'),
    ], string='Tono de Comunicación',
       required=True,
       #tracking=True
    )

    tono_notas = fields.Text(
        string='Notas sobre Tono y Estilo',
        #tracking=True,
        help="Los detalles adicionales sobre el estilo visual y verbal. "
             "Colores de marca, tipografías, referencias visuales, "
             "ejemplos de lo que SÍ y lo que NO se debe hacer."
    )

    # --- SECCIÓN 5: CANALES Y DISTRIBUCIÓN ---
    canal_principal = fields.Selection([
        (CANAL_DIGITAL,  'Digital (web, banners, email)'),
        (CANAL_IMPRESO,  'Impreso (revistas, flyers, catálogos)'),
        (CANAL_REDES,    'Redes Sociales'),
        (CANAL_VIDEO,    'Video (TV, YouTube, streaming)'),
        (CANAL_OOH,      'Out of Home (espectaculares, vallas)'),
        (CANAL_EMAIL,    'Email Marketing'),
        (CANAL_MIXTO,    'Mixto / Multiplataforma'),
    ], string='Canal Principal de Distribución',
       tracking=True
    )

    canales_descripcion = fields.Text(
        string='Detalle de Canales y Formatos',
        tracking=True,
        help="Especifica las plataformas exactas, formatos y dimensiones requeridas. "
             "Ej: Instagram Stories 1080x1920, Facebook Post 1200x628, etc."
    )

    # --- SECCIÓN 6: RESTRICCIONES Y CONSIDERACIONES ---
    restricciones_marca = fields.Text(
        string='Restricciones de Marca',
        tracking=True,
        help="Lo que NO se puede hacer: colores prohibidos, palabras vetadas, "
             "competidores que no se deben mencionar, guías de marca a respetar."
    )

    referencias_visuales = fields.Text(
        string='Referencias e Inspiración',
        tracking=True,
        help="URLs, ejemplos o descripciones de trabajos que el cliente admira "
             "o que sirven como referencia de dirección creativa."
    )

    consideraciones_legales = fields.Text(
        string='Consideraciones Legales / Regulatorias',
        tracking=True,
        help="Disclaimers obligatorios, restricciones legales del sector "
             "(farmacéutico, financiero, etc.), derechos de imagen."
    )

    # --- SECCIÓN 7: MOTIVOS DE RECHAZO (trazabilidad) ---
    motivo_rechazo = fields.Text(
        string='Motivo de Rechazo',
        tracking=True,
        readonly=True,
        help="Razón por la que el cliente rechazó este brief. "
             "Registrado automáticamente al ejecutar la acción de rechazo."
    )

    # --- CAMPO COMPUTED: RESUMEN DE ESTADO ---
    dias_para_vencimiento = fields.Integer(
        string='Días para Vencimiento',
        compute='_compute_dias_vencimiento',
        help="Días restantes para que venza la fecha límite de aprobación"
    )

    brief_vencido = fields.Boolean(
        string='Brief Vencido',
        compute='_compute_brief_vencido',
        store=True
    )

    # --- LÓGICA COMPUTED ---

    @api.depends('fecha_entrega_brief', 'estado_brief')
    def _compute_dias_vencimiento(self):
        """
        Calcula días restantes para aprobación del brief.
        Campo NO stored — se recalcula en cada lectura.
        """
        today = fields.Date.today()
        for brief in self:
            if (brief.fecha_entrega_brief and 
                brief.estado_brief in [ESTADO_BORRADOR, ESTADO_EN_REVISION]):
                brief.dias_para_vencimiento = (brief.fecha_entrega_brief - today).days
            else:
                brief.dias_para_vencimiento = 0

    @api.depends('fecha_entrega_brief', 'estado_brief')
    def _compute_brief_vencido(self):
        """
        Determina si el brief está vencido.
        Campo stored — permite búsquedas y filtros por vencimiento.
        """
        today = fields.Date.today()
        for brief in self:
            if (brief.fecha_entrega_brief and 
                brief.estado_brief in [ESTADO_BORRADOR, ESTADO_EN_REVISION]):
                brief.brief_vencido = brief.fecha_entrega_brief < today
            else:
                brief.brief_vencido = False

    # --- VALIDACIONES ---

    @api.constrains('estado_brief', 'proyecto_id')
    def _check_un_brief_aprobado(self):
        """
        Valida que no existan dos briefs aprobados para el mismo proyecto.
        Un proyecto solo puede tener un brief activo aprobado.
        """
        for brief in self:
            if brief.estado_brief == ESTADO_APROBADO:
                otros_aprobados = self.search([
                    ('proyecto_id', '=', brief.proyecto_id.id),
                    ('estado_brief', '=', ESTADO_APROBADO),
                    ('id', '!=', brief.id),
                ])
                if otros_aprobados:
                    raise ValidationError(_(
                        "El proyecto '%(proyecto)s' ya tiene un brief aprobado. "
                        "Rechaza el brief actual antes de aprobar uno nuevo."
                    ) % {'proyecto': brief.proyecto_id.name})

    @api.constrains('problema_oportunidad', 'objetivo_principal',
                    'audiencia_primaria', 'mensaje_clave')
    def _check_campos_criticos_aprobacion(self):
        """
        Los campos críticos del brief no pueden estar vacíos
        si el estado es 'en_revision' o 'aprobado'.
        """
        campos_criticos = [
            'problema_oportunidad', 'objetivo_principal',
            'audiencia_primaria', 'mensaje_clave'
        ]
        for brief in self:
            if brief.estado_brief in [ESTADO_EN_REVISION, ESTADO_APROBADO]:
                faltantes = [
                    f for f in campos_criticos
                    if not getattr(brief, f)
                ]
                if faltantes:
                    raise ValidationError(_(
                        "Para enviar a revisión o aprobar el brief, "
                        "completa los campos obligatorios: %s"
                    ) % ', '.join(faltantes))

    # --- ACCIONES DE WORKFLOW ---

    def action_enviar_a_revision(self):
        """
        Cambia el estado del brief a 'en_revision' y notifica
        al equipo via Chatter que el brief está listo para revisión del cliente.
        """
        self.ensure_one()
        if self.estado_brief != ESTADO_BORRADOR:
            raise UserError(_(
                "Solo se puede enviar a revisión un brief en estado Borrador."
            ))

        self.write({'estado_brief': ESTADO_EN_REVISION})

        # Notificación interna en Chatter
        self.message_post(
            body=Markup(_(
                "📋 <strong>Brief enviado a revisión.</strong><br/>"
                "El brief <em>%(nombre)s</em> está listo para revisión "
                "y aprobación del cliente."
            )) % {'nombre': self.name},
            subject=_("Brief en Revisión"),
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        # Email al cliente
        if self.cliente_id and self.cliente_id.email:
            try:
                template = self.env.ref(
                    'caletti_creative.email_template_brief_revision',
                    raise_if_not_found=False
                )
                if template:
                    template.send_mail(self.id, force_send=True)
                    _logger.info(
                        "✉️ Brief '%s' enviado a revisión — email a %s",
                        self.name, self.cliente_id.email
                    )
            except Exception as e:
                _logger.error(
                    "❌ Error enviando email de brief a revisión '%s': %s",
                    self.name, str(e)
                )
        else:
            _logger.warning(
                "⚠️ Brief '%s' enviado a revisión sin email de cliente",
                self.name
            )

        _logger.info(
            "📋 Brief '%s' del proyecto '%s' enviado a revisión",
            self.name, self.proyecto_id.name
        )

    def action_aprobar(self):
        """
        Aprueba el brief, registra fecha y usuario,
        notifica al equipo interno que pueden iniciar producción.
        """
        self.ensure_one()
        if self.estado_brief != ESTADO_EN_REVISION:
            raise UserError(_(
                "Solo se puede aprobar un brief que está En Revisión."
            ))

        ahora = fields.Datetime.now()
        self.write({
            'estado_brief': ESTADO_APROBADO,
            'fecha_aprobacion': ahora,
            'aprobado_por_id': self.env.user.id,
        })

        # Notificación interna en Chatter
        self.message_post(
            body=Markup(_(
                "✅ <strong>¡Brief Aprobado!</strong><br/>"
                "Aprobado por: <strong>%(usuario)s</strong><br/>"
                "Fecha: <strong>%(fecha)s</strong><br/><br/>"
                "El equipo puede iniciar la producción creativa."
            )) % {
                'usuario': self.env.user.name,
                'fecha': ahora.strftime('%d/%m/%Y %H:%M'),
            },
            subject=_("Brief Aprobado — ¡Producción Autorizada!"),
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        # Notificar también en el Chatter del proyecto padre
        self.proyecto_id.message_post(
            body=Markup(_(
                "✅ <strong>Brief Aprobado por el Cliente.</strong><br/>"
                "El brief <em>%(brief)s</em> fue aprobado por "
                "<strong>%(usuario)s</strong>.<br/>"
                "El equipo puede iniciar la producción creativa."
            )) % {
                'brief': self.name,
                'usuario': self.env.user.name,
            },
            subject=_("Brief Aprobado — Producción Autorizada"),
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )
        _logger.info(
            "✅ Notificación de brief aprobado registrada "
            "en proyecto '%s'",
            self.proyecto_id.name
        )

        # Email al equipo interno
        try:
            template = self.env.ref(
                'caletti_creative.email_template_brief_aprobado',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(self.id, force_send=True)
                _logger.info(
                    "✉️ Email de brief aprobado enviado — proyecto '%s'",
                    self.proyecto_id.name
                )
        except Exception as e:
            _logger.error(
                "❌ Error enviando email de brief aprobado '%s': %s",
                self.name, str(e)
            )

        _logger.info(
            "✅ Brief '%s' aprobado por %s",
            self.name, self.env.user.name
        )
        

    def action_rechazar(self, motivo=''):
        """
        Rechaza el brief con registro del motivo.
        El motivo se registra en Chatter y en el campo motivo_rechazo
        para trazabilidad completa.
        """
        self.ensure_one()
        if self.estado_brief not in [ESTADO_EN_REVISION, ESTADO_BORRADOR]:
            raise UserError(_(
                "Solo se puede rechazar un brief en Borrador o En Revisión."
            ))

        self.write({
            'estado_brief': ESTADO_RECHAZADO,
            'motivo_rechazo': motivo or _("Sin motivo especificado."),
        })
        self.message_post(
            body=_(
                "❌ <strong>Brief Rechazado.</strong><br/>"
                "Motivo: %(motivo)s<br/><br/>"
                "Se requiere crear una nueva versión del brief "
                "incorporando los cambios solicitados."
            ) % {'motivo': motivo or _("Sin motivo especificado.")},
            subject=_("Brief Rechazado — Requiere Revisión")
        )
        _logger.warning(
            "❌ Brief '%s' rechazado. Motivo: %s",
            self.name, motivo
        )

        # Notificar en el Chatter del proyecto padre
        self.proyecto_id.message_post(
            body=Markup(_(
                "❌ <strong>Brief Rechazado por el Cliente.</strong><br/>"
                "El brief <em>%(brief)s</em> fue rechazado.<br/>"
                "Motivo: %(motivo)s"
            )) % {
                'brief': self.name,
                'motivo': motivo or _("Sin motivo especificado."),
            },
            subject=_("Brief Rechazado — Requiere Nueva Versión"),
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    def action_nueva_version(self):
        """
        Crea una nueva versión del brief basándose en el rechazado.
        Copia todos los campos al nuevo registro con estado Borrador
        y versión incrementada para mantener trazabilidad histórica.
        """
        self.ensure_one()
        if self.estado_brief != ESTADO_RECHAZADO:
            raise UserError(_(
                "Solo se puede crear nueva versión de un brief Rechazado."
            ))

        nueva_version = self.copy({
            'name': f"{self.name} (v{self.version + 1})",
            'version': self.version + 1,
            'estado_brief': ESTADO_BORRADOR,
            'fecha_aprobacion': False,
            'aprobado_por_id': False,
            'motivo_rechazo': False,
        })

        self.message_post(
            body=_(
                "🔄 Nueva versión del brief creada: "
                "<strong>%(nombre)s</strong>"
            ) % {'nombre': nueva_version.name},
            subject=_("Nueva Versión de Brief Creada")
        )
        _logger.info(
            "🔄 Nueva versión de brief creada: '%s' → '%s'",
            self.name, nueva_version.name
        )

        # Redirigir al nuevo brief
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'creative.brief',
            'res_id': nueva_version.id,
            'view_mode': 'form',
            'target': 'current',
        }