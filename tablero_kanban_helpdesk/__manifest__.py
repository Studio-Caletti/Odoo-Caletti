# -*- coding: utf-8 -*-
# tablero_kanban_helpdesk/__manifest__.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------
{
    'name': 'Caletti Helpdesk Extension ',
    'version': '17.0.2.0.0', #Nueva versión
    'category': 'Adminisration/Services/Helpdesk',
    'summary': 'Extensión Sistema de Tickets con Mail Alias y Portal para el Core de Caletti Studio',
    'description': """

    
        Caletti Creative — Vertical HelpDesk Tickets system
        ====================================================

        Módulo vertical que extiende el Core de Caletti Studio
        con funcionalidades específicas para HelpDesk:

        * Generación de Tickets en tablero
        * Gestión de equipo de atencion con roles por proyecto
        * Portal del Cliente con integracion al Chatter
        * Awarness visual y sistema de creacion de tikets por Email
        * Tipos de Tikcets por área (Mantenimiento, Soporte Técnico Consultoria)

        Requiere: tablero_kanban_caletti (Core)
    """,
    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'MXN',
    'support': 'hola@cstudio.caletti.com.mx',

    # Core es dependencia obligatoria.
    'depends': ['tablero_kanban_caletti'], # La base para la integración 
    'data': [
        'data/helpdesk_data.xml',
        'views/helpdesk_views.xml',# Aquí los nuevos XML de tickets
        'views/portal_helpdesk_views.xml',
    ],

     

     'images': [
        'static/description/icon.png',
    ],

    'installable': True,
    'application': True,
}