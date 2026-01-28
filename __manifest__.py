{
    'name': 'Tablero Kanban Caletti',
    'category': 'Project/Management', # 'Extra Tools' es muy genérico, esta es más precisa
    'version': '17.0.1.2', # Indica compatibilidad nativa con Odoo 17
    'summary': 'Gestión visual de tareas con Business Intelligence y Portal de Cliente',
    'author': 'Carlos Caletti',
    'license': 'LGPL-3', # Muy importante para ser Partner
    'depends': ['base', 'mail', 'portal'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'security/tablero_rules.xml',
        'views/views.xml',
        'views/report_tarea.xml',
        'views/portal_templates.xml',
        'data/mail_template_data.xml',
        'data/ir_cron.xml',
    ],
    'images': [
        'static/description/screenshot_kanban.png',
        'static/description/screenshot_kanban_detalle.png',
        'static/description/screenshot_kanban_detalle_chatter_tabs.png',
        'static/description/screenshot_portaltareas.png',
        'static/description/screenshot_portaldetalle_tarea.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

