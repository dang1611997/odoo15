# -*- coding: utf-8 -*-
import random

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Appointment'
    _rec_name = 'ref'
    _order = 'id desc'
    name = fields.Char(string="Sequence", default='New', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string="Patient", ondelete='restrict', tracking=1)
    gender = fields.Selection(related='patient_id.gender')
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    booking_date = fields.Date(string="Booking Date", default=fields.Date.context_today, tracking=True)
    ref = fields.Char(string="Reference")
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    pharmacy_lines_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string='Pharmacy Lines')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_consultation', 'In Consultation'), ('done', 'Done'), ('canceled', 'Canceled')],
        default='draft', required=True, string='Status', tracking=2)
    hide_sale_price = fields.Boolean(string='Hide Sale Price')
    operation_id = fields.Many2one('hospital.operation', string='Operation')
    progress = fields.Integer(string='Progress', compute='_compute_progress')
    duration = fields.Float(string='Duration', tracking=110)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        return super(HospitalAppointment, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_('You can delete appointment only in "Draft" status !'))
        print("Test......")
        return super(HospitalAppointment, self).unlink()

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_notification(self):
        message = 'Button Click Successful'
        action = self.env.ref('om_hospital.action_hospital_patient')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Click to open the patient record'),
                'sticky': False,                #Bien mat sau vai giay
                'message': '%s',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient',
                }],

            }
        }

    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=10)

    def action_test(self):
        # url action
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'contactus'
        }

    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_('Missing phone number in patient record'))
        message = 'Hi *%s*, you *appointment* number is: %s , Thank you' % (self.patient_id.name, self.name)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, message)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Done',

                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        action = self.env.ref('om_hospital.action_cancel_appointment').read()[0]
        return action

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = random.randrange(0, 25)
            elif rec.state == 'in_consultation':
                progress = random.randrange(25, 99)
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress


class AppointmentPharmacyLines(models.Model):
    _name = 'appointment.pharmacy.lines'
    _description = 'Appointment Pharmacy Lines'

    product_id = fields.Many2one('product.product', required=True)
    price_unit = fields.Float(related='product_id.lst_price', digits='Product Price', string='Price')
    qty = fields.Integer(string='Quantity', default=1)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')

    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id',
                                  )
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal',
                                     currency_field='currency_id')

    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty

    amount_total = fields.Monetary(string='Subtotal', compute='_compute_amount_total',
                                   currency_field='currency_id')
