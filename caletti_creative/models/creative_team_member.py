# caletti_creative/models/creative_team_member.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#   Part of Caletti Studio.
#   See LICENSE file for full copyright and licensing details.
#
#   Caletti Studio / MEXICO - BUENOS AIRES - ROMA
#   Lead Architect & Developer: Carlos Caletti - 2026
# --------------------------------------------------------------------------

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# === CONSTANTES: TIPO DE COLABORADOR ===
TIPO_INTERNO  = 'interno'
TIPO_EXTERNO  = 'externo'

# === CONSTANTES: ROLES CREATIVOS ===
ROL_DIRECTOR_CREATIVO  = 'director_creativo'
ROL_DISENADOR          = 'disenador'
ROL_COPYWRITER         = 'copywriter'
ROL_FOTOGRAFO          = 'fotografo'
ROL_VIDEOASTA          = 'videoasta'
ROL_ILUSTRADOR         = 'ilustrador'
ROL_MOTION             = 'motion'
ROL_DESARROLLADOR      = 'desarrollador'
ROL_ACCOUNT            = 'account'
ROL_PRODUCTOR          = 'productor'
ROL_OTRO               = 'otro'


class CreativeTeamMember(models.Model):
    """
    Miembro del equipo creativo asignado a un proyecto.

    Soporta dos tipos de colaboradores:
    - Interno: usuario de Odoo (staff de la agencia)
    - Externo: contacto res.partner (freelancer, proveedor, colaborador)

    Un proyecto tiene exactamente un Director Creativo responsable.
    Los demás roles son múltiples y no exclusivos.
    """
    _name = 'creative.team.member'