# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
import time
from functools import reduce

class WizardReportRotatingInventory(models.TransientModel):
    _name = 'report.rotating.inventory'
    _description = 'Report Rotating Inventory'

    
    company_id = fields.Many2one("res.company", string="Company")
    initial_date = fields.Date('Initial', help="You should specify a initial date", required=True)
    final_date = fields.Date('Final', help="You should specify a final date", required=True)
    category_id = fields.Many2one("product.category",string="Category")
    location_id = fields.Many2one("stock.location", string="Location")

    def open_table(self):
        self.ensure_one()

        tree_view_id = self.env.ref('report_rotating_inventory.view_report_rotating_inventory_tree').id
        form_view_id = self.env.ref('report_rotating_inventory.view_report_rotating_inventory_form').id
        action = {
        'type': 'ir.actions.act_window',
        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        'view_mode': 'tree,form',
        'name': _('Rotating Inventory'),
        'res_model': 'stock.quant',
        'context': {'initial_date': self.initial_date, 'final_date': self.final_date}
        }
        action = self.getDomain({'company_id': self.company_id, 'location_id': self.location_id, 'product_id.product_tmpl_id.categ_id': self.category_id}, action)
        return action
    
    def getDomain(self, fields, action):
        domains = [(k, '=',v.id) for k,v in fields.items() if v]
        if domains:
            action['domain'] = domains
        return action

class stock_quant_rotating(models.Model):
    _inherit = 'stock.quant'

    category            = fields.Many2one('product.category', string='Category', related='product_id.product_tmpl_id.categ_id')
    initial             = fields.Float(string="Initial", compute='_compute_initial')
    purchase            = fields.Float(string="Purchase")
    purchase_refund     = fields.Float(string="purchase Dev.")
    sale                = fields.Float(string="Sale")
    sale_refund         = fields.Float(string="Sale Refund")
    internal_in     = fields.Float(string="Internal In")
    internal_out      = fields.Float(string="Internal Out")
    mrp_in  = fields.Float(string="MRP In")
    mrp_out   = fields.Float(string="MRP Out")
    transfer_in    = fields.Float(string="Transfer In")
    transfer_out     = fields.Float(string="Transfer Out")
    consignment_in  = fields.Float(string="Consignment In")
    consignment_out   = fields.Float(string="Consignment Out")
    adjust             = fields.Float(string="adjust")
    final               = fields.Float(string="Final")
    kgs			        = fields.Float(string="KG")

    @api.one
    @api.depends('product_id', 'location_id', 'lot_id', 'package_id')
    def _compute_initial(self):
        cr = self.env.cr
        initial_date = self.env.context.get('initial_date', False)
        final_date = self.env.context.get('final_date', False)

        self.initial = 0.0
        self.final = 0.0
        self.kgs = 0.0
        lot_id = "=" + str(self.lot_id.id) if self.lot_id.id else 'is null'
        package_id = "=" + str(self.package_id.id) if self.package_id.id else 'is null'
        sql_range = """SELECT sm.product_uom_qty, sm.location_id, sm.location_dest_id,
                CASE
                    WHEN sm.purchase_line_id is not null THEN 'purchase'
                    WHEN sm.sale_line_id     is not null THEN 'sale'
                    WHEN sm.inventory_id     is not null THEN 'inventary'
                    WHEN sm_sp_spt.code = 'internal' and sm_sl.location_id = sm_sld.location_id THEN 'internal'
                    WHEN sm_sp_spt.code = 'internal' and sm_sl.location_id != sm_sld.location_id THEN (
                        CASE
                            WHEN sm_sl.partner_id is not null or sm_sld.partner_id is not null THEN 'consignment'
                            ELSE 'transfer'
                        END
                    )
                    WHEN sm_sp_spt.code = 'incoming' THEN 'purchase'
                    WHEN sm_sp_spt.code = 'outgoing' and pt.sale_ok = true THEN 'sale'
                    WHEN sm_sp_spt.code = 'outgoing' and pt.purchase_ok = true THEN 'purchase'
                    ELSE sm_sp_spt.code
                END as move_type
                FROM stock_move sm
                LEFT JOIN stock_location sm_sl         ON sm_sl.id     = sm.location_id
                LEFT JOIN stock_location sm_sld        ON sm_sld.id    = sm.location_dest_id
                LEFT JOIN stock_picking sm_sp          ON sm_sp.id     = sm.picking_id
                LEFT JOIN stock_picking_type sm_sp_spt ON sm_sp_spt.id = sm_sp.picking_type_id
                LEFT JOIN product_product pp           ON pp.id        = sm.product_id
                LEFT JOIN product_template pt          ON pt.id        = pp.product_tmpl_id
                LEFT JOIN stock_move_line sml          ON sml.move_id  = sm.id
                WHERE sm.state = 'done' AND sm.product_id = {0} AND (sm.location_id = {1} or sm.location_dest_id = {1})
                AND sml.lot_id {2} AND sml.package_id {3} AND sm.date BETWEEN '{4}' AND '{5}'
                """.format(self.product_id.id, self.location_id.id, lot_id, package_id, initial_date, final_date)
        sql_initial = """SELECT COALESCE(SUM(CASE 
                            WHEN sm.location_dest_id = {1} THEN sm.product_uom_qty
                            ELSE sm.product_uom_qty * -1
                            END),0)
                        FROM stock_move sm
                        LEFT JOIN stock_move_line sml ON sml.move_id  = sm.id
                        WHERE sm.state  = 'done' AND sm.product_id   = {0} AND (sm.location_dest_id = {1} or sm.location_id = {1})
                        AND sml.lot_id  {2} AND sml.package_id  {3} AND sm.date < '{4}'
                """.format(self.product_id.id, self.location_id.id, lot_id, package_id, initial_date)
        sql_final = """SELECT COALESCE(SUM(CASE 
                            WHEN sm.location_dest_id = {1} THEN sm.product_uom_qty
                            ELSE sm.product_uom_qty * -1
                            END),0)
                        FROM stock_move sm
                        LEFT JOIN stock_move_line sml ON sml.move_id  = sm.id
                        WHERE sm.state  = 'done' AND sm.product_id   = {0} AND (sm.location_dest_id = {1} or sm.location_id = {1})
                        AND sml.lot_id  {2} AND sml.package_id  {3} AND sm.date <= '{4}'
                """.format(self.product_id.id, self.location_id.id, lot_id, package_id, final_date)
        cr.execute(str(sql_initial))
        self.initial  = max(cr.fetchone())
        cr.execute(str(sql_final))
        self.final    = max(cr.fetchone())

        if self.final > 0.0:
            if self.product_id.weight:
                self.kgs = self.final * self.product_id.weight
        cr.execute(str(sql_range))
        range_moves = cr.fetchall()

        if(range_moves != []):
	        range_moves = [{'qty':float(x[0]), 'location_id':int(x[1]), 'location_dest_id':int(x[2]), 'type':str(x[3])} for x in range_moves]
        self.purchase             = self.sumFilter(range_moves, self.location_id.id, move_type='purchase', location_dest=True)
        self.purchase_refund  = self.sumFilter(range_moves, self.location_id.id, move_type='purchase')
        self.sale              = self.sumFilter(range_moves, self.location_id.id, move_type='sale')
        self.sale_refund   = self.sumFilter(range_moves, self.location_id.id, move_type='sale',     location_dest=True)
        self.internal_in     = self.sumFilter(range_moves, self.location_id.id, move_type='internal', location_dest=True)
        self.internal_out      = self.sumFilter(range_moves, self.location_id.id, move_type='internal')
        self.mrp_in  = self.sumFilter(range_moves, self.location_id.id, move_type='mrp_operation', location_dest=True)
        self.mrp_out   = self.sumFilter(range_moves, self.location_id.id, move_type='mrp_operation')
        self.transfer_in    = self.sumFilter(range_moves, self.location_id.id, move_type='transfer', location_dest=True)
        self.transfer_out     = self.sumFilter(range_moves, self.location_id.id, move_type='transfer')
        self.consignment_in  = self.sumFilter(range_moves, self.location_id.id, move_type='consignment', location_dest=True)
        self.consignment_out   = self.sumFilter(range_moves, self.location_id.id, move_type='consignment')
        self.adjust             = self.sumFilter(range_moves, self.location_id.id, move_type='inventary', location_dest=True) - self.sumFilter(range_moves, self.location_id.id, move_type='inventary')

    def sumFilter(self, moves, location, location_dest=False, move_type=False):
        location_type = "location_dest_id" if location_dest else "location_id"
        if(moves != []):
            moves = [x for x in moves if x[location_type] == location]
            if move_type and moves:
                moves = [x for x in moves if x['type'] == move_type]
            if moves:
                qtys = [x['qty'] for x in moves]
                return reduce(lambda x, y: x + y, qtys) if len(qtys) > 1 else qtys[0]
        return 0.0
