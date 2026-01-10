{
    'name': 'Tablero Kanban Caletti',
    'category': 'Extra Tools',
    'version': '1.0',
    'summary': 'Gestión visual de tareas',
    'author': 'Carlos Caletti',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/report_tarea.xml',
    ],
    'installable': True,
    'application': True,
}
