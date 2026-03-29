# caletti_creative/controllers/creative_portal.py
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


class CalettiCreativePortal(CustomerPortal):
    """
    Portal del cliente para el vertical creativo.
    Extiende CustomerPortal — mismo patrón que CalettiPortal del Core.
    
    El cliente puede:
    - Ver sus proyectos creativos
    - Ver el detalle de cada proyecto
    - Ver y navegar el brief creativo
    - Aprobar o rechazar el brief directamente desde el portal
    
    Seguridad: Record Rules filtran automáticamente por partner_id.
    Sin sudo() — el cliente solo ve lo que le corresponde.
    """

    def _prepare_home_portal_values(self, counters):
        """
        Agrega contador de proyectos creativos al portal home.
        Solo proyectos donde el cliente es partner_id.
        """
        values = super()._prepare_home_portal_values(counters)

        if 'proyecto_creativo_count' in counters:
            # Sin sudo() — Record Rules aplican automáticamente
            values['proyecto_creativo_count'] = request.env[
                'tablero.tarea'
            ].search_count([
                ('es_proyecto_creativo', '=', True)
            ])

        return values

    # ------------------------------------------------------------------
    # RUTA: Lista de proyectos creativos del cliente
    # ------------------------------------------------------------------

    @http.route(
        ['/my/proyectos-creativos',
         '/my/proyectos-creativos/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_mis_proyectos_creativos(
        self, page=1, sortby=None, filterby=None, search=None, **kw
    ):
        """
        Lista paginada de proyectos creativos del cliente.
        Record Rules garantizan aislamiento por partner_id.
        """
        values = self._prepare_portal_layout_values()
        Proyecto = request.env['tablero.tarea']  # Sin sudo()

        # --- Filtros disponibles ---
        searchbar_filters = {
            'all':     {'label': _('Todos'),
                        'domain': [('es_proyecto_creativo', '=', True)]},
            'nuevo':   {'label': _('Nuevos'),
                        'domain': [('es_proyecto_creativo', '=', True),
                                   ('state', '=', 'nuevo')]},
            'proceso': {'label': _('En Proceso'),
                        'domain': [('es_proyecto_creativo', '=', True),
                                   ('state', '=', 'proceso')]},
            'hecho':   {'label': _('Finalizados'),
                        'domain': [('es_proyecto_creativo', '=', True),
                                   ('state', '=', 'hecho')]},
        }

        # --- Ordenamientos disponibles ---
        searchbar_sortings = {
            'date':     {'label': _('Fecha Límite'),
                         'order': 'date_deadline asc'},
            'name':     {'label': _('Nombre'),
                         'order': 'name asc'},
            'progress': {'label': _('Progreso'),
                         'order': 'progress desc'},
        }

        # Valores por defecto
        if not filterby:
            filterby = 'all'
        if not sortby:
            sortby = 'date'

        domain     = searchbar_filters[filterby]['domain']
        sort_order = searchbar_sortings[sortby]['order']

        # Búsqueda por texto
        if search:
            domain += [('name', 'ilike', search)]

        # Conteo y paginación
        proyecto_count = Proyecto.search_count(domain)
        pager = portal_pager(
            url='/my/proyectos-creativos',
            url_args={
                'sortby': sortby,
                'filterby': filterby,
                'search': search,
            },
            total=proyecto_count,
            page=page,
            step=9  # 3x3 grid en kanban del portal
        )

        proyectos = Proyecto.search(
            domain,
            limit=9,
            offset=pager['offset'],
            order=sort_order
        )

        _logger.debug(
            "Portal Creative: %s viendo %d proyectos",
            request.env.user.name, len(proyectos)
        )

        values.update({
            'proyectos': proyectos,
            'page_name': 'proyectos_creativos',
            'pager': pager,
            'default_url': '/my/proyectos-creativos',
            'searchbar_filters': OrderedDict(
                sorted(searchbar_filters.items())
            ),
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'filterby': filterby,
            'search': search,
        })

        return request.render(
            'caletti_creative.portal_mis_proyectos_creativos',
            values
        )

    # ------------------------------------------------------------------
    # RUTA: Detalle de proyecto creativo
    # ------------------------------------------------------------------

    @http.route(
        ['/my/proyecto-creativo/<int:proyecto_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_detalle_proyecto_creativo(self, proyecto_id, **kw):
        """
        Detalle de un proyecto creativo específico.
        Muestra brief, equipo, entregables y estado de presupuesto.
        Record Rules validan acceso automáticamente.
        """
        # Sin sudo() — si no tiene acceso retorna vacío
        proyecto = request.env['tablero.tarea'].search([
            ('id', '=', proyecto_id),
            ('es_proyecto_creativo', '=', True),
        ], limit=1)

        if not proyecto:
            _logger.warning(
                "Portal Creative: %s intentó acceder a proyecto %d sin permiso",
                request.env.user.name, proyecto_id
            )
            return request.redirect('/my/proyectos-creativos')

        # Brief activo — aprobado o en revisión
        brief_activo = proyecto.brief_ids.filtered(
            lambda b: b.estado_brief in ['en_revision', 'aprobado', 'borrador']
        )
        brief_activo = brief_activo[:1]  # El más reciente

        _logger.debug(
            "Portal Creative: %s viendo proyecto '%s'",
            request.env.user.name, proyecto.name
        )

        values = {
            'proyecto': proyecto,
            'brief_activo': brief_activo,
            'page_name': 'proyectos_creativos',
        }

        return request.render(
            'caletti_creative.portal_detalle_proyecto_creativo',
            values
        )

    # ------------------------------------------------------------------
    # RUTA: Detalle del brief — vista completa para lectura del cliente
    # ------------------------------------------------------------------

    @http.route(
        ['/my/brief/<int:brief_id>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_detalle_brief(self, brief_id, **kw):
        """
        Vista completa del brief para lectura del cliente.
        Muestra todas las secciones y los botones de acción
        si el brief está en estado 'en_revision'.
        """
        brief = request.env['creative.brief'].search([
            ('id', '=', brief_id),
        ], limit=1)

        if not brief:
            _logger.warning(
                "Portal Creative: %s intentó acceder a brief %d sin permiso",
                request.env.user.name, brief_id
            )
            return request.redirect('/my/proyectos-creativos')

        # Mensaje de confirmación tras aprobar/rechazar
        mensaje = kw.get('mensaje')

        values = {
            'brief': brief,
            'proyecto': brief.proyecto_id,
            'page_name': 'proyectos_creativos',
            'mensaje': mensaje,
        }

        return request.render(
            'caletti_creative.portal_detalle_brief',
            values
        )

    # ------------------------------------------------------------------
    # RUTA POST: Aprobar brief desde el portal
    # ------------------------------------------------------------------

    @http.route(
        ['/my/brief/<int:brief_id>/aprobar'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True
    )
    def portal_aprobar_brief(self, brief_id, **post):
        """
        Acción de aprobación del brief por el cliente desde el portal.
        Llama a action_aprobar() del modelo — mismo flujo que el backend.
        Redirige al detalle del proyecto con mensaje de confirmación.
        """
        brief = request.env['creative.brief'].search([
            ('id', '=', brief_id),
        ], limit=1)

        if not brief:
            return request.redirect('/my/proyectos-creativos')

        if brief.estado_brief != 'en_revision':
            _logger.warning(
                "Portal Creative: intento de aprobar brief %d "
                "en estado incorrecto: %s",
                brief_id, brief.estado_brief
            )
            return request.redirect(
                f'/my/brief/{brief_id}?mensaje=estado_invalido'
            )

        try:
            # Usar sudo() solo para la acción de aprobación —
            # el cliente portal no tiene permisos de escritura
            # en creative.brief por Record Rules
            brief.sudo().action_aprobar()
            _logger.info(
                "✅ Brief %d aprobado desde portal por %s",
                brief_id, request.env.user.name
            )
        except Exception as e:
            _logger.error(
                "❌ Error aprobando brief %d desde portal: %s",
                brief_id, str(e)
            )
            return request.redirect(
                f'/my/brief/{brief_id}?mensaje=error'
            )

        return request.redirect(
            f'/my/proyecto-creativo/{brief.proyecto_id.id}'
            f'?mensaje=brief_aprobado'
        )

    # ------------------------------------------------------------------
    # RUTA POST: Rechazar brief desde el portal
    # ------------------------------------------------------------------

    @http.route(
        ['/my/brief/<int:brief_id>/rechazar'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True
    )
    def portal_rechazar_brief(self, brief_id, **post):
        """
        Acción de rechazo del brief por el cliente desde el portal.
        Captura el motivo del formulario POST.
        Redirige al detalle del proyecto con mensaje de confirmación.
        """
        brief = request.env['creative.brief'].search([
            ('id', '=', brief_id),
        ], limit=1)

        if not brief:
            return request.redirect('/my/proyectos-creativos')

        if brief.estado_brief not in ['en_revision', 'borrador']:
            return request.redirect(
                f'/my/brief/{brief_id}?mensaje=estado_invalido'
            )

        # Capturar motivo del formulario
        motivo = post.get('motivo', '').strip()
        if not motivo:
            return request.redirect(
                f'/my/brief/{brief_id}?mensaje=motivo_requerido'
            )

        try:
            brief.sudo().action_rechazar(motivo=motivo)
            _logger.info(
                "❌ Brief %d rechazado desde portal por %s. Motivo: %s",
                brief_id, request.env.user.name, motivo
            )
        except Exception as e:
            _logger.error(
                "❌ Error rechazando brief %d desde portal: %s",
                brief_id, str(e)
            )
            return request.redirect(
                f'/my/brief/{brief_id}?mensaje=error'
            )

        return request.redirect(
            f'/my/proyecto-creativo/{brief.proyecto_id.id}'
            f'?mensaje=brief_rechazado'
        )