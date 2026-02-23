# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#   
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict
import logging

_logger = logging.getLogger(__name__)

class CalettiHelpdeskPortal(CustomerPortal):
    """
    Controlador para el portal de Helpdesk
    """

    def _prepare_home_portal_values(self, counters):
        """Agrega contador de tickets al portal home"""
        values = super()._prepare_home_portal_values(counters)
        
        if 'ticket_count' in counters:
            # Sin sudo() - las Record Rules manejan la seguridad
            Tarea = request.env['tablero.tarea']
            values['ticket_count'] = Tarea.search_count([('es_ticket', '=', True)])
        
        return values

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, sortby=None, filterby=None, search=None, **kw):
        """
        Lista de tickets del cliente en el portal
        """
        values = self._prepare_portal_layout_values()
        Tarea = request.env['tablero.tarea']

        # Filtros disponibles
        searchbar_filters = {
            'all': {'label': _('Todos'), 'domain': [('es_ticket', '=', True)]},
            'abiertos': {'label': _('Abiertos'), 'domain': [('es_ticket', '=', True), ('state', '!=', 'hecho')]},
            'resueltos': {'label': _('Resueltos'), 'domain': [('es_ticket', '=', True), ('state', '=', 'hecho')]},
            'criticos': {'label': _('Críticos'), 'domain': [('es_ticket', '=', True), ('prioridad_ticket', '=', '3')]},
        }

        # Ordenamientos disponibles
        searchbar_sortings = {
            'date': {'label': _('Fecha de Creación'), 'order': 'create_date desc'},
            'prioridad': {'label': _('Prioridad'), 'order': 'prioridad_ticket desc'},
            'estado': {'label': _('Estado'), 'order': 'state asc'},
        }

        # Valores por defecto
        if not filterby:
            filterby = 'all'
        if not sortby:
            sortby = 'date'

        domain = searchbar_filters[filterby]['domain']
        sort_order = searchbar_sortings[sortby]['order']

        # Búsqueda
        if search:
            domain += ['|', ('name', 'ilike', search), ('ticket_ref', 'ilike', search)]

        # Conteo y paginación
        ticket_count = Tarea.search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'sortby': sortby, 'filterby': filterby, 'search': search},
            total=ticket_count,
            page=page,
            step=10
        )

        # Búsqueda de tickets (Record Rules aplican automáticamente)
        tickets = Tarea.search(domain, limit=10, offset=pager['offset'], order=sort_order)

        _logger.debug("Portal Tickets: Usuario %s viendo %d tickets", request.env.user.name, len(tickets))

        values.update({
            'tickets': tickets,
            'page_name': 'tickets',
            'pager': pager,
            'default_url': '/my/tickets',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'filterby': filterby,
            'search': search,
        })

        return request.render("tablero_kanban_helpdesk.portal_my_tickets_template", values)

    @http.route(['/my/ticket/nuevo'], type='http', auth="user", website=True)
    def portal_create_ticket(self, **kw):
        """
        Formulario para crear un nuevo ticket
        """
        values = {
            'page_name': 'tickets',
        }
        return request.render("tablero_kanban_helpdesk.portal_create_ticket_template", values)

    @http.route(['/my/ticket/submit'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_submit_ticket(self, **post):
        """
        Procesa el formulario de creación de ticket
        """
        # Extraer datos del formulario
        asunto = post.get('asunto', '').strip()
        tipo = post.get('tipo', 'consulta')
        prioridad = post.get('prioridad', '1')
        descripcion = post.get('descripcion', '').strip()

        if not asunto or not descripcion:
            # Manejar error de validación
            return request.redirect('/my/ticket/nuevo?error=missing_fields')

        # Crear el ticket
        try:
            ticket = request.env['tablero.tarea'].create({
                'name': asunto,
                'description': descripcion,
                'es_ticket': True,
                'tipo_ticket': tipo,
                'prioridad_ticket': prioridad,
                'state': 'nuevo',
                'partner_id': request.env.user.partner_id.id,
                'ticket_email': request.env.user.email,
            })

            _logger.info("✅ Ticket creado desde portal: %s por %s", ticket.ticket_ref, request.env.user.name)

            # Redirigir al detalle del ticket creado
            return request.redirect(f'/my/ticket/{ticket.id}?message=created')

        except Exception as e:
            _logger.error("❌ Error creando ticket desde portal: %s", str(e))
            return request.redirect('/my/ticket/nuevo?error=creation_failed')

    @http.route(['/my/ticket/<int:ticket_id>'], type='http', auth="user", website=True)
    def portal_ticket_detail(self, ticket_id, access_token=None, message=None, **kw):
        """
        Detalle de un ticket específico
        """
        try:
            # Sin sudo() - Record Rules validan el acceso
            ticket = request.env['tablero.tarea'].search([
                ('id', '=', ticket_id),
                ('es_ticket', '=', True)
            ], limit=1)
        except Exception as e:
            _logger.warning("Error accediendo a ticket %d: %s", ticket_id, str(e))
            ticket = request.env['tablero.tarea'].browse()

        if not ticket:
            _logger.warning("Usuario %s sin acceso a ticket %d", request.env.user.name, ticket_id)
            return request.redirect('/my/tickets')

        values = {
            'ticket': ticket,
            'page_name': 'tickets',
            'message': message,  # Para mostrar mensaje de confirmación si viene de crear
        }

        _logger.debug("Portal: Usuario %s viendo ticket %s", request.env.user.name, ticket.ticket_ref)

        return request.render("tablero_kanban_helpdesk.portal_ticket_detail_template", values)
