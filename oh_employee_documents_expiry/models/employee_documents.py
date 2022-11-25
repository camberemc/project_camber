# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    name = fields.Char(string='Document Number', required=True, copy=False, help='You can give your'
                                                                                 'Document number.')
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    employee_id = fields.Many2one('hr.employee', copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date',  copy=False)
    active = fields.Boolean(default=True)

    document_type_id = fields.Many2one('hr.document.type', string='Document Type')

    alert_date  = fields.Date(string='Alert Date')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].sudo().search([('employee_id', '=', each.id)])
            each.document_count = len(document_ids)

    document_count = fields.Integer(compute='_document_count', string='# Documents')

class HRDocumentType(models.Model):
    _name = 'hr.document.type'

    name = fields.Char(string='Document Type')

