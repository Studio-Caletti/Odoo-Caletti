# caletti_real_estate/models/re_prospecto.py
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

# =============================================================================
# CONSTANTES: ETAPAS DEL PIPELINE
# Flujo lineal con posibilidad de descarte en cualquier punto
# =============================================================================
ETAPA_NUEVO          = 'nuevo'
ETAPA_CONTACTADO     = 'contactado'
ETAPA_VISITA_AGEND   = 'visita_agendada'
ETAPA_VISITA_REAL    = 'visita_realizada'
ETAPA_INVESTIGACION  = 'investigacion'
ETAPA_NEGOCIACION    = 'negociacion'
ETAPA_CERRADO        = 'cerrado'
ETAPA_DESCARTADO     = 'descartado'

# =============================================================================
# CONSTANTES: TIPO DE OPERACIÓN DE INTERÉS
# =============================================================================
INTERES_RENTA  = 'renta'
INTERES_VENTA  = 'venta'
INTERES_AMBAS  = 'ambas'

# =============================================================================
# CONSTANTES: FUENTES DE CAPTACIÓN
# Crítico para medir ROI de canales de marketing del asesor
# =============================================================================
FUENTE_REFERIDO      = 'referido'
FUENTE_PORTAL_WEB    = 'portal_web'
FUENTE_REDES         = 'redes_sociales'
FUENTE_LAMUDI        = 'lamudi'
FUENTE_INMUEBLES24   = 'inmuebles24'
FUENTE_VIVANUNCIOS   = 'vivanuncios'
FUENTE_WHATSAPP      = 'whatsapp'
FUENTE_LLAMADA       = 'llamada_directa'
FUENTE_CARTEL        = 'cartel_en_propiedad'
FUENTE_OTRO          = 'otro'

# =============================================================================
# CONSTANTES: CALIFICACIÓN DEL PROSPECTO
# Basada en capacidad económica verificada y urgencia de decisión
# =============================================================================
CALIF_CALIENTE = 'caliente'   # Listo para cerrar, tiene recursos
CALIF_TIBIO    = 'tibio'      # Interesado pero en proceso de decidir
CALIF_FRIO     = 'frio'       # Apenas explorando, sin urgencia

# =============================================================================
# CONSTANTES: MOTIVOS DE DESCARTE
# Trazabilidad para análisis de pipeline y mejora del proceso
# =============================================================================
DESCARTE_PRECIO        = 'precio_fuera_rango'
DESCARTE_ZONA          = 'zona_no_conveniente'
DESCARTE_CARACTERIST   = 'caracteristicas_no_match'
DESCARTE_CREDITO       = 'credito_no_aprobado'
DESCARTE_INVESTIGACION = 'investigacion_negativa'
DESCARTE_DESISTIO      = 'prospecto_desistio'
DESCARTE_CERRO_OTRO    = 'cerro_con_otro_asesor'
DESCARTE_OTRO          = 'otro'

# =============================================================================
# CONSTANTE: PRESUPUESTO — rango máximo de búsqueda
# =============================================================================
PRESUPUESTO_BAJO  = 'bajo'    # < 5,000 MXN renta / < 500k venta
PRESUPUESTO_MEDIO = 'medio'   # 5k-15k renta / 500k-2M venta
PRESUPUESTO_ALTO  = 'alto'    # > 15k renta / > 2M venta


class ReProspecto(models.Model):
    """
    Prospecto inmobiliario — Lead de captación del asesor.

    Representa a una persona o empresa interesada en rentar o comprar
    una o más propiedades de la cartera del asesor.

    Pipeline: nuevo → contactado → visita_agendada → visita_realizada
              → investigacion → negociacion → cerrado / descartado

    Relación con propiedades: Many2many — un prospecto puede estar
    interesado en múltiples propiedades simultáneamente (el asesor
    le muestra varias opciones antes de que decida).

    Las visitas se registran como mail.activity (tipo personalizado).
    re.visita reservado para v2.0 — administradoras con cartera >50
    propiedades activas que requieran métricas de conversión por visita.

    Al cerrar el prospecto, se vincula al re.contrato generado.
    El cierre actualiza automáticamente el estado de la propiedad
    seleccionada a 'en_negociacion' via chatter.
    """
    _name = 're.prospecto'
    _description = 'Prospecto Inmobiliario — Caletti Real Estate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'etapa asc, calificacion asc, date_contacto desc'

    # =========================================================================
    # SECCIÓN 1: IDENTIFICACIÓN DEL PROSPECTO
    # =========================================================================

    name = fields.Char(
        string='Nombre del Prospecto',
        required=True,
        index=True,
        tracking=True,
        help="Nombre completo de la persona o razón social de la empresa"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto en Odoo',
        index=True,
        tracking=True,
        help="Vincula este prospecto a un contacto existente en Odoo. "
             "Opcional — el asesor puede registrar el lead sin contacto previo."
    )

    telefono = fields.Char(
        string='Teléfono / WhatsApp',
        tracking=True,
        help="Número principal de contacto. Incluir código de país. Ej: +52 55 1234 5678"
    )

    email = fields.Char(
        string='Correo Electrónico',
        tracking=True
    )

    empresa = fields.Char(
        string='Empresa / Organización',
        tracking=True,
        help="Para prospectos corporativos: razón social o nombre comercial"
    )

    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor Responsable',
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
        help="Asesor que captó y gestiona este prospecto"
    )

    # =========================================================================
    # SECCIÓN 2: CLASIFICACIÓN Y FUENTE
    # =========================================================================

    etapa = fields.Selection([
        (ETAPA_NUEVO,         '🆕 Nuevo Lead'),
        (ETAPA_CONTACTADO,    '📞 Contactado'),
        (ETAPA_VISITA_AGEND,  '📅 Visita Agendada'),
        (ETAPA_VISITA_REAL,   '🏠 Visita Realizada'),
        (ETAPA_INVESTIGACION, '🔍 En Investigación'),
        (ETAPA_NEGOCIACION,   '🤝 En Negociación'),
        (ETAPA_CERRADO,       '✅ Cerrado'),
        (ETAPA_DESCARTADO,    '❌ Descartado'),
    ], string='Etapa del Pipeline',
       default=ETAPA_NUEVO,
       required=True,
       tracking=True,
       index=True
    )

    calificacion = fields.Selection([
        (CALIF_CALIENTE, '🔥 Caliente — Listo para cerrar'),
        (CALIF_TIBIO,    '🌡️ Tibio — Evaluando opciones'),
        (CALIF_FRIO,     '❄️ Frío — Explorando mercado'),
    ], string='Calificación',
       default=CALIF_TIBIO,
       required=True,
       tracking=True,
       help="Temperatura del lead basada en urgencia y capacidad económica verificada"
    )

    fuente_captacion = fields.Selection([
        (FUENTE_REFERIDO,    '👥 Referido de cliente'),
        (FUENTE_PORTAL_WEB,  '🌐 Portal Web Caletti'),
        (FUENTE_REDES,       '📱 Redes Sociales'),
        (FUENTE_LAMUDI,      '🏠 Lamudi'),
        (FUENTE_INMUEBLES24, '🏘️ Inmuebles24'),
        (FUENTE_VIVANUNCIOS, '📢 Vivanuncios'),
        (FUENTE_WHATSAPP,    '💬 WhatsApp Directo'),
        (FUENTE_LLAMADA,     '📞 Llamada Directa'),
        (FUENTE_CARTEL,      '🪧 Cartel en Propiedad'),
        (FUENTE_OTRO,        '📋 Otro'),
    ], string='Fuente de Captación',
       tracking=True,
       help="Canal por el que el prospecto llegó al asesor. "
            "Fundamental para medir ROI de canales de marketing."
    )

    tipo_interes = fields.Selection([
        (INTERES_RENTA, '🔑 Renta'),
        (INTERES_VENTA, '💰 Compra'),
        (INTERES_AMBAS, '🔑💰 Renta o Compra'),
    ], string='Tipo de Operación de Interés',
       required=True,
       tracking=True,
       default=INTERES_RENTA
    )

    # =========================================================================
    # SECCIÓN 3: PROPIEDADES DE INTERÉS (Many2many — núcleo del sprint)
    # =========================================================================

    propiedad_ids = fields.Many2many(
        're.propiedad',
        'rel_prospecto_propiedad',   # tabla intermedia explícita
        'prospecto_id',
        'propiedad_id',
        string='Propiedades de Interés',
        tracking=True,
        help="El prospecto puede evaluar múltiples propiedades simultáneamente. "
             "El asesor las agrega conforme las va mostrando. "
             "Al cerrar, se selecciona la propiedad final en 'Propiedad Elegida'."
    )

    propiedad_count = fields.Integer(
        string='Propiedades Evaluadas',
        compute='_compute_propiedad_count',
        store=True
    )

    # Propiedad final elegida al momento del cierre
    propiedad_elegida_id = fields.Many2one(
        're.propiedad',
        string='Propiedad Elegida',
        tracking=True,
        help="La propiedad seleccionada para formalizar el contrato. "
             "Debe pertenecer a las propiedades de interés del prospecto."
    )

    # =========================================================================
    # SECCIÓN 4: CRITERIOS DE BÚSQUEDA
    # Permiten al asesor hacer matching con propiedades disponibles
    # =========================================================================

    zona_interes = fields.Char(
        string='Zona / Colonia de Interés',
        tracking=True,
        help="Colonias, municipios o zonas donde el prospecto busca. "
             "Ej: 'Del Valle, Narvarte, Roma Norte'"
    )

    presupuesto_nivel = fields.Selection([
        (PRESUPUESTO_BAJO,  '🟢 Bajo  (< $5k renta / < $500k compra)'),
        (PRESUPUESTO_MEDIO, '🟡 Medio ($5k-$15k renta / $500k-$2M compra)'),
        (PRESUPUESTO_ALTO,  '🔴 Alto  (> $15k renta / > $2M compra)'),
    ], string='Rango de Presupuesto',
       tracking=True,
       help="Clasificación rápida del presupuesto declarado por el prospecto"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    presupuesto_min = fields.Monetary(
        string='Presupuesto Mínimo',
        currency_field='currency_id',
        tracking=True,
        help="Monto mínimo que el prospecto puede/quiere pagar"
    )

    presupuesto_max = fields.Monetary(
        string='Presupuesto Máximo',
        currency_field='currency_id',
        tracking=True,
        help="Monto máximo que el prospecto puede pagar. "
             "Para venta: incluir capacidad de crédito hipotecario si aplica."
    )

    recamaras_min = fields.Integer(
        string='Recámaras Mínimas',
        help="Número mínimo de recámaras requerido. Solo para residencial."
    )

    m2_min = fields.Float(
        string='M² Mínimos',
        digits=(10, 0),
        help="Superficie mínima requerida en metros cuadrados"
    )

    tipo_propiedad_interes = fields.Selection([
        ('residencial', '🏠 Residencial'),
        ('comercial',   '🏢 Comercial'),
        ('terreno',     '🌿 Terreno'),
        ('cualquiera',  '🔍 Cualquiera'),
    ], string='Tipo de Propiedad Buscada',
       default='residencial',
       tracking=True
    )

    requiere_estacionamiento = fields.Boolean(
        string='Requiere Estacionamiento',
        default=False
    )

    requiere_amueblado = fields.Boolean(
        string='Requiere Amueblado',
        default=False
    )

    notas_busqueda = fields.Text(
        string='Criterios Adicionales de Búsqueda',
        help="Preferencias específicas: planta baja, mascotas, jardín, "
             "número de baños, uso de suelo, amenidades requeridas, etc."
    )

    # =========================================================================
    # SECCIÓN 5: FECHAS Y SEGUIMIENTO
    # =========================================================================

    date_captacion = fields.Date(
        string='Fecha de Captación',
        default=fields.Date.today,
        required=True,
        tracking=True,
        help="Fecha en que el asesor registró el lead por primera vez"
    )

    date_contacto = fields.Date(
        string='Fecha de Primer Contacto',
        tracking=True,
        help="Fecha en que se estableció el primer contacto real con el prospecto"
    )

    date_visita = fields.Date(
        string='Fecha de Última Visita',
        tracking=True,
        help="Fecha de la visita más reciente a alguna propiedad. "
             "Las visitas se agendan como actividades en el Chatter."
    )

    date_cierre_estimado = fields.Date(
        string='Fecha Estimada de Cierre',
        tracking=True,
        help="Fecha en que el asesor estima que se firmará el contrato"
    )

    date_cierre_real = fields.Date(
        string='Fecha de Cierre Real',
        readonly=True,
        tracking=True,
        help="Fecha en que efectivamente se cerró la operación"
    )

    dias_en_pipeline = fields.Integer(
        string='Días en Pipeline',
        compute='_compute_dias_pipeline',
        help="Días transcurridos desde la captación del lead"
    )

    # =========================================================================
    # SECCIÓN 6: INVESTIGACIÓN SOCIOECONÓMICA
    # Aplica principalmente para renta — investigación del inquilino
    # =========================================================================

    requiere_investigacion = fields.Boolean(
        string='Requiere Investigación',
        default=True,
        help="Marcar si se debe realizar investigación socioeconómica "
             "antes de proceder con el contrato. Estándar para renta."
    )

    investigacion_completada = fields.Boolean(
        string='Investigación Completada',
        tracking=True,
        help="El asesor confirma que la investigación socioeconómica "
             "fue completada y el resultado es favorable"
    )

    resultado_investigacion = fields.Selection([
        ('aprobado',          '✅ Aprobado'),
        ('aprobado_con_obs',  '⚠️ Aprobado con Observaciones'),
        ('rechazado',         '❌ Rechazado'),
        ('pendiente',         '⏳ Pendiente'),
    ], string='Resultado de Investigación',
       tracking=True,
       default='pendiente'
    )

    notas_investigacion = fields.Text(
        string='Notas de Investigación',
        tracking=True,
        help="Documentos revisados, referencias contactadas, "
             "historial crediticio, observaciones del proceso."
    )

    # =========================================================================
    # SECCIÓN 7: CIERRE Y DESCARTE
    # =========================================================================

    motivo_descarte = fields.Selection([
        (DESCARTE_PRECIO,        '💰 Precio fuera de rango'),
        (DESCARTE_ZONA,          '📍 Zona no conveniente'),
        (DESCARTE_CARACTERIST,   '🏠 Características no match'),
        (DESCARTE_CREDITO,       '🏦 Crédito no aprobado'),
        (DESCARTE_INVESTIGACION, '🔍 Investigación negativa'),
        (DESCARTE_DESISTIO,      '🚶 Prospecto desistió'),
        (DESCARTE_CERRO_OTRO,    '🤝 Cerró con otro asesor'),
        (DESCARTE_OTRO,          '📋 Otro motivo'),
    ], string='Motivo de Descarte',
       tracking=True,
       help="Razón por la que el prospecto no cerró operación. "
            "Esencial para análisis de pipeline y mejora del proceso."
    )

    notas_descarte = fields.Text(
        string='Notas del Descarte',
        tracking=True,
        help="Detalle adicional sobre el motivo de descarte. "
             "Ej: precio específico que buscaba, zona exacta, competidor."
    )

    # Vínculo al contrato generado al cerrar
    contrato_id = fields.Many2one(
        're.contrato',
        string='Contrato Generado',
        readonly=True,
        tracking=True,
        help="Contrato de renta o compraventa generado al cerrar este prospecto"
    )

    # =========================================================================
    # SECCIÓN 8: NOTAS GENERALES
    # =========================================================================

    notas = fields.Text(
        string='Notas del Asesor',
        help="Observaciones generales del proceso: preferencias especiales, "
             "condiciones particulares, historial de la relación."
    )

    color = fields.Integer(string='Color Index', default=0)

    # =========================================================================
    # INTEGRACIÓN re.visita
    # =========================================================================

    visita_ids = fields.One2many(
        're.visita',
        'prospecto_id',
        string='Visitas',
        help="Visitas realizadas por este prospecto"
    )

    visitas_count = fields.Integer(
        string='Total Visitas',
        compute='_compute_visitas_prospecto',
        store=True
    )

    primera_visita = fields.Datetime(
        string='Fecha Primera Visita',
        compute='_compute_visitas_prospecto',
        store=True,
        help="Fecha de la primera visita realizada por este prospecto"
    )

    dias_primer_cierre = fields.Integer(
        string='Días hasta Cierre',
        compute='_compute_visitas_prospecto',
        store=True,
        help="Días transcurridos desde la primera visita hasta el cierre. "
             "Métrica clave para medir la velocidad del pipeline."
    )

    @api.depends('visita_ids', 'visita_ids.estado',
                 'visita_ids.fecha_visita', 'visita_ids.convirtio',
                 'visita_ids.dias_hasta_cierre')
    def _compute_visitas_prospecto(self):
        for prospecto in self:
            visitas_realizadas = prospecto.visita_ids.filtered(
                lambda v: v.estado == 'realizada'
            ).sorted('fecha_visita')

            prospecto.visitas_count = len(visitas_realizadas)

            if visitas_realizadas:
                prospecto.primera_visita = visitas_realizadas[0].fecha_visita
            else:
                prospecto.primera_visita = False

            # Días hasta cierre: desde primera visita hasta el contrato
            visitas_convertidas = visitas_realizadas.filtered('convirtio')
            if visitas_convertidas and prospecto.primera_visita:
                prospecto.dias_primer_cierre = (
                    visitas_convertidas[0].dias_hasta_cierre
                )
            else:
                prospecto.dias_primer_cierre = 0


    # =========================================================================
    # CAMPOS COMPUTED
    # =========================================================================

    @api.depends('propiedad_ids')
    def _compute_propiedad_count(self):
        """Contador de propiedades evaluadas — para stat button."""
        for prospecto in self:
            prospecto.propiedad_count = len(prospecto.propiedad_ids)

    @api.depends('date_captacion', 'date_cierre_real', 'etapa')
    def _compute_dias_pipeline(self):
        """
        Calcula días en pipeline desde captación.
        Si está cerrado o descartado: usa fecha de cierre real.
        Si sigue activo: usa fecha de hoy.
        """
        today = fields.Date.today()
        for prospecto in self:
            inicio = prospecto.date_captacion or today
            if prospecto.etapa in [ETAPA_CERRADO, ETAPA_DESCARTADO]:
                fin = prospecto.date_cierre_real or today
            else:
                fin = today
            prospecto.dias_en_pipeline = (fin - inicio).days

    # =========================================================================
    # VALIDACIONES
    # =========================================================================

    @api.constrains('presupuesto_min', 'presupuesto_max')
    def _check_presupuesto_coherente(self):
        """El presupuesto máximo no puede ser menor al mínimo."""
        for prospecto in self:
            if (prospecto.presupuesto_min
                    and prospecto.presupuesto_max
                    and prospecto.presupuesto_max < prospecto.presupuesto_min):
                raise ValidationError(_(
                    "El presupuesto máximo no puede ser menor "
                    "al presupuesto mínimo para '%(nombre)s'."
                ) % {'nombre': prospecto.name})

    @api.constrains('etapa', 'motivo_descarte')
    def _check_descarte_con_motivo(self):
        """Al descartar un prospecto el motivo es obligatorio."""
        for prospecto in self:
            if (prospecto.etapa == ETAPA_DESCARTADO
                    and not prospecto.motivo_descarte):
                raise ValidationError(_(
                    "Para descartar a '%(nombre)s' debes especificar "
                    "el motivo del descarte.\n\n"
                    "Esta información es clave para el análisis del pipeline."
                ) % {'nombre': prospecto.name})

    @api.constrains('propiedad_elegida_id', 'propiedad_ids')
    def _check_propiedad_elegida_en_lista(self):
        """
        La propiedad elegida debe estar en la lista de propiedades de interés.
        Garantiza coherencia del pipeline — no se puede cerrar en una propiedad
        que el prospecto nunca evaluó.
        """
        for prospecto in self:
            if (prospecto.propiedad_elegida_id
                    and prospecto.propiedad_elegida_id
                    not in prospecto.propiedad_ids):
                raise ValidationError(_(
                    "La propiedad elegida '%(propiedad)s' debe estar "
                    "en la lista de propiedades de interés de '%(nombre)s'.\n\n"
                    "Agrégala primero a las propiedades evaluadas."
                ) % {
                    'propiedad': prospecto.propiedad_elegida_id.name,
                    'nombre': prospecto.name,
                })

    @api.constrains('etapa', 'propiedad_elegida_id')
    def _check_cierre_requiere_propiedad(self):
        """Al cerrar el pipeline la propiedad elegida es obligatoria."""
        for prospecto in self:
            if (prospecto.etapa == ETAPA_CERRADO
                    and not prospecto.propiedad_elegida_id):
                raise ValidationError(_(
                    "Para cerrar el pipeline de '%(nombre)s' debes "
                    "seleccionar la propiedad elegida."
                ) % {'nombre': prospecto.name})

    @api.constrains('etapa', 'investigacion_completada',
                    'requiere_investigacion', 'resultado_investigacion')
    def _check_investigacion_antes_de_negociar(self):
        """
        Si requiere investigación, debe estar completada y aprobada
        antes de avanzar a negociación o cierre.
        Solo warning en log — no bloquea para flexibilidad del asesor.
        """
        for prospecto in self:
            if (prospecto.etapa in [ETAPA_NEGOCIACION, ETAPA_CERRADO]
                    and prospecto.requiere_investigacion
                    and not prospecto.investigacion_completada):
                _logger.warning(
                    "⚠️ Prospecto '%s' en %s sin investigación completada",
                    prospecto.name, prospecto.etapa
                )

    # =========================================================================
    # ACCIONES DE WORKFLOW
    # =========================================================================

    def action_avanzar_etapa(self):
        """
        Avanza el prospecto a la siguiente etapa del pipeline.
        Registra el cambio en el Chatter con contexto.
        """
        self.ensure_one()

        flujo = [
            ETAPA_NUEVO,
            ETAPA_CONTACTADO,
            ETAPA_VISITA_AGEND,
            ETAPA_VISITA_REAL,
            ETAPA_INVESTIGACION,
            ETAPA_NEGOCIACION,
            ETAPA_CERRADO,
        ]

        if self.etapa == ETAPA_DESCARTADO:
            raise UserError(_(
                "Un prospecto descartado no puede avanzar en el pipeline. "
                "Reactívalo primero si el prospecto retoma el proceso."
            ))

        if self.etapa == ETAPA_CERRADO:
            raise UserError(_(
                "El pipeline de '%(nombre)s' ya está cerrado."
            ) % {'nombre': self.name})

        idx_actual = flujo.index(self.etapa)
        siguiente = flujo[idx_actual + 1]

        # Validación especial: visita agendada requiere al menos una propiedad
        if siguiente == ETAPA_VISITA_AGEND and not self.propiedad_ids:
            raise UserError(_(
                "Agrega al menos una propiedad de interés antes de "
                "agendar la visita."
            ))

        # Validación especial: cierre requiere propiedad elegida
        if siguiente == ETAPA_CERRADO and not self.propiedad_elegida_id:
            raise UserError(_(
                "Selecciona la propiedad elegida antes de cerrar el pipeline."
            ))

        self.write({'etapa': siguiente})
        _logger.info(
            "📊 Prospecto '%s' avanzó: %s → %s",
            self.name, self.etapa, siguiente
        )

    def action_agendar_visita(self):
        """
        Abre el wizard de actividades para agendar visita.
        La visita queda registrada como mail.activity en el Chatter.
        Patrón v1.0 — re.visita reservado para v2.0.
        """
        self.ensure_one()

        if not self.propiedad_ids:
            raise UserError(_(
                "Agrega al menos una propiedad de interés antes de "
                "agendar la visita."
            ))

        # Buscar tipo de actividad personalizado para visitas
        tipo_visita = self.env.ref(
            'caletti_real_estate.mail_activity_type_visita',
            raise_if_not_found=False
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 're.prospecto',
                'default_res_id': self.id,
                'default_activity_type_id': tipo_visita.id if tipo_visita else False,
                'default_summary': _(
                    "Visita a propiedad — %s"
                ) % (self.propiedad_ids[0].name if self.propiedad_ids else ''),
            }
        }

    def action_descartar(self):
        """
        Descarta el prospecto. El motivo de descarte
        es obligatorio — validado via @api.constrains.
        """
        self.ensure_one()
        if not self.motivo_descarte:
            raise UserError(_(
                "Selecciona el motivo de descarte antes de continuar.\n"
                "Esta información es fundamental para el análisis del pipeline."
            ))
        self.write({
            'etapa': ETAPA_DESCARTADO,
            'date_cierre_real': fields.Date.today(),
        })

    def action_reactivar(self):
        """
        Reactiva un prospecto descartado.
        Regresa a etapa 'contactado' — el lead ya fue contactado antes.
        """
        self.ensure_one()
        if self.etapa != ETAPA_DESCARTADO:
            raise UserError(_("Solo se puede reactivar un prospecto descartado."))

        self.write({
            'etapa': ETAPA_CONTACTADO,
            'motivo_descarte': False,
            'notas_descarte': False,
            'date_cierre_real': False,
        })
        self.message_post(
            body=Markup(_(
                "🔄 <strong>Prospecto reactivado.</strong><br/>"
                "El prospecto retomó el proceso de búsqueda."
            )),
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )
        _logger.info("🔄 Prospecto '%s' reactivado", self.name)

    # =========================================================================
    # OVERRIDE write — CHATTER AUTOMÁTICO EN CAMBIOS CRÍTICOS
    # =========================================================================

    def write(self, vals):
        """
        Registra cambios de etapa y calificación en el Chatter.
        Al cerrar: actualiza estado de la propiedad elegida a 'en_negociacion'.
        Patrón idéntico a re_propiedad.py y creative_project.py.
        """
        resultado = super(ReProspecto, self).write(vals)

        # --- Cambio de etapa ---
        if 'etapa' in vals:
            nueva_etapa = vals['etapa']
            etiquetas   = dict(self._fields['etapa'].selection)

            for prospecto in self:
                etiqueta = etiquetas.get(nueva_etapa, nueva_etapa)

                if nueva_etapa == ETAPA_CONTACTADO:
                    prospecto.write({'date_contacto': fields.Date.today()})
                    prospecto.message_post(
                        body=Markup(_(
                            "📞 <strong>Primer contacto establecido.</strong><br/>"
                            "El asesor inició comunicación con el prospecto."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nueva_etapa == ETAPA_VISITA_AGEND:
                    prospecto.message_post(
                        body=Markup(_(
                            "📅 <strong>Visita agendada.</strong><br/>"
                            "Propiedades a visitar: <em>%(props)s</em><br/>"
                            "Agenda la actividad en el Chatter para "
                            "recibir recordatorio."
                        )) % {
                            'props': ', '.join(
                                prospecto.propiedad_ids.mapped('name')
                            ) or _("Sin propiedades asignadas")
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nueva_etapa == ETAPA_VISITA_REAL:
                    prospecto.write({'date_visita': fields.Date.today()})
                    prospecto.message_post(
                        body=Markup(_(
                            "🏠 <strong>Visita realizada.</strong><br/>"
                            "Registra el feedback del prospecto en las notas "
                            "para guiar el proceso de negociación."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nueva_etapa == ETAPA_INVESTIGACION:
                    prospecto.message_post(
                        body=Markup(_(
                            "🔍 <strong>Investigación socioeconómica iniciada.</strong><br/>"
                            "Documenta el avance en la sección de Investigación."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nueva_etapa == ETAPA_NEGOCIACION:
                    prospecto.message_post(
                        body=Markup(_(
                            "🤝 <strong>Prospecto en Negociación.</strong><br/>"
                            "Propiedad en proceso: "
                            "<strong>%(propiedad)s</strong>"
                        )) % {
                            'propiedad': prospecto.propiedad_elegida_id.name
                                if prospecto.propiedad_elegida_id
                                else _("Sin seleccionar aún")
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                    # Actualizar estado de la propiedad elegida
                    if prospecto.propiedad_elegida_id:
                        prospecto.propiedad_elegida_id.write(
                            {'estado': 'en_negociacion'}
                        )
                        _logger.info(
                            "🏠 Propiedad '%s' → en_negociacion "
                            "(prospecto '%s')",
                            prospecto.propiedad_elegida_id.name,
                            prospecto.name
                        )

                elif nueva_etapa == ETAPA_CERRADO:
                    prospecto.write({'date_cierre_real': fields.Date.today()})
                    prospecto.message_post(
                        body=Markup(_(
                            "✅ <strong>¡Pipeline Cerrado!</strong><br/>"
                            "Propiedad: <strong>%(propiedad)s</strong><br/>"
                            "Días en pipeline: <strong>%(dias)d</strong><br/>"
                            "Fuente: <em>%(fuente)s</em><br/><br/>"
                            "Genera el contrato desde el menú "
                            "Contratos → Nuevo."
                        )) % {
                            'propiedad': prospecto.propiedad_elegida_id.name
                                if prospecto.propiedad_elegida_id
                                else '—',
                            'dias': prospecto.dias_en_pipeline,
                            'fuente': dict(
                                self._fields['fuente_captacion'].selection
                            ).get(
                                prospecto.fuente_captacion,
                                _("No registrada")
                            ),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                    _logger.info(
                        "✅ Prospecto '%s' cerrado en %d días. "
                        "Propiedad: '%s'",
                        prospecto.name,
                        prospecto.dias_en_pipeline,
                        prospecto.propiedad_elegida_id.name
                        if prospecto.propiedad_elegida_id else '—'
                    )

                elif nueva_etapa == ETAPA_DESCARTADO:
                    motivo_label = dict(
                        self._fields['motivo_descarte'].selection
                    ).get(prospecto.motivo_descarte, _("Sin motivo"))

                    prospecto.message_post(
                        body=Markup(_(
                            "❌ <strong>Prospecto Descartado.</strong><br/>"
                            "Motivo: <em>%(motivo)s</em><br/>"
                            "%(notas)s"
                            "Días en pipeline: <strong>%(dias)d</strong>"
                        )) % {
                            'motivo': motivo_label,
                            'notas': (
                                _("Notas: %(n)s<br/>") % {
                                    'n': prospecto.notas_descarte
                                }
                                if prospecto.notas_descarte else ''
                            ),
                            'dias': prospecto.dias_en_pipeline,
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                    _logger.warning(
                        "❌ Prospecto '%s' descartado. Motivo: %s. "
                        "Días en pipeline: %d",
                        prospecto.name,
                        motivo_label,
                        prospecto.dias_en_pipeline
                    )

        # --- Cambio de calificación ---
        if 'calificacion' in vals:
            nueva_calif = vals['calificacion']
            etiquetas_calif = dict(self._fields['calificacion'].selection)
            for prospecto in self:
                prospecto.message_post(
                    body=Markup(_(
                        "🌡️ <strong>Calificación actualizada:</strong> "
                        "%(calif)s"
                    )) % {
                        'calif': etiquetas_calif.get(nueva_calif, nueva_calif)
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        return resultado

    # =========================================================================
    # OVERRIDE create — NOTIFICACIÓN INICIAL AL REGISTRAR EL LEAD
    # =========================================================================

    @api.model
    def create(self, vals):
        """
        Registra en el Chatter la captación del lead con su fuente.
        Patrón idéntico a creative_project.py.
        """
        prospecto = super(ReProspecto, self).create(vals)

        fuente_label = dict(
            self._fields['fuente_captacion'].selection
        ).get(
            prospecto.fuente_captacion,
            _("No especificada")
        )

        prospecto.message_post(
            body=Markup(_(
                "🆕 <strong>Nuevo lead registrado.</strong><br/>"
                "Fuente de captación: <em>%(fuente)s</em><br/>"
                "Tipo de operación: <em>%(tipo)s</em><br/>"
                "Asesor responsable: <strong>%(asesor)s</strong>"
            )) % {
                'fuente': fuente_label,
                'tipo': dict(
                    self._fields['tipo_interes'].selection
                ).get(prospecto.tipo_interes, '—'),
                'asesor': prospecto.asesor_id.name
                    if prospecto.asesor_id else _("Sin asignar"),
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(
            "🆕 Nuevo prospecto '%s' captado via %s por %s",
            prospecto.name,
            fuente_label,
            prospecto.asesor_id.name if prospecto.asesor_id else '—'
        )

        return prospecto
