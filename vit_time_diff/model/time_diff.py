from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class time_diff(models.Model):
    _name = 'vit.time_diff'

    depart = fields.Datetime(string="Departure", required=False, )
    arrive = fields.Datetime(string="Arrival", required=False, )
    time_diff  = fields.Char(string="Time Diff", required=False, compute='_calc_time')
    
    @api.depends('depart','arrive')
    def _calc_time(self):
        for rec in self:
            depart_obj = datetime.strptime(rec.depart, "%Y-%m-%d %H:%M:%S")
            arrive_obj = datetime.strptime(rec.arrive, "%Y-%m-%d %H:%M:%S")
    
            delta = arrive_obj - depart_obj
            
            seconds = delta.total_seconds()
            d = divmod(seconds, 86400)  # kalau seconds=100000 => (1, 13600)
            _logger.warning(d)
            
            h = divmod(d[1], 3600)  # hours (1, 1200)
            _logger.warning(h)
            
            m = divmod(h[1], 60)  # minutes
            _logger.warning(m)

            if d[0] > 0:
                ret = "%sd %sh %sm" % (int(d[0]), int(h[0]), int(m[0]))
            else:
                ret = "%sh %sm" % (int(h[0]), int(m[0]))

            rec.time_diff = ret
        