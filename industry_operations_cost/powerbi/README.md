# Industry Operations & Cost Optimization - Power BI

Dashboard design built from the clean CSVs in [Python](../python), using the same portfolio design system as the Wastewater Effluent Quality dashboard: header band, single blue accent, neutral supporting visuals, KPI cards at the top, and one written finding per page.

## Tools

- Power BI Desktop
- Power Query
- DAX measures

## Pages

**Overview**

![Overview](../images/overview.png)

Headline OEE cards plus monthly downtime, OEE by line, and units by line. The page leads with the operating benchmark: average OEE is below the 85% world-class target.

**OEE Breakdown**

![OEE Breakdown](../images/oee_breakdown.png)

Line-level factor table for Availability, Performance, Quality, and OEE, followed by downtime by reason and downtime by reason/line. The main finding is that Line 3's gap is availability, not speed or defects.

**Cost Analysis**

![Cost Analysis](../images/cost_analysis.png)

Cost cards and visuals for cost type, cost type by month, and cost per unit by line over time. Materials are the largest cost category, so the cost story starts there.

## Power BI Build Notes

The editable Power BI project is in [industry_operations_cost_pbip](./industry_operations_cost_pbip):

- `IndustryOperationsCost.pbip` opens the report in Power BI Desktop.
- `IndustryOperationsCost.Report/` contains the PBIR report pages and visuals.
- `IndustryOperationsCost.SemanticModel/` contains the local TMDL semantic model, CSV imports, relationships, and measures.

The model, DAX, page map, and formatting rules are documented in [dashboard_spec.md](./dashboard_spec.md). The project can be rebuilt with:

```powershell
python tools\generate_powerbi_pbip_projects.py
```

## How to run

Open `industry_operations_cost/powerbi/industry_operations_cost_pbip/IndustryOperationsCost.pbip` in Power BI Desktop.

To create a single-file `.pbix`, use Power BI Desktop: **File > Save As > Power BI report (.pbix)** and save it as `industry_operations_cost.pbix`. The CLI-generated PBIP is committed because `pbir` cannot embed a local `.SemanticModel` into a `.pbix` binary without Power BI Desktop.

## Project Status

Done
