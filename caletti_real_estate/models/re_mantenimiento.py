# caletti_real_estate/models/re_mantenimiento.py
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
# CONSTANTES: ESTADOS DEL MANTENIMIENTO
# =============================================================================
ESTADO_SOLICITADO  = 'solicitado'    # registrado, sin asignar aún
ESTADO_EVALUANDO   = 'evaluando'     # asesor revisando alcance y costo
ESTADO_APROBADO    = 'aprobado'      # propietario autorizó el trabajo
ESTADO_EN_PROCESO  = 'en_proceso'    # trabajo iniciado
ESTADO_RESUELTO    = 'resuelto'      # trabajo terminado, pendiente cierre
ESTADO_CERRADO     = 'cerrado'       # confirmado y archivado
ESTADO_CANCELADO   = 'cancelado'     # cancelado antes de ejecutarse

# =============================================================================
# CONSTANTES: PRIORIDAD
# =============================================================================
PRIO_URGENTE  = 'urgente'    # riesgo para la propiedad o el inquilino
PRIO_ALTA     = 'alta'       # afecta habitabilidad / uso normal
PRIO_NORMAL   = 'normal'     # molestia pero no urgente
PRIO_BAJA     = 'baja'       # mejora estética o preventiva

# =============================================================================
# CONSTANTES: CATEGORÍAS DE MANTENIMIENTO
# Más granular que re.propiedad.tipo_mantenimiento — aplica a solicitudes
# =============================================================================
CAT_FONTANERIA       = 'fontaneria'
CAT_ELECTRICIDAD     = 'electricidad'
CAT_PINTURA          = 'pintura'
CAT_CARPINTERIA      = 'carpinteria'
CAT_HERRERIA         = 'herreria'
CAT_IMPERMEABILIZ    = 'impermeabilizacion'
CAT_CLIMATIZACION    = 'climatizacion'     # A/C, calefacción, ventilación
CAT_FUMIGACION       = 'fumigacion'
CAT_LIMPIEZA         = 'limpieza_profunda'
CAT_ALBAÑILERIA      = 'albañileria'
CAT_VIDRIERIA        = 'vidrieria'
CAT_JARDINERIA       = 'jardineria'
CAT_CERRAJERIA       = 'cerrajeria'
CAT_ELECTRODOMESTICO = 'electrodomestico'
CAT_REMODELACION     = 'remodelacion'
CAT_OTRO             = 'otro'

# =============================================================================
# CONSTANTES: TIPO DE EJECUTOR
# =============================================================================
EJECUTOR_ASESOR    = 'asesor'
EJECUTOR_PROVEEDOR = 'proveedor_externo'

# =============================================================================
# CONSTANTES: ORIGEN DE LA SOLICITUD
# Diferencia solicitudes internas (asesor) de tickets de portal (inquilino)
# =============================================================================
ORIGEN_ASESOR    = 'asesor'
ORIGEN_PROPIET   = 'propietario'
ORIGEN_INQUILINO = 'inquilino'      # ticket desde portal — v1.1
ORIGEN_INSPECCION = 'inspeccion'   # detectado en visita de inspección

# =============================================================================
# CONSTANTE: APROBACIÓN DE COSTO
# Umbral a partir del cual se requiere autorización del propietario
# En v1.0 el asesor define el umbral por propiedad — campo en re.propiedad v1.1
# Por ahora constante global orientativa
# =============================================================================
UMBRAL_APROBACION_PROPIETARIO = 2000.0   # MXN


class ReMantenimiento(models.Model):
    """
    Solicitud de mantenimiento inmobiliario — Caletti Real Estate.

    Aplica a propiedades en cualquier estado:
    - Vacante / suspendida: mantenimiento entre inquilinos o preventivo
    - En mantenimiento: seguimiento del trabajo en curso registrado
      en re.propiedad.estado
    - Ocupada: solicitudes del inquilino durante la renta activa
    - Disponible / en negociación: preparación para nueva operación

    La relación con re.contrato es OPCIONAL — el mantenimiento
    es independiente del ciclo contractual.

    Tipo de ejecutor:
    - asesor: el asesor resuelve directamente (casos menores)
    - proveedor_externo: tercero con nombre, teléfono y costo

    Origen de solicitud:
    - asesor / propietario / inspeccion: flujo interno
    - inquilino: ticket desde portal del cliente (v1.1)
      re.mantenimiento ya está preparado para recibirlo via
      message_new() o ruta de portal dedicada.

    El Chatter registra todo el ciclo: solicitud → evaluación
    → aprobación del propietario → ejecución → cierre.
    """
    _name = 're.mantenimiento'
    _description = 'Mantenimiento Inmobiliario — Caletti Real Estate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'prioridad asc, estado asc, fecha_solicitud desc'

    # =========================================================================
    # SECCIÓN 1: IDENTIFICACIÓN
    # =========================================================================

    name = fields.Char(
        string='Descripción del Mantenimiento',
        required=True,
        index=True,
        tracking=True,
        help="Descripción breve y clara del problema o trabajo requerido. "
             "Ej: 'Fuga en tubería cocina', 'Pintura exterior fachada', "
             "'Cambio de chapa puerta principal'"
    )

    # Número de ticket — para solicitudes del inquilino desde portal
    ticket_ref = fields.Char(
        string='Referencia / Ticket',
        copy=False,
        index=True,
        readonly=True,
        help="Referencia automática generada al crear la solicitud. "
             "Visible al inquilino en el portal como número de seguimiento."
    )

    # =========================================================================
    # SECCIÓN 2: PROPIEDAD Y VÍNCULOS
    # propiedad_id: OBLIGATORIO — el mantenimiento siempre es de una propiedad
    # contrato_id:  OPCIONAL — puede existir sin contrato activo
    # =========================================================================

    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad',
        required=True,
        index=True,
        tracking=True,
        help="Inmueble donde se realizará el mantenimiento. "
             "Campo obligatorio — independiente del estado de la propiedad."
    )

    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        related='propiedad_id.propietario_id',
        store=True,
        readonly=True,
        help="Propietario del inmueble — obtenido automáticamente"
    )

    contrato_id = fields.Many2one(
        're.contrato',
        string='Contrato Relacionado',
        index=True,
        tracking=True,
        domain="[('propiedad_id', '=', propiedad_id)]",
        help="Contrato de renta activo relacionado. OPCIONAL — "
             "el mantenimiento puede existir sin contrato activo "
             "(propiedades vacantes, suspendidas, en preparación)."
    )

    inquilino_id = fields.Many2one(
        'res.partner',
        string='Inquilino Solicitante',
        related='contrato_id.inquilino_id',
        store=True,
        readonly=True,
        help="Inquilino del contrato activo — se obtiene automáticamente "
             "si existe contrato relacionado"
    )

    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor Responsable',
        related='propiedad_id.asesor_id',
        store=True,
        readonly=True,
        help="Asesor responsable — heredado de la propiedad"
    )

    # =========================================================================
    # SECCIÓN 3: CLASIFICACIÓN
    # =========================================================================

    categoria = fields.Selection([
        (CAT_FONTANERIA,       '🚿 Fontanería / Plomería'),
        (CAT_ELECTRICIDAD,     '⚡ Electricidad'),
        (CAT_PINTURA,          '🎨 Pintura'),
        (CAT_CARPINTERIA,      '🪚 Carpintería'),
        (CAT_HERRERIA,         '🔩 Herrería'),
        (CAT_IMPERMEABILIZ,    '💧 Impermeabilización'),
        (CAT_CLIMATIZACION,    '❄️ Climatización / A/C'),
        (CAT_FUMIGACION,       '🐛 Fumigación'),
        (CAT_LIMPIEZA,         '🧹 Limpieza Profunda'),
        (CAT_ALBAÑILERIA,      '🧱 Albañilería'),
        (CAT_VIDRIERIA,        '🪟 Vidriería'),
        (CAT_JARDINERIA,       '🌿 Jardinería'),
        (CAT_CERRAJERIA,       '🔑 Cerrajería'),
        (CAT_ELECTRODOMESTICO, '🏠 Electrodoméstico'),
        (CAT_REMODELACION,     '🔨 Remodelación'),
        (CAT_OTRO,             '📋 Otro'),
    ], string='Categoría',
       required=True,
       tracking=True,
       index=True
    )

    prioridad = fields.Selection([
        (PRIO_URGENTE, '🚨 Urgente — Riesgo para propiedad o inquilino'),
        (PRIO_ALTA,    '🔴 Alta — Afecta habitabilidad'),
        (PRIO_NORMAL,  '🟡 Normal — Sin urgencia inmediata'),
        (PRIO_BAJA,    '🟢 Baja — Mejora o preventivo'),
    ], string='Prioridad',
       default=PRIO_NORMAL,
       required=True,
       tracking=True,
       index=True,
       help="Urgente: fuga de agua activa, corto circuito, falla de gas. "
            "Alta: A/C roto en verano, puerta que no cierra, calentador sin funcionar. "
            "Normal: pintura deteriorada, grietas menores, jardinería. "
            "Baja: mejoras estéticas, mantenimiento preventivo programado."
    )

    estado = fields.Selection([
        (ESTADO_SOLICITADO, '📋 Solicitado'),
        (ESTADO_EVALUANDO,  '🔍 En Evaluación'),
        (ESTADO_APROBADO,   '✅ Aprobado por Propietario'),
        (ESTADO_EN_PROCESO, '🔄 En Proceso'),
        (ESTADO_RESUELTO,   '🏁 Resuelto'),
        (ESTADO_CERRADO,    '📦 Cerrado'),
        (ESTADO_CANCELADO,  '❌ Cancelado'),
    ], string='Estado',
       default=ESTADO_SOLICITADO,
       required=True,
       tracking=True,
       index=True
    )

    origen_solicitud = fields.Selection([
        (ORIGEN_ASESOR,     '👤 Asesor — Detección directa'),
        (ORIGEN_PROPIET,    '🏠 Propietario — Solicitud directa'),
        (ORIGEN_INQUILINO,  '🧑 Inquilino — Ticket desde portal'),
        (ORIGEN_INSPECCION, '🔍 Inspección — Detectado en visita'),
    ], string='Origen de Solicitud',
       default=ORIGEN_ASESOR,
       required=True,
       tracking=True,
       help="Canal por el que se originó esta solicitud de mantenimiento. "
            "El origen 'Inquilino' corresponde a tickets generados desde "
            "el portal del cliente (v1.1)."
    )

    # =========================================================================
    # SECCIÓN 4: EJECUTOR (campo tipo_ejecutor + proveedor opcional)
    # =========================================================================

    tipo_ejecutor = fields.Selection([
        (EJECUTOR_ASESOR,    '👤 Asesor — Resolución directa'),
        (EJECUTOR_PROVEEDOR, '🔧 Proveedor Externo'),
    ], string='Tipo de Ejecutor',
       default=EJECUTOR_PROVEEDOR,
       required=True,
       tracking=True,
       help="Asesor: el asesor resuelve personalmente (casos menores: "
            "cambio de foco, entrega de llave, ajuste de cerradura). "
            "Proveedor Externo: tercero especializado (plomero, electricista, "
            "pintor, etc.) con costo asociado."
    )

    # Proveedor externo — visible solo cuando tipo_ejecutor = proveedor_externo
    proveedor_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        index=True,
        tracking=True,
        help="Contacto del proveedor externo en Odoo. "
             "Si no existe, captura nombre y teléfono en el campo manual."
    )

    proveedor_nombre = fields.Char(
        string='Nombre del Proveedor',
        tracking=True,
        help="Nombre del proveedor cuando no está registrado como "
             "contacto en Odoo. Ej: 'Juan García — Plomero'"
    )

    proveedor_telefono = fields.Char(
        string='Teléfono del Proveedor',
        tracking=True,
        help="Teléfono directo del proveedor para coordinar el trabajo"
    )

    # =========================================================================
    # SECCIÓN 5: FECHAS
    # =========================================================================

    fecha_solicitud = fields.Date(
        string='Fecha de Solicitud',
        default=fields.Date.today,
        required=True,
        tracking=True,
        help="Fecha en que se registró o recibió la solicitud"
    )

    fecha_programada = fields.Date(
        string='Fecha Programada',
        tracking=True,
        help="Fecha acordada con el proveedor o asesor para realizar el trabajo"
    )

    fecha_inicio_real = fields.Date(
        string='Fecha de Inicio Real',
        tracking=True,
        help="Fecha en que efectivamente comenzó el trabajo"
    )

    fecha_resolucion = fields.Date(
        string='Fecha de Resolución',
        tracking=True,
        help="Fecha en que el trabajo quedó completado"
    )

    dias_resolucion = fields.Integer(
        string='Días para Resolver',
        compute='_compute_dias_resolucion',
        help="Días transcurridos desde la solicitud hasta la resolución. "
             "Métrica de eficiencia del asesor."
    )

    # =========================================================================
    # SECCIÓN 6: COSTOS Y APROBACIÓN
    # =========================================================================

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='propiedad_id.currency_id',
        readonly=True
    )

    costo_estimado = fields.Monetary(
        string='Costo Estimado',
        currency_field='currency_id',
        tracking=True,
        help="Cotización o estimación del costo antes de iniciar el trabajo"
    )

    costo_real = fields.Monetary(
        string='Costo Real',
        currency_field='currency_id',
        tracking=True,
        help="Costo final al cerrar el mantenimiento. "
             "Puede diferir del estimado."
    )

    diferencia_costo = fields.Monetary(
        string='Diferencia de Costo',
        currency_field='currency_id',
        compute='_compute_diferencia_costo',
        help="Costo real menos costo estimado. "
             "Positivo = sobrecosto. Negativo = ahorro."
    )

    requiere_aprobacion = fields.Boolean(
        string='Requiere Aprobación del Propietario',
        compute='_compute_requiere_aprobacion',
        store=True,
        help=f"True automáticamente cuando el costo estimado supera "
             f"${UMBRAL_APROBACION_PROPIETARIO:,.0f} MXN. "
             f"El propietario debe autorizar antes de iniciar el trabajo."
    )

    aprobado_por_propietario = fields.Boolean(
        string='Aprobado por el Propietario',
        tracking=True,
        default=False,
        help="Confirma que el propietario autorizó el gasto. "
             "Obligatorio para avanzar a 'En Proceso' cuando "
             "requiere_aprobacion es True."
    )

    fecha_aprobacion = fields.Date(
        string='Fecha de Aprobación',
        tracking=True,
        help="Fecha en que el propietario autorizó el trabajo"
    )

    pagado_por = fields.Selection([
        ('propietario', '🏠 Propietario'),
        ('inquilino',   '🧑 Inquilino'),
        ('asesor',      '👤 Asesor (adelanto)'),
        ('pendiente',   '⏳ Por definir'),
    ], string='Pagado por',
       default='propietario',
       tracking=True,
       help="Quién asume el costo del mantenimiento. "
            "En general el propietario cubre mantenimiento estructural; "
            "el inquilino cubre daños por mal uso."
    )

    # =========================================================================
    # SECCIÓN 7: DESCRIPCIÓN Y EVIDENCIA
    # =========================================================================

    descripcion_problema = fields.Text(
        string='Descripción del Problema',
        tracking=True,
        help="Detalle del problema reportado: ubicación exacta dentro "
             "del inmueble, síntomas, cuándo comenzó, impacto actual."
    )

    descripcion_trabajo = fields.Text(
        string='Trabajo Realizado',
        tracking=True,
        help="Descripción del trabajo ejecutado, materiales utilizados, "
             "solución aplicada y condición final del área."
    )

    notas_internas = fields.Text(
        string='Notas Internas',
        help="Observaciones privadas del asesor: negociaciones con el proveedor, "
             "acuerdos con el propietario, advertencias para futuros mantenimientos."
    )

    # Campo para evidencia fotográfica — v1.1 integrar con adjuntos del Chatter
    # En v1.0 el asesor sube las fotos como adjuntos al mensaje del Chatter
    tiene_evidencia_fotos = fields.Boolean(
        string='Fotos Adjuntas',
        default=False,
        help="Marca cuando hayas adjuntado fotos del antes/después "
             "en el Chatter. Las fotos se suben como adjuntos al mensaje."
    )

    # =========================================================================
    # LÓGICA COMPUTED
    # =========================================================================

    @api.depends('fecha_solicitud', 'fecha_resolucion', 'estado')
    def _compute_dias_resolucion(self):
        """
        Días desde la solicitud hasta la resolución.
        Si sigue abierto: cuenta desde hoy para medir tiempo de respuesta.
        """
        today = fields.Date.today()
        for mant in self:
            inicio = mant.fecha_solicitud or today
            if mant.estado in [ESTADO_RESUELTO, ESTADO_CERRADO]:
                fin = mant.fecha_resolucion or today
            else:
                fin = today
            mant.dias_resolucion = (fin - inicio).days

    @api.depends('costo_estimado', 'costo_real')
    def _compute_diferencia_costo(self):
        for mant in self:
            mant.diferencia_costo = (
                mant.costo_real - mant.costo_estimado
            )

    @api.depends('costo_estimado')
    def _compute_requiere_aprobacion(self):
        """
        Activa la bandera de aprobación automáticamente
        cuando el costo estimado supera el umbral definido.
        """
        for mant in self:
            mant.requiere_aprobacion = (
                mant.costo_estimado > UMBRAL_APROBACION_PROPIETARIO
            )

    # =========================================================================
    # VALIDACIONES
    # =========================================================================

    @api.constrains('contrato_id', 'propiedad_id')
    def _check_contrato_de_propiedad(self):
        """
        Si se vincula un contrato, debe ser de la misma propiedad.
        Evita asociar un mantenimiento de casa A con el contrato de casa B.
        """
        for mant in self:
            if (mant.contrato_id
                    and mant.contrato_id.propiedad_id != mant.propiedad_id):
                raise ValidationError(_(
                    "El contrato '%(contrato)s' no pertenece a la "
                    "propiedad '%(propiedad)s'.\n\n"
                    "Selecciona un contrato de la misma propiedad "
                    "o deja el campo vacío."
                ) % {
                    'contrato':  mant.contrato_id.name,
                    'propiedad': mant.propiedad_id.name,
                })

    @api.constrains('tipo_ejecutor', 'proveedor_id', 'proveedor_nombre')
    def _check_proveedor_cuando_externo(self):
        """
        Cuando tipo_ejecutor = proveedor_externo,
        al menos uno de los campos de proveedor debe estar lleno.
        Flexibilidad: puede ser el contacto en Odoo o el nombre manual.
        """
        for mant in self:
            if (mant.tipo_ejecutor == EJECUTOR_PROVEEDOR
                    and mant.estado not in [ESTADO_SOLICITADO, ESTADO_EVALUANDO]
                    and not mant.proveedor_id
                    and not mant.proveedor_nombre):
                raise ValidationError(_(
                    "Para avanzar con un Proveedor Externo debes indicar "
                    "el nombre o seleccionar el contacto del proveedor "
                    "en '%(nombre)s'."
                ) % {'nombre': mant.name})

    @api.constrains('costo_estimado', 'costo_real')
    def _check_costos_positivos(self):
        for mant in self:
            if mant.costo_estimado < 0 or mant.costo_real < 0:
                raise ValidationError(_(
                    "Los costos no pueden ser negativos."
                ))

    @api.constrains('fecha_solicitud', 'fecha_programada', 'fecha_resolucion')
    def _check_fechas_coherentes(self):
        """Las fechas deben seguir el orden lógico del proceso."""
        for mant in self:
            if (mant.fecha_programada
                    and mant.fecha_solicitud
                    and mant.fecha_programada < mant.fecha_solicitud):
                raise ValidationError(_(
                    "La fecha programada no puede ser anterior "
                    "a la fecha de solicitud."
                ))
            if (mant.fecha_resolucion
                    and mant.fecha_solicitud
                    and mant.fecha_resolucion < mant.fecha_solicitud):
                raise ValidationError(_(
                    "La fecha de resolución no puede ser anterior "
                    "a la fecha de solicitud."
                ))

    # =========================================================================
    # ACCIONES DE WORKFLOW
    # =========================================================================

    def action_iniciar_evaluacion(self):
        """Pasa de solicitado a evaluando — asesor revisa alcance y costo."""
        self.ensure_one()
        if self.estado != ESTADO_SOLICITADO:
            raise UserError(_(
                "Solo se puede iniciar evaluación desde estado Solicitado."
            ))
        self.write({'estado': ESTADO_EVALUANDO})
        _logger.info(
            "🔍 Mantenimiento '%s' → evaluando", self.name
        )

    def action_aprobar(self):
        """
        Marca el mantenimiento como aprobado por el propietario.
        Registra fecha de aprobación automáticamente.
        """
        self.ensure_one()
        if self.estado != ESTADO_EVALUANDO:
            raise UserError(_(
                "El mantenimiento debe estar En Evaluación "
                "para ser aprobado."
            ))
        self.write({
            'estado':                  ESTADO_APROBADO,
            'aprobado_por_propietario': True,
            'fecha_aprobacion':        fields.Date.today(),
        })
        _logger.info(
            "✅ Mantenimiento '%s' aprobado por propietario", self.name
        )

    def action_iniciar_trabajo(self):
        """
        Inicia el trabajo. Valida aprobación del propietario
        si el costo supera el umbral configurado.
        """
        self.ensure_one()
        if self.estado not in [ESTADO_APROBADO, ESTADO_EVALUANDO]:
            raise UserError(_(
                "El mantenimiento debe estar Aprobado o En Evaluación "
                "para iniciar el trabajo."
            ))

        # Validar aprobación del propietario si es requerida
        if self.requiere_aprobacion and not self.aprobado_por_propietario:
            raise UserError(_(
                "El costo estimado supera $%(umbral)s %(moneda)s.\n\n"
                "El propietario debe aprobar el gasto antes de iniciar.\n"
                "Usa el botón 'Aprobar' o confirma la autorización "
                "marcando el campo 'Aprobado por Propietario'."
            ) % {
                'umbral': f"{UMBRAL_APROBACION_PROPIETARIO:,.0f}",
                'moneda': self.currency_id.symbol
                    if self.currency_id else 'MXN',
            })

        self.write({
            'estado':           ESTADO_EN_PROCESO,
            'fecha_inicio_real': fields.Date.today(),
        })
        _logger.info(
            "🔄 Mantenimiento '%s' iniciado. Ejecutor: %s",
            self.name, self.tipo_ejecutor
        )

    def action_marcar_resuelto(self):
        """
        Marca el mantenimiento como resuelto.
        El asesor confirma que el trabajo fue completado
        antes del cierre definitivo.
        """
        self.ensure_one()
        if self.estado != ESTADO_EN_PROCESO:
            raise UserError(_(
                "El mantenimiento debe estar En Proceso "
                "para marcarse como resuelto."
            ))
        self.write({
            'estado':           ESTADO_RESUELTO,
            'fecha_resolucion': fields.Date.today(),
        })
        _logger.info(
            "🏁 Mantenimiento '%s' resuelto en %d días",
            self.name, self.dias_resolucion
        )

    def action_cerrar(self):
        """
        Cierre definitivo del mantenimiento.
        Registra el costo real si no fue capturado aún.
        """
        self.ensure_one()
        if self.estado != ESTADO_RESUELTO:
            raise UserError(_(
                "El mantenimiento debe estar Resuelto para cerrarse. "
                "Confirma primero que el trabajo fue completado."
            ))
        self.write({'estado': ESTADO_CERRADO})
        _logger.info(
            "📦 Mantenimiento '%s' cerrado. "
            "Costo real: %.2f. Días: %d",
            self.name,
            self.costo_real,
            self.dias_resolucion
        )

    def action_cancelar(self):
        """Cancela el mantenimiento antes de que sea ejecutado."""
        self.ensure_one()
        if self.estado in [ESTADO_RESUELTO, ESTADO_CERRADO]:
            raise UserError(_(
                "No se puede cancelar un mantenimiento "
                "ya resuelto o cerrado."
            ))
        self.write({'estado': ESTADO_CANCELADO})
        _logger.warning(
            "❌ Mantenimiento '%s' cancelado", self.name
        )

    # =========================================================================
    # OVERRIDE write — CHATTER AUTOMÁTICO
    # Patrón idéntico al resto de modelos del vertical
    # =========================================================================

    def write(self, vals):
        """
        Registra cambios de estado críticos en el Chatter.
        Notifica al propietario cuando se requiere su aprobación.
        """
        resultado = super(ReMantenimiento, self).write(vals)

        if 'estado' in vals:
            nuevo_estado = vals['estado']
            etiquetas    = dict(self._fields['estado'].selection)

            for mant in self:
                etiqueta = etiquetas.get(nuevo_estado, nuevo_estado)

                if nuevo_estado == ESTADO_EVALUANDO:
                    ejecutor_txt = (
                        _("Asesor: <strong>%(asesor)s</strong>") % {
                            'asesor': mant.asesor_id.name
                                if mant.asesor_id else '—'
                        }
                        if mant.tipo_ejecutor == EJECUTOR_ASESOR
                        else _(
                            "Proveedor: <strong>%(prov)s</strong>"
                        ) % {
                            'prov': (
                                mant.proveedor_id.name
                                or mant.proveedor_nombre
                                or _("Por asignar")
                            )
                        }
                    )
                    mant.message_post(
                        body=Markup(_(
                            "🔍 <strong>Mantenimiento en Evaluación.</strong><br/>"
                            "Categoría: <em>%(cat)s</em><br/>"
                            "%(ejecutor)s<br/>"
                            "%(costo)s"
                        )) % {
                            'cat': dict(
                                self._fields['categoria'].selection
                            ).get(mant.categoria, '—'),
                            'ejecutor': ejecutor_txt,
                            'costo': (
                                _("Costo estimado: "
                                  "<strong>%(m)s %(s)s</strong>") % {
                                    'm': f"{mant.costo_estimado:,.2f}",
                                    's': mant.currency_id.symbol
                                        if mant.currency_id else 'MXN',
                                }
                                if mant.costo_estimado else ''
                            ),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nuevo_estado == ESTADO_APROBADO:
                    mant.message_post(
                        body=Markup(_(
                            "✅ <strong>Aprobado por el Propietario.</strong><br/>"
                            "Fecha: <strong>%(fecha)s</strong><br/>"
                            "Costo autorizado: "
                            "<strong>%(costo)s %(moneda)s</strong><br/>"
                            "El trabajo puede iniciarse."
                        )) % {
                            'fecha': str(mant.fecha_aprobacion or
                                         fields.Date.today()),
                            'costo': f"{mant.costo_estimado:,.2f}",
                            'moneda': mant.currency_id.symbol
                                if mant.currency_id else 'MXN',
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nuevo_estado == ESTADO_EN_PROCESO:
                    prov_txt = (
                        _("Resuelto por el asesor directamente.")
                        if mant.tipo_ejecutor == EJECUTOR_ASESOR
                        else _(
                            "Proveedor asignado: <strong>%(prov)s</strong>"
                            "%(tel)s"
                        ) % {
                            'prov': (
                                mant.proveedor_id.name
                                or mant.proveedor_nombre
                                or _("Sin nombre")
                            ),
                            'tel': (
                                f" · {mant.proveedor_telefono}"
                                if mant.proveedor_telefono else ''
                            ),
                        }
                    )
                    mant.message_post(
                        body=Markup(_(
                            "🔄 <strong>Trabajo Iniciado.</strong><br/>"
                            "%(prov)s<br/>"
                            "Fecha programada: <strong>%(fecha)s</strong>"
                        )) % {
                            'prov': prov_txt,
                            'fecha': str(mant.fecha_programada or
                                         _("Sin fecha programada")),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nuevo_estado == ESTADO_RESUELTO:
                    mant.message_post(
                        body=Markup(_(
                            "🏁 <strong>Mantenimiento Resuelto.</strong><br/>"
                            "Días de resolución: "
                            "<strong>%(dias)d</strong><br/>"
                            "Costo real: "
                            "<strong>%(costo)s %(moneda)s</strong>"
                            "%(diferencia)s"
                        )) % {
                            'dias': mant.dias_resolucion,
                            'costo': f"{mant.costo_real:,.2f}",
                            'moneda': mant.currency_id.symbol
                                if mant.currency_id else 'MXN',
                            'diferencia': (
                                Markup(_(
                                    "<br/>⚠️ Sobrecosto: "
                                    "<strong>%(d)s %(s)s</strong>"
                                )) % {
                                    'd': f"{mant.diferencia_costo:,.2f}",
                                    's': mant.currency_id.symbol
                                        if mant.currency_id else 'MXN',
                                }
                                if mant.diferencia_costo > 0 else ''
                            ),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nuevo_estado == ESTADO_CERRADO:
                    mant.message_post(
                        body=Markup(_(
                            "📦 <strong>Mantenimiento Cerrado y Archivado.</strong><br/>"
                            "Costo final: "
                            "<strong>%(costo)s %(moneda)s</strong> · "
                            "Pagado por: <em>%(pagador)s</em>"
                        )) % {
                            'costo': f"{mant.costo_real:,.2f}",
                            'moneda': mant.currency_id.symbol
                                if mant.currency_id else 'MXN',
                            'pagador': dict(
                                self._fields['pagado_por'].selection
                            ).get(mant.pagado_por, '—'),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                elif nuevo_estado == ESTADO_CANCELADO:
                    mant.message_post(
                        body=Markup(_(
                            "❌ <strong>Mantenimiento Cancelado.</strong>"
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

        # Alerta cuando se activa requiere_aprobacion
        if 'requiere_aprobacion' in vals and vals['requiere_aprobacion']:
            for mant in self:
                mant.message_post(
                    body=Markup(_(
                        "⚠️ <strong>Se requiere aprobación del propietario.</strong><br/>"
                        "El costo estimado de "
                        "<strong>%(costo)s %(moneda)s</strong> "
                        "supera el umbral de autorización "
                        "(<strong>%(umbral)s %(moneda)s</strong>).<br/>"
                        "Contacta al propietario antes de iniciar el trabajo."
                    )) % {
                        'costo': f"{mant.costo_estimado:,.2f}",
                        'moneda': mant.currency_id.symbol
                            if mant.currency_id else 'MXN',
                        'umbral': f"{UMBRAL_APROBACION_PROPIETARIO:,.0f}",
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        return resultado

    # =========================================================================
    # OVERRIDE create — TICKET REF Y NOTIFICACIÓN INICIAL
    # =========================================================================

    @api.model
    def create(self, vals):
        """
        Genera referencia de ticket automática al crear el registro.
        Notifica en Chatter con el origen y prioridad de la solicitud.

        La referencia ticket_ref es visible al inquilino en el portal
        como número de seguimiento (v1.1).
        """
        # Generar referencia de ticket secuencial
        if not vals.get('ticket_ref'):
            secuencia = self.env['ir.sequence'].next_by_code(
                're.mantenimiento'
            )
            vals['ticket_ref'] = secuencia or f"MANT-{fields.Date.today().year}-????"

        mant = super(ReMantenimiento, self).create(vals)

        prioridad_label = dict(
            self._fields['prioridad'].selection
        ).get(mant.prioridad, mant.prioridad)

        origen_label = dict(
            self._fields['origen_solicitud'].selection
        ).get(mant.origen_solicitud, mant.origen_solicitud)

        mant.message_post(
            body=Markup(_(
                "📋 <strong>Nueva solicitud de mantenimiento registrada.</strong><br/>"
                "Ticket: <strong>%(ticket)s</strong><br/>"
                "Propiedad: <strong>%(prop)s</strong><br/>"
                "Categoría: <em>%(cat)s</em><br/>"
                "Prioridad: <em>%(prio)s</em><br/>"
                "Origen: <em>%(origen)s</em>"
                "%(contrato)s"
            )) % {
                'ticket':  mant.ticket_ref,
                'prop':    mant.propiedad_id.name,
                'cat':     dict(
                    self._fields['categoria'].selection
                ).get(mant.categoria, '—'),
                'prio':    prioridad_label,
                'origen':  origen_label,
                'contrato': (
                    Markup(_(
                        "<br/>Contrato relacionado: "
                        "<strong>%(c)s</strong>"
                    )) % {'c': mant.contrato_id.name}
                    if mant.contrato_id else ''
                ),
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(
            "📋 Nuevo mantenimiento '%s' (ticket: %s) "
            "en propiedad '%s'. Prioridad: %s. Origen: %s",
            mant.name,
            mant.ticket_ref,
            mant.propiedad_id.name,
            mant.prioridad,
            mant.origen_solicitud
        )

        return mant
