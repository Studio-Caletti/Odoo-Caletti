# caletti_real_estate/models/re_contrato.py
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
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES: TIPO DE OPERACIÓN DEL CONTRATO
# Un solo modelo maneja renta Y venta — diferenciado por tipo_operacion
# =============================================================================
TIPO_RENTA  = 'renta'
TIPO_VENTA  = 'venta'

# =============================================================================
# CONSTANTES: ESTADOS DEL CONTRATO contemplados
# =============================================================================
ESTADO_BORRADOR    = 'borrador'      # en preparación, aún no firmado
ESTADO_ACTIVO      = 'activo'        # firmado y vigente
ESTADO_POR_VENCER  = 'por_vencer'   # dentro de los 60 días de vencimiento
ESTADO_VENCIDO     = 'vencido'      # fecha fin superada sin renovar
ESTADO_RENOVADO    = 'renovado'     # fue reemplazado por nuevo contrato
ESTADO_TERMINADO   = 'terminado'    # terminación anticipada o normal
ESTADO_CANCELADO   = 'cancelado'    # cancelado antes de firma

# =============================================================================
# CONSTANTES: MOTIVOS DE TERMINACIÓN
# =============================================================================
TERMINO_VENCIMIENTO   = 'vencimiento_natural'
TERMINO_MUTUO         = 'acuerdo_mutuo'
TERMINO_INCUMPLIMIENTO = 'incumplimiento_inquilino'
TERMINO_PROPIETARIO   = 'decision_propietario'
TERMINO_ESCRITURACION = 'escrituracion_completada'   # solo venta
TERMINO_OTRO          = 'otro'

# =============================================================================
# CONSTANTES: PERIODICIDAD DE RENTA
# =============================================================================
PERIODO_MENSUAL    = 'mensual'
PERIODO_BIMESTRAL  = 'bimestral'
PERIODO_TRIMESTRAL = 'trimestral'
PERIODO_ANUAL      = 'anual'

# =============================================================================
# CONSTANTES: ALERTAS DE VENCIMIENTO
# Días antes del vencimiento para disparar notificación al asesor
# =============================================================================
DIAS_ALERTA_VENCIMIENTO = 60

# =============================================================================
# CONSTANTES: SUBMODELO RE.PAGO — ESTADOS
# =============================================================================
PAGO_PENDIENTE  = 'pendiente'
PAGO_PAGADO     = 'pagado'
PAGO_ATRASADO   = 'atrasado'
PAGO_PARCIAL    = 'parcial'
PAGO_CANCELADO  = 'cancelado'

# =============================================================================
# CONSTANTES: MÉTODOS DE PAGO
# =============================================================================
METODO_TRANSFERENCIA = 'transferencia'
METODO_EFECTIVO      = 'efectivo'
METODO_CHEQUE        = 'cheque'
METODO_DEPOSITO      = 'deposito'
METODO_OTRO          = 'otro'

# =============================================================================
# CONSTANTE: UMBRAL DE CALIDAD DE INQUILINO
# Pagos atrasados antes de marcar al inquilino como riesgo
# =============================================================================
UMBRAL_PAGOS_ATRASADOS = 2


class ReContrato(models.Model):
    """
    Contrato inmobiliario — Caletti Real Estate.

    Modelo unificado que maneja tanto contratos de RENTA como de VENTA,
    diferenciados por el campo tipo_operacion. Esta decisión simplifica
    la gestión del asesor independiente que maneja ambas operaciones
    desde una sola vista.

    RENTA:
    - Vigencia: fecha_inicio → fecha_fin (plazo en meses)
    - Depósito en garantía registrado y devuelto al terminar
    - Submodelo re.pago para seguimiento mensual de cobros
    - Alerta automática 60 días antes del vencimiento (cron)
    - Renovación: nuevo contrato vinculado via contrato_origen_id

    VENTA:
    - Precio final, enganche y saldo
    - Comisión del asesor pagada por el propietario
    - Estados: borrador → activo → terminado (escrituración completada)
    - Sin re.pago — la venta es una sola operación de cierre

    Comisión: capturada manualmente por el asesor.
    Pagador: siempre el propietario del inmueble (v1.0).

    Integración con account.move evaluada para v1.1
    previa revisión arquitectónica Carlos Caletti + asesor técnico.
    """
    _name = 're.contrato'
    _description = 'Contrato Inmobiliario — Caletti Real Estate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _order = 'estado asc, fecha_inicio desc'

    # =========================================================================
    # SECCIÓN 1: IDENTIFICACIÓN
    # =========================================================================

    name = fields.Char(
        string='Referencia del Contrato',
        required=True,
        index=True,
        tracking=True,
        copy=False,
        help="Clave única del contrato. Ej: 'CONT-RENTA-2026-001' "
             "o 'CONT-VENTA-2026-001'"
    )

    tipo_operacion = fields.Selection([
        (TIPO_RENTA, '🔑 Renta'),
        (TIPO_VENTA, '💰 Venta / Compraventa'),
    ], string='Tipo de Operación',
       required=True,
       tracking=True,
       index=True,
       help="Define si es contrato de arrendamiento o compraventa. "
            "Controla qué campos y secciones son relevantes."
    )

    estado = fields.Selection([
        (ESTADO_BORRADOR,   '📝 Borrador'),
        (ESTADO_ACTIVO,     '✅ Activo'),
        (ESTADO_POR_VENCER, '⚠️ Por Vencer'),
        (ESTADO_VENCIDO,    '🔴 Vencido'),
        (ESTADO_RENOVADO,   '🔄 Renovado'),
        (ESTADO_TERMINADO,  '🏁 Terminado'),
        (ESTADO_CANCELADO,  '❌ Cancelado'),
    ], string='Estado',
       default=ESTADO_BORRADOR,
       required=True,
       tracking=True,
       index=True
    )

    # =========================================================================
    # SECCIÓN 2: PARTES DEL CONTRATO
    # =========================================================================

    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad',
        required=True,
        index=True,
        tracking=True,
        help="Inmueble objeto del contrato"
    )

    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        related='propiedad_id.propietario_id',
        store=True,
        readonly=True,
        help="Propietario legal — se obtiene automáticamente de la propiedad"
    )

    # Para renta: el inquilino
    inquilino_id = fields.Many2one(
        'res.partner',
        string='Inquilino',
        index=True,
        tracking=True,
        invisible="tipo_operacion != 'renta'",
        help="Persona o empresa que ocupará el inmueble en arrendamiento"
    )

    # Para venta: el comprador
    comprador_id = fields.Many2one(
        'res.partner',
        string='Comprador',
        index=True,
        tracking=True,
        invisible="tipo_operacion != 'venta'",
        help="Persona o empresa que adquiere el inmueble"
    )

    # Campo computed unificado para mostrar la contraparte en listas
    contraparte_id = fields.Many2one(
        'res.partner',
        string='Contraparte',
        compute='_compute_contraparte',
        store=True,
        help="Inquilino o comprador según tipo de operación"
    )

    prospecto_id = fields.Many2one(
        're.prospecto',
        string='Prospecto Origen',
        tracking=True,
        help="Prospecto del pipeline que originó este contrato. "
             "Vincula el cierre con el lead de captación."
    )

    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor Responsable',
        related='propiedad_id.asesor_id',
        store=True,
        readonly=True,
        help="Asesor responsable — se hereda de la propiedad"
    )

    # =========================================================================
    # SECCIÓN 3: VIGENCIA (renta y venta tienen lógica distinta)
    # =========================================================================

    fecha_inicio = fields.Date(
        string='Fecha de Inicio / Firma',
        required=True,
        tracking=True,
        help="Fecha de inicio del arrendamiento o firma de compraventa"
    )

    # Solo para renta
    plazo_meses = fields.Integer(
        string='Plazo (meses)',
        default=12,
        tracking=True,
        help="Duración del contrato de renta en meses. "
             "Estándar: 12 meses. La fecha fin se calcula automáticamente."
    )

    fecha_fin = fields.Date(
        string='Fecha de Vencimiento',
        compute='_compute_fecha_fin',
        store=True,
        tracking=True,
        help="Para renta: calculada automáticamente desde fecha inicio + plazo. "
             "Para venta: fecha estimada de escrituración."
    )

    fecha_fin_manual = fields.Date(
        string='Fecha Fin Manual',
        tracking=True,
        help="Sobreescribe el cálculo automático de fecha fin. "
             "Úsalo cuando el plazo no es exactamente en meses."
    )

    # Para venta: fecha de escrituración
    fecha_escrituracion = fields.Date(
        string='Fecha de Escrituración',
        tracking=True,
        help="Fecha en que se realizará o realizó la escritura ante notario"
    )

    dias_para_vencer = fields.Integer(
        string='Días para Vencer',
        compute='_compute_dias_vencer',
        store=True,
        help="Días restantes hasta el vencimiento del contrato"
    )

    alerta_vencimiento = fields.Boolean(
        string='Alerta de Vencimiento Activa',
        compute='_compute_dias_vencer',
        store=True,
        help=f"True cuando faltan menos de {DIAS_ALERTA_VENCIMIENTO} días "
             f"para el vencimiento del contrato de renta"
    )

    # =========================================================================
    # SECCIÓN 4: CONDICIONES ECONÓMICAS — RENTA
    # =========================================================================

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    monto_renta = fields.Monetary(
        string='Renta Mensual',
        currency_field='currency_id',
        tracking=True,
        help="Monto mensual pactado en el contrato de arrendamiento"
    )

    periodicidad_pago = fields.Selection([
        (PERIODO_MENSUAL,    'Mensual'),
        (PERIODO_BIMESTRAL,  'Bimestral'),
        (PERIODO_TRIMESTRAL, 'Trimestral'),
        (PERIODO_ANUAL,      'Anual'),
    ], string='Periodicidad de Pago',
       default=PERIODO_MENSUAL,
       tracking=True,
       help="Frecuencia con la que se cobra la renta"
    )

    dia_pago = fields.Integer(
        string='Día de Pago',
        default=1,
        tracking=True,
        help="Día del mes en que vence el pago de renta. Ej: 1, 5, 15"
    )

    monto_deposito = fields.Monetary(
        string='Depósito en Garantía',
        currency_field='currency_id',
        tracking=True,
        help="Monto recibido como garantía. Equivale usualmente a 1-2 meses de renta."
    )

    deposito_recibido = fields.Boolean(
        string='Depósito Recibido',
        tracking=True,
        default=False,
        help="Confirma que el depósito en garantía fue efectivamente recibido "
             "por el propietario antes de la entrega de llaves"
    )

    deposito_devuelto = fields.Boolean(
        string='Depósito Devuelto',
        tracking=True,
        default=False,
        help="Confirma que el depósito fue devuelto al inquilino "
             "al término del contrato"
    )

    fecha_devolucion_deposito = fields.Date(
        string='Fecha Devolución Depósito',
        tracking=True,
        help="Fecha en que se devolvió el depósito al inquilino"
    )

    incremento_anual_pct = fields.Float(
        string='Incremento Anual (%)',
        digits=(5, 2),
        default=0.0,
        tracking=True,
        help="Porcentaje de incremento anual pactado sobre la renta mensual. "
             "Común vincularlo al INPC. Ej: 4.5"
    )

    # =========================================================================
    # SECCIÓN 5: CONDICIONES ECONÓMICAS — VENTA
    # =========================================================================

    precio_venta_final = fields.Monetary(
        string='Precio de Venta Final',
        currency_field='currency_id',
        tracking=True,
        help="Precio de compraventa acordado entre propietario y comprador"
    )

    monto_enganche = fields.Monetary(
        string='Enganche',
        currency_field='currency_id',
        tracking=True,
        help="Monto del enganche o anticipo pactado"
    )

    saldo_escrituracion = fields.Monetary(
        string='Saldo a Pagar en Escrituración',
        currency_field='currency_id',
        compute='_compute_saldo_escrituracion',
        store=True,
        help="Precio final menos el enganche. Puede provenir de crédito hipotecario."
    )

    tipo_financiamiento = fields.Selection([
        ('contado',    '💵 Contado'),
        ('hipotecario', '🏦 Crédito Hipotecario'),
        ('infonavit',  '🏠 INFONAVIT'),
        ('fovissste',  '🏛️ FOVISSSTE'),
        ('mixto',      '🔀 Mixto'),
        ('otro',       '📋 Otro'),
    ], string='Tipo de Financiamiento',
       tracking=True,
       help="Forma en que el comprador financiará la adquisición"
    )

    banco_hipotecario = fields.Char(
        string='Banco / Institución',
        tracking=True,
        help="Institución financiera que otorga el crédito hipotecario"
    )

    # =========================================================================
    # SECCIÓN 6: COMISIÓN DEL ASESOR
    # Capturada manualmente — pagador siempre es el propietario (v1.0)
    # =========================================================================

    comision_monto = fields.Monetary(
        string='Comisión del Asesor',
        currency_field='currency_id',
        tracking=True,
        help="Monto de comisión acordado con el propietario. "
             "Captura manual — referencia: porcentaje en re.propiedad."
    )

    comision_pagada = fields.Boolean(
        string='Comisión Cobrada',
        tracking=True,
        default=False,
        help="Confirma que el asesor recibió el pago de su comisión "
             "por parte del propietario"
    )

    fecha_cobro_comision = fields.Date(
        string='Fecha de Cobro de Comisión',
        tracking=True,
        help="Fecha en que el propietario pagó la comisión al asesor"
    )

    # Nota: comision_pagador = propietario — hardcoded en v1.0
    # Si en v2.0 se requiere dividir entre partes, agregar campo Selection aquí

    # =========================================================================
    # INTEGRACIÓN CONTABLE — v1.1
    # Diario contable para facturas de renta y registro de comisión.
    # El usuario puede seleccionar el diario emisor por contrato.
    # =========================================================================

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario Contable',
        domain=[('type', 'in', ['sale', 'general'])],
        tracking=True,
        help="Diario contable usado para generar facturas de renta "
             "y registros de comisión. Si no se selecciona, "
             "se usará el diario de ventas por defecto de la compañía."
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Documentos Contables',
        compute='_compute_move_ids',
        help="Facturas y registros contables generados por este contrato."
    )
    move_count = fields.Integer(
        string='Documentos Contables',
        compute='_compute_move_ids'
    )

    @api.depends('name')
    def _compute_move_ids(self):
        for contrato in self:
            if not contrato.name:
                contrato.move_ids   = False
                contrato.move_count = 0
                continue
            moves = self.env['account.move'].search([
                ('ref', 'like', contrato.name),
                ('move_type', 'in', [
                    'out_invoice', 'in_invoice',
                    'out_receipt',  'in_receipt'
                ]),
            ])
            contrato.move_ids   = moves
            contrato.move_count = len(moves)


    # =========================================================================
    # SECCIÓN 7: RENOVACIÓN Y TRAZABILIDAD DE HISTORIAL
    # =========================================================================

    contrato_origen_id = fields.Many2one(
        're.contrato',
        string='Contrato Anterior',
        tracking=True,
        copy=False,
        help="Contrato de renta que este reemplaza en una renovación. "
             "Permite trazabilidad completa del historial de la propiedad."
    )

    contrato_renovacion_id = fields.Many2one(
        're.contrato',
        string='Contrato de Renovación',
        readonly=True,
        copy=False,
        help="Nuevo contrato generado al renovar este. "
             "Se asigna automáticamente al crear la renovación."
    )

    veces_renovado = fields.Integer(
        string='Número de Renovación',
        default=0,
        readonly=True,
        help="0 = contrato original. 1 = primera renovación. Etc."
    )

    motivo_terminacion = fields.Selection([
        (TERMINO_VENCIMIENTO,    '📅 Vencimiento natural'),
        (TERMINO_MUTUO,          '🤝 Acuerdo mutuo'),
        (TERMINO_INCUMPLIMIENTO, '⚠️ Incumplimiento del inquilino'),
        (TERMINO_PROPIETARIO,    '🏠 Decisión del propietario'),
        (TERMINO_ESCRITURACION,  '✅ Escrituración completada'),
        (TERMINO_OTRO,           '📋 Otro motivo'),
    ], string='Motivo de Terminación',
       tracking=True,
       help="Razón por la que el contrato fue dado por terminado"
    )

    notas_terminacion = fields.Text(
        string='Notas de Terminación',
        tracking=True,
        help="Detalle adicional sobre la terminación del contrato"
    )

    # =========================================================================
    # SECCIÓN 8: FECHAS DE ENTREGA FÍSICA
    # =========================================================================

    fecha_entrega_llaves = fields.Date(
        string='Entrega de Llaves al Inquilino/Comprador',
        tracking=True,
        help="Fecha en que se hizo entrega física del inmueble "
             "con acta de entrega-recepción"
    )

    fecha_devolucion_llaves = fields.Date(
        string='Devolución de Llaves',
        tracking=True,
        help="Fecha en que el inquilino devolvió las llaves y el inmueble "
             "al propietario al término del contrato"
    )

    # =========================================================================
    # SECCIÓN 9: SUBMODELO RE.PAGO (solo renta)
    # =========================================================================

    pago_ids = fields.One2many(
        're.pago',
        'contrato_id',
        string='Registro de Pagos',
        help="Historial de pagos mensuales de renta. "
             "Solo aplica para contratos de arrendamiento."
    )

    pago_count = fields.Integer(
        string='Total Pagos',
        compute='_compute_metricas_pago',
        store=True
    )

    pagos_atrasados_count = fields.Integer(
        string='Pagos Atrasados',
        compute='_compute_metricas_pago',
        store=True,
        help="Número de pagos marcados como atrasados. "
             "Alimenta la calidad del inquilino."
    )

    pago_puntualidad_pct = fields.Float(
        string='Puntualidad de Pagos (%)',
        compute='_compute_metricas_pago',
        store=True,
        digits=(5, 1),
        help="Porcentaje de pagos realizados a tiempo. "
             "Métrica de calidad del inquilino."
    )

    inquilino_riesgo = fields.Boolean(
        string='Inquilino en Riesgo',
        compute='_compute_metricas_pago',
        store=True,
        help=f"True cuando el inquilino acumula más de "
             f"{UMBRAL_PAGOS_ATRASADOS} pagos atrasados"
    )

    mantenimiento_ids = fields.One2many(
        're.mantenimiento', # Modelo destino
        'contrato_id',      # Campo inverso en re.mantenimiento
        string='Mantenimientos Relacionados',
        help="Historial de mantenimientos realizados durante la vigencia de este contrato."
    )

    # =========================================================================
    # SECCIÓN 10: NOTAS
    # =========================================================================

    notas = fields.Text(
        string='Notas',
        help="Observaciones sobre el pago: acuerdos especiales, "
             "descuentos aplicados, penalizaciones, restricciones, etc."
    )


    clausulas_especiales = fields.Text(
        string='Cláusulas Especiales',
        tracking=True,
        help="Condiciones particulares pactadas: mascotas, remodelaciones "
             "autorizadas, uso del inmueble, restricciones especiales."
    )

    notas_internas = fields.Text(
        string='Notas Internas del Asesor',
        help="Observaciones privadas del asesor sobre el contrato "
             "o las partes involucradas"
    )

    color = fields.Integer(string='Color Index', default=0)



    # =========================================================================
    # LÓGICA COMPUTED
    # =========================================================================

    @api.depends('inquilino_id', 'comprador_id', 'tipo_operacion')
    def _compute_contraparte(self):
        """Unifica inquilino/comprador en un campo para vistas de lista."""
        for contrato in self:
            if contrato.tipo_operacion == TIPO_RENTA:
                contrato.contraparte_id = contrato.inquilino_id
            else:
                contrato.contraparte_id = contrato.comprador_id

    @api.depends('fecha_inicio', 'plazo_meses', 'fecha_fin_manual',
                 'tipo_operacion')
    def _compute_fecha_fin(self):
        """
        Calcula fecha de vencimiento del contrato de renta.
        Si existe fecha_fin_manual, la usa como override.
        Para venta: no aplica cálculo automático.
        """
        for contrato in self:
            if contrato.fecha_fin_manual:
                contrato.fecha_fin = contrato.fecha_fin_manual
            elif (contrato.tipo_operacion == TIPO_RENTA
                  and contrato.fecha_inicio
                  and contrato.plazo_meses):
                contrato.fecha_fin = (
                    contrato.fecha_inicio
                    + relativedelta(months=contrato.plazo_meses)
                )
            else:
                contrato.fecha_fin = False

    @api.depends('fecha_fin', 'estado', 'tipo_operacion')
    def _compute_dias_vencer(self):
        """
        Calcula días restantes para el vencimiento.
        Activa alerta_vencimiento cuando faltan <= DIAS_ALERTA_VENCIMIENTO.
        Solo aplica a contratos de renta activos o por_vencer.
        """
        today = fields.Date.today()
        for contrato in self:
            if (contrato.tipo_operacion == TIPO_RENTA
                    and contrato.fecha_fin
                    and contrato.estado in [ESTADO_ACTIVO, ESTADO_POR_VENCER]):
                dias = (contrato.fecha_fin - today).days
                contrato.dias_para_vencer  = dias
                contrato.alerta_vencimiento = dias <= DIAS_ALERTA_VENCIMIENTO
            else:
                contrato.dias_para_vencer   = 0
                contrato.alerta_vencimiento = False

    @api.depends('precio_venta_final', 'monto_enganche')
    def _compute_saldo_escrituracion(self):
        """Saldo pendiente de pago en escrituración = precio - enganche."""
        for contrato in self:
            contrato.saldo_escrituracion = max(
                0.0,
                contrato.precio_venta_final - contrato.monto_enganche
            )

    @api.depends('pago_ids', 'pago_ids.estado')
    def _compute_metricas_pago(self):
        """
        Calcula métricas de calidad del inquilino basadas en historial de pagos.
        Alimenta inquilino_riesgo para alertas proactivas del asesor.
        """
        for contrato in self:
            pagos = contrato.pago_ids
            total = len(pagos)
            atrasados = len(pagos.filtered(
                lambda p: p.estado == PAGO_ATRASADO
            ))
            pagados_a_tiempo = len(pagos.filtered(
                lambda p: p.estado == PAGO_PAGADO
                and not p.pago_tardio
            ))

            contrato.pago_count             = total
            contrato.pagos_atrasados_count  = atrasados
            contrato.pago_puntualidad_pct   = (
                (pagados_a_tiempo / total * 100.0) if total > 0 else 0.0
            )
            contrato.inquilino_riesgo = atrasados > UMBRAL_PAGOS_ATRASADOS

    # =========================================================================
    # VALIDACIONES
    # =========================================================================

    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas_coherentes(self):
        """La fecha fin no puede ser anterior a la fecha de inicio."""
        for contrato in self:
            if (contrato.fecha_fin
                    and contrato.fecha_inicio
                    and contrato.fecha_fin <= contrato.fecha_inicio):
                raise ValidationError(_(
                    "La fecha de vencimiento debe ser posterior "
                    "a la fecha de inicio en el contrato '%(nombre)s'."
                ) % {'nombre': contrato.name})

    @api.constrains('plazo_meses')
    def _check_plazo_positivo(self):
        """El plazo debe ser mayor a cero para contratos de renta."""
        for contrato in self:
            if (contrato.tipo_operacion == TIPO_RENTA
                    and contrato.plazo_meses <= 0):
                raise ValidationError(_(
                    "El plazo del contrato de renta debe ser "
                    "mayor a cero meses."
                ))

    @api.constrains('dia_pago')
    def _check_dia_pago_valido(self):
        """El día de pago debe estar entre 1 y 28."""
        for contrato in self:
            if (contrato.tipo_operacion == TIPO_RENTA
                    and not (1 <= contrato.dia_pago <= 28)):
                raise ValidationError(_(
                    "El día de pago debe estar entre 1 y 28 "
                    "para garantizar compatibilidad con todos los meses."
                ))

    @api.constrains('monto_renta')
    def _check_monto_renta_positivo(self):
        """Verifica que el monto el pago de la renta sea mayor a 0."""
        for contrato in self:
            if contrato.tipo_operacion == TIPO_RENTA and contrato.monto_renta <= 0:
                raise ValidationError(_(
                    "El monto de renta debe ser mayor a cero."
                ))

    @api.constrains('precio_venta_final')
    def _check_precio_venta_positivo(self):
        for contrato in self:
            if (contrato.tipo_operacion == TIPO_VENTA
                    and contrato.precio_venta_final <= 0):
                raise ValidationError(_(
                    "El precio de venta debe ser mayor a cero."
                ))

    @api.constrains('tipo_operacion', 'inquilino_id', 'comprador_id')
    def _check_contraparte_requerida(self):
        """Renta requiere inquilino, venta requiere comprador."""
        for contrato in self:
            if (contrato.tipo_operacion == TIPO_RENTA
                    and contrato.estado != ESTADO_BORRADOR
                    and not contrato.inquilino_id):
                raise ValidationError(_(
                    "El contrato de renta requiere un inquilino "
                    "antes de activarse."
                ))
            if (contrato.tipo_operacion == TIPO_VENTA
                    and contrato.estado != ESTADO_BORRADOR
                    and not contrato.comprador_id):
                raise ValidationError(_(
                    "El contrato de compraventa requiere un comprador "
                    "antes de activarse."
                ))

    @api.constrains('contrato_origen_id')
    def _check_sin_autoreferencia(self):
        """Un contrato no puede ser su propio origen."""
        for contrato in self:
            if (contrato.contrato_origen_id
                    and contrato.contrato_origen_id.id == contrato.id):
                raise ValidationError(_(
                    "Un contrato no puede referenciarse a sí mismo "
                    "como contrato anterior."
                ))

    # =========================================================================
    # ACCIONES DE WORKFLOW
    # =========================================================================

    def action_view_pagos(self):
        """ Acción para el Stat Button: abre la lista de pagos vinculados """
        self.ensure_one()
        return {
            'name': _('Pagos de Renta'),
            'type': 'ir.actions.act_window',
            'res_model': 're.pago',
            'view_mode': 'tree,form',
            'domain': [('contrato_id', '=', self.id)],
            'context': {'default_contrato_id': self.id},
        }

   
    def action_activar(self):
        """
        Activa el contrato — de borrador a activo.
        Actualiza el estado de la propiedad a 'ocupada' (renta)
        o deja en 'en_negociacion' hasta escriturar (venta).
        """
        self.ensure_one()
        if self.estado != ESTADO_BORRADOR:
            raise UserError(_(
                "Solo se puede activar un contrato en estado Borrador."
            ))

        self.write({'estado': ESTADO_ACTIVO})

        # Actualizar estado de la propiedad según tipo de operación
        if self.tipo_operacion == TIPO_RENTA:
            self.propiedad_id.write({'estado': 'ocupada'})
            _logger.info(
                "🔑 Contrato de renta '%s' activado. "
                "Propiedad '%s' → ocupada",
                self.name, self.propiedad_id.name
            )
        else:
            _logger.info(
                "💰 Contrato de venta '%s' activado. "
                "Propiedad permanece en 'en_negociacion' hasta escriturar.",
                self.name
            )

        # Generar pagos automáticos para contrato de renta
        if self.tipo_operacion == TIPO_RENTA:
            self._generar_pagos_renta()

    def action_terminar(self):
        """
        Termina el contrato. Requiere motivo de terminación.
        Para renta: actualiza propiedad a 'vacante'.
        Para venta: actualiza propiedad a 'vendida'.
        """
        self.ensure_one()
        if not self.motivo_terminacion:
            raise UserError(_(
                "Especifica el motivo de terminación antes de continuar."
            ))

        if self.tipo_operacion == TIPO_RENTA:
            self.propiedad_id.write({'estado': 'vacante'})
            _logger.info(
                "🏁 Contrato de renta '%s' terminado. "
                "Propiedad '%s' → vacante",
                self.name, self.propiedad_id.name
            )
        else:
            self.propiedad_id.write({'estado': 'vendida'})
            _logger.info(
                "✅ Contrato de venta '%s' terminado. "
                "Propiedad '%s' → vendida",
                self.name, self.propiedad_id.name
            )

        self.write({'estado': ESTADO_TERMINADO})

    def action_cancelar(self):
        """Cancela el contrato antes de que sea firmado (desde borrador)."""
        self.ensure_one()
        if self.estado not in [ESTADO_BORRADOR]:
            raise UserError(_(
                "Solo se puede cancelar un contrato en estado Borrador. "
                "Para contratos activos usa 'Terminar'."
            ))
        self.write({'estado': ESTADO_CANCELADO})

    def action_crear_renovacion(self):
        """
        Crea un nuevo contrato de renta vinculado a este como origen.
        El nuevo contrato hereda: propiedad, partes, condiciones base.
        El asesor ajusta monto, plazo y fecha inicio antes de activar.

        Alerta 60 días antes del vencimiento disparada por cron
        lleva al asesor a esta acción.
        """
        self.ensure_one()
        if self.tipo_operacion != TIPO_RENTA:
            raise UserError(_(
                "Las renovaciones solo aplican a contratos de renta."
            ))
        if self.estado not in [ESTADO_ACTIVO, ESTADO_POR_VENCER, ESTADO_VENCIDO]:
            raise UserError(_(
                "Solo se puede renovar un contrato Activo, "
                "Por Vencer o Vencido."
            ))
        if self.contrato_renovacion_id:
            raise UserError(_(
                "Este contrato ya tiene una renovación generada: "
                "%(nombre)s"
            ) % {'nombre': self.contrato_renovacion_id.name})

        # Calcular incremento de renta si aplica
        nueva_renta = self.monto_renta
        if self.incremento_anual_pct > 0:
            nueva_renta = self.monto_renta * (
                1 + self.incremento_anual_pct / 100.0
            )

        nueva_fecha_inicio = self.fecha_fin or fields.Date.today()

        renovacion = self.copy({
            'name': f"{self.name} — Renovación {self.veces_renovado + 1}",
            'estado': ESTADO_BORRADOR,
            'fecha_inicio': nueva_fecha_inicio,
            'monto_renta': nueva_renta,
            'contrato_origen_id': self.id,
            'veces_renovado': self.veces_renovado + 1,
            'contrato_renovacion_id': False,
            'pago_ids': False,
            'deposito_recibido': False,
            'deposito_devuelto': False,
            'comision_pagada': False,
            'fecha_cobro_comision': False,
            'fecha_entrega_llaves': False,
            'fecha_devolucion_llaves': False,
            'motivo_terminacion': False,
            'notas_terminacion': False,
        })

        # Marcar este contrato como renovado y vincular al nuevo
        self.write({
            'estado': ESTADO_RENOVADO,
            'contrato_renovacion_id': renovacion.id,
        })

        self.message_post(
            body=Markup(_(
                "🔄 <strong>Contrato renovado.</strong><br/>"
                "Nueva renovación generada: "
                "<strong>%(nombre)s</strong><br/>"
                "Nueva renta: <strong>%(renta)s</strong> "
                "(incremento %(pct).1f%%)<br/>"
                "Nuevo inicio: <strong>%(fecha)s</strong>"
            )) % {
                'nombre': renovacion.name,
                'renta': f"{nueva_renta:,.2f} {self.currency_id.symbol}",
                'pct': self.incremento_anual_pct,
                'fecha': str(nueva_fecha_inicio),
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(
            "🔄 Renovación '%s' creada desde '%s'. "
            "Nueva renta: %.2f. Inicio: %s",
            renovacion.name, self.name,
            nueva_renta, nueva_fecha_inicio
        )

        # Redirigir al nuevo contrato en borrador para revisión
        return {
            'type': 'ir.actions.act_window',
            'res_model': 're.contrato',
            'res_id': renovacion.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _generar_pagos_renta(self):
        """
        Genera los registros de re.pago para todos los meses del contrato.
        Se llama automáticamente al activar un contrato de renta.
        Cada pago queda en estado 'pendiente' con su fecha de vencimiento.
        """
        self.ensure_one()
        if self.tipo_operacion != TIPO_RENTA:
            return
        if not self.fecha_inicio or not self.fecha_fin:
            _logger.warning(
                "⚠️ Contrato '%s' sin fechas definidas — "
                "no se generan pagos",
                self.name
            )
            return

        pagos_a_crear = []
        fecha_actual = self.fecha_inicio.replace(day=self.dia_pago)

        # Si el día de pago ya pasó en el mes de inicio, empezar en el siguiente
        if fecha_actual < self.fecha_inicio:
            fecha_actual = fecha_actual + relativedelta(months=1)

        numero_pago = 1
        while fecha_actual <= self.fecha_fin:
            pagos_a_crear.append({
                'contrato_id':  self.id,
                'numero_pago':  numero_pago,
                'fecha_vencimiento': fecha_actual,
                'monto_esperado': self.monto_renta,
                'estado':       PAGO_PENDIENTE,
                'name': _(
                    "Pago %(num)d — %(mes)s"
                ) % {
                    'num': numero_pago,
                    'mes': fecha_actual.strftime('%B %Y'),
                }
            })
            fecha_actual = fecha_actual + relativedelta(months=1)
            numero_pago += 1

        if pagos_a_crear:
            self.env['re.pago'].create(pagos_a_crear)
            _logger.info(
                "📅 %d pagos generados para contrato '%s'",
                len(pagos_a_crear), self.name
            )

    # =========================================================================
    # CRON: ALERTAS DE VENCIMIENTO
    # Se llama diariamente — mismo patrón que _cron_check_overdue_tasks del Core
    # =========================================================================

    def _cron_alertas_vencimiento(self):
        """
        Revisa contratos de renta activos próximos a vencer.
        Actualiza estado a 'por_vencer' y notifica al asesor via Chatter.
        Disparado 60 días antes del vencimiento.
        """
        _logger.info("🔄 Revisando vencimientos de contratos de renta...")
        today = fields.Date.today()
        fecha_limite = today + relativedelta(days=DIAS_ALERTA_VENCIMIENTO)

        contratos_por_vencer = self.search([
            ('tipo_operacion', '=', TIPO_RENTA),
            ('estado', '=', ESTADO_ACTIVO),
            ('fecha_fin', '<=', fecha_limite),
            ('fecha_fin', '>=', today),
        ])

        for contrato in contratos_por_vencer:
            dias = (contrato.fecha_fin - today).days
            contrato.write({'estado': ESTADO_POR_VENCER})
            contrato.message_post(
                body=Markup(_(
                    "⚠️ <strong>Contrato próximo a vencer.</strong><br/>"
                    "Vence en <strong>%(dias)d días</strong> "
                    "(%(fecha)s).<br/>"
                    "Contacta al propietario e inquilino para definir "
                    "renovación o terminación.<br/>"
                    "Usa el botón <strong>Crear Renovación</strong> "
                    "si ambas partes acuerdan continuar."
                )) % {
                    'dias': dias,
                    'fecha': str(contrato.fecha_fin),
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
            _logger.info(
                "⚠️ Contrato '%s' → por_vencer. Días restantes: %d",
                contrato.name, dias
            )

        # Marcar como vencidos los que ya pasaron su fecha fin
        contratos_vencidos = self.search([
            ('tipo_operacion', '=', TIPO_RENTA),
            ('estado', 'in', [ESTADO_ACTIVO, ESTADO_POR_VENCER]),
            ('fecha_fin', '<', today),
        ])

        for contrato in contratos_vencidos:
            contrato.write({'estado': ESTADO_VENCIDO})
            contrato.message_post(
                body=Markup(_(
                    "🔴 <strong>Contrato Vencido.</strong><br/>"
                    "La vigencia del contrato expiró el %(fecha)s.<br/>"
                    "Gestiona la renovación o la terminación "
                    "del arrendamiento a la brevedad."
                )) % {'fecha': str(contrato.fecha_fin)},
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
            _logger.warning(
                "🔴 Contrato '%s' → vencido. Fecha fin: %s",
                contrato.name, contrato.fecha_fin
            )

        _logger.info(
            "✅ Revisión de vencimientos completada. "
            "Por vencer: %d. Vencidos: %d",
            len(contratos_por_vencer),
            len(contratos_vencidos)
        )

    # =========================================================================
    # MÉTODO helper para obtener el diario 
    # =========================================================================


    def _get_journal(self, journal_type='sale'):
        """
        Obtiene el diario contable configurado en el contrato.
        Si no hay uno seleccionado, usa el diario por defecto
        de la compañía para el tipo indicado.
        """
        self.ensure_one()
        if self.journal_id:
            return self.journal_id

        journal = self.env['account.journal'].search([
            ('type', '=', journal_type),
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        if not journal:
            raise UserError(_(
                "No se encontró un diario contable de tipo '%s' "
                "configurado en la compañía. "
                "Configura uno en Contabilidad → Diarios."
            ) % journal_type)

        return journal

    # =========================================================================
    # MÉTODO Over write para generar factura cuando se marque comision pagada
    # =========================================================================


    def write(self, vals):
        """
        Override para generar el registro contable de comisión
        cuando comision_pagada cambia a True.
        """
        res = super().write(vals)

        if vals.get('comision_pagada'):
            for contrato in self:
                if contrato.comision_monto > 0:
                    contrato._generar_move_comision()

        return res

    def _generar_move_comision(self):
        """
        Genera un vendor bill (in_invoice) registrando el egreso
        de la comisión del asesor hacia el propietario o la inmobiliaria.

        Tipo: in_invoice (egreso — dinero que sale hacia el asesor)
        Partner: El usuario asesor responsable del contrato
                 (su partner_id en res.users)
        """
        self.ensure_one()

        if not self.comision_monto or self.comision_monto <= 0:
            _logger.warning(
                "⚠️ Contrato '%s' sin monto de comisión — "
                "registro contable no generado",
                self.name
            )
            return

        asesor_partner = self.asesor_id.partner_id if self.asesor_id else None

        if not asesor_partner:
            _logger.warning(
                "⚠️ Contrato '%s' sin asesor asignado — "
                "registro de comisión no generado",
                self.name
            )
            return

        # Para egreso usamos diario de compras o general
        journal = self._get_journal(journal_type='purchase')

        cuenta_gastos = self.env['account.account'].search([
            ('account_type', 'in', [
                'expense', 'expense_other'
            ]),
            ('company_id', '=', self.env.company.id),
            ('deprecated', '=', False),
        ], limit=1)

        if not cuenta_gastos:
            _logger.error(
                "❌ No se encontró cuenta de gastos — "
                "comisión del contrato '%s' no registrada",
                self.name
            )
            return

        concepto = _(
            "Comisión del asesor — %(propiedad)s\n"
            "Contrato: %(contrato)s\n"
            "Asesor: %(asesor)s"
        ) % {
            'propiedad': self.propiedad_id.name,
            'contrato':  self.name,
            'asesor':    asesor_partner.name,
        }

        move_vals = {
            'move_type':        'in_invoice',
            'journal_id':       journal.id,
            'partner_id':       asesor_partner.id,
            'invoice_date':     self.fecha_cobro_comision
                                or fields.Date.today(),
            'ref':              f"{self.name} / Comisión Asesor",
            'narration':        concepto,
            'invoice_line_ids': [(0, 0, {
                'name':       concepto,
                'quantity':   1.0,
                'price_unit': self.comision_monto,
                'account_id': cuenta_gastos.id,
            })],
        }

        try:
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            _logger.info(
                "💼 Registro de comisión %s generado — "
                "contrato '%s' asesor '%s' monto %.2f",
                move.name,
                self.name,
                asesor_partner.name,
                self.comision_monto
            )

            self.message_post(
                body=Markup(_(
                    "💼 <strong>Comisión registrada contablemente.</strong><br/>"
                    "Documento: <strong>%(move)s</strong><br/>"
                    "Asesor: <strong>%(asesor)s</strong><br/>"
                    "Monto: <strong>%(monto)s %(moneda)s</strong>"
                )) % {
                    'move':   move.name,
                    'asesor': asesor_partner.name,
                    'monto':  f"{self.comision_monto:,.2f}",
                    'moneda': self.currency_id.symbol,
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        except Exception as e:
            _logger.error(
                "❌ Error generando registro de comisión "
                "para contrato '%s': %s",
                self.name, str(e)
            )


    # =========================================================================
    # OVERRIDE write — CHATTER AUTOMÁTICO
    # =========================================================================

    def write(self, vals):
        """
        Registra cambios críticos en el Chatter.
        Patrón idéntico a re_propiedad.py y re_prospecto.py.
        """
        resultado = super(ReContrato, self).write(vals)

        if 'comision_pagada' in vals and vals['comision_pagada']:
            for contrato in self:
                contrato.message_post(
                    body=Markup(_(
                        "💰 <strong>Comisión cobrada.</strong><br/>"
                        "Monto: <strong>%(monto)s %(moneda)s</strong><br/>"
                        "Pagada por el propietario: "
                        "<strong>%(propietario)s</strong>"
                    )) % {
                        'monto': f"{contrato.comision_monto:,.2f}",
                        'moneda': contrato.currency_id.symbol,
                        'propietario': contrato.propietario_id.name
                            if contrato.propietario_id else '—',
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        if 'deposito_recibido' in vals and vals['deposito_recibido']:
            for contrato in self:
                contrato.message_post(
                    body=Markup(_(
                        "🏦 <strong>Depósito en garantía recibido.</strong><br/>"
                        "Monto: <strong>%(monto)s %(moneda)s</strong>"
                    )) % {
                        'monto': f"{contrato.monto_deposito:,.2f}",
                        'moneda': contrato.currency_id.symbol,
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        if 'inquilino_riesgo' in vals and vals['inquilino_riesgo']:
            for contrato in self:
                contrato.message_post(
                    body=Markup(_(
                        "🚨 <strong>Alerta: Inquilino en Riesgo.</strong><br/>"
                        "El inquilino <strong>%(inquilino)s</strong> "
                        "acumula <strong>%(atrasados)d pagos atrasados</strong>.<br/>"
                        "Se recomienda contactar al inquilino y al propietario."
                    )) % {
                        'inquilino': contrato.inquilino_id.name
                            if contrato.inquilino_id else '—',
                        'atrasados': contrato.pagos_atrasados_count,
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )
                _logger.warning(
                    "🚨 Inquilino en riesgo — contrato '%s': "
                    "%d pagos atrasados",
                    contrato.name, contrato.pagos_atrasados_count
                )

        return resultado


# =============================================================================
# SUBMODELO: re.pago
# Seguimiento de pagos mensuales de renta
# Métrica de calidad de inquilino — base para pasarela v1.1
# =============================================================================

class RePago(models.Model):
    """
    Pago mensual de renta — Caletti Real Estate.

    Submodelo One2many de re.contrato.
    Se generan automáticamente al activar un contrato de renta,
    uno por cada mes de vigencia, en estado 'pendiente'.

    El asesor registra el pago manualmente cuando el inquilino paga.
    El campo pago_tardio se calcula al momento de marcar como pagado.

    Métricas generadas:
    - pago_puntualidad_pct en re.contrato
    - inquilino_riesgo cuando se superan UMBRAL_PAGOS_ATRASADOS atrasos

    v1.1: Integración con account.move para generar facturas automáticas
    y ofrecer pasarela de pago en el portal del propietario e inquilino.
    Arquitectura a revisar con Carlos Caletti antes de implementar.
    """
    _name = 're.pago'
    _description = 'Pago de Renta — Caletti Real Estate'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'fecha_vencimiento asc'

    name = fields.Char(
        string='Referencia del Pago',
        required=True,
        help="Generado automáticamente. Ej: 'Pago 1 — enero 2026'"
    )

    contrato_id = fields.Many2one(
        're.contrato',
        string='Contrato',
        required=True,
        ondelete='cascade',
        index=True
    )

    # Campos relacionados del contrato para facilitar búsquedas y reportes
    propiedad_id = fields.Many2one(
        're.propiedad',
        string='Propiedad',
        related='contrato_id.propiedad_id',
        store=True,
        readonly=True
    )

    inquilino_id = fields.Many2one(
        'res.partner',
        string='Inquilino',
        related='contrato_id.inquilino_id',
        store=True,
        readonly=True
    )

    numero_pago = fields.Integer(
        string='Número de Pago',
        help="Número secuencial dentro del contrato. Pago 1 = primer mes."
    )

    # =========================================================================
    # FECHAS Y MONTOS
    # =========================================================================

    fecha_vencimiento = fields.Date(
        string='Fecha de Vencimiento',
        required=True,
        tracking=True,
        help="Fecha límite para realizar el pago sin incurrir en atraso"
    )

    fecha_pago = fields.Date(
        string='Fecha de Pago Real',
        tracking=True,
        help="Fecha en que el inquilino realizó el pago efectivo"
    )

    monto_esperado = fields.Monetary(
        string='Monto Esperado',
        currency_field='currency_id',
        help="Monto de renta mensual según el contrato"
    )

    monto_pagado = fields.Monetary(
        string='Monto Pagado',
        currency_field='currency_id',
        tracking=True,
        help="Monto efectivamente recibido. Puede diferir del esperado "
             "en caso de pagos parciales."
    )

    diferencia = fields.Monetary(
        string='Diferencia',
        currency_field='currency_id',
        compute='_compute_diferencia',
        help="Monto esperado menos monto pagado. Positivo = saldo pendiente."
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='contrato_id.currency_id',
        readonly=True
    )

    # =========================================================================
    # ESTADO Y CALIDAD
    # =========================================================================

    estado = fields.Selection([
        (PAGO_PENDIENTE, '⏳ Pendiente'),
        (PAGO_PAGADO,    '✅ Pagado'),
        (PAGO_ATRASADO,  '🔴 Atrasado'),
        (PAGO_PARCIAL,   '⚠️ Pago Parcial'),
        (PAGO_CANCELADO, '❌ Cancelado'),
    ], string='Estado',
       default=PAGO_PENDIENTE,
       required=True,
       tracking=True,
       index=True
    )

    pago_tardio = fields.Boolean(
        string='Pago Tardío',
        readonly=True,
        tracking=True,
        help="True si el pago se realizó después de la fecha de vencimiento. "
             "Calculado automáticamente al registrar el pago."
    )

    dias_atraso = fields.Integer(
        string='Días de Atraso',
        compute='_compute_dias_atraso',
        help="Días transcurridos desde la fecha de vencimiento sin pago"
    )

    metodo_pago = fields.Selection([
        (METODO_TRANSFERENCIA, '🏦 Transferencia Bancaria'),
        (METODO_EFECTIVO,      '💵 Efectivo'),
        (METODO_CHEQUE,        '📝 Cheque'),
        (METODO_DEPOSITO,      '🏧 Depósito Bancario'),
        (METODO_OTRO,          '📋 Otro'),
    ], string='Método de Pago',
       tracking=True
    )

    referencia_pago = fields.Char(
        string='Referencia / Folio',
        tracking=True,
        help="Número de referencia de la transferencia, folio del cheque, etc."
    )

    notas = fields.Text(
        string='Notas',
        help="Observaciones sobre el pago: acuerdos especiales, "
             "descuentos aplicados, penalizaciones, etc."
    )

    # =========================================================================
    # COMPUTED
    # =========================================================================

    @api.depends('monto_esperado', 'monto_pagado')
    def _compute_diferencia(self):
        for pago in self:
            pago.diferencia = pago.monto_esperado - pago.monto_pagado

    @api.depends('fecha_vencimiento', 'fecha_pago', 'estado')
    def _compute_dias_atraso(self):
        today = fields.Date.today()
        for pago in self:
            if pago.estado in [PAGO_PENDIENTE, PAGO_ATRASADO]:
                if pago.fecha_vencimiento and pago.fecha_vencimiento < today:
                    pago.dias_atraso = (today - pago.fecha_vencimiento).days
                else:
                    pago.dias_atraso = 0
            elif pago.pago_tardio and pago.fecha_pago:
                pago.dias_atraso = (
                    pago.fecha_pago - pago.fecha_vencimiento
                ).days
            else:
                pago.dias_atraso = 0

    # =========================================================================
    # ACCIÓN: REGISTRAR PAGO
    # =========================================================================

    def action_registrar_pago(self):
        """
        Registra el pago del mes. Calcula si es tardío automáticamente.
        Actualiza el estado según si el monto es completo o parcial.
        """
        self.ensure_one()
        if self.estado in [PAGO_PAGADO, PAGO_CANCELADO]:
            raise UserError(_(
                "Este pago ya fue registrado o está cancelado."
            ))
        if not self.monto_pagado or self.monto_pagado <= 0:
            raise UserError(_(
                "Ingresa el monto pagado antes de registrar."
            ))

        today = fields.Date.today()
        es_tardio = (
            self.fecha_pago or today
        ) > self.fecha_vencimiento

        # Determinar estado según monto
        if self.monto_pagado >= self.monto_esperado:
            nuevo_estado = PAGO_PAGADO
        else:
            nuevo_estado = PAGO_PARCIAL

        self.write({
            'estado':      nuevo_estado,
            'fecha_pago':  self.fecha_pago or today,
            'pago_tardio': es_tardio,
        })

        # Notificación en Chatter del contrato
        self.contrato_id.message_post(
            body=Markup(_(
                "%(icono)s <strong>Pago %(num)d registrado.</strong><br/>"
                "Monto: <strong>%(monto)s %(moneda)s</strong> "
                "de <strong>%(esperado)s %(moneda)s</strong> esperados.<br/>"
                "Fecha: <strong>%(fecha)s</strong>"
                "%(atraso)s"
            )) % {
                'icono': '✅' if nuevo_estado == PAGO_PAGADO else '⚠️',
                'num': self.numero_pago,
                'monto': f"{self.monto_pagado:,.2f}",
                'esperado': f"{self.monto_esperado:,.2f}",
                'moneda': self.currency_id.symbol,
                'fecha': str(self.fecha_pago or today),
                'atraso': (
                    _("<br/>⚠️ Pago tardío — %(dias)d días de atraso.") % {
                        'dias': self.dias_atraso
                    }
                ) if es_tardio else '',
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(
            "💰 Pago %d del contrato '%s' registrado. "
            "Estado: %s. Tardío: %s",
            self.numero_pago, self.contrato_id.name,
            nuevo_estado, es_tardio
        )
        
        # Integración contable v1.1 — generar factura al inquilino
        if nuevo_estado == PAGO_PAGADO:
            self._generar_factura_renta()


    def action_marcar_atrasado(self):
        """
        Marca el pago como atrasado.
        Llamado manualmente por el asesor o via cron de seguimiento.
        """
        self.ensure_one()
        if self.estado != PAGO_PENDIENTE:
            raise UserError(_(
                "Solo se puede marcar como atrasado un pago pendiente."
            ))
        self.write({'estado': PAGO_ATRASADO})
        _logger.warning(
            "🔴 Pago %d del contrato '%s' marcado como atrasado",
            self.numero_pago, self.contrato_id.name
        )

    # =========================================================================
    # INTEGRACIÓN CONTABLE — v1.1
    # =========================================================================

    def _generar_factura_renta(self):
        """
        Genera una factura de cliente (out_invoice) al registrar un pago
        de renta confirmado. Se llama desde action_registrar_pago.

        Emisor:  La compañía activa en Odoo (configurable via journal_id).
        Cliente: El inquilino del contrato.
        Concepto: Renta mensual — mes N del contrato.
        """
        self.ensure_one()

        contrato  = self.contrato_id
        inquilino = contrato.inquilino_id

        if not inquilino:
            _logger.warning(
                "⚠️ Pago %d sin inquilino — factura no generada",
                self.numero_pago
            )
            return

        journal = contrato._get_journal(journal_type='sale')

        # Cuenta de ingresos por arrendamiento
        # Odoo busca la cuenta de ingresos del producto o la por defecto
        cuenta_ingresos = self.env['account.account'].search([
            ('account_type', 'in', [
                'income', 'income_other'
            ]),
            ('company_id', '=', self.env.company.id),
            ('deprecated', '=', False),
        ], limit=1)

        if not cuenta_ingresos:
            _logger.error(
                "❌ No se encontró cuenta de ingresos — "
                "factura de renta no generada para pago %d",
                self.numero_pago
            )
            return

        concepto = _(
            "Renta mensual — %(propiedad)s\n"
            "Contrato: %(contrato)s | Pago %(num)d de %(total)d\n"
            "Período: %(fecha_ini)s → %(fecha_fin)s"
        ) % {
            'propiedad': contrato.propiedad_id.name,
            'contrato':  contrato.name,
            'num':       self.numero_pago,
            'total':     contrato.plazo_meses or 0,
            'fecha_ini': str(contrato.fecha_inicio or ''),
            'fecha_fin': str(contrato.fecha_fin or ''),
        }

        move_vals = {
            'move_type':       'out_invoice',
            'journal_id':      journal.id,
            'partner_id':      inquilino.id,
            'invoice_date':    self.fecha_pago or fields.Date.today(),
            'ref':             f"{contrato.name} / Pago #{self.numero_pago}",
            'narration':       concepto,
            'invoice_line_ids': [(0, 0, {
                'name':         concepto,
                'quantity':     1.0,
                'price_unit':   self.monto_pagado,
                'account_id':   cuenta_ingresos.id,
            })],
        }

        try:
            factura = self.env['account.move'].create(move_vals)
            # Confirmar la factura automáticamente
            factura.action_post()

            _logger.info(
                "🧾 Factura %s generada — pago %d contrato '%s' inquilino '%s'",
                factura.name,
                self.numero_pago,
                contrato.name,
                inquilino.name
            )

            # Nota en Chatter del contrato con link a la factura
            contrato.message_post(
                body=Markup(_(
                    "🧾 <strong>Factura generada automáticamente.</strong><br/>"
                    "Factura: <strong>%(factura)s</strong><br/>"
                    "Inquilino: <strong>%(inquilino)s</strong><br/>"
                    "Monto: <strong>%(monto)s %(moneda)s</strong>"
                )) % {
                    'factura':  factura.name,
                    'inquilino': inquilino.name,
                    'monto':    f"{self.monto_pagado:,.2f}",
                    'moneda':   self.currency_id.symbol,
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        except Exception as e:
            _logger.error(
                "❌ Error generando factura para pago %d: %s",
                self.numero_pago, str(e)
            )

    # =========================================================================
    # CRON: MARCADO AUTOMÁTICO DE PAGOS ATRASADOS
    # Se ejecuta diariamente — complementa el cron de vencimientos de contratos
    # =========================================================================

    @api.model
    def _cron_marcar_pagos_atrasados(self):
        """
        Proceso automático diario que identifica pagos pendientes
        cuya fecha de vencimiento ya fue superada y los marca como atrasados.

        Solo actúa sobre pagos en estado 'pendiente' con contrato activo
        o por_vencer — no toca contratos terminados, cancelados o renovados.
        """
        _logger.info("🔄 Iniciando marcado automático de pagos atrasados...")

        today = fields.Date.today()

        # Buscar pagos pendientes vencidos con contrato activo
        pagos_vencidos = self.search([
            ('estado', '=', PAGO_PENDIENTE),
            ('fecha_vencimiento', '<', today),
            ('contrato_id.estado', 'in', [
                'activo', 'por_vencer', 'vencido'
            ]),
        ])

        if not pagos_vencidos:
            _logger.info("✅ Sin pagos atrasados nuevos detectados.")
            return

        _logger.info(
            "📋 %d pagos pendientes vencidos detectados — marcando como atrasados",
            len(pagos_vencidos)
        )

        for pago in pagos_vencidos:
            pago.write({'estado': PAGO_ATRASADO})

            # Notificar en el Chatter del contrato
            pago.contrato_id.message_post(
                body=Markup(_(
                    "🔴 <strong>Pago atrasado detectado automáticamente.</strong><br/>"
                    "Pago <strong>%(num)d</strong> — Vencimiento: "
                    "<strong>%(fecha)s</strong><br/>"
                    "Monto pendiente: "
                    "<strong>%(monto)s %(moneda)s</strong><br/>"
                    "Inquilino: <strong>%(inquilino)s</strong>"
                )) % {
                    'num':      pago.numero_pago,
                    'fecha':    str(pago.fecha_vencimiento),
                    'monto':    f"{pago.monto_esperado:,.2f}",
                    'moneda':   pago.currency_id.symbol
                                if pago.currency_id else 'MXN',
                    'inquilino': pago.inquilino_id.name
                                 if pago.inquilino_id else _("Sin inquilino"),
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

            _logger.warning(
                "🔴 Pago %d del contrato '%s' marcado como atrasado. "
                "Vencimiento: %s. Inquilino: %s",
                pago.numero_pago,
                pago.contrato_id.name,
                pago.fecha_vencimiento,
                pago.inquilino_id.name if pago.inquilino_id else '—'
            )

        # Forzar recomputación de métricas en los contratos afectados
        # para que inquilino_riesgo y pago_puntualidad_pct se actualicen
        contratos_afectados = pagos_vencidos.mapped('contrato_id')
        contratos_afectados._compute_metricas_pago()

        _logger.info(
            "✅ Marcado completado. %d pagos atrasados. %d contratos afectados.",
            len(pagos_vencidos),
            len(contratos_afectados)
        )
        
