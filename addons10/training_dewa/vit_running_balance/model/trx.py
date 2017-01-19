from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class trx(models.Model):
    _name = 'vit.trx'
    _rec_name = 'name'
    _order = 'id asc'
    
    name    = fields.Char("Description")
    date    = fields.Datetime(string="Date", )
    debit   = fields.Float(string="Debit", )
    credit  = fields.Float(string="Credit", )
    balance = fields.Float(compute='_get_balance',
                           string="Balance", required=False)
    
    user_id = fields.Many2one(comodel_name="res.users",
                              string="Owner", required=False,
                              default=lambda self: self.env.user.id )
    
    @api.depends('debit', 'credit')
    def _get_balance(self):
        for record in self.sorted(lambda x: x.id):
            prev = self.search_read([('id', '<', record.id)],
                                    limit=1, order='date desc')
            prev_balance = prev[0]['balance'] if prev else 0
            record.balance = prev_balance + record.debit - record.credit

