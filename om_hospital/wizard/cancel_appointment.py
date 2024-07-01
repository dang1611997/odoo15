import datetime

from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        res['date_cancel'] = datetime.date.today()
        print("........context", self.env.context.get('active_id'))
        if self.env.context.get('active_id'):
            res['appointment_id'] = self.env.context.get('active_id')
        return res

    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    reason = fields.Text(string='Reason')
    date_cancel = fields.Date(string='Cancellation Date')

    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].get_param('om_hospital.cancel_day')
        allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(days=int(cancel_day))
        if allowed_date < datetime.date.today():
            raise ValidationError(_('Sorry, cancellation is not allowed for this booking !'))
        self.appointment_id.state = 'canceled'
        return {

            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancel.appointment.wizard',
            'target': 'new',
            'res_id': self.id


        }

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload'
        # }

        # if self.appointment_id.booking_date == fields.Date.today():
        #     raise ValidationError(_("Sorry,cancellation is not allowed on the same day of booking!"))
        # self.appointment_id.state = 'canceled'
        # return
