from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.model
    def create(self, vals):
        self.add_followers(vals)
        new_id = super(sale_order, self).create(vals)

        new_id.message_subscribe([x.partner_id.id for x in
                                  new_id.message_follower_ids])

        body = "SO created, please check"
        new_id.send_followers(body)
        new_id.send_to_channel(body)
        return new_id

    #########################################
    # menambah followers di SO
    #########################################
    
    def add_followers(self, vals):
        uid = self.env.uid
        group_ids = self.find_notif_users()
        partner_ids = []
        
        for group in group_ids:
            for user in group.users:
                if user.id != uid:
                    partner_ids.append(user.partner_id.id)
                    
            if partner_ids:
                vals['message_follower_ids'] = [(0, 0, {
                    'res_model': 'sale.order',
                    'partner_id': pid}) for pid in partner_ids]

    #########################################
    # mencari nama2 grup yg hendak di notif
    #########################################
    def find_notif_users(self):
        group_obj = self.env['res.groups']
        group_ids = group_obj.sudo().search([
            ('category_id','=','Sales'),
            ('name', '=', 'Manager')])
        return group_ids

    #########################################
    # send message to followers
    #########################################
    @api.multi
    def send_followers(self, body):
        # to inbox followers and write notes: [10,2,3,21,2]
        followers = [x.partner_id.id for x in
                     self.message_follower_ids]
        self.message_post(body=body,
                          type="notification", subtype="mt_comment",
                          partner_ids=followers,
                          )
    
        return

    #########################################
    # send to channel
    #########################################
    def send_to_channel(self, body):
        ch_obj = self.env['mail.channel']
        ch = ch_obj.sudo().search([('name', 'ilike',
                                    'Budi, Administrator')])
    
        body = body + " <a href='#id=%s&view_type=form&model=sale.order&menu_id=398&action=563'>%s</a>" % (self.id, self.name)
    
        ch.message_post(attachment_ids=[], body=body,
                        content_subtype='html', message_type='comment',
                        partner_ids=[], subtype='mail.mt_comment')
        return True

    @api.multi
    def action_confirm(self):
        ret = super(sale_order, self).action_confirm()
        
        body = "SO confirmed, please check"
        self.send_followers(body)
        self.send_to_channel(body)
        
        return ret