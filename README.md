# report_rotating_inventory
## Reporte de inventario rotativo para Odoo

Genera dentro del modulo de Almacenes de Odoo v11 un reporte que permite filtra mediante un periodo(**_Fecha Inicial_** y **_Fecha Final_**) las existencias que tiene cada ubicación (basado en stock.quant y stock.move), mostrando los siguientes datos:

**Producto**: Es el nombre del producto en formato *[REFERENCIA] NOMBRE*.
**Categoria**: Es la categoria interna asignada al producto en formato *ALL/CATEGORIA*.
**Ubicación**: Es el lugar en el cual se encuentran las existencias del producto en formato *Almacén/Ubicación*.
**Lote/Num Serie**: Puede contener el número de seguimiento que se le asigno al conjunto de producto.
**Paquete**: Es el número de secuenta que odoo asigna a varios productos cuando se ejecuta el empaquetado.
**Inicial**: Es la suma de todos los ingresos menos los egresos antes de la **_Fecha inicial_**.
**Compras**: Es la suma de todos los movimientos de ingreso generados por compra en el periodo.
**Compras Dev**: Es la suma de todos los movimientos de devolución(egreso) correspondientes a la compra en el periodo.
**Ventas**: Es la suma de todos los movimientos de egreso generados por venta en el periodo.
**Ventas Dev**: Es la suma de todos los movimientos de devolución(ingreso) correspondientes a la venta en el periodo.
**Interno Entrada**: Es la suma de todos los ingresos correspondientes a los movimientos entre ubicaciones del mismo almacen en el periodo.
**Interno Salida**: Es la suma de todos los egresos correspondientes a los movimientos entre ubicaciones del mismo almacen en el periodo.
**Traspaso Entrada**: Es la suma de todos los ingresos correspondientes a los movimientos entre ubicaciones de diferentes almacenes en el periodo.
**Traspaso Salida**: Es la suma de todos los egresos correspondientes a los movimientos entre ubicaciones de diferentes almacenes en el periodo.
**Maquilador Entrada**: Es la suma de todos los ingresos en el periodo hechos desde una ubicación que tienen asignado un propietaro.
**Maquilador Salida**: Es la suma de todos los egresos en el periodo hechos desde una ubicación que tienen asignado un propietaro.
**Ajustes**: Es la suma de todos los ingresos menos los egresos correspondientes a movimientos de ajuste de inventario en el periodo.
**Final**: Es la suma de todos los ingresos menos los egresos con fecha menor o igual a la **_Fecha Final_**.
**KG**: Es el total de Kilogramos del producto según las cantidades calculadas en el campo Final
