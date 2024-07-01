# -*- coding: utf-8 -*-
from dateutil import relativedelta

from odoo import fields, models, api, _
from datetime import date

from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Patient'
    # _rec_name = 'name'
    name = fields.Char(string="Name", tracking=True, default='Odoo Mates')
    date_of_birth = fields.Date(string="Date Of Birth")
    ref = fields.Char(string="Reference")
    age = fields.Integer(string="Age", tracking=True, compute='_compute_age', inverse='_inverse_compute_age',
                         search='_search_age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True, default='male')
    active = fields.Boolean(string="Active", default=True)
    appointment_id = fields.Many2one("hospital.appointment", string="Appointment")
    image = fields.Image(string='Image')
    tag_ids = fields.Many2many('patient.tag', string='Tags')
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count', store=True)
    appointment_ids = fields.One2many("hospital.appointment", "patient_id", string="Appointments")
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection([('married', 'Married'), ('single', 'Single')], string='Marital Status',
                                      tracking=True)
    partner_name = fields.Char(string='Partner Name')
    is_birthday = fields.Boolean(string='Birthday ?', compute='_compute_is_birthday')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        appointment_group = self.env['hospital.appointment'].read_group(domain=[],
                                                                        fields=['patient_id'],
                                                                        groupby=[
                                                                            'patient_id'])  # Nhóm dữ liệu lại theo tiêu chí
        for appointment in appointment_group:  # Lặp qua từng nhóm cuộc hẹn đã được nhóm lại theo patient_id
            patient_id = appointment.get('patient_id')[0]  # Lấy id các bệnh nhân trong nhóm
            patient_rec = self.browse(patient_id)  # Lấy bản ghi bệnh nhân dựa trên id đã lấy đc
            patient_rec.appointment_count = appointment['patient_id_count']  # là số lượng cuộc hẹn hoàn thành cho bệnh nhân đó. Cập nhật trường appointment_count của bản ghi bệnh nhân với giá trị này.
            self -= patient_rec  # Loại bỏ bệnh nhân vừa cập nhật khỏi self. Điều này đảm bảo rằng những bệnh nhân không có cuộc hẹn hoàn thành sẽ được xử lý sau.
        self.appointment_count = 0  # Sau khi vòng lặp kết thúc, self vẫn còn chứa các bệnh nhân không có cuộc hẹn hoàn thành. Thiết lập appointment_count về 0 cho tất cả các bản ghi bệnh nhân còn lại trong self.

        # for rec in self:
        #     rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_('The entered date of birth is not acceptable!'))

    @api.ondelete(at_uninstall=False)
    def _check_appointment(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_('You cannot delete a patient with appointments !'))

    @api.model
    def create(self, vals):
        print("Odoo Mates")
        vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(vals)

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
            print("Write method is triggered")
        return super(HospitalPatient, self).write(vals)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 1

    @api.depends('age')
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)

    def _search_age(self, operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        start_of_year = date_of_birth.replace(day=1, month=1)
        end_of_year = date_of_birth.replace(day=31, month=12)
        return [('date_of_birth', '>=', start_of_year), ('date_of_birth', '<=', end_of_year)]

    def name_get(self):

        return [(record.id, "%s:%s" % (record.ref, record.name)) for record in self]

    def action_done(self):
        print("test")
        return

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True

            rec.is_birthday = is_birthday

    def action_view_appointments(self):
        return {
            'name': _('Appointments'),
            'view_mode': 'list,form,calendar,activity',
            'res_model': 'hospital.appointment',
            'domain': [('patient_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_patient_id': self.id}
        }
