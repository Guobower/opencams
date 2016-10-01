# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _


class ReConnectorAbstractModel(models.AbstractModel):
    """ AbstractModel for Import Connector """
    _name = 're.connector.abstract.model'

    name = fields.Char('Target Field')
    ttype = fields.Char('Source Field')
    required = fields.Boolean('Required')
    field_description = fields.Char('Description')
    source_field = fields.Char('Source Field')
    compute_transform = fields.Text("Compute", help="Code to transform the value of the field.\n"
                            "Iterate on the recordset 'self' and assign the field's value:\n\n"
                            "    for record in self:\n"
                            "        record['size'] = len(record.name)\n\n"
                            "Modules time, datetime, dateutil are available.")