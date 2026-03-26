# caletti_creative/models/__init__.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

# Orden de carga:
# 1. creative_project   — _inherit tablero.tarea (Core), define los One2many
# 2. creative_brief     — modelo propio, referenciado por creative_project
# 3. creative_deliverable — modelo propio, alimenta costo_real del proyecto
# 4. creative_team_member — modelo propio, gestiona equipo interno y externo

from . import creative_project
from . import creative_brief
from . import creative_deliverable
from . import creative_team_member