# -*- coding: utf-8 -*-
{
    'name': 'Tablero Kanban - Helpdesk Extension',
    'version': '17.0.2.0.0', #Nueva versión
    'category': 'Services/Helpdesk',
    'summary': 'Extensión Sistema de Tickets con Mail Alias y Portal para el Core de Caletti Studio',
    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'depends': ['tablero_kanban_caletti'], # La base para la integración 
    'data': [
        'data/helpdesk_data.xml',
        'views/helpdesk_views.xml',# Aquí los nuevos XML de tickets
        'views/portal_helpdesk_views.xml',
    ],
    'installable': True,
    'application': False,
}