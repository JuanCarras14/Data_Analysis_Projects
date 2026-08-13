from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANVAS = (1280, 720)
BG = "#F4F6F8"
WHITE = "#FFFFFF"
INK = "#1C2530"
TEXT = "#38424D"
MUTED = "#5A6B7B"
ACCENT = "#1F4E79"
GREY = "#B9C3CF"
LIGHT_GREY = "#E6EAEF"
GRID = "#EDF0F3"
GOOD = "#2B7A78"
BAD = "#D4602E"


def rect(x, y, w, h):
    return [x / CANVAS[0], 1 - (y + h) / CANVAS[1], w / CANVAS[0], h / CANVAS[1]]


def figure():
    return plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)


def add_header(fig, title, slicer="All Lines"):
    ax = fig.add_axes(rect(24, 24, 500, 48))
    ax.axis("off")
    ax.text(0, 0.54, title, ha="left", va="center", fontsize=16, fontweight="bold", color=INK)
    ax_slicer = fig.add_axes(rect(1016, 24, 240, 48))
    ax_slicer.axis("off")
    ax_slicer.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=WHITE, edgecolor=LIGHT_GREY, linewidth=1))
    ax_slicer.text(0.06, 0.68, "Slicer", ha="left", va="center", fontsize=8, color=MUTED)
    ax_slicer.text(0.06, 0.32, slicer, ha="left", va="center", fontsize=11, color=INK)


def add_finding(fig, text):
    ax = fig.add_axes(rect(24, 58, 900, 24))
    ax.axis("off")
    ax.text(0, 0.5, text, ha="left", va="center", wrap=True, fontsize=10.5, color=TEXT)


def add_card(fig, slot, value, label, note=None, status=None):
    x = [24, 336, 648, 960][slot - 1]
    ax = fig.add_axes(rect(x, 88, 296, 120))
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=WHITE, edgecolor=LIGHT_GREY, linewidth=1))
    color = ACCENT if status is None else (GOOD if status == "good" else BAD)
    ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=30, fontweight="bold", color=color)
    ax.text(0.5, 0.32, label, ha="center", va="center", fontsize=11, color=MUTED)
    if note:
        ax.text(0.5, 0.13, note, ha="center", va="center", fontsize=9, color=MUTED)


def add_callout(fig, x, y, w, h, text):
    ax = fig.add_axes(rect(x, y, w, h))
    ax.axis("off")
    ax.text(0, 0.5, text, ha="left", va="center", wrap=True, fontsize=11, color=TEXT)


def style(ax, title):
    ax.set_facecolor(WHITE)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C9D1DB")
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=8)
    ax.title.set_position((0, 1.02))


def horizontal_bars_with_inside_labels(ax, labels, values, colors, xmax=None):
    y = np.arange(len(labels))
    ax.barh(y, values, color=colors)
    ax.set_yticks(y, [])
    limit = xmax or max(values) * 1.08
    ax.set_xlim(0, limit)
    for yi, label, color in zip(y, labels, colors):
        ax.text(limit * 0.012, yi, label, ha="left", va="center", fontsize=9, color=WHITE if color == ACCENT else MUTED)


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def industry():
    base = ROOT / "industry_operations_cost" / "python" / "data" / "processed"
    lines = pd.read_csv(base / "lines_clean.csv")
    production = pd.read_csv(base / "production_log_clean.csv", parse_dates=["production_date"])
    costs = pd.read_csv(base / "monthly_costs_clean.csv")
    production = production.merge(lines, on="line_id", how="left")
    production["runtime_minutes"] = production["planned_minutes"] - production["downtime_minutes"]
    production["theoretical_units"] = production["runtime_minutes"] / 60 * production["target_units_per_hour"]
    production["good_units"] = production["units_produced"] - production["units_defective"]
    production["year_month"] = production["production_date"].dt.strftime("%Y-%m")
    return lines, production, costs


def oee_frame(production, keys):
    grouped = production.groupby(keys, as_index=False).agg(
        planned=("planned_minutes", "sum"),
        downtime=("downtime_minutes", "sum"),
        units=("units_produced", "sum"),
        defects=("units_defective", "sum"),
        theoretical=("theoretical_units", "sum"),
    )
    grouped["availability"] = (grouped["planned"] - grouped["downtime"]) / grouped["planned"]
    grouped["performance"] = grouped["units"] / grouped["theoretical"]
    grouped["quality"] = (grouped["units"] - grouped["defects"]) / grouped["units"]
    grouped["oee"] = grouped["availability"] * grouped["performance"] * grouped["quality"]
    return grouped


def industry_overview():
    _, production, _ = industry()
    totals = oee_frame(production.assign(all="all"), ["all"]).iloc[0]
    by_month = production.groupby("year_month", as_index=False)["downtime_minutes"].sum()
    by_line = oee_frame(production, ["line_name"]).sort_values("oee", ascending=True)
    units = production.groupby("line_name", as_index=False)["units_produced"].sum().sort_values("units_produced")
    fig = figure()
    add_header(fig, "Operations Overview")
    add_card(fig, 1, f"{totals.oee:.1%}", "OEE", f"{totals.oee - 0.85:+.1%} vs 85% target", "good" if totals.oee >= 0.85 else "bad")
    add_card(fig, 2, f"{totals.availability:.1%}", "Availability", f"{totals.availability - 0.90:+.1%} vs 90% target", "good" if totals.availability >= 0.90 else "bad")
    add_card(fig, 3, f"{totals.performance:.1%}", "Performance")
    add_card(fig, 4, f"{totals.quality:.1%}", "Quality", f"{totals.quality - 0.99:+.1%} vs 99% target", "good" if totals.quality >= 0.99 else "bad")
    add_finding(fig, "Downtime is not evenly distributed through the year; the monthly view keeps the OEE story tied to operating time lost.")
    ax = fig.add_axes(rect(24, 224, 1232, 232))
    style(ax, "Downtime Minutes by Month")
    ax.bar(by_month["year_month"], by_month["downtime_minutes"], color=ACCENT)
    ax.tick_params(axis="x", labelbottom=False)
    ax.set_ylabel("Minutes", color=MUTED)
    ax1 = fig.add_axes(rect(24, 472, 608, 224))
    style(ax1, "OEE % by Line")
    colors = [ACCENT if name == "Line 3" else GREY for name in by_line["line_name"]]
    horizontal_bars_with_inside_labels(ax1, by_line["line_name"], by_line["oee"] * 100, colors, xmax=90)
    ax1.axvline(85, color=MUTED, linestyle="--", linewidth=1)
    ax1.text(85.5, len(by_line) - 0.8, "World class", color=MUTED, fontsize=9)
    ax1.set_xlabel("OEE %", color=MUTED)
    ax2 = fig.add_axes(rect(648, 472, 608, 224))
    style(ax2, "Total Units by Line")
    horizontal_bars_with_inside_labels(ax2, units["line_name"], units["units_produced"], [ACCENT] * len(units))
    ax2.set_xlabel("Units", color=MUTED)
    save(fig, ROOT / "industry_operations_cost" / "images" / "overview.png")


def industry_oee_breakdown():
    _, production, _ = industry()
    by_line = oee_frame(production, ["line_name", "area"]).sort_values("oee")
    reason = production.groupby("downtime_reason", as_index=False)["downtime_minutes"].sum().sort_values("downtime_minutes", ascending=True)
    pivot = production.pivot_table(index="downtime_reason", columns="line_name", values="downtime_minutes", aggfunc="sum").fillna(0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]
    fig = figure()
    add_header(fig, "OEE Breakdown")
    add_card(fig, 1, "Line 3", "Lowest OEE Line")
    add_card(fig, 2, f"{by_line.iloc[0].availability:.1%}", "Line 3 Availability", "main gap vs peers", "bad")
    add_card(fig, 3, f"{by_line.iloc[0].performance:.1%}", "Line 3 Performance")
    add_card(fig, 4, f"{by_line.iloc[0].quality:.1%}", "Line 3 Quality")
    add_finding(fig, "Line 3 sits at 73.4% OEE. The gap is availability, not speed or defects - a downtime problem, not a quality problem.")
    ax = fig.add_axes(rect(24, 224, 1232, 232))
    ax.axis("off")
    table = by_line.copy()
    table[["availability", "performance", "quality", "oee"]] *= 100
    display = table[["line_name", "area", "availability", "performance", "quality", "oee"]]
    cell_text = [[r.line_name, r.area, f"{r.availability:.1f}%", f"{r.performance:.1f}%", f"{r.quality:.1f}%", f"{r.oee:.1f}%"] for r in display.itertuples()]
    tbl = ax.table(cellText=cell_text, colLabels=["Line", "Area", "Availability", "Performance", "Quality", "OEE"], cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.45)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(LIGHT_GREY)
        if row == 0:
            cell.set_facecolor(BG)
            cell.set_text_props(weight="bold", color=INK)
        elif display.iloc[row - 1]["line_name"] == "Line 3":
            cell.set_facecolor("#F6E9E3" if col in [2, 5] else WHITE)
        else:
            cell.set_facecolor(WHITE)
    ax.set_title("OEE Factors by Line", loc="left", fontsize=12, fontweight="bold", color=INK, pad=8)
    ax1 = fig.add_axes(rect(24, 472, 608, 224))
    style(ax1, "Downtime Minutes by Reason")
    horizontal_bars_with_inside_labels(ax1, reason["downtime_reason"], reason["downtime_minutes"], [ACCENT] * len(reason))
    ax1.set_xlabel("Minutes", color=MUTED)
    ax2 = fig.add_axes(rect(648, 472, 608, 224))
    style(ax2, "Downtime Minutes by Reason and Line")
    left = np.zeros(len(pivot))
    for col in pivot.columns:
        color = ACCENT if col == "Line 3" else GREY
        ax2.barh(pivot.index, pivot[col], left=left, label=col, color=color)
        left += pivot[col].values
    ax2.legend(ncol=3, fontsize=8, frameon=False)
    ax2.set_yticklabels([str(i) for i in pivot.index], fontsize=8)
    ax2.set_xlabel("Minutes", color=MUTED)
    save(fig, ROOT / "industry_operations_cost" / "images" / "oee_breakdown.png")


def industry_cost():
    _, production, costs = industry()
    units_by_line_month = production.groupby(["line_id", "line_name", "year_month"], as_index=False)["units_produced"].sum()
    monthly_cost = costs.groupby(["line_id", "cost_month"], as_index=False)["amount"].sum()
    cpu = units_by_line_month.merge(monthly_cost, left_on=["line_id", "year_month"], right_on=["line_id", "cost_month"], how="left")
    cpu["cost_per_unit"] = cpu["amount"] / cpu["units_produced"]
    total_cost = costs["amount"].sum()
    total_units = production["units_produced"].sum()
    by_type = costs.groupby("cost_type", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    type_month = costs.pivot_table(index="cost_month", columns="cost_type", values="amount", aggfunc="sum").fillna(0)
    fig = figure()
    add_header(fig, "Cost Analysis")
    add_card(fig, 1, f"${total_cost / 1_000_000:.1f}M", "Total Cost")
    add_card(fig, 2, f"${total_cost / total_units:.2f}", "Cost per Unit")
    add_card(fig, 3, f"{total_units / 1_000_000:.1f}M", "Total Units")
    ax = fig.add_axes(rect(24, 224, 608, 232))
    style(ax, "Cost by Type")
    ax.bar(by_type["cost_type"], by_type["amount"] / 1_000, color=[ACCENT] + [GREY] * (len(by_type) - 1))
    ax.tick_params(axis="x", labelbottom=False)
    ax.set_ylabel("$K", color=MUTED)
    ax2 = fig.add_axes(rect(648, 224, 608, 232))
    style(ax2, "Cost by Type by Month")
    bottom = np.zeros(len(type_month))
    for i, col in enumerate(type_month.columns):
        ax2.bar(type_month.index, type_month[col] / 1_000, bottom=bottom / 1_000, label=col, color=ACCENT if i == 0 else GREY)
        bottom += type_month[col].values
    ax2.tick_params(axis="x", labelbottom=False)
    ax2.legend(frameon=False, fontsize=8, ncol=4)
    add_finding(fig, "Materials are the largest cost category, so cost optimization starts with usage, yield, and purchasing before smaller expense lines.")
    ax3 = fig.add_axes(rect(24, 472, 1232, 224))
    style(ax3, "Cost per Unit by Line over Time")
    pivot = cpu.pivot_table(index="year_month", columns="line_name", values="cost_per_unit", aggfunc="mean")
    for col in pivot.columns:
        ax3.plot(pivot.index, pivot[col], label=col, color=ACCENT if col == "Line 3" else GREY, linewidth=2 if col == "Line 3" else 1.2)
    ax3.tick_params(axis="x", rotation=35)
    ax3.set_ylabel("$ / Unit", color=MUTED)
    ax3.legend(frameon=False, fontsize=8, ncol=6)
    save(fig, ROOT / "industry_operations_cost" / "images" / "cost_analysis.png")


def supply():
    db = ROOT / "supply_chain_inventory" / "sql" / "database" / "supply_chain.db"
    with sqlite3.connect(db) as con:
        products = pd.read_sql("select * from products", con)
        suppliers = pd.read_sql("select * from suppliers", con)
        inventory = pd.read_sql("select * from inventory_snapshots", con, parse_dates=["snapshot_date"])
        orders = pd.read_sql("select * from purchase_orders", con, parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"])
    inventory = inventory.merge(products, on="product_id", how="left")
    orders = orders.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
    orders = orders.merge(suppliers, on="supplier_id", how="left")
    orders["on_time"] = orders["actual_delivery_date"] <= orders["expected_delivery_date"]
    orders["delay_days"] = (orders["actual_delivery_date"] - orders["expected_delivery_date"]).dt.days.clip(lower=0)
    return products, suppliers, inventory, orders


def supply_overview():
    _, _, inventory, orders = supply()
    latest_date = inventory["snapshot_date"].max()
    latest = inventory[inventory["snapshot_date"] == latest_date].copy()
    latest["inventory_value"] = latest["stock_on_hand"] * latest["unit_cost"]
    weekly = inventory.groupby("snapshot_date", as_index=False).agg(stockout_rate=("stockout", "mean"))
    by_cat = latest.groupby("category", as_index=False)["inventory_value"].sum().sort_values("inventory_value", ascending=False)
    fig = figure()
    add_header(fig, "Inventory Overview", "All Regions")
    add_card(fig, 1, f"${latest['inventory_value'].sum() / 1000:.1f}K", "Inventory Value", f"latest week {latest_date:%Y-%m-%d}")
    add_card(fig, 2, f"{inventory['stockout'].mean():.1%}", "Stockout Rate")
    add_card(fig, 3, f"{orders['on_time'].mean():.1%}", "On-Time Orders")
    ax = fig.add_axes(rect(24, 224, 1232, 232))
    style(ax, "Stockout Rate by Week")
    ax.plot(weekly["snapshot_date"], weekly["stockout_rate"] * 100, color=ACCENT, linewidth=2.5)
    ax.tick_params(axis="x", labelbottom=False)
    ax.set_ylabel("Stockout %", color=MUTED)
    add_finding(fig, "Inventory value is filtered to the latest snapshot week so historical snapshots do not double-count the current inventory position.")
    ax1 = fig.add_axes(rect(24, 472, 608, 224))
    style(ax1, "Inventory Value by Category")
    ax1.bar(by_cat["category"], by_cat["inventory_value"] / 1000, color=[ACCENT] + [GREY] * (len(by_cat) - 1))
    ax1.tick_params(axis="x", rotation=15)
    ax1.set_ylabel("$K", color=MUTED)
    ax2 = fig.add_axes(rect(648, 472, 608, 224))
    style(ax2, "Purchase Orders by Region")
    region = orders.groupby("region", as_index=False)["po_id"].count().sort_values("po_id")
    ax2.barh(region["region"], region["po_id"], color=ACCENT)
    ax2.set_xlabel("Orders", color=MUTED)
    save(fig, ROOT / "supply_chain_inventory" / "images" / "overview.png")


def supply_stockouts():
    _, _, inventory, _ = supply()
    stockout = inventory.groupby(["product_id", "product_name", "category"], as_index=False).agg(stockout_rate=("stockout", "mean"), weeks=("stockout", "count"))
    top = stockout.sort_values("stockout_rate", ascending=False).head(15)
    fig = figure()
    add_header(fig, "Stockouts", "All Categories")
    add_finding(fig, f"{top.iloc[0]['product_name']} was stocked out {top.iloc[0]['stockout_rate']:.1%} of tracked weeks, pointing to a reorder point below demand.")
    add_card(fig, 1, top.iloc[0]["product_name"], "Worst Product")
    add_card(fig, 2, f"{top.iloc[0]['stockout_rate']:.1%}", "Worst Stockout Rate", status="bad")
    add_card(fig, 3, f"{stockout['stockout_rate'].mean():.1%}", "Average Product Stockout")
    ax = fig.add_axes(rect(24, 224, 1232, 232))
    style(ax, "Worst 15 Products by Stockout Rate")
    plot = top.sort_values("stockout_rate")
    colors = [ACCENT if name == top.iloc[0]["product_name"] else GREY for name in plot["product_name"]]
    horizontal_bars_with_inside_labels(ax, plot["product_name"], plot["stockout_rate"] * 100, colors, xmax=35)
    ax.set_xlabel("Stockout %", color=MUTED)
    ax2 = fig.add_axes(rect(24, 492, 1232, 204))
    ax2.axis("off")
    display = top[["product_id", "product_name", "category", "stockout_rate"]].copy()
    display["stockout_rate"] = display["stockout_rate"].map(lambda v: f"{v:.1%}")
    tbl = ax2.table(cellText=display.values, colLabels=["Product ID", "Product", "Category", "Stockout Rate"], cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.05)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(LIGHT_GREY)
        cell.set_facecolor(BG if row == 0 else WHITE)
        if row == 0:
            cell.set_text_props(weight="bold", color=INK)
    save(fig, ROOT / "supply_chain_inventory" / "images" / "stockouts.png")


def supply_suppliers():
    _, suppliers, _, orders = supply()
    perf = orders.dropna(subset=["supplier_name"]).groupby(["supplier_name", "region"], as_index=False).agg(
        total_orders=("po_id", "count"),
        on_time=("on_time", "mean"),
    )
    perf = perf.sort_values("on_time", ascending=True)
    fig = figure()
    add_header(fig, "Suppliers", "All Regions")
    add_card(fig, 1, f"{len(suppliers)}", "Suppliers")
    add_card(fig, 2, f"{orders['on_time'].mean():.1%}", "On-Time Orders")
    add_card(fig, 3, perf.iloc[0]["supplier_name"], "Lowest On-Time Supplier", status="bad")
    add_finding(fig, f"{perf.iloc[0]['supplier_name']} has the lowest on-time rate, so average lead time alone would hide the reliability risk.")
    ax = fig.add_axes(rect(24, 224, 1232, 232))
    style(ax, "Supplier On-Time %")
    colors = [ACCENT if name == perf.iloc[0]["supplier_name"] else GREY for name in perf["supplier_name"]]
    ax.bar(perf["supplier_name"], perf["on_time"] * 100, color=colors)
    ax.tick_params(axis="x", rotation=25, labelsize=8)
    ax.set_ylabel("On-Time %", color=MUTED)
    ax2 = fig.add_axes(rect(24, 492, 1232, 204))
    ax2.axis("off")
    display = perf.copy()
    display["on_time"] = display["on_time"].map(lambda v: f"{v:.1%}")
    tbl = ax2.table(cellText=display[["supplier_name", "region", "total_orders", "on_time"]].values, colLabels=["Supplier", "Region", "Total Orders", "On-Time %"], cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.08)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(LIGHT_GREY)
        cell.set_facecolor(BG if row == 0 else WHITE)
        if row == 0:
            cell.set_text_props(weight="bold", color=INK)
    save(fig, ROOT / "supply_chain_inventory" / "images" / "suppliers.png")


if __name__ == "__main__":
    industry_overview()
    industry_oee_breakdown()
    industry_cost()
    supply_overview()
    supply_stockouts()
    supply_suppliers()
