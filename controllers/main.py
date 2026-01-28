from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict

class CalettiPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """ Actualiza el contador de 'Mis Tareas' en la página principal del portal """
        values = super(CalettiPortal, self)._prepare_home_portal_values(counters)
        if 'tarea_count' in counters:
            # Contamos solo las tareas del partner actual (o sus contactos comerciales)
            values['tarea_count'] = request.env['tablero.tarea'].sudo().search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
        return values

    @http.route(['/my/tareas', '/my/tareas/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tareas(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        Tarea = request.env['tablero.tarea']

        searchbar_filters = {
            'all': {'label': _('Todas'), 'domain': []},
            'nuevo': {'label': _('Nuevas'), 'domain': [('state', '=', 'nuevo')]},
            'proceso': {'label': _('En Proceso'), 'domain': [('state', '=', 'proceso')]},
            'hecho': {'label': _('Finalizadas'), 'domain': [('state', '=', 'hecho')]},
            'vencidas': {'label': _('Vencidas'), 'domain': [('is_overdue', '=', True)]},
        }
        
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Tareas')},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # Filtro de seguridad obligatorio
        domain += [('partner_id', '=', request.env.user.partner_id.id)]

        if search and search_in:
            domain += [('name', 'ilike', search)]

        tarea_count = Tarea.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tareas",
            total=tarea_count,
            page=page,
            step=10
        )

        # Buscamos las tareas con el límite del paginador
        tareas = Tarea.sudo().search(domain, limit=10, offset=pager['offset'], order="date_deadline asc")

        values.update({
            'tareas': tareas,
            'page_name': 'tareas_caletti',
            'pager': pager,
            'default_url': '/my/tareas',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render("tablero_kanban.portal_my_tareas_template", values)

    @http.route(['/my/tarea/<int:tarea_id>'], type='http', auth="user", website=True)
    def portal_my_tarea_detail(self, tarea_id, **kw):
        tarea = request.env['tablero.tarea'].sudo().search([
            ('id', '=', tarea_id),
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)

        if not tarea:
            return request.redirect('/my/tareas')

        values = {
            'tarea': tarea,
            'page_name': 'tareas_caletti', # Mantiene el breadcrumb activo
        }
        return request.render("tablero_kanban.portal_tarea_page", values)