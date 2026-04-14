# caletti_real_estate/models/re_propiedad.py
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

# =============================================================================
# CONSTANTES: TIPOS DE PROPIEDAD
# =============================================================================
TIPO_RESIDENCIAL = 'residencial'
TIPO_COMERCIAL   = 'comercial'
TIPO_TERRENO     = 'terreno'

# =============================================================================
# CONSTANTES: SUBTIPOS POR TIPO PRINCIPAL
# =============================================================================
# Residencial
SUBTIPO_CASA         = 'casa'
SUBTIPO_DEPARTAMENTO = 'departamento'
SUBTIPO_TOWNHOUSE    = 'townhouse'
SUBTIPO_PENTHOUSE    = 'penthouse'
SUBTIPO_ESTUDIO      = 'estudio'
SUBTIPO_CUARTO       = 'cuarto'

# Comercial
SUBTIPO_LOCAL        = 'local'
SUBTIPO_OFICINA      = 'oficina'
SUBTIPO_BODEGA       = 'bodega'
SUBTIPO_NAVE         = 'nave_industrial'
SUBTIPO_CONSULTORIO  = 'consultorio'
SUBTIPO_HOTEL        = 'hotel'
SUBTIPO_EDIFICIO     = 'edificio'

# Terreno
SUBTIPO_URBANO       = 'urbano'
SUBTIPO_HABITACIONAL = 'habitacional'
SUBTIPO_COM_TERRENO  = 'comercial_terreno'
SUBTIPO_AGRICOLA     = 'agricola'
SUBTIPO_EJIDAL       = 'ejidal'

# =============================================================================
# CONSTANTES: ESTADOS DE LA PROPIEDAD
# =============================================================================
ESTADO_DISPONIBLE      = 'disponible'
ESTADO_EN_NEGOCIACION  = 'en_negociacion'
ESTADO_OCUPADA         = 'ocupada'
ESTADO_VENDIDA         = 'vendida'
ESTADO_VACANTE         = 'vacante'
ESTADO_EN_MANT         = 'en_mantenimiento'
ESTADO_SUSPENDIDA      = 'suspendida'

# =============================================================================
# CONSTANTES: OPERACIÓN OBJETIVO
# =============================================================================
OPERACION_RENTA  = 'renta'
OPERACION_VENTA  = 'venta'
OPERACION_AMBAS  = 'ambas'

# =============================================================================
# CONSTANTES: CONTROL DE FOTOS
# Cambiar este valor en v1.1 si se requiere ampliar el límite
# =============================================================================
MAX_FOTOS_PROPIEDAD = 10

# =============================================================================
# CONSTANTES: TIPOS DE MANTENIMIENTO (campo descripción)
# =============================================================================
MANT_AMPLIACION  = 'ampliacion'
MANT_PINTURA     = 'pintura'
MANT_REMODELACION = 'remodelacion'
MANT_ELECTRICIDAD = 'electricidad'
MANT_FONTANERIA  = 'fontaneria'
MANT_IMPERMEABILIZACION = 'impermeabilizacion'
MANT_TECHADO     = 'techado'
MANT_OTRO        = 'otro'


class RePropiedad(models.Model):
    """
    Modelo central del vertical inmobiliario Caletti Real Estate.

    Representa el activo inmobiliario gestionado por el asesor.
    El asesor SIEMPRE maneja propiedades de terceros — propietario_id es requerido.

    Soporta tres tipos principales desde v1.0:
    - Residencial: casa, departamento, townhouse, penthouse, estudio, cuarto
    - Comercial: local, oficina, bodega, nave industrial, consultorio, hotel, edificio
    - Terreno: urbano, habitacional, comercial, agrícola, ejidal

    Estados del ciclo de vida:
    disponible → en_negociacion → ocupada / vendida → vacante
    Con estados especiales: en_mantenimiento, suspendida

    Las fotos se gestionan via submodelo re.propiedad.foto (One2many),
    límite configurable via constante MAX_FOTOS_PROPIEDAD.

    Las visitas se registran como mail.activity — re.visita reservado para v2.0
    (administradoras con cartera >50 propiedades activas).
    """
    _name = 're.propiedad'
    _description = 'Propiedad Inmobiliaria — Caletti Real Estate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'estado asc, date_disponible desc'

    # =========================================================================
    # SECCIÓN 1: IDENTIFICACIÓN
    # =========================================================================

    name = fields.Char(
        string='Nombre / Referencia',
        required=True,
        index=True,
        tracking=True,
        help="Nombre interno de referencia. Ej: 'Casa Pedregal 3 recámaras' "
             "o 'Local Av. Insurgentes PB'"
    )

    referencia_interna = fields.Char(
        string='Clave Interna',
        copy=False,
        index=True,
        help="Clave alfanumérica única del asesor. Ej: 'RE-2026-001'"
    )

    # El asesor SIEMPRE maneja propiedades de terceros — campo obligatorio
    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        required=True,
        index=True,
        tracking=True,
        help="Propietario legal del inmueble. "
             "El asesor gestiona propiedades de terceros — campo obligatorio."
    )

    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor Responsable',
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
        help="Asesor inmobiliario de Caletti asignado a esta propiedad"
    )

    # =========================================================================
    # SECCIÓN 2: CLASIFICACIÓN — TIPO Y SUBTIPO
    # =========================================================================

    tipo_propiedad = fields.Selection([
        (TIPO_RESIDENCIAL, '🏠 Residencial'),
        (TIPO_COMERCIAL,   '🏢 Comercial'),
        (TIPO_TERRENO,     '🌿 Terreno'),
    ], string='Tipo',
       required=True,
       tracking=True,
       index=True
    )

    # Subtipo unificado — la vista filtra opciones visibles según tipo_propiedad
    # usando invisible. Todos los subtipos viven en un solo campo Selection.
    subtipo_propiedad = fields.Selection([
        # Residencial
        (SUBTIPO_CASA,         '🏠 Casa'),
        (SUBTIPO_DEPARTAMENTO, '🏙️ Departamento'),
        (SUBTIPO_TOWNHOUSE,    '🏘️ Townhouse / Cluster'),
        (SUBTIPO_PENTHOUSE,    '✨ Penthouse'),
        (SUBTIPO_ESTUDIO,      '🛋️ Estudio'),
        (SUBTIPO_CUARTO,       '🚪 Cuarto / Habitación'),
        # Comercial
        (SUBTIPO_LOCAL,        '🏪 Local Comercial'),
        (SUBTIPO_OFICINA,      '💼 Oficina'),
        (SUBTIPO_BODEGA,       '📦 Bodega'),
        (SUBTIPO_NAVE,         '🏭 Nave Industrial'),
        (SUBTIPO_CONSULTORIO,  '🩺 Consultorio'),
        (SUBTIPO_HOTEL,        '🏨 Hotel / Hostal'),
        (SUBTIPO_EDIFICIO,     '🏗️ Edificio'),
        # Terreno
        (SUBTIPO_URBANO,       '🏙️ Urbano'),
        (SUBTIPO_HABITACIONAL, '🏡 Habitacional'),
        (SUBTIPO_COM_TERRENO,  '🏬 Comercial'),
        (SUBTIPO_AGRICOLA,     '🌾 Agrícola'),
        (SUBTIPO_EJIDAL,       '📜 Ejidal'),
    ], string='Subtipo',
       tracking=True
    )

    operacion_objetivo = fields.Selection([
        (OPERACION_RENTA, '🔑 Renta'),
        (OPERACION_VENTA, '💰 Venta'),
        (OPERACION_AMBAS, '🔑💰 Renta y Venta'),
    ], string='Operación',
       required=True,
       tracking=True,
       help="Tipo de operación que el propietario autoriza al asesor"
    )

    # =========================================================================
    # SECCIÓN 3: ESTADO DEL CICLO DE VIDA
    # =========================================================================

    estado = fields.Selection([
        (ESTADO_DISPONIBLE,     '🟢 Disponible'),
        (ESTADO_EN_NEGOCIACION, '🟡 En Negociación'),
        (ESTADO_OCUPADA,        '🔵 Ocupada'),
        (ESTADO_VENDIDA,        '✅ Vendida'),
        (ESTADO_VACANTE,        '⚪ Vacante'),
        (ESTADO_EN_MANT,        '🔧 En Mantenimiento'),
        (ESTADO_SUSPENDIDA,     '⛔ Suspendida'),
    ], string='Estado',
       default=ESTADO_DISPONIBLE,
       required=True,
       tracking=True,
       index=True,
       help="El asesor actualiza el estado manualmente al avanzar en el flujo. "
            "v2.0: considerar computed automático desde re.contrato activo."
    )

    # Fecha desde la que está disponible para su operación objetivo
    date_disponible = fields.Date(
        string='Disponible desde',
        tracking=True,
        help="Fecha desde la que el propietario autoriza operar el inmueble"
    )

    # =========================================================================
    # SECCIÓN 4: MANTENIMIENTO (estado especial documentado)
    # =========================================================================

    tipo_mantenimiento = fields.Selection([
        (MANT_AMPLIACION,        '🏗️ Ampliación'),
        (MANT_PINTURA,           '🎨 Pintura'),
        (MANT_REMODELACION,      '🔨 Remodelación General'),
        (MANT_ELECTRICIDAD,      '⚡ Instalación Eléctrica'),
        (MANT_FONTANERIA,        '🚿 Fontanería / Plomería'),
        (MANT_IMPERMEABILIZACION,'💧 Impermeabilización'),
        (MANT_TECHADO,           '🏚️ Techado / Azotea'),
        (MANT_OTRO,              '🔧 Otro'),
    ], string='Tipo de Mantenimiento',
       tracking=True,
       help="Clasificación del trabajo en curso cuando el estado es 'En Mantenimiento'"
    )

    notas_mantenimiento = fields.Text(
        string='Descripción del Mantenimiento',
        tracking=True,
        help="Descripción detallada del trabajo: alcance, materiales, "
             "contratista, fecha estimada de finalización."
    )

    date_fin_mantenimiento = fields.Date(
        string='Fin Estimado de Mantenimiento',
        tracking=True,
        help="Fecha estimada en que la propiedad estará disponible "
             "para operación nuevamente"
    )

    # =========================================================================
    # SECCIÓN 5: UBICACIÓN
    # =========================================================================

    calle = fields.Char(string='Calle y Número', tracking=True)
    colonia = fields.Char(string='Colonia / Fraccionamiento', tracking=True)
    municipio = fields.Char(string='Municipio / Alcaldía', tracking=True)
    estado_geografico = fields.Char(
        string='Estado / Provincia',
        tracking=True
    )
    codigo_postal = fields.Char(string='Código Postal', tracking=True)

    country_id = fields.Many2one(
        'res.country',
        string='País',
        default=lambda self: self.env.ref('base.mx', raise_if_not_found=False),
        tracking=True
    )

    # Referencia de Google Maps o coordenadas — útil para el portal
    maps_url = fields.Char(
        string='Link Google Maps',
        help="URL de Google Maps para compartir ubicación con prospectos"
    )

    # Dirección compuesta para display — computed
    direccion_completa = fields.Char(
        string='Dirección Completa',
        compute='_compute_direccion_completa',
        store=True,
        help="Dirección formateada automáticamente para reportes y portal"
    )

    # =========================================================================
    # SECCIÓN 6: CARACTERÍSTICAS FÍSICAS
    # Los campos se muestran/ocultan según tipo_propiedad via invisible en vista
    # =========================================================================

    # --- Comunes a Residencial y Comercial ---
    m2_construccion = fields.Float(
        string='M² Construcción',
        digits=(10, 2),
        tracking=True,
        help="Metros cuadrados de superficie construida"
    )

    # --- Comunes a todos los tipos ---
    m2_terreno = fields.Float(
        string='M² Terreno',
        digits=(10, 2),
        tracking=True,
        help="Metros cuadrados totales del terreno"
    )

    # --- Residencial ---
    recamaras = fields.Integer(
        string='Recámaras',
        help="Número de recámaras. Aplica solo a tipo residencial."
    )

    banos = fields.Float(
        string='Baños',
        digits=(4, 1),
        help="Número de baños completos y medios. Ej: 2.5 = 2 completos + 1 medio"
    )

    medios_banos = fields.Integer(
        string='Medios Baños',
        help="Baños sin ducha (solo WC y lavabo)"
    )

    niveles = fields.Integer(
        string='Niveles / Pisos',
        help="Número de plantas de la propiedad"
    )

    nivel_piso = fields.Integer(
        string='Nivel / Piso',
        help="En departamentos u oficinas: número de piso donde se ubica"
    )

    amueblado = fields.Selection([
        ('sin_muebles', 'Sin muebles'),
        ('semi',        'Semi-amueblado'),
        ('completo',    'Completamente amueblado'),
    ], string='Amueblado',
       help="Aplica a residencial y algunos comerciales"
    )

    # --- Residencial y Comercial ---
    estacionamientos = fields.Integer(
        string='Cajones de Estacionamiento',
        help="Número de espacios de estacionamiento incluidos"
    )

    # --- Comercial específico ---
    altura_bodega = fields.Float(
        string='Altura Interior (m)',
        digits=(6, 2),
        help="Altura libre interior en metros. Relevante para bodegas y naves."
    )

    uso_suelo = fields.Char(
        string='Uso de Suelo',
        help="Clasificación de uso de suelo del inmueble. "
             "Aplica a comercial y terrenos."
    )

    # --- Antigüedad ---
    anio_construccion = fields.Integer(
        string='Año de Construcción',
        help="Año en que se construyó el inmueble"
    )

    # =========================================================================
    # SECCIÓN 7: CONDICIONES ECONÓMICAS
    # =========================================================================

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    precio_renta = fields.Monetary(
        string='Precio de Renta Mensual',
        currency_field='currency_id',
        tracking=True,
        help="Precio de renta mensual autorizado por el propietario"
    )

    precio_venta = fields.Monetary(
        string='Precio de Venta',
        currency_field='currency_id',
        tracking=True,
        help="Precio de lista de venta autorizado por el propietario"
    )

    precio_negociable = fields.Boolean(
        string='Precio Negociable',
        default=True,
        help="Indica si el propietario autoriza negociación de precio"
    )

    deposito_requerido = fields.Monetary(
        string='Depósito Requerido',
        currency_field='currency_id',
        tracking=True,
        help="Monto de depósito en garantía requerido al inquilino"
    )

    comision_pct = fields.Float(
        string='Comisión del Asesor (%)',
        digits=(5, 2),
        default=5.0,
        tracking=True,
        help="Porcentaje de comisión acordado con el propietario. "
             "Estándar de mercado: 3% - 6% del valor de la operación."
    )

    # Comisión calculada — informativa, no stored para no duplicar lógica con re.contrato
    comision_estimada_venta = fields.Monetary(
        string='Comisión Estimada (Venta)',
        currency_field='currency_id',
        compute='_compute_comisiones',
        help="Comisión estimada si se cierra la venta al precio de lista"
    )

    comision_estimada_renta = fields.Monetary(
        string='Comisión Estimada (Renta)',
        currency_field='currency_id',
        compute='_compute_comisiones',
        help="Comisión estimada equivalente a un mes de renta"
    )

    # =========================================================================
    # SECCIÓN 8: FOTOS (submodelo re.propiedad.foto)
    # Límite: MAX_FOTOS_PROPIEDAD = 10 en v1.0
    # Para ampliar en v1.1: cambiar la constante únicamente
    # =========================================================================

    foto_ids = fields.One2many(
        're.propiedad.foto',
        'propiedad_id',
        string='Galería de Fotos',
        help=f"Máximo {MAX_FOTOS_PROPIEDAD} fotos por propiedad. "
             f"Formato recomendado: JPG o PNG · 1080 × 1920 px (vertical) "
             f"o 1920 × 1080 px (horizontal) · Peso máximo: 5 MB por imagen."
    )

    foto_count = fields.Integer(
        string='Fotos',
        compute='_compute_foto_count',
        store=True
    )

    # =========================================================================
    # SECCIÓN 9: NOTAS Y DESCRIPCIÓN PARA PORTAL
    # =========================================================================

    descripcion_portal = fields.Text(
        string='Descripción para Portal / Anuncio',
        tracking=True,
        help="Texto de presentación de la propiedad para el portal del cliente "
             "y plataformas de publicación. Resalta los puntos clave del inmueble."
    )

    notas_internas = fields.Text(
        string='Notas Internas del Asesor',
        help="Notas privadas: acceso, llaves, condiciones especiales del propietario, "
             "historial relevante. No se muestra en el portal."
    )

    amenidades = fields.Text(
        string='Amenidades / Características Extra',
        help="Piscina, gimnasio, seguridad 24h, cisterna, paneles solares, etc."
    )
    
    color = fields.Integer(string='Color Index', default=0)

    # =========================================================================
    # LÓGICA COMPUTED
    # =========================================================================

    @api.depends('calle', 'colonia', 'municipio', 'estado_geografico', 'codigo_postal')
    def _compute_direccion_completa(self):
        """
        Construye la dirección completa para display en reportes y portal.
        """
        for prop in self:
            partes = filter(None, [
                prop.calle,
                prop.colonia,
                prop.municipio,
                prop.estado_geografico,
                prop.codigo_postal,
            ])
            prop.direccion_completa = ', '.join(partes) or _("Sin dirección registrada")

    @api.depends('foto_ids')
    def _compute_foto_count(self):
        """Contador de fotos para el stat button de la vista form."""
        for prop in self:
            prop.foto_count = len(prop.foto_ids)

    @api.depends('precio_venta', 'precio_renta', 'comision_pct')
    def _compute_comisiones(self):
        """
        Calcula comisiones estimadas informativas.
        La comisión real y definitiva se registra en re.contrato.
        """
        for prop in self:
            factor = prop.comision_pct / 100.0
            prop.comision_estimada_venta = prop.precio_venta * factor
            prop.comision_estimada_renta = prop.precio_renta * factor

    # =========================================================================
    # VALIDACIONES
    # =========================================================================

    @api.constrains('comision_pct')
    def _check_comision_rango(self):
        """La comisión debe estar entre 0% y 20% — techo razonable de mercado."""
        for prop in self:
            if not (0.0 <= prop.comision_pct <= 20.0):
                raise ValidationError(_(
                    "La comisión debe estar entre 0%% y 20%%. "
                    "Valor actual: %.2f%%"
                ) % prop.comision_pct)

    @api.constrains('precio_renta', 'precio_venta')
    def _check_precios_positivos(self):
        """Los precios no pueden ser negativos."""
        for prop in self:
            if prop.precio_renta < 0 or prop.precio_venta < 0:
                raise ValidationError(_(
                    "Los precios no pueden ser negativos."
                ))

    @api.constrains('estado', 'tipo_mantenimiento')
    def _check_mantenimiento_coherente(self):
        """
        Si el estado es 'en_mantenimiento', el tipo de mantenimiento es obligatorio.
        Garantiza trazabilidad del motivo de baja temporal.
        """
        for prop in self:
            if prop.estado == ESTADO_EN_MANT and not prop.tipo_mantenimiento:
                raise ValidationError(_(
                    "Al marcar una propiedad como 'En Mantenimiento' "
                    "debes especificar el tipo de trabajo en curso."
                ))

    @api.constrains('operacion_objetivo', 'precio_renta', 'precio_venta')
    def _check_precios_segun_operacion(self):
        """
        Valida que exista precio para la operación declarada.
        Solo advertencia en log — no bloquea para flexibilidad del asesor.
        """
        for prop in self:
            if prop.operacion_objetivo in [OPERACION_RENTA, OPERACION_AMBAS]:
                if not prop.precio_renta:
                    _logger.warning(
                        "⚠️ Propiedad '%s' en renta sin precio de renta registrado",
                        prop.name
                    )
            if prop.operacion_objetivo in [OPERACION_VENTA, OPERACION_AMBAS]:
                if not prop.precio_venta:
                    _logger.warning(
                        "⚠️ Propiedad '%s' en venta sin precio de venta registrado",
                        prop.name
                    )

    # =========================================================================
    # OVERRIDE write — ALERTAS AUTOMÁTICAS EN CHATTER
    # =========================================================================

    def write(self, vals):
        """
        Registra cambios críticos de estado en el Chatter de la propiedad.
        Patrón idéntico a creative_project.py y mensaje.py del Core.
        """
        from markupsafe import Markup

        resultado = super(RePropiedad, self).write(vals)

        if 'estado' in vals:
            nuevo_estado = vals['estado']
            etiquetas = dict(self._fields['estado'].selection)

            for prop in self:
                etiqueta = etiquetas.get(nuevo_estado, nuevo_estado)

                if nuevo_estado == ESTADO_DISPONIBLE:
                    prop.message_post(
                        body=Markup(_(
                            "🟢 <strong>Propiedad marcada como Disponible.</strong><br/>"
                            "El asesor puede iniciar la difusión y captación de prospectos."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                elif nuevo_estado == ESTADO_EN_NEGOCIACION:
                    prop.message_post(
                        body=Markup(_(
                            "🟡 <strong>Propiedad en Negociación.</strong><br/>"
                            "Existe un prospecto activo en proceso de cierre."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                elif nuevo_estado == ESTADO_OCUPADA:
                    prop.message_post(
                        body=Markup(_(
                            "🔵 <strong>Propiedad Ocupada.</strong><br/>"
                            "Contrato de renta activo. "
                            "Inicia el ciclo de administración mensual."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                elif nuevo_estado == ESTADO_VENDIDA:
                    prop.message_post(
                        body=Markup(_(
                            "✅ <strong>¡Propiedad Vendida!</strong><br/>"
                            "Operación de compraventa cerrada exitosamente. "
                            "Verifica cobro de comisión en re.contrato."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                elif nuevo_estado == ESTADO_EN_MANT:
                    tipo_mant = dict(
                        self._fields['tipo_mantenimiento'].selection
                    ).get(prop.tipo_mantenimiento, _("No especificado"))
                    prop.message_post(
                        body=Markup(_(
                            "🔧 <strong>Propiedad en Mantenimiento.</strong><br/>"
                            "Trabajo en curso: <em>%(tipo)s</em><br/>"
                            "No disponible para operación hasta nueva actualización."
                        )) % {'tipo': tipo_mant},
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )
                elif nuevo_estado == ESTADO_SUSPENDIDA:
                    prop.message_post(
                        body=Markup(_(
                            "⛔ <strong>Propiedad Suspendida.</strong><br/>"
                            "El propietario ha retirado temporalmente "
                            "el inmueble del mercado."
                        )),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

                _logger.info(
                    "🏠 Propiedad '%s' → estado: %s",
                    prop.name, etiqueta
                )

        return resultado

    def action_marcar_disponible(self):
        """Acción rápida desde botón — marca la propiedad como disponible."""
        return self.write({'estado': ESTADO_DISPONIBLE})

    def action_marcar_suspendida(self):
        """Acción rápida — suspende la propiedad del mercado."""
        return self.write({'estado': ESTADO_SUSPENDIDA})

    def action_view_photos(self):
    self.ensure_one()
    return {
        'name': _('Fotos de la Propiedad'),
        'type': 'ir.actions.act_window',
        'res_model': 're.propiedad.foto',
        'view_mode': 'kanban,tree,form',
        'domain': [('propiedad_id', '=', self.id)],
        'context': {'default_propiedad_id': self.id},
    }


# =============================================================================
# SUBMODELO: re.propiedad.foto
# Patrón idéntico a product.image de Odoo nativo
# Límite es controlado por constante MAX_FOTOS_PROPIEDAD en re.propiedad
# =============================================================================

class RePropiedadFoto(models.Model):
    """
    Galería de fotos de una propiedad inmobiliaria.

    Submodelo One2many de re.propiedad.
    Soporta N fotos ordenables por secuencia (drag-and-drop en vista).
    El límite de fotos por propiedad se controla via @api.constrains
    en el modelo padre usando la constante MAX_FOTOS_PROPIEDAD.

    Formato recomendado al asesor:
    - Tipo: JPG o PNG
    - Resolución: 1080 × 1920 px (vertical) o 1920 × 1080 px (horizontal)
    - Peso máximo: 5 MB por imagen

    Para v1.1: considerar integración con CDN o almacenamiento externo
    si la cartera supera 100 propiedades con galería completa.
    """
    _name = 're.propiedad.foto'
    _description = 'Foto de Propiedad — Caletti Real Estate'
    _order = 'sequence asc, id asc'

    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad',
        required=True,
        ondelete='cascade',
        index=True
    )

    name = fields.Char(
        string='Descripción de la Foto',
        help="Ej: 'Sala principal', 'Cocina integral', 'Fachada frontal', "
             "'Vista aérea del terreno'"
    )

    sequence = fields.Integer(
        string='Orden',
        default=10,
        help="Orden de aparición en la galería. "
             "Arrastra para reordenar en la vista lista."
    )

    # Odoo 17 nativo: image_1920 genera automáticamente
    # los thumbnails image_1024, image_512, image_256, image_128
    imagen = fields.Image(
        string='Foto',
        required=True,
        max_width=1920,
        max_height=1920,
        help="Formato: JPG o PNG · "
             "Resolución recomendada: 1920 × 1080 px (horizontal) "
             "o 1080 × 1920 px (vertical) · "
             "Peso máximo: 5 MB por imagen."
    )

    imagen_512 = fields.Image(
        string='Miniatura',
        related='imagen',
        max_width=512,
        max_height=512,
        store=True,
        help="Miniatura generada automáticamente para galería y portal"
    )

    es_portada = fields.Boolean(
        string='Foto de Portada',
        default=False,
        help="La foto de portada aparece primero en el portal y los reportes. "
             "Solo puede haber una foto de portada por propiedad."
    )

    # =========================================================================
    # VALIDACIONES DEL SUBMODELO
    # =========================================================================

    @api.constrains('propiedad_id')
    def _check_limite_fotos(self):
        """
        Valida que no se supere el límite de fotos por propiedad.
        Límite controlado por constante MAX_FOTOS_PROPIEDAD.
        Para ampliar en v1.1: cambiar el valor de la constante únicamente.
        """
        for foto in self:
            total = self.search_count([
                ('propiedad_id', '=', foto.propiedad_id.id)
            ])
            if total > MAX_FOTOS_PROPIEDAD:
                raise ValidationError(_(
                    "La propiedad '%(propiedad)s' ya tiene %(max)d fotos "
                    "(límite máximo de v1.0).\n\n"
                    "Elimina una foto existente antes de agregar una nueva."
                ) % {
                    'propiedad': foto.propiedad_id.name,
                    'max': MAX_FOTOS_PROPIEDAD,
                })

    @api.constrains('es_portada', 'propiedad_id')
    def _check_una_sola_portada(self):
        """Solo puede existir una foto de portada por propiedad."""
        for foto in self:
            if foto.es_portada:
                otras_portadas = self.search([
                    ('propiedad_id', '=', foto.propiedad_id.id),
                    ('es_portada', '=', True),
                    ('id', '!=', foto.id),
                ])
                if otras_portadas:
                    raise ValidationError(_(
                        "La propiedad '%(propiedad)s' ya tiene una foto "
                        "de portada asignada.\n"
                        "Desmarca la portada actual antes de asignar una nueva."
                    ) % {'propiedad': foto.propiedad_id.name})