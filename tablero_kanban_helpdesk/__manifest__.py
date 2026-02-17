# -*- coding: utf-8 -*-
{
    'name': 'Tablero Kanban - Helpdesk Extension',
    'version': '1.0',
    'category': 'Services/Helpdesk',
    'summary': 'Extensión de Tickets para el Core de Caletti Studio',
    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'depends': ['tablero_kanban_caletti'], # La base para la integración 
    'data': [
        'views/helpdesk_views.xml',# Aquí los nuevos XML de tickets
    ],
    'installable': True,
    'application': False,
}