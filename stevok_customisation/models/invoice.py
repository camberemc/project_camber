from odoo import api, fields, models, _
from datetime import datetime, date
import csv
import base64
import logging
import io
from datetime import date, datetime, timedelta
# import datetime
from odoo.exceptions import Warning, UserError

_logger = logging.getLogger(__name__)


class AccountMoveExtend(models.Model):
    _inherit = "account.move"

    file_to_upload = fields.Binary('File')
    bank_details = fields.Text(string="Bank Details",
                               default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                   'stevok_erp.bank_details'))

    def get_csv_partner_id(self, customer_name):
        partner_id = self.env['res.partner'].search([('name', '=', customer_name)], limit=1)
        if partner_id:
            return partner_id.id
        # return self.env['res.partner'].create({
        #     'name': customer_name
        # }).id

    def get_csv_user_id(self, user):
        user_id = self.env['res.users'].search([('id', '=', user)])
        return user_id.id

    def get_csv_product_id(self, product_name):
        product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
        if product_id:
            return product_id.id
        return self.env['product.product'].create({
            'name': product_name,
        }).id

    def get_csv_account_id(self, account):
        account_id = self.env['account.account'].search([('code', '=', account)], limit=1)
        if account_id:
            return account_id.id
        else:
            raise UserError(_("There is no account"))

    def create_invoice(self, values):
        invoice_object = self.env['account.move']
        if values.get('date'):
            date = values.get('date')
            customer_name = values.get('customer_name')
            account = values.get('account')
            product_name = values.get('product_name')
            amount = values.get('amount')
            vat = values.get('vat')
            type = values.get('type')
            user = values.get('user')
            # print(asgda)

            invoice_line_ids = [(0, 0, {
                # 'product_id': self.get_csv_product_id(product_name),
                'name': product_name,
                'quantity': 1,
                'price_unit': amount,
                'tax_ids': [(6, 0, [1])] if vat else False,
                'account_id': self.get_csv_account_id(account),

            })]

            if values.get('ref'):
                name = values.get('ref')
            else:
                if type == 'out_invoice':
                    name = 'HECQINS' + self.env['ir.sequence'].next_by_code('old.invoice')
                elif type == 'in_invoice':
                    name = 'BILL' + self.env['ir.sequence'].next_by_code('old.bill')

            vals = {
                'partner_id': self.get_csv_partner_id(customer_name),
                'date': date,
                'invoice_date': date,
                'name': name,
                'move_type': type,
                'user_id': self.get_csv_user_id(user),
                'invoice_line_ids': invoice_line_ids,

            }
            invoice_id = invoice_object.create(vals)
            # invoice_id.action_post()
            # payment_id = self.env['account.payment.register'].with_context(
            #     {'active_ids': invoice_id.ids,
            #      'active_model': 'account.move'}).create({
            #     'payment_date': date
            # })
            # payment_id.action_create_payments()

    def invoice_xls(self):
        if self.file_to_upload:
            keys = ['date', 'customer_name', 'account', 'product_name', 'amount', 'vat', 'ref', 'type', 'user']
            csv_data = base64.b64decode(self.file_to_upload)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0),
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
            # except Exception:
            #     raise exceptions.Warning(_("Invalid file!"))
            values = {}
            lines = []
            for i in range(len(file_reader)):
                field = map(str, file_reader[i])
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        self.create_invoice(values)
        else:
            raise UserError(_("There is no File"))
