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
ROL_MODELO             = 'modelo'
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
    _description = 'Miembro del Equipo Creativo'
    _rec_name = 'nombre_display'
    _order = 'es_responsable desc, rol asc'

    # --- PROYECTO ---
    proyecto_id = fields.Many2one(
        'tablero.tarea',
        string='Proyecto',
        required=True,
        ondelete='cascade',
        index=True
    )

    # --- TIPO DE COLABORADOR ---
    tipo_colaborador = fields.Selection([
        (TIPO_INTERNO, '🏢 Interno (Staff)'),
        (TIPO_EXTERNO, '🤝 Externo (Freelancer / Proveedor)'),
    ], string='Tipo',
       required=True,
       default=TIPO_INTERNO,
    #   tracking=True
    )

    # --- IDENTIDAD: INTERNO ---
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
    # tracking=True,
        help="Usuario interno de Odoo. Solo aplica para colaboradores internos."
    )

    # --- IDENTIDAD: EXTERNO ---
    partner_id = fields.Many2one(
        'res.partner',
        string='Colaborador Externo',
    #    tracking=True,
        help="Contacto en Odoo del colaborador externo: "
             "fotógrafo freelance, proveedor de video, ilustrador, etc."
    )

    # --- NOMBRE UNIFICADO (computed) ---
    nombre_display = fields.Char(
        string='Colaborador',
        compute='_compute_nombre_display',
        store=True,
        help="Nombre resuelto según tipo: usuario interno o contacto externo"
    )

    # --- ROL EN EL PROYECTO ---
    rol = fields.Selection([
        (ROL_DIRECTOR_CREATIVO, '🎯 Director Creativo'),
        (ROL_DISENADOR,         '🎨 Diseñador Gráfico'),
        (ROL_COPYWRITER,        '✍️ Copywriter'),
        (ROL_FOTOGRAFO,         '📷 Fotógrafo'),
        (ROL_VIDEOASTA,         '🎬 Videografp / Editor'),
        (ROL_ILUSTRADOR,        '🖌️ Ilustrador'),
        (ROL_MOTION,            '✨ Motion Designer'),
        (ROL_MODELO,            '👩 Modelo talento'),
        (ROL_DESARROLLADOR,     '💻 Desarrollador'),
        (ROL_ACCOUNT,           '📋 Account Manager'),
        (ROL_PRODUCTOR,         '🎙️ Productor'),
        (ROL_OTRO,              '📦 Otro'),
    ], string='Rol',
       required=True,
    #   tracking=True
    )

    rol_descripcion = fields.Char(
        string='Descripción del Rol',
        help="Detalle adicional del rol cuando se selecciona 'Otro' "
             "o para especificar responsabilidades concretas en el proyecto."
    )

    # --- RESPONSABILIDAD PRINCIPAL ---
    es_responsable = fields.Boolean(
        string='Director Creativo del Proyecto',
        default=False,
        tracking=True,
        help="Marca al responsable creativo principal del proyecto. "
             "Solo puede haber uno por proyecto."
    )

    # --- DISPONIBILIDAD Y PARTICIPACIÓN ---
    fecha_entrada = fields.Date(
        string='Fecha de Incorporación',
        default=fields.Date.today,
        help="Fecha desde la que este colaborador participa en el proyecto"
    )

    fecha_salida = fields.Date(
        string='Fecha de Salida',
        help="Fecha hasta la que este colaborador participa. "
             "Vacío indica participación hasta el cierre del proyecto."
    )

    activo_en_proyecto = fields.Boolean(
        string='Activo en Proyecto',
        compute='_compute_activo_en_proyecto',
        store=True,
        help="False si la fecha de salida ya fue superada"
    )

    notas = fields.Text(
        string='Notas',
        help="Condiciones especiales, tarifas acordadas, "
             "restricciones de disponibilidad o cualquier nota relevante "
             "sobre la participación de este colaborador."
    )

    # --- COMPUTED ---

    @api.depends('tipo_colaborador', 'user_id', 'partner_id')
    def _compute_nombre_display(self):
        """
        Resuelve el nombre del colaborador según su tipo.
        Interno → nombre del usuario de Odoo
        Externo → nombre del contacto res.partner
        Garantiza que las vistas Kanban y reportes
        siempre tengan un nombre sin lógica condicional en XML.
        """
        for member in self:
            if member.tipo_colaborador == TIPO_INTERNO and member.user_id:
                member.nombre_display = member.user_id.name
            elif member.tipo_colaborador == TIPO_EXTERNO and member.partner_id:
                member.nombre_display = member.partner_id.name
            else:
                member.nombre_display = _("Sin asignar")

    @api.depends('fecha_salida')
    def _compute_activo_en_proyecto(self):
        """
        Un colaborador está activo si no tiene fecha de salida
        o si su fecha de salida aún no ha llegado.
        """
        today = fields.Date.today()
        for member in self:
            if member.fecha_salida:
                member.activo_en_proyecto = member.fecha_salida >= today
            else:
                member.activo_en_proyecto = True

    # --- VALIDACIONES ---

    @api.constrains('tipo_colaborador', 'user_id', 'partner_id')
    def _check_identidad_completa(self):
        """
        Garantiza que cada miembro tenga identidad según su tipo.
        Interno debe tener user_id.
        Externo debe tener partner_id.
        """
        for member in self:
            if member.tipo_colaborador == TIPO_INTERNO and not member.user_id:
                raise ValidationError(_(
                    "Un colaborador interno debe tener un usuario "
                    "de Odoo asignado."
                ))
            if member.tipo_colaborador == TIPO_EXTERNO and not member.partner_id:
                raise ValidationError(_(
                    "Un colaborador externo debe tener un contacto "
                    "asignado en Odoo."
                ))

    @api.constrains('es_responsable', 'proyecto_id')
    def _check_un_solo_director(self):
        """
        Garantiza que solo exista un Director Creativo por proyecto.
        Regla de responsabilidad única — evita conflictos de autoridad
        en decisiones creativas.
        """
        for member in self:
            if member.es_responsable:
                otros_directores = self.search([
                    ('proyecto_id', '=', member.proyecto_id.id),
                    ('es_responsable', '=', True),
                    ('id', '!=', member.id),
                ])
                if otros_directores:
                    raise ValidationError(_(
                        "El proyecto '%(proyecto)s' ya tiene un "
                        "Director Creativo asignado: %(director)s.\n\n"
                        "Un proyecto solo puede tener un Director Creativo."
                    ) % {
                        'proyecto': member.proyecto_id.name,
                        'director': otros_directores[0].nombre_display,
                    })

    @api.constrains('fecha_entrada', 'fecha_salida')
    def _check_fechas_coherentes(self):
        """
        La fecha de salida no puede ser anterior a la fecha de entrada.
        """
        for member in self:
            if (member.fecha_entrada
                    and member.fecha_salida
                    and member.fecha_salida < member.fecha_entrada):
                raise ValidationError(_(
                    "La fecha de salida de %(nombre)s no puede ser "
                    "anterior a su fecha de incorporación al proyecto."
                ) % {'nombre': member.nombre_display})

    @api.constrains('tipo_colaborador', 'user_id', 'proyecto_id')
    def _check_sin_duplicados(self):
        """
        Un usuario interno no puede aparecer dos veces
        en el mismo proyecto con el mismo rol.
        """
        for member in self:
            if member.tipo_colaborador == TIPO_INTERNO and member.user_id:
                duplicados = self.search([
                    ('proyecto_id', '=', member.proyecto_id.id),
                    ('user_id', '=', member.user_id.id),
                    ('rol', '=', member.rol),
                    ('id', '!=', member.id),
                ])
                if duplicados:
                    raise ValidationError(_(
                        "%(nombre)s ya está asignado como %(rol)s "
                        "en este proyecto."
                    ) % {
                        'nombre': member.user_id.name,
                        'rol': dict(
                            self._fields['rol'].selection
                        ).get(member.rol),
                    })

    # --- OVERRIDE create PARA LOGGING Y NOTIFICACIÓN ---

    @api.model
    def create(self, vals):
        """
        Notifica al colaborador interno via Chatter del proyecto
        cuando es incorporado al equipo.
        """
        member = super(CreativeTeamMember, self).create(vals)

        # Notificar en el Chatter del proyecto
        rol_label = dict(
            self._fields['rol'].selection
        ).get(member.rol, member.rol)

        member.proyecto_id.message_post(
            body=_(
                "👥 <strong>Nuevo miembro en el equipo:</strong> "
                "%(nombre)s como <em>%(rol)s</em>%(tipo)s"
            ) % {
                'nombre': member.nombre_display,
                'rol': rol_label,
                'tipo': _(
                    " (colaborador externo)"
                ) if member.tipo_colaborador == TIPO_EXTERNO else '',
            },
            subject=_("Equipo Actualizado")
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

        # Si es interno, suscribirlo automáticamente al Chatter del proyecto
        if member.tipo_colaborador == TIPO_INTERNO and member.user_id:
            member.proyecto_id.message_subscribe(
                partner_ids=[member.user_id.partner_id.id]
            )
            _logger.info(
                "👥 %s agregado al equipo de '%s' como %s. "
                "Suscrito al Chatter.",
                member.nombre_display,
                member.proyecto_id.name,
                rol_label
            )
        else:
            _logger.info(
                "🤝 Colaborador externo '%s' agregado al equipo de '%s' "
                "como %s.",
                member.nombre_display,
                member.proyecto_id.name,
                rol_label
            )

        return member

    def unlink(self):
        """
        Notifica en el Chatter del proyecto cuando se remueve
        un colaborador del equipo.
        """
        for member in self:
            member.proyecto_id.message_post(
                body=_(
                    "👤 <strong>%(nombre)s</strong> ha sido removido "
                    "del equipo del proyecto."
                ) % {'nombre': member.nombre_display},
                subject=_("Equipo Actualizado")
                message_type='comment'
                subtype_xmlid='mail.mt_note'
            )
            _logger.info(
                "👤 %s removido del equipo de '%s'",
                member.nombre_display,
                member.proyecto_id.name
            )
        return super(CreativeTeamMember, self).unlink()