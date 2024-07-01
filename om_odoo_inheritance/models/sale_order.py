from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmed_user_id = fields.Many2one('res.users', string='Confirmed User')

    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        print("Sucess")
        # user nào đã confirm bản ghi này
        self.confirmed_user_id = self.env.user.id  # cung cap id cua nguoi dung hien tai
