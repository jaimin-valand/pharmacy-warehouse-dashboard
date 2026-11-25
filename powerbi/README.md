# PharmaFlow: Power BI version

Needs: Windows with Power BI Desktop (free from the Microsoft Store).
Power BI Desktop does not run on a Mac.

## How to open
1. Download or clone this repo. Keep everything in this `powerbi` folder together.
2. Open Power BI Desktop. Go to File > Options and settings > Options >
   Preview features, tick "Power BI Project (.pbip) save option", click OK
   and restart Power BI Desktop. If you see that option, also tick
   "Store reports using enhanced metadata format (PBIR)". On newer
   versions these are already switched on and may not be listed.
3. Double-click PharmaFlow.pbip (or File > Open > PharmaFlow.pbip).
4. Click Refresh on the Home ribbon. The data is built into the file,
   so there is nothing to connect and no file paths to change.

## Save as a normal .pbix file
   File > Save as > choose "Power BI file (*.pbix)".

## What's inside
- 6 tables (Products, Warehouses, Suppliers, Inventory, Orders, Shipments)
  plus a Date table, all linked.
- 30 DAX measures matching the Python dashboard, including usable stock
  (expired batches excluded), stock-out risk, cost to restock, expiry
  value at risk, on-time delivery, inventory turnover, forecast accuracy
  (1 - WAPE) and network utilisation.
- Page 1 "Overview": 8 KPI cards, replenishment chart, capacity gauge,
  expiry exposure, supplier performance, monthly inbound vs outbound.
- Page 2 "Stock & expiry detail": top moving products, low-stock alerts
  table, expiry risk table.
- Slicers for warehouse, category and date range, synced across pages.

All data is synthetic and generated for demonstration.
