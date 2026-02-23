# ---------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#   
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# ---------------------------------------------------------------------------
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict
import logging

_logger = logging.getLogger(__name__)

# EXTENSIÓN DE PORTAL: Sobrescribe la clase CustomerPortal para integrar la lógica de Caletti Studio
class CalettiPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """ Actualiza el contador de 'Mis Tareas' en la página principal del portal """
        values = super(CalettiPortal, self)._prepare_home_portal_values(counters)
        if 'tarea_count' in counters:
            # SIN sudo() - Las Record Rules manejan la seguridad
            values['tarea_count'] = request.env['tablero.tarea'].search_count([])
        return values

    @http.route(['/my/tareas', '/my/tareas/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tareas(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        """
        Vista principal del portal de tareas para clientes.
        La seguridad se maneja mediante Record Rules (NO con sudo()).
        """
        values = self._prepare_portal_layout_values()
        Tarea = request.env['tablero.tarea']  # SIN sudo()

        # Definición de filtros disponibles
        searchbar_filters = {
            'all': {'label': _('Todas'), 'domain': []},
            'nuevo': {'label': _('Nuevas'), 'domain': [('state', '=', 'nuevo')]},
            'proceso': {'label': _('En Proceso'), 'domain': [('state', '=', 'proceso')]},
            'hecho': {'label': _('Finalizadas'), 'domain': [('state', '=', 'hecho')]},
            'vencidas': {'label': _('Vencidas'), 'domain': [('is_overdue', '=', True)]},
        }
        
        searchbar_sortings = {
            'date': {'label': _('Fecha Límite'), 'order': 'date_deadline asc'},
            'name': {'label': _('Nombre'), 'order': 'name asc'},
            'priority': {'label': _('Prioridad'), 'order': 'priority desc'},
            'progress': {'label': _('Progreso'), 'order': 'progress desc'},
        }
        
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Tareas')},
        }

        # Valores por defecto
        if not filterby:
            filterby = 'all'
        if not sortby:
            sortby = 'date'
        
        domain = searchbar_filters[filterby]['domain']
        sort_order = searchbar_sortings[sortby]['order']

        # NOTA: Ya NO agregamos filtro manual de partner_id
        # Las Record Rules automáticamente filtran por partner_id del usuario actual
        
        # Búsqueda por texto
        if search and search_in:
            domain += [('name', 'ilike', search)]

        # Conteo total (respetando Record Rules automáticamente)
        tarea_count = Tarea.search_count(domain)
        
        # Configuración del paginador
        pager = portal_pager(
            url="/my/tareas",
            url_args={'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=tarea_count,
            page=page,
            step=10
        )

        # Búsqueda de tareas (SIN sudo - las Record Rules aplican automáticamente)
        tareas = Tarea.search(domain, limit=10, offset=pager['offset'], order=sort_order)
        
        _logger.debug("Portal: Usuario %s accediendo a %d tareas", request.env.user.name, len(tareas))

        values.update({
            'tareas': tareas,
            'page_name': 'tareas_caletti',
            'pager': pager,
            'default_url': '/my/tareas',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render("tablero_kanban_caletti.portal_my_tareas_template", values)

    @http.route(['/my/tarea/<int:tarea_id>'], type='http', auth="user", website=True)
    def portal_my_tarea_detail(self, tarea_id, access_token=None, **kw):
        """
        Vista de detalle de una tarea individual.
        La seguridad se valida mediante Record Rules automáticamente.
        """
        try:
            # SIN sudo() - Si el usuario no tiene acceso, search retornará vacío
            tarea = request.env['tablero.tarea'].search([('id', '=', tarea_id)], limit=1)
        except Exception as e:
            _logger.warning("Error accediendo a tarea %d: %s", tarea_id, str(e))
            tarea = request.env['tablero.tarea'].browse()

        # Si no hay tarea (por Record Rules o no existe), redirigir
        if not tarea:
            _logger.warning("Usuario %s intentó acceder a tarea %d sin permiso", request.env.user.name, tarea_id)
            return request.redirect('/my/tareas')

        values = {
            'tarea': tarea,
            'page_name': 'tareas_caletti',
        }
        
        _logger.debug("Portal: Usuario %s viendo detalle de tarea '%s'", request.env.user.name, tarea.name)
        
        return request.render("tablero_kanban_caletti.portal_tarea_page", values)
    
    @http.route(['/my/tarea/<int:tarea_id>/comment'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_tarea_add_comment(self, tarea_id, **post):
        """
        Permite a los clientes del portal agregar comentarios a sus tareas.
        """
        tarea = request.env['tablero.tarea'].search([('id', '=', tarea_id)], limit=1)
        
        if not tarea:
            return request.redirect('/my/tareas')
        
        comment = post.get('comment', '').strip()
        if comment:
            tarea.sudo().message_post(
                body=comment,
                author_id=request.env.user.partner_id.id,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
            _logger.info("Comentario agregado por %s en tarea '%s'", request.env.user.name, tarea.name)
        
        return request.redirect(f'/my/tarea/{tarea_id}')
