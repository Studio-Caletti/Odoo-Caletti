# caletti_real_estate/models/__init__.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

# Orden de carga:
# 1. re_propiedad     — modelo central + submodelo re.propiedad.foto
# 2. re_prospecto     — lead / interesado (renta o compra)
# 3. re_operacion     — _inherit tablero.tarea, una operación por propiedad
# 4. re_contrato      — venta O renta (un solo modelo, tipo_operacion)
# 5. re_mantenimiento — solicitudes vinculadas a propiedad y contrato

from . import re_propiedad