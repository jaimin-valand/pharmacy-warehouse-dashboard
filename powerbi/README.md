# PharmaFlow: Power BI version

A complete Power BI report for a pharmacy warehouse, with data, model, DAX measures and visuals all included. Download it, open it and start exploring. It's free to use for practice while you learn Power BI.

## What you need

- A Windows PC (Power BI Desktop doesn't run on Mac).
- Power BI Desktop, free from the Microsoft Store or the Microsoft website.

## Load and run it from GitHub

1. On the repo's main page, click the green **Code** button, then **Download ZIP**.
   If you use Git, you can run `git clone https://github.com/jaimin-valand/pharmacy-warehouse-dashboard.git` instead.
2. Unzip the download and open the `powerbi` folder. Keep all the files in it together.
3. Open Power BI Desktop. If your version shows them under
   **File > Options and settings > Options > Preview features**, tick
   **Power BI Project (.pbip) save option** and
   **Store reports using enhanced metadata format (PBIR)**, then restart Power BI Desktop.
   Newer versions have these switched on already.
4. Double-click **PharmaFlow.pbip** (or go to **File > Open** and pick it).
5. Click **Refresh** on the Home ribbon. The data is built into the file,
   so there's nothing to connect and no file paths to change.
6. Optional: to get a normal `.pbix` file, go to **File > Save as** and choose
   **Power BI file (*.pbix)**.

## What's inside

- **Data model:** Products, Warehouses, Suppliers, Inventory, Orders and Shipments, plus a Date table, all linked.
- **About 30 DAX measures:** usable stock (expired batches excluded), stock-out risk, cost to restock, expiry value at risk, on-time delivery, inventory turnover, forecast accuracy (1 - WAPE) and network utilisation.
- **Page 1, Overview:** 8 KPI cards, replenishment chart, capacity gauge, expiry exposure, supplier performance, monthly inbound vs outbound.
- **Page 2, Stock & expiry detail:** top moving products, low-stock alerts table, expiry risk table.
- **Slicers:** warehouse, category and date range, synced across both pages.

## Use it for Power BI practice

If you're learning Power BI, this is a good project to take apart and rebuild.

- **Read the DAX:** open the Inventory, Orders and Shipments tables in the Data pane. The measures are grouped into folders and the trickier ones have comments.
- **Explore Power Query:** click **Transform data** to see how each table is loaded, renamed, typed and given extra columns like Days To Expiry and Expiry Risk.
- **Check the model:** open Model view and follow how the tables connect.
- **Rebuild a visual:** delete a chart and recreate it from scratch, then compare it with the original.
- **Write your own measures,** for example:
  - Days of cover: usable stock divided by average daily units moved.
  - Month-on-month change in units moved.
  - Top 5 suppliers by late deliveries.
- **Add a page:** build a supplier scorecard or a warehouse comparison page.
- **Use your own data:** swap in your own CSV files with the same column names and refresh.

All data is synthetic and generated for demonstration.
