from odoo import api, fields, models


class OdooPlayGround(models.Model):
    _name = 'odoo.playground'
    _description = 'Odoo PlayGround'

    # DEFAULT_ENV_VARIABLES =
    # default = DEFAULT_ENV_VARIABLES

    model_id = fields.Many2one('ir.model', string='Model')
    code = fields.Text(string='Code')
    result = fields.Text(string='Result')
