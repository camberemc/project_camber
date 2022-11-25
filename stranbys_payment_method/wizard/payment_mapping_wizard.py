from datetime import datetime
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime as dt


class PaymentMapping(models.TransientModel):
    _name = 'account.invoice.matching.wizard'
    _description = 'Payment Mapping'


    move_type = fields.Char('Move Type')
    state = fields.Char('state')
    move_line_ids = fields.Many2many('account.move.line', string='Invoices')
    move_id = fields.Many2one('account.move', string='Move')
    move_line_id = fields.Many2one('account.move.line', string='Move Line')
    date = fields.Date('Date', default= lambda self : dt.date.today())

    def action_vaidate(self):
        date = self.date
        move_line_ids = self.move_line_ids.filtered(
            lambda r: r.payment_selection_ok).sorted(key=lambda r: r.date, reverse = False)
        matching_line_ids = []
        for line in move_line_ids:
            matching_line_ids.append((0,0,{
                'date' : date,
                'amount' : line.allocated_amount,
                'move_line_id' : line.id,
            }))

        vals = {
                'date' : date,
                'amount' : sum(move_line_ids.mapped('allocated_amount')),
                'move_line_id' : self.move_line_id.id,
                'invoice_matching' : True,
                'matching_line_ids' : matching_line_ids
            }

        self.env['account.payment.matching.line'].create(vals)
        move_line_ids.write({
            'payment_selection_ok' : False,
            'allocated_amount' : 0
        })

            
        

            # payment_matching_ids.append((0,0, {
            #     'date' : fields.Date.today(),
            #     'amount' : amount,
            #     'move_id' : inv.id
            # }))
            # amount_residual -= amount

            
            
        # self.move_id.write({
        #     'ch_move_ids' : payment_matching_ids
        # })
        # invoice_ids.write({'payment_selection_ok' : False})