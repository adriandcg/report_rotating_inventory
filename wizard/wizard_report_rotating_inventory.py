# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
import time
from functools import reduce

class WizardReportRotatingInventory(models.TransientModel):
    _name = 'stock.report.rotating.inventory'
    _description = 'Reporte de Inventario Rotativo'


    initial_date = fields.Date('Fecha Inicial', help="Debe seleccionar una fecha inicial", required=True)
    final_date = fields.Date('Fecha Final', help="Debe seleccionar una fecha final", required=True)

    def open_table(self):
        self.ensure_one()

        tree_view_id = self.env.ref('filtro_valoracion_inventario.view_stock_report_rotating_inventory_tree').id
        form_view_id = self.env.ref('filtro_valoracion_inventario.view_stock_report_rotating_inventory_form').id
        action = {
        'type': 'ir.actions.act_window',
        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        'view_mode': 'tree,form',
        'name': _('Inventario Rotativo'),
        'res_model': 'stock.quant',
        'context': {'initial_date': self.initial_date, 'final_date': self.final_date}
        }
        return action

class stock_quant_rotating(models.Model):
    _inherit = 'stock.quant'

    categoria_interna   = fields.Many2one('product.category', string='Categoria interna', related='product_id.product_tmpl_id.categ_id')
    inventario_inicial  = fields.Float(string="Inventario Inicial", compute='_compute_inventario_inicial')
    compras             = fields.Float(string="Compras")
    compras_devolucion  = fields.Float(string="Compras Devolucion")
    ventas              = fields.Float(string="Ventas")
    ventas_devolucion   = fields.Float(string="Ventas Devolucion")
    interno_entrada     = fields.Float(string="Interno Entradas")
    interno_salida      = fields.Float(string="Interno Salidas")
    produccion_entrada  = fields.Float(string="Produccion Entradas")
    produccion_salida   = fields.Float(string="Produccion Salidas")
    traspaso_entrada    = fields.Float(string="Traspaso Entradas")
    traspaso_salida     = fields.Float(string="Traspaso Salidas")
    maquilador_entrada  = fields.Float(string="Maquilador Entradas")
    maquilador_salida   = fields.Float(string="Maquilador Salidas")
    ajustes             = fields.Float(string="Ajustes")
    inventario_final    = fields.Float(string="Inventario Final")
    kgs			        = fields.Float(string="KG")

    @api.one
    @api.depends('product_id', 'location_id', 'lot_id', 'package_id')
    def _compute_inventario_inicial(self):
        cr = self.env.cr
        search_feci = self.env.context.get('initial_date', False)
        search_fecf = self.env.context.get('final_date', False)

        self.inventario_inicial = 0.0
        self.inventario_final = 0.0
        self.kgs = 0.0
        lote = "=" + str(self.lot_id.id) if self.lot_id.id else 'is null'
        paquete = "=" + str(self.package_id.id) if self.package_id.id else 'is null'
        sql_periodo = """SELECT sm.product_uom_qty, sm.location_id, sm.location_dest_id,
                CASE
                    WHEN sm.purchase_line_id is not null THEN 'purchase'
                    WHEN sm.sale_line_id     is not null THEN 'sale'
                    WHEN sm.inventory_id     is not null THEN 'inventary'
                    WHEN sm_sp_spt.code = 'internal' and sm_sl.location_id = sm_sld.location_id THEN 'internal'
                    WHEN sm_sp_spt.code = 'internal' and sm_sl.location_id != sm_sld.location_id THEN (
                        CASE
                            WHEN sm_sl.partner_id is not null or sm_sld.partner_id is not null THEN 'external'
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
                """.format(self.product_id.id, self.location_id.id, lote, paquete, search_feci, search_fecf)
        sql_inicial = """SELECT COALESCE(SUM(CASE 
                            WHEN sm.location_dest_id = {1} THEN sm.product_uom_qty
                            ELSE sm.product_uom_qty * -1
                            END),0)
                        FROM stock_move sm
                        LEFT JOIN stock_move_line sml ON sml.move_id  = sm.id
                        WHERE sm.state  = 'done' AND sm.product_id   = {0} AND (sm.location_dest_id = {1} or sm.location_id = {1})
                        AND sml.lot_id  {2} AND sml.package_id  {3} AND sm.date < '{4}'
                """.format(self.product_id.id, self.location_id.id, lote, paquete, search_feci)
        sql_final = """SELECT COALESCE(SUM(CASE 
                            WHEN sm.location_dest_id = {1} THEN sm.product_uom_qty
                            ELSE sm.product_uom_qty * -1
                            END),0)
                        FROM stock_move sm
                        LEFT JOIN stock_move_line sml ON sml.move_id  = sm.id
                        WHERE sm.state  = 'done' AND sm.product_id   = {0} AND (sm.location_dest_id = {1} or sm.location_id = {1})
                        AND sml.lot_id  {2} AND sml.package_id  {3} AND sm.date <= '{4}'
                """.format(self.product_id.id, self.location_id.id, lote, paquete, search_fecf)
        cr.execute(str(sql_inicial))
        self.inventario_inicial  = max(cr.fetchone())
        cr.execute(str(sql_final))
        self.inventario_final    = max(cr.fetchone())

        if self.inventario_final > 0.0:
            if self.product_id.weight:
                self.kgs = self.inventario_final * self.product_id.weight
        cr.execute(str(sql_periodo))
        filas_periodo = cr.fetchall()

        if(filas_periodo != []):
	        filas_periodo = [{'qty':float(x[0]), 'location_id':int(x[1]), 'location_dest_id':int(x[2]), 'type':str(x[3])} for x in filas_periodo]
            #filas_periodo = list(map(lambda x: {'qty':float(x[0]), 'location_id':int(x[1]), 'location_dest_id':int(x[2]), 'type':str(x[3])}, filas_periodo))
        self.compras             = self.sumFilter(filas_periodo, self.location_id.id, move_type='purchase', location_dest=True)
        self.compras_devolucion  = self.sumFilter(filas_periodo, self.location_id.id, move_type='purchase')
        self.ventas              = self.sumFilter(filas_periodo, self.location_id.id, move_type='sale')
        self.ventas_devolucion   = self.sumFilter(filas_periodo, self.location_id.id, move_type='sale',     location_dest=True)
        self.interno_entrada     = self.sumFilter(filas_periodo, self.location_id.id, move_type='internal', location_dest=True)
        self.interno_salida      = self.sumFilter(filas_periodo, self.location_id.id, move_type='internal')
        self.produccion_entrada  = self.sumFilter(filas_periodo, self.location_id.id, move_type='mrp_operation', location_dest=True)
        self.produccion_salida   = self.sumFilter(filas_periodo, self.location_id.id, move_type='mrp_operation')
        self.traspaso_entrada    = self.sumFilter(filas_periodo, self.location_id.id, move_type='transfer', location_dest=True)
        self.traspaso_salida     = self.sumFilter(filas_periodo, self.location_id.id, move_type='transfer')
        self.maquilador_entrada  = self.sumFilter(filas_periodo, self.location_id.id, move_type='external', location_dest=True)
        self.maquilador_salida   = self.sumFilter(filas_periodo, self.location_id.id, move_type='external')
        self.ajustes             = self.sumFilter(filas_periodo, self.location_id.id, move_type='inventary', location_dest=True) - self.sumFilter(filas_periodo, self.location_id.id, move_type='inventary')

    def sumFilter(self, moves, location, location_dest=False, move_type=False):
        location_type = "location_dest_id" if location_dest else "location_id"
        if(moves != []):
            #Filtra todos los movimientos donde la location origen/destino sea la indicada
            moves = [x for x in moves if x[location_type] == location]
            #aplica filtro por move_type si el valor esta asignado
            if move_type and moves:
                moves = [x for x in moves if x['type'] == move_type]
            #obtiene todas las cantidades de los data data_filtered
            if moves:
                qtys = [x['qty'] for x in moves]
                return reduce(lambda x, y: x + y, qtys) if len(qtys) > 1 else qtys[0]
        return 0.0
