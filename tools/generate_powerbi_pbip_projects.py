"""Generate local PBIP Power BI projects for the portfolio dashboards.

The generated projects are thick PBIP packages: each contains a report folder
and a local SemanticModel folder. Power BI Desktop can open the .pbip files and
save them as .pbix when a binary deliverable is required.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import stat
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[1]
PBIR = pathlib.Path(os.environ["APPDATA"]) / "Python" / "Python314" / "Scripts" / "pbir.exe"
MODEL_COLUMNS = {
    "lines.line_id",
    "lines.line_name",
    "lines.area",
    "lines.target_units_per_hour",
    "production_log.log_id",
    "production_log.line_id",
    "production_log.production_date",
    "production_log.planned_minutes",
    "production_log.downtime_minutes",
    "production_log.downtime_reason",
    "production_log.units_produced",
    "production_log.units_defective",
    "monthly_costs.cost_id",
    "monthly_costs.line_id",
    "monthly_costs.cost_month",
    "monthly_costs.cost_type",
    "monthly_costs.amount",
    "products.product_id",
    "products.product_name",
    "products.category",
    "products.supplier_id",
    "products.unit_cost",
    "products.reorder_point",
    "products.order_quantity",
    "suppliers.supplier_id",
    "suppliers.supplier_name",
    "suppliers.region",
    "suppliers.nominal_lead_time_days",
    "inventory_snapshots.product_id",
    "inventory_snapshots.snapshot_date",
    "inventory_snapshots.stock_on_hand",
    "inventory_snapshots.stockout",
    "purchase_orders.po_id",
    "purchase_orders.product_id",
    "purchase_orders.supplier_id",
    "purchase_orders.order_date",
    "purchase_orders.expected_delivery_date",
    "purchase_orders.actual_delivery_date",
    "purchase_orders.quantity_ordered",
}


@dataclass(frozen=True)
class Visual:
    visual_type: str
    page: str
    name: str
    title: str
    x: int
    y: int
    width: int
    height: int
    data: tuple[str, ...]


def run(args: list[str], cwd: pathlib.Path) -> None:
    result = subprocess.run(
        [str(PBIR), "--rawdog", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    if result.returncode:
        raise RuntimeError(f"pbir {' '.join(args)} failed:\n{result.stdout}")


def write_json(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def m_csv(path: pathlib.Path) -> str:
    safe = path.resolve().as_posix()
    return (
        "let\n"
        f"    Source = Csv.Document(File.Contents(\"{safe}\"),"
        "[Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n"
        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "in\n"
        "    PromotedHeaders"
    )


def build_table_tmdl(
    name: str,
    columns: list[tuple[str, str]],
    source_path: pathlib.Path,
    measures: list[tuple[str, str, str | None]] | None = None,
) -> str:
    lines = [
        f"table {name}",
        "\tlineageTag: " + os.urandom(16).hex(),
        "",
        "\tpartition " + name + " = m",
        "\t\tmode: import",
        "\t\tsource =",
    ]
    for expression_line in m_csv(source_path).splitlines():
        lines.append("\t\t\t\t" + expression_line)
    lines.append("")
    for column_name, data_type in columns:
        lines.extend(
            [
                f"\tcolumn {column_name}",
                f"\t\tdataType: {data_type}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {column_name}",
                "",
            ]
        )
    for measure_name, expression, fmt in measures or []:
        lines.append(f"\tmeasure '{measure_name}' = {expression}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_semantic_model(project_dir: pathlib.Path, model_name: str, tables: dict[str, str], relationships: list[str]) -> pathlib.Path:
    model_dir = project_dir / f"{model_name}.SemanticModel"
    definition = model_dir / "definition"
    tables_dir = definition / "tables"
    tables_dir.mkdir(parents=True)
    write_json(
        model_dir / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {},
        },
    )
    write_json(
        model_dir / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {
                "type": "SemanticModel",
                "displayName": model_name,
            },
            "config": {
                "version": "2.0",
                "logicalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"powerbi-semantic-model:{model_name}")),
            },
        },
    )
    (definition / "database.tmdl").write_text(f"database {model_name}\n\tcompatibilityLevel: 1600\n", encoding="utf-8")
    model_lines = ["model Model", "\tculture: en-US", "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", ""]
    model_lines.extend(relationships)
    (definition / "model.tmdl").write_text("\n".join(model_lines).rstrip() + "\n", encoding="utf-8")
    for name, content in tables.items():
        (tables_dir / f"{name}.tmdl").write_text(content, encoding="utf-8")
    return model_dir


def create_report_shell(project_dir: pathlib.Path, report_name: str, model_name: str) -> pathlib.Path:
    run(["new", "report", f"{report_name}.Report", "--thick", "--no-title"], project_dir)
    report = project_dir / f"{report_name}.Report"
    write_json(
        report / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {
                "byConnection": {
                    "connectionString": (
                        'Data Source="powerbi://api.powerbi.com/v1.0/myorg/LocalWorkspace";'
                        f'initial catalog="{model_name}";access mode=readonly;'
                        "integrated security=ClaimsToken;semanticmodelid=00000000-0000-0000-0000-000000000000"
                    )
                }
            },
        },
    )
    return report


def add_pages_and_visuals(project_dir: pathlib.Path, report_name: str, pages: list[str], visuals: list[Visual]) -> None:
    run(["pages", "rename", f"{report_name}.Report/Page 1.Page", "--to", pages[0], "-f"], project_dir)
    for page in pages[1:]:
        run(["add", "page", f"{report_name}.Report/{page}.Page", "-n", page, "--width", "1280", "--height", "720"], project_dir)
    run(
        [
            "theme",
            "set-colors",
            f"{report_name}.Report",
            "--background",
            "#F4F6F8",
            "--accent",
            "#1F4E79",
            "--good",
            "#2B7A78",
            "--bad",
            "#D4602E",
            "--neutral",
            "#B9C3CF",
            "--data-colors",
            '["#1F4E79","#2B7A78","#D4602E","#B9C3CF","#6C7A89"]',
        ],
        project_dir,
    )
    for visual in visuals:
        args = [
            "add",
            "visual",
            visual.visual_type,
            f"{report_name}.Report/{visual.page}.Page",
            "--name",
            visual.name,
            "--title",
            visual.title,
            "--x",
            str(visual.x),
            "--y",
            str(visual.y),
            "--width",
            str(visual.width),
            "--height",
            str(visual.height),
            "--force",
        ]
        for binding in visual.data:
            pass
        run(args, project_dir)
        if visual.data:
            for binding in visual.data:
                field = binding.split(":", 1)[1]
                field_type = "Column" if field in MODEL_COLUMNS else "Measure"
                run(
                    [
                        "visuals",
                        "bind",
                        f"{report_name}.Report/{visual.page}.Page/{visual.name}.Visual",
                        "--no-validate",
                        "--type",
                        field_type,
                        "-a",
                        binding,
                    ],
                    project_dir,
                )
    run(["validate", f"{report_name}.Report", "--all"], project_dir)


def merge_thick(project_dir: pathlib.Path, report_name: str, model_name: str, destination: pathlib.Path) -> None:
    if destination.exists():
        def reset_permissions(function, path, _exc_info):
            os.chmod(path, stat.S_IWRITE)
            function(path)

        shutil.rmtree(destination, onexc=reset_permissions)
    run(["report", "merge-to-thick", f"{report_name}.Report", f"{model_name}.SemanticModel", "-o", str(destination)], project_dir)
    pbip_path = destination / f"{report_name}.pbip"
    # Keep the PBIP launcher in the minimal format produced by pbi-cli and
    # accepted by Power BI Desktop Store. The local model is referenced from
    # definition.pbir via datasetReference.byPath.
    write_json(
        pbip_path,
        {
            "version": "1.0",
            "artifacts": [{"report": {"path": f"{report_name}.Report"}}],
        },
    )


def build_industry() -> None:
    project = ROOT / "industry_operations_cost"
    out = project / "powerbi" / "industry_operations_cost_pbip"
    work = pathlib.Path(tempfile.gettempdir()) / f"industry_pbip_{int(time.time())}"
    work.mkdir()
    data = project / "python" / "data" / "processed"
    tables = {
        "lines": build_table_tmdl(
            "lines",
            [("line_id", "int64"), ("line_name", "string"), ("area", "string"), ("target_units_per_hour", "int64")],
            data / "lines_clean.csv",
        ),
        "production_log": build_table_tmdl(
            "production_log",
            [
                ("log_id", "int64"),
                ("line_id", "int64"),
                ("production_date", "dateTime"),
                ("planned_minutes", "int64"),
                ("downtime_minutes", "int64"),
                ("downtime_reason", "string"),
                ("units_produced", "int64"),
                ("units_defective", "int64"),
            ],
            data / "production_log_clean.csv",
            [
                ("Total Units", "SUM(production_log[units_produced])", "#,0"),
                ("Total Defects", "SUM(production_log[units_defective])", "#,0"),
                ("Good Units", "[Total Units] - [Total Defects]", "#,0"),
                ("Planned Minutes", "SUM(production_log[planned_minutes])", "#,0"),
                ("Downtime Minutes", "SUM(production_log[downtime_minutes])", "#,0"),
                ("Runtime Minutes", "[Planned Minutes] - [Downtime Minutes]", "#,0"),
                ("Downtime Rate %", "DIVIDE([Downtime Minutes], [Planned Minutes])", "0.0%"),
                ("Availability %", "DIVIDE([Runtime Minutes], [Planned Minutes])", "0.0%"),
                ("Quality %", "DIVIDE([Total Units] - [Total Defects], [Total Units])", "0.0%"),
                ("Defect Rate %", "DIVIDE([Total Defects], [Total Units])", "0.0%"),
                (
                    "Theoretical Units",
                    "SUMX(production_log, DIVIDE(production_log[planned_minutes] - production_log[downtime_minutes], 60) * RELATED(lines[target_units_per_hour]))",
                    "#,0",
                ),
                ("Performance %", "DIVIDE([Total Units], [Theoretical Units])", "0.0%"),
                ("OEE %", "[Availability %] * [Performance %] * [Quality %]", "0.0%"),
                ("OEE Target", "0.85", "0.0%"),
                ("OEE Gap", "[OEE %] - [OEE Target]", "0.0%"),
                ("OEE Gap Label", 'FORMAT([OEE Gap], "+0.0%;-0.0%") & " vs 85% target"', None),
                ("Lines Below OEE Target", "COUNTROWS(FILTER(VALUES(lines[line_name]), [OEE %] < [OEE Target]))", "#,0"),
                ("Worst OEE Line", "CONCATENATEX(TOPN(1, VALUES(lines[line_name]), [OEE %], ASC), lines[line_name], \", \")", None),
                ("Top Downtime Reason", "CONCATENATEX(TOPN(1, VALUES(production_log[downtime_reason]), [Downtime Minutes], DESC), production_log[downtime_reason], \", \")", None),
                ("Line 3 Availability", "CALCULATE([Availability %], lines[line_name] = \"Line 3\")", "0.0%"),
                ("Line 3 Performance", "CALCULATE([Performance %], lines[line_name] = \"Line 3\")", "0.0%"),
                ("Line 3 Quality", "CALCULATE([Quality %], lines[line_name] = \"Line 3\")", "0.0%"),
            ],
        ),
        "monthly_costs": build_table_tmdl(
            "monthly_costs",
            [("cost_id", "int64"), ("line_id", "int64"), ("cost_month", "string"), ("cost_type", "string"), ("amount", "decimal")],
            data / "monthly_costs_clean.csv",
            [
                ("Total Cost", "SUM(monthly_costs[amount])", "$#,0"),
                ("Cost per Unit", "DIVIDE([Total Cost], [Total Units])", "$0.00"),
                ("Materials Cost", "CALCULATE([Total Cost], monthly_costs[cost_type] = \"Materials\")", "$#,0"),
                ("Materials Share %", "DIVIDE([Materials Cost], [Total Cost])", "0.0%"),
                ("Maintenance Cost", "CALCULATE([Total Cost], monthly_costs[cost_type] = \"Maintenance\")", "$#,0"),
                ("Maintenance Share %", "DIVIDE([Maintenance Cost], [Total Cost])", "0.0%"),
                ("Highest Cost Type", "CONCATENATEX(TOPN(1, VALUES(monthly_costs[cost_type]), [Total Cost], DESC), monthly_costs[cost_type], \", \")", None),
            ],
        ),
    }
    relationships = [
        "\trelationship production_log_line_id_lines_line_id\n\t\tfromColumn: production_log.line_id\n\t\ttoColumn: lines.line_id",
        "\trelationship monthly_costs_line_id_lines_line_id\n\t\tfromColumn: monthly_costs.line_id\n\t\ttoColumn: lines.line_id",
    ]
    write_semantic_model(work, "IndustryOperationsCost", tables, relationships)
    create_report_shell(work, "IndustryOperationsCost", "IndustryOperationsCost")
    visuals = [
        Visual("slicer", "Overview", "line_slicer", "Line", 1016, 24, 240, 48, ("Values:lines.line_name",)),
        Visual("card", "Overview", "oee_card", "OEE %", 24, 88, 296, 120, ("Values:production_log.OEE %",)),
        Visual("card", "Overview", "availability_card", "Availability %", 336, 88, 296, 120, ("Values:production_log.Availability %",)),
        Visual("card", "Overview", "performance_card", "Performance %", 648, 88, 296, 120, ("Values:production_log.Performance %",)),
        Visual("card", "Overview", "below_target_card", "Lines Below Target", 960, 88, 296, 120, ("Values:production_log.Lines Below OEE Target",)),
        Visual("lineChart", "Overview", "downtime_trend", "Downtime by Date", 24, 224, 600, 232, ("Category:production_log.production_date", "Y:production_log.Downtime Minutes")),
        Visual("barChart", "Overview", "oee_by_line", "OEE by Line", 648, 224, 296, 232, ("Category:lines.line_name", "Y:production_log.OEE %")),
        Visual("columnChart", "Overview", "units_by_line", "Units by Line", 960, 224, 296, 232, ("Category:lines.line_name", "Y:production_log.Total Units")),
        Visual("tableEx", "Overview", "overview_detail", "Operating Detail", 24, 472, 1232, 200, ("Values:lines.line_name", "Values:production_log.OEE %", "Values:production_log.OEE Gap", "Values:production_log.Downtime Rate %", "Values:production_log.Defect Rate %", "Values:production_log.Total Units")),
        Visual("slicer", "OEE Breakdown", "line_slicer_oee", "Line", 1016, 24, 240, 48, ("Values:lines.line_name",)),
        Visual("card", "OEE Breakdown", "worst_line", "Worst OEE Line", 24, 88, 296, 120, ("Values:production_log.Worst OEE Line",)),
        Visual("card", "OEE Breakdown", "line3_availability", "Line 3 Availability", 336, 88, 296, 120, ("Values:production_log.Line 3 Availability",)),
        Visual("card", "OEE Breakdown", "line3_performance", "Line 3 Performance", 648, 88, 296, 120, ("Values:production_log.Line 3 Performance",)),
        Visual("card", "OEE Breakdown", "top_downtime_reason", "Top Downtime Reason", 960, 88, 296, 120, ("Values:production_log.Top Downtime Reason",)),
        Visual("tableEx", "OEE Breakdown", "oee_table", "OEE Component Table", 24, 224, 600, 232, ("Values:lines.line_name", "Values:lines.area", "Values:production_log.Availability %", "Values:production_log.Performance %", "Values:production_log.Quality %", "Values:production_log.OEE %", "Values:production_log.OEE Gap")),
        Visual("barChart", "OEE Breakdown", "downtime_reason", "Downtime by Reason", 648, 224, 608, 232, ("Category:production_log.downtime_reason", "Y:production_log.Downtime Minutes")),
        Visual("barChart", "OEE Breakdown", "downtime_reason_line", "Downtime Reason by Line", 24, 472, 1232, 200, ("Category:production_log.downtime_reason", "Y:production_log.Downtime Minutes", "Series:lines.line_name")),
        Visual("slicer", "Cost Analysis", "line_slicer_cost", "Line", 1016, 24, 240, 48, ("Values:lines.line_name",)),
        Visual("card", "Cost Analysis", "total_cost", "Total Cost", 24, 88, 296, 120, ("Values:monthly_costs.Total Cost",)),
        Visual("card", "Cost Analysis", "cost_unit", "Cost per Unit", 336, 88, 296, 120, ("Values:monthly_costs.Cost per Unit",)),
        Visual("card", "Cost Analysis", "materials_share", "Materials Share %", 648, 88, 296, 120, ("Values:monthly_costs.Materials Share %",)),
        Visual("card", "Cost Analysis", "highest_cost_type", "Highest Cost Type", 960, 88, 296, 120, ("Values:monthly_costs.Highest Cost Type",)),
        Visual("barChart", "Cost Analysis", "cost_type", "Cost by Type", 24, 224, 600, 232, ("Category:monthly_costs.cost_type", "Y:monthly_costs.Total Cost")),
        Visual("columnChart", "Cost Analysis", "cost_month", "Monthly Cost by Type", 648, 224, 608, 232, ("Category:monthly_costs.cost_month", "Y:monthly_costs.Total Cost", "Series:monthly_costs.cost_type")),
        Visual("lineChart", "Cost Analysis", "cost_per_unit_month", "Cost per Unit by Month", 24, 472, 1232, 200, ("Category:monthly_costs.cost_month", "Y:monthly_costs.Cost per Unit")),
    ]
    add_pages_and_visuals(work, "IndustryOperationsCost", ["Overview", "OEE Breakdown", "Cost Analysis"], visuals)
    merge_thick(work, "IndustryOperationsCost", "IndustryOperationsCost", out)


def build_supply() -> None:
    project = ROOT / "supply_chain_inventory"
    out = project / "powerbi" / "supply_chain_inventory_pbip"
    work = pathlib.Path(tempfile.gettempdir()) / f"supply_pbip_{int(time.time())}"
    work.mkdir()
    data = project / "python" / "data" / "processed"
    tables = {
        "products": build_table_tmdl(
            "products",
            [("product_id", "int64"), ("product_name", "string"), ("category", "string"), ("supplier_id", "int64"), ("unit_cost", "decimal"), ("reorder_point", "int64"), ("order_quantity", "int64")],
            data / "products_clean.csv",
        ),
        "suppliers": build_table_tmdl(
            "suppliers",
            [("supplier_id", "int64"), ("supplier_name", "string"), ("region", "string"), ("nominal_lead_time_days", "int64")],
            data / "suppliers_clean.csv",
        ),
        "inventory_snapshots": build_table_tmdl(
            "inventory_snapshots",
            [("product_id", "int64"), ("snapshot_date", "dateTime"), ("stock_on_hand", "int64"), ("stockout", "int64")],
            data / "inventory_snapshots_clean.csv",
            [
                ("Total Stock On Hand", "SUM(inventory_snapshots[stock_on_hand])", "#,0"),
                ("Inventory Value", "SUMX(inventory_snapshots, inventory_snapshots[stock_on_hand] * RELATED(products[unit_cost]))", "$#,0"),
                ("Latest Snapshot Date", "MAX(inventory_snapshots[snapshot_date])", "Short Date"),
                ("Latest Stock On Hand", "VAR LatestDate = [Latest Snapshot Date] RETURN CALCULATE([Total Stock On Hand], inventory_snapshots[snapshot_date] = LatestDate)", "#,0"),
                ("Latest Inventory Value", "VAR LatestDate = [Latest Snapshot Date] RETURN CALCULATE([Inventory Value], inventory_snapshots[snapshot_date] = LatestDate)", "$#,0"),
                ("Stockout Weeks", "SUM(inventory_snapshots[stockout])", "#,0"),
                ("Stockout Rate %", "DIVIDE([Stockout Weeks], COUNTROWS(inventory_snapshots))", "0.0%"),
                ("Products Stocked Out", "COUNTROWS(FILTER(VALUES(products[product_name]), CALCULATE(MAX(inventory_snapshots[stockout])) = 1))", "#,0"),
                ("Worst Product", "CONCATENATEX(TOPN(1, VALUES(products[product_name]), [Stockout Rate %], DESC), products[product_name], \", \")", None),
                ("Worst Product Stockout Rate %", "MAXX(TOPN(1, VALUES(products[product_name]), [Stockout Rate %], DESC), [Stockout Rate %])", "0.0%"),
                ("Average Product Stockout Rate %", "AVERAGEX(VALUES(products[product_name]), [Stockout Rate %])", "0.0%"),
            ],
        ),
        "purchase_orders": build_table_tmdl(
            "purchase_orders",
            [("po_id", "int64"), ("product_id", "int64"), ("supplier_id", "int64"), ("order_date", "dateTime"), ("expected_delivery_date", "dateTime"), ("actual_delivery_date", "dateTime"), ("quantity_ordered", "int64")],
            data / "purchase_orders_clean.csv",
            [
                ("Total Orders", "COUNTROWS(purchase_orders)", "#,0"),
                ("On-Time Orders", "CALCULATE(COUNTROWS(purchase_orders), purchase_orders[actual_delivery_date] <= purchase_orders[expected_delivery_date])", "#,0"),
                ("On-Time %", "DIVIDE([On-Time Orders], [Total Orders])", "0.0%"),
                ("Late Orders", "[Total Orders] - [On-Time Orders]", "#,0"),
                ("Supplier Count", "DISTINCTCOUNT(suppliers[supplier_id])", "#,0"),
                ("Lowest On-Time Supplier", "CONCATENATEX(TOPN(1, VALUES(suppliers[supplier_name]), [On-Time %], ASC), suppliers[supplier_name], \", \")", None),
                ("Lowest Supplier On-Time %", "MINX(VALUES(suppliers[supplier_name]), [On-Time %])", "0.0%"),
            ],
        ),
    }
    relationships = [
        "\trelationship inventory_snapshots_product_id_products_product_id\n\t\tfromColumn: inventory_snapshots.product_id\n\t\ttoColumn: products.product_id",
        "\trelationship purchase_orders_product_id_products_product_id\n\t\tfromColumn: purchase_orders.product_id\n\t\ttoColumn: products.product_id",
        "\trelationship purchase_orders_supplier_id_suppliers_supplier_id\n\t\tfromColumn: purchase_orders.supplier_id\n\t\ttoColumn: suppliers.supplier_id",
    ]
    write_semantic_model(work, "SupplyChainInventory", tables, relationships)
    create_report_shell(work, "SupplyChainInventory", "SupplyChainInventory")
    visuals = [
        Visual("slicer", "Inventory Overview", "region_slicer", "Region", 1016, 24, 240, 48, ("Values:suppliers.region",)),
        Visual("card", "Inventory Overview", "inventory_value", "Latest Inventory Value", 24, 88, 296, 120, ("Values:inventory_snapshots.Latest Inventory Value",)),
        Visual("card", "Inventory Overview", "stockout_rate", "Stockout Rate %", 336, 88, 296, 120, ("Values:inventory_snapshots.Stockout Rate %",)),
        Visual("card", "Inventory Overview", "on_time", "On-Time %", 648, 88, 296, 120, ("Values:purchase_orders.On-Time %",)),
        Visual("card", "Inventory Overview", "products_stocked_out", "Products Stocked Out", 960, 88, 296, 120, ("Values:inventory_snapshots.Products Stocked Out",)),
        Visual("lineChart", "Inventory Overview", "stockout_trend", "Stockout Rate by Week", 24, 224, 600, 232, ("Category:inventory_snapshots.snapshot_date", "Y:inventory_snapshots.Stockout Rate %")),
        Visual("barChart", "Inventory Overview", "value_category", "Latest Inventory Value by Category", 648, 224, 296, 232, ("Category:products.category", "Y:inventory_snapshots.Latest Inventory Value")),
        Visual("columnChart", "Inventory Overview", "orders_region", "Orders by Region", 960, 224, 296, 232, ("Category:suppliers.region", "Y:purchase_orders.Total Orders")),
        Visual("tableEx", "Inventory Overview", "inventory_detail", "Inventory Detail", 24, 472, 1232, 200, ("Values:products.category", "Values:inventory_snapshots.Latest Inventory Value", "Values:inventory_snapshots.Products Stocked Out", "Values:inventory_snapshots.Stockout Rate %", "Values:purchase_orders.On-Time %")),
        Visual("slicer", "Stockouts", "category_slicer", "Category", 1016, 24, 240, 48, ("Values:products.category",)),
        Visual("card", "Stockouts", "worst_product", "Worst Product", 24, 88, 296, 120, ("Values:inventory_snapshots.Worst Product",)),
        Visual("card", "Stockouts", "worst_product_rate", "Worst Product Rate", 336, 88, 296, 120, ("Values:inventory_snapshots.Worst Product Stockout Rate %",)),
        Visual("card", "Stockouts", "avg_product_rate", "Avg Product Rate", 648, 88, 296, 120, ("Values:inventory_snapshots.Average Product Stockout Rate %",)),
        Visual("card", "Stockouts", "stockout_weeks", "Stockout Weeks", 960, 88, 296, 120, ("Values:inventory_snapshots.Stockout Weeks",)),
        Visual("barChart", "Stockouts", "product_stockout", "Products by Stockout Rate", 24, 224, 1232, 232, ("Category:products.product_name", "Y:inventory_snapshots.Stockout Rate %")),
        Visual("tableEx", "Stockouts", "stockout_table", "Stockout Detail", 24, 472, 1232, 200, ("Values:products.product_id", "Values:products.product_name", "Values:products.category", "Values:inventory_snapshots.Stockout Weeks", "Values:inventory_snapshots.Stockout Rate %", "Values:inventory_snapshots.Latest Stock On Hand")),
        Visual("slicer", "Suppliers", "supplier_region", "Region", 1016, 24, 240, 48, ("Values:suppliers.region",)),
        Visual("card", "Suppliers", "supplier_count", "Supplier Count", 24, 88, 296, 120, ("Values:purchase_orders.Supplier Count",)),
        Visual("card", "Suppliers", "supplier_on_time", "On-Time %", 336, 88, 296, 120, ("Values:purchase_orders.On-Time %",)),
        Visual("card", "Suppliers", "lowest_supplier", "Lowest On-Time Supplier", 648, 88, 296, 120, ("Values:purchase_orders.Lowest On-Time Supplier",)),
        Visual("card", "Suppliers", "late_orders", "Late Orders", 960, 88, 296, 120, ("Values:purchase_orders.Late Orders",)),
        Visual("barChart", "Suppliers", "supplier_performance", "On-Time % by Supplier", 24, 224, 1232, 232, ("Category:suppliers.supplier_name", "Y:purchase_orders.On-Time %")),
        Visual("tableEx", "Suppliers", "supplier_detail", "Supplier Detail", 24, 472, 1232, 200, ("Values:suppliers.supplier_name", "Values:suppliers.region", "Values:purchase_orders.Total Orders", "Values:purchase_orders.Late Orders", "Values:purchase_orders.On-Time %")),
    ]
    add_pages_and_visuals(work, "SupplyChainInventory", ["Inventory Overview", "Stockouts", "Suppliers"], visuals)
    merge_thick(work, "SupplyChainInventory", "SupplyChainInventory", out)


def main() -> None:
    build_industry()
    build_supply()


if __name__ == "__main__":
    main()
