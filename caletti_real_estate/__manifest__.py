# caletti_real_estate/__manifest__.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------
{
    'name': 'Caletti Real Estate — Vertical Gestión Inmobiliaria',
    'version': '17.0.1.1.0',
    'category': 'Administration/Real Estate',
    'summary': 'Gestión de propiedades, prospectos, contratos y mantenimiento para asesores inmobiliarios',
    'description': """

        Caletti Real Estate — Vertical para Asesores Inmobiliarios
        ===========================================================

        Módulo vertical que extiende el Core de Caletti Studio
        con funcionalidades específicas para asesores y administradoras:

        * Cartera de propiedades: residencial, comercial y terrenos
        * Gestión de prospectos con pipeline de captación
        * Contrato unificado: renta O venta en un solo modelo
        * Seguimiento de mantenimientos por propiedad
        * Operaciones como tareas del Core (kanban, chatter, portal)
        * Alertas automáticas: vencimientos, rentas, comisiones

        Requiere: tablero_kanban_caletti (Core)

        NOTA ARQUITECTÓNICA — re.visita:
        Las visitas a propiedades se gestionan como mail.activity en v1.0.
        Para v2.0 (administradoras con cartera >50 propiedades activas)
        considerar migración a modelo propio re.visita con campos:
        propiedad_id, prospecto_id, fecha, duración, resultado,
        feedback_estructurado, tasa_conversión_a_contrato.
    """,
    'author': 'Carlos Caletti',
    'website': 'https://studio.caletti.com.mx',
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'MXN',
    'support': 'hola@studio.caletti.com.mx',

    'depends': [
        'tablero_kanban_caletti',  # Core — obligatorio
        'account',                 # Para campos Monetary (currency_id, precios)
        'portal',                  
    ],

    'data': [
    'security/security_groups.xml',
    'security/ir.model.access.csv',
    'security/ir_rule.xml',
    'data/re_sequences.xml',
    'views/re_visita_views.xml',
    'views/re_propiedad_views.xml',
    'views/re_prospecto_views.xml',
    'views/re_operacion_views.xml',
    'views/re_contrato_views.xml',
    'views/re_mantenimiento_views.xml',
    'views/re_analisis_views.xml',
    'views/portal_re_templates.xml',
        # 'data/re_data.xml',               # se agregara
    ],

    'images': [
        'static/description/icon.png',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
