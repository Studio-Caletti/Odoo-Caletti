# caletti_real_estate/controllers/re_portal.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

from markupsafe import Markup
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict
import logging

_logger = logging.getLogger(__name__)


class CalettiREPortal(CustomerPortal):
    """
    Portal del cliente para el vertical inmobiliario Caletti Real Estate.

    Detecta automáticamente el rol del usuario autenticado:
    - Propietario: partner_id coincide con re.propiedad.propietario_id
    - Inquilino:   partner_id coincide con re.contrato.inquilino_id activo

    Un usuario puede ser propietario e inquilino simultáneamente.
    El portal muestra ambas secciones cuando aplica.

    Seguridad: Record Rules filtran automáticamente por partner_id.
    Sin sudo() en consultas de datos — el usuario solo ve lo suyo.
    sudo() solo en acciones de escritura autorizadas (aprobar mantenimiento,
    crear ticket) para superar restricciones de portal sobre write/create.
    """

    # =========================================================================
    # HELPERS PRIVADOS — detección de rol
    # =========================================================================

    def _es_propietario(self):
        """Verifica si el usuario actual tiene propiedades en cartera."""
        return request.env['re.propiedad'].search_count([
            ('propietario_id', '=', request.env.user.partner_id.id)
        ]) > 0

    def _es_inquilino(self):
        """Verifica si el usuario actual tiene contratos de renta activos."""
        return request.env['re.contrato'].search_count([
            ('inquilino_id', '=', request.env.user.partner_id.id),
            ('estado', 'in', ['activo', 'por_vencer', 'vencido']),
            ('tipo_operacion', '=', 'renta'),
        ]) > 0

    # =========================================================================
    # PORTAL HOME — contador en el hub principal de Odoo
    # =========================================================================

    def _prepare_home_portal_values(self, counters):
        """
        Agrega contadores al portal home de Odoo según el rol detectado.
        Propietario: número de propiedades en cartera.
        Inquilino: número de pagos pendientes o atrasados.
        """
        values = super()._prepare_home_portal_values(counters)

        partner_id = request.env.user.partner_id.id

        if 're_propiedad_count' in counters:
            values['re_propiedad_count'] = request.env['re.propiedad'].search_count([
                ('propietario_id', '=', partner_id)
            ])

        if 're_pago_pendiente_count' in counters:
            # Inquilino: pagos pendientes o atrasados de sus contratos
            values['re_pago_pendiente_count'] = request.env['re.pago'].search_count([
                ('inquilino_id', '=', partner_id),
                ('estado', 'in', ['pendiente', 'atrasado', 'parcial']),
            ])

        if 're_ticket_count' in counters:
            # Inquilino: tickets de mantenimiento abiertos
            values['re_ticket_count'] = request.env['re.mantenimiento'].search_count([
                ('inquilino_id', '=', partner_id),
                ('estado', 'not in', ['cerrado', 'cancelado']),
            ])

        return values

    # =========================================================================
    # HUB CENTRAL — /my/re-home
    # Detecta rol y redirige o muestra resumen según contexto
    # =========================================================================

    @http.route(
        ['/my/re-home'],
        type='http',
        auth='user',
        website=True
    )
    def portal_re_home(self, **kw):
        """
        Hub central del portal inmobiliario.
        Detecta si el usuario es propietario, inquilino o ambos
        y prepara el contexto para la vista de bienvenida.
        """
        partner_id = request.env.user.partner_id.id
        values = self._prepare_portal_layout_values()

        es_propietario = self._es_propietario()
        es_inquilino   = self._es_inquilino()

        # Si solo tiene un rol, redirigir directamente
        if es_propietario and not es_inquilino:
            return request.redirect('/my/mis-propiedades')
        if es_inquilino and not es_propietario:
            return request.redirect('/my/mis-pagos')

        # Si tiene ambos roles o ninguno — mostrar hub
        values.update({
            'es_propietario': es_propietario,
            'es_inquilino':   es_inquilino,
            'page_name':      're_home',
        })

        return request.render(
            'caletti_real_estate.portal_re_home',
            values
        )

    # =========================================================================
    # SECCIÓN PROPIETARIO
    # =========================================================================

    @http.route(
        ['/my/mis-propiedades',
         '/my/mis-propiedades/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_mis_propiedades(self, page=1, sortby=None, filterby=None, **kw):
        """
        Lista de propiedades del propietario autenticado.
        Record Rules garantizan que solo ve las suyas.
        """
        values = self._prepare_portal_layout_values()
        Propiedad = request.env['re.propiedad']  # Sin sudo()

        searchbar_filters = {
            'all':         {'label': _('Todas'),
                            'domain': []},
            'disponible':  {'label': _('Disponibles'),
                            'domain': [('estado', '=', 'disponible')]},
            'ocupada':     {'label': _('Ocupadas'),
                            'domain': [('estado', '=', 'ocupada')]},
            'en_mant':     {'label': _('En Mantenimiento'),
                            'domain': [('estado', '=', 'en_mantenimiento')]},
        }

        searchbar_sortings = {
            'name':   {'label': _('Nombre'),   'order': 'name asc'},
            'estado': {'label': _('Estado'),   'order': 'estado asc'},
        }

        if not filterby:
            filterby = 'all'
        if not sortby:
            sortby = 'name'

        domain     = searchbar_filters[filterby]['domain']
        sort_order = searchbar_sortings[sortby]['order']

        propiedad_count = Propiedad.search_count(domain)
        pager = portal_pager(
            url='/my/mis-propiedades',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=propiedad_count,
            page=page,
            step=9
        )

        propiedades = Propiedad.search(
            domain,
            limit=9,
            offset=pager['offset'],
            order=sort_order
        )

        _logger.debug(
            "Portal RE: propietario %s viendo %d propiedades",
            request.env.user.name, len(propiedades)
        )

        values.update({
            'propiedades':        propiedades,
            'page_name':          're_propiedades',
            'pager':              pager,
            'searchbar_filters':  OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'sortby':             sortby,
            'filterby':           filterby,
        })

        return request.render(
            'caletti_real_estate.portal_mis_propiedades',
            values
        )

    @http.route(
        ['/my/propiedad/<int:propiedad_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_detalle_propiedad(self, propiedad_id, **kw):
        """
        Detalle de una propiedad del propietario.
        Muestra: datos generales, contratos activos, pagos realizados
        y mantenimientos — en ese orden de prioridad de negocio.
        Record Rules validan acceso automáticamente.
        """
        propiedad = request.env['re.propiedad'].search([
            ('id', '=', propiedad_id)
        ], limit=1)

        if not propiedad:
            _logger.warning(
                "Portal RE: %s intentó acceder a propiedad %d sin permiso",
                request.env.user.name, propiedad_id
            )
            return request.redirect('/my/mis-propiedades')

        # Contratos activos de esta propiedad
        contratos = request.env['re.contrato'].sudo().search([
            ('propiedad_id', '=', propiedad_id),
            ('estado', 'not in', ['cancelado']),
        ], order='fecha_inicio desc')

        # Pagos de todos los contratos de esta propiedad — ordenados por fecha
        # El propietario quiere ver primero los más recientes
        pagos = request.env['re.pago'].sudo().search([
            ('propiedad_id', '=', propiedad_id),
        ], order='fecha_vencimiento desc', limit=24)  # Últimos 24 meses

        # Mantenimientos activos de esta propiedad
        mantenimientos = request.env['re.mantenimiento'].sudo().search([
            ('propiedad_id', '=', propiedad_id),
            ('estado', 'not in', ['cerrado', 'cancelado']),
        ], order='prioridad asc, fecha_solicitud desc')

        # Mantenimientos pendientes de aprobación — los más urgentes para el propietario
        mant_por_aprobar = mantenimientos.filtered(
            lambda m: m.requiere_aprobacion and not m.aprobado_por_propietario
        )

        mensaje = kw.get('mensaje')

        values = {
            'propiedad':         propiedad,
            'contratos':         contratos,
            'pagos':             pagos,
            'mantenimientos':    mantenimientos,
            'mant_por_aprobar':  mant_por_aprobar,
            'page_name':         're_propiedades',
            'mensaje':           mensaje,
        }

        return request.render(
            'caletti_real_estate.portal_detalle_propiedad',
            values
        )

    @http.route(
        ['/my/propiedad/<int:propiedad_id>/aprobar-mantenimiento/<int:mant_id>'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True
    )
    def portal_aprobar_mantenimiento(self, propiedad_id, mant_id, **post):
        """
        Aprobación de mantenimiento por el propietario desde el portal.
        Valida que el mantenimiento pertenece a la propiedad del propietario.
        Registra la aprobación con nota en el Chatter — trazabilidad completa.
        """
        # Verificar acceso a la propiedad
        propiedad = request.env['re.propiedad'].search([
            ('id', '=', propiedad_id)
        ], limit=1)

        if not propiedad:
            return request.redirect('/my/mis-propiedades')

        # Verificar que el mantenimiento pertenece a esta propiedad
        mantenimiento = request.env['re.mantenimiento'].sudo().search([
            ('id', '=', mant_id),
            ('propiedad_id', '=', propiedad_id),
        ], limit=1)

        if not mantenimiento:
            _logger.warning(
                "Portal RE: %s intentó aprobar mantenimiento %d sin permiso",
                request.env.user.name, mant_id
            )
            return request.redirect(f'/my/propiedad/{propiedad_id}')

        if mantenimiento.aprobado_por_propietario:
            return request.redirect(
                f'/my/propiedad/{propiedad_id}?mensaje=ya_aprobado'
            )

        try:
            mantenimiento.sudo().write({
                'aprobado_por_propietario': True,
                'fecha_aprobacion':         request.env['ir.fields'].date.today()
                                            if hasattr(request.env, 'ir')
                                            else __import__('odoo').fields.Date.today(),
            })

            # Nota en Chatter con trazabilidad del propietario
            mantenimiento.sudo().message_post(
                body=Markup(_(
                    "✅ <strong>Mantenimiento aprobado por el Propietario desde el Portal.</strong><br/>"
                    "Propietario: <strong>%(propietario)s</strong><br/>"
                    "Costo autorizado: "
                    "<strong>%(costo)s %(moneda)s</strong><br/>"
                    "El asesor puede proceder con la ejecución del trabajo."
                )) % {
                    'propietario': request.env.user.partner_id.name,
                    'costo':       f"{mantenimiento.costo_estimado:,.2f}",
                    'moneda':      mantenimiento.currency_id.symbol
                                   if mantenimiento.currency_id else 'MXN',
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

            _logger.info(
                "✅ Mantenimiento %d aprobado desde portal por propietario %s",
                mant_id, request.env.user.name
            )

        except Exception as e:
            _logger.error(
                "❌ Error aprobando mantenimiento %d desde portal: %s",
                mant_id, str(e)
            )
            return request.redirect(
                f'/my/propiedad/{propiedad_id}?mensaje=error'
            )

        return request.redirect(
            f'/my/propiedad/{propiedad_id}?mensaje=aprobado'
        )

    # =========================================================================
    # SECCIÓN INQUILINO — PAGOS
    # =========================================================================

    @http.route(
        ['/my/mis-pagos',
         '/my/mis-pagos/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_mis_pagos(self, page=1, filterby=None, **kw):
        """
        Lista de pagos del inquilino autenticado.
        Muestra primero pendientes y atrasados, luego historial.
        Record Rules garantizan aislamiento por partner_id.
        """
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id

        searchbar_filters = {
            'pendientes': {'label': _('Pendientes'),
                           'domain': [('estado', 'in', ['pendiente', 'atrasado', 'parcial'])]},
            'pagados':    {'label': _('Pagados'),
                           'domain': [('estado', '=', 'pagado')]},
            'todos':      {'label': _('Todos'),
                           'domain': []},
        }

        if not filterby:
            filterby = 'pendientes'

        domain = searchbar_filters[filterby]['domain']
        # Agregar filtro por inquilino — complementa la Record Rule
        domain += [('inquilino_id', '=', partner_id)]

        pago_count = request.env['re.pago'].sudo().search_count(domain)
        pager = portal_pager(
            url='/my/mis-pagos',
            url_args={'filterby': filterby},
            total=pago_count,
            page=page,
            step=12
        )

        pagos = request.env['re.pago'].sudo().search(
            domain,
            limit=12,
            offset=pager['offset'],
            order='fecha_vencimiento desc'
        )

        # Contrato activo del inquilino para mostrar resumen
        contrato_activo = request.env['re.contrato'].sudo().search([
            ('inquilino_id', '=', partner_id),
            ('tipo_operacion', '=', 'renta'),
            ('estado', 'in', ['activo', 'por_vencer']),
        ], limit=1)

        values.update({
            'pagos':             pagos,
            'contrato_activo':   contrato_activo,
            'page_name':         're_pagos',
            'pager':             pager,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby':          filterby,
            'pago_count':        pago_count,
        })

        return request.render(
            'caletti_real_estate.portal_mis_pagos',
            values
        )

    @http.route(
        ['/my/mis-pagos/<int:contrato_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_pagos_contrato(self, contrato_id, **kw):
        """
        Detalle de pagos de un contrato específico del inquilino.
        Muestra historial completo con métricas de puntualidad.
        """
        partner_id = request.env.user.partner_id.id

        contrato = request.env['re.contrato'].sudo().search([
            ('id', '=', contrato_id),
            ('inquilino_id', '=', partner_id),
            ('tipo_operacion', '=', 'renta'),
        ], limit=1)

        if not contrato:
            _logger.warning(
                "Portal RE: %s intentó acceder a contrato %d sin permiso",
                request.env.user.name, contrato_id
            )
            return request.redirect('/my/mis-pagos')

        pagos = request.env['re.pago'].sudo().search([
            ('contrato_id', '=', contrato_id),
        ], order='fecha_vencimiento asc')

        values = {
            'contrato':  contrato,
            'pagos':     pagos,
            'page_name': 're_pagos',
        }

        return request.render(
            'caletti_real_estate.portal_pagos_contrato',
            values
        )

    # =========================================================================
    # SECCIÓN INQUILINO — TICKETS DE MANTENIMIENTO
    # =========================================================================

    @http.route(
        ['/my/mis-tickets',
         '/my/mis-tickets/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_mis_tickets(self, page=1, filterby=None, **kw):
        """
        Lista de tickets de mantenimiento del inquilino.
        Record Rules filtran automáticamente por propiedad del inquilino.
        """
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id

        searchbar_filters = {
            'activos':  {'label': _('Activos'),
                         'domain': [('estado', 'not in', ['cerrado', 'cancelado'])]},
            'cerrados': {'label': _('Cerrados'),
                         'domain': [('estado', 'in', ['cerrado', 'cancelado'])]},
            'todos':    {'label': _('Todos'),
                         'domain': []},
        }

        if not filterby:
            filterby = 'activos'

        domain = searchbar_filters[filterby]['domain']
        domain += [('inquilino_id', '=', partner_id)]

        ticket_count = request.env['re.mantenimiento'].sudo().search_count(domain)
        pager = portal_pager(
            url='/my/mis-tickets',
            url_args={'filterby': filterby},
            total=ticket_count,
            page=page,
            step=10
        )

        tickets = request.env['re.mantenimiento'].sudo().search(
            domain,
            limit=10,
            offset=pager['offset'],
            order='prioridad asc, fecha_solicitud desc'
        )

        # Propiedad del inquilino para el formulario de nuevo ticket
        contrato_activo = request.env['re.contrato'].sudo().search([
            ('inquilino_id', '=', partner_id),
            ('tipo_operacion', '=', 'renta'),
            ('estado', 'in', ['activo', 'por_vencer']),
        ], limit=1)

        values.update({
            'tickets':           tickets,
            'contrato_activo':   contrato_activo,
            'page_name':         're_tickets',
            'pager':             pager,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby':          filterby,
        })

        return request.render(
            'caletti_real_estate.portal_mis_tickets',
            values
        )

    @http.route(
        ['/my/ticket/nuevo'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True
    )
    def portal_crear_ticket(self, **post):
        """
        Crea un nuevo ticket de mantenimiento desde el portal del inquilino.
        Valida que el inquilino tiene un contrato activo con la propiedad.
        Registra el origen como 'inquilino' para trazabilidad del asesor.
        """
        partner_id = request.env.user.partner_id.id

        # Validar que tiene contrato activo
        contrato = request.env['re.contrato'].sudo().search([
            ('inquilino_id', '=', partner_id),
            ('tipo_operacion', '=', 'renta'),
            ('estado', 'in', ['activo', 'por_vencer']),
        ], limit=1)

        if not contrato:
            _logger.warning(
                "Portal RE: %s intentó crear ticket sin contrato activo",
                request.env.user.name
            )
            return request.redirect('/my/mis-tickets')

        nombre      = post.get('nombre', '').strip()
        categoria   = post.get('categoria', 'otro')
        descripcion = post.get('descripcion', '').strip()
        prioridad   = post.get('prioridad', 'normal')

        if not nombre:
            return request.redirect('/my/mis-tickets?mensaje=sin_nombre')

        try:
            ticket = request.env['re.mantenimiento'].sudo().create({
                'name':              nombre,
                'propiedad_id':      contrato.propiedad_id.id,
                'contrato_id':       contrato.id,
                'categoria':         categoria,
                'descripcion_problema': descripcion,
                'prioridad':         prioridad,
                'origen_solicitud':  'inquilino',
                'tipo_ejecutor':     'proveedor_externo',
            })

            # Nota en Chatter con contexto del inquilino
            ticket.sudo().message_post(
                body=Markup(_(
                    "🧑 <strong>Ticket creado por el Inquilino desde el Portal.</strong><br/>"
                    "Inquilino: <strong>%(inquilino)s</strong><br/>"
                    "Propiedad: <strong>%(propiedad)s</strong>"
                )) % {
                    'inquilino': request.env.user.partner_id.name,
                    'propiedad': contrato.propiedad_id.name,
                },
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

            _logger.info(
                "🧑 Ticket '%s' creado desde portal por inquilino %s — propiedad '%s'",
                nombre,
                request.env.user.name,
                contrato.propiedad_id.name
            )

        except Exception as e:
            _logger.error(
                "❌ Error creando ticket desde portal: %s", str(e)
            )
            return request.redirect('/my/mis-tickets?mensaje=error')

        return request.redirect(
            f'/my/ticket/{ticket.id}?mensaje=creado'
        )

    @http.route(
        ['/my/ticket/<int:ticket_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_detalle_ticket(self, ticket_id, **kw):
        """
        Detalle de un ticket de mantenimiento del inquilino.
        Muestra estado, descripción, progreso y canal de comunicación (Chatter).
        """
        partner_id = request.env.user.partner_id.id

        ticket = request.env['re.mantenimiento'].sudo().search([
            ('id', '=', ticket_id),
            ('inquilino_id', '=', partner_id),
        ], limit=1)

        if not ticket:
            _logger.warning(
                "Portal RE: %s intentó acceder a ticket %d sin permiso",
                request.env.user.name, ticket_id
            )
            return request.redirect('/my/mis-tickets')

        mensaje = kw.get('mensaje')

        values = {
            'ticket':    ticket,
            'page_name': 're_tickets',
            'mensaje':   mensaje,
        }

        return request.render(
            'caletti_real_estate.portal_detalle_ticket',
            values
        )