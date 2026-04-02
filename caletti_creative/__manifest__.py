# caletti_creative/__manifest__.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------
{
    'name': 'Caletti Creative — Vertical Gestión Creativa',
    'version': '17.0.1.0.0',
    'category': 'Project/Creative',
    'summary': 'Gestión de proyectos creativos: Brief, Equipo, Entregables y Presupuesto',
    'description': """
    
        Caletti Creative — Vertical para Agencias Creativas
        ====================================================

        Módulo vertical que extiende el Core de Caletti Studio
        con funcionalidades específicas para agencias creativas:

        * Brief creativo integrado al proyecto (aprobación por cliente)
        * Gestión de equipo creativo con roles por proyecto
        * Entregables como subtareas propias del vertical
        * Presupuesto básico con seguimiento de costo real
        * Tipos de proyecto creativo (branding, campaña, web, etc.)

        Requiere: tablero_kanban_caletti (Core)
    """,
    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'MXN',
    'support': 'hola@studio.caletti.com.mx',

    # Core es dependencia obligatoria. Helpdesk es opcional — no se declara aquí.
    'depends': [
        'tablero_kanban_caletti',
        'account',  # Para campos Monetary (currency_id, presupuesto)
    ],

    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/creative_project_views.xml',
        'views/creative_brief_views.xml',
        'views/creative_deliverable_views.xml',
        'views/portal_creative_templates.xml',
        'data/creative_data.xml',
    ],

    

    'images': [
        'static/description/icon.png',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}