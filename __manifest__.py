{
    'name': 'Tablero Kanban Caletti',
    'category': 'Project/Management',
    'version': '17.0.1.2', 
    'summary': 'Gestión visual de tareas con Business Intelligence y Portal de Cliente',
    'description': """
        Tablero Kanban Avanzado - Caletti Studio
        =========================================
        
        Características principales:
        * Sistema de alertas automatizado
        * Portal de cliente personalizado
        * Vistas de análisis BI (Gráfico/Pivote)
        * Integración total con Chatter
        * Sistema de semáforos visuales
        * Gestión de plazos y retrasos
        
        Ideal para agencias creativas y equipos de proyecto.
    """,

    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'license': 'LGPL-3', 
    'price': 0.00,
    'currency': 'MXN',
    'support': 'hola@cstudio.caletti.com.mx',
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

