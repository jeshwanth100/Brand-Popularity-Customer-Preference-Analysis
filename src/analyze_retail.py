"""
EDAV Project: Brand Popularity and Customer Preference Analysis
Dataset: UCI Online Retail (real transactional data)
Important: this dataset has product descriptions, not explicit brand labels or customer satisfaction ratings.
Product descriptions are used as a proxy for product popularity.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "visualizations"
REPORT_DIR = ROOT / "report"
DATA_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")

def load_data():
    local_xlsx = DATA_DIR / "Online Retail.xlsx"
    local_csv = DATA_DIR / "Online Retail.csv"
    if local_xlsx.exists():
        df = pd.read_excel(local_xlsx)
    elif local_csv.exists():
        df = pd.read_csv(local_csv, encoding="latin1")
    else:
        try:
            from ucimlrepo import fetch_ucirepo
            dataset = fetch_ucirepo(id=352)
            df = pd.concat([dataset.data.features, dataset.data.targets], axis=1)
            df.to_csv(DATA_DIR / "online_retail_downloaded.csv", index=False)
        except Exception as exc:
            raise RuntimeError(
                "Dataset not found and automatic download failed. Download 'Online Retail.xlsx' "
                "from https://archive.ics.uci.edu/dataset/352/online+retail and place it in the data folder. "
                "Install openpyxl if needed."
            ) from exc
    # Normalize common column names
    df.columns = [str(c).strip() for c in df.columns]
    return df

def main():
    df = load_data()
    required = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "Country"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    original_rows = len(df)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    if "CustomerID" not in df.columns:
        df["CustomerID"] = np.nan

    df = df.dropna(subset=["Description", "InvoiceDate", "Quantity", "UnitPrice", "InvoiceNo"])
    # Exclude cancelled invoices (InvoiceNo beginning with C), returns/negative quantities,
    # and non-positive prices from sales-based charts.
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    sales = df[
        ~df["InvoiceNo"].str.upper().str.startswith("C")
        & (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
    ].copy()
    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]
    sales["Month"] = sales["InvoiceDate"].dt.to_period("M").astype(str)

    if sales.empty:
        raise ValueError("No valid sales rows remain after cleaning. Check the dataset.")

    # Product popularity: transaction-line frequency and quantity sold
    product_lines = sales.groupby("Description", as_index=False).agg(
        TransactionLines=("InvoiceNo", "count"),
        UnitsSold=("Quantity", "sum"),
        Revenue=("Revenue", "sum"),
        UniqueInvoices=("InvoiceNo", "nunique"),
    )
    top_units = product_lines.sort_values("UnitsSold", ascending=False).head(10)
    top_lines = product_lines.sort_values("TransactionLines", ascending=False).head(10)
    top_revenue = product_lines.sort_values("Revenue", ascending=False).head(10)

    plt.figure(figsize=(12, 7))
    sns.barplot(data=top_units, y="Description", x="UnitsSold")
    plt.title("Top 10 Products by Units Sold")
    plt.xlabel("Units sold"); plt.ylabel("Product description")
    plt.tight_layout(); plt.savefig(OUT_DIR / "top_products_units.png", dpi=180); plt.close()

    plt.figure(figsize=(12, 7))
    sns.barplot(data=top_revenue, y="Description", x="Revenue")
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue (£)"); plt.ylabel("Product description")
    plt.tight_layout(); plt.savefig(OUT_DIR / "top_products_revenue.png", dpi=180); plt.close()

    country_sales = sales.groupby("Country", as_index=False).agg(
        Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique")
    ).sort_values("Revenue", ascending=False).head(10)
    plt.figure(figsize=(11, 6))
    sns.barplot(data=country_sales, y="Country", x="Revenue")
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue (£)"); plt.ylabel("Country")
    plt.tight_layout(); plt.savefig(OUT_DIR / "country_revenue.png", dpi=180); plt.close()

    monthly = sales.groupby("Month", as_index=False).agg(Revenue=("Revenue", "sum"))
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=monthly, x="Month", y="Revenue", marker="o")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month"); plt.ylabel("Revenue (£)")
    plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig(OUT_DIR / "monthly_revenue.png", dpi=180); plt.close()

    known_customers = sales.dropna(subset=["CustomerID"]).copy()
    customer_orders = known_customers.groupby("CustomerID")["InvoiceNo"].nunique()
    repeat_customer_share = float((customer_orders > 1).mean() * 100) if len(customer_orders) else float("nan")
    summary = {
        "source_rows": original_rows,
        "clean_sales_rows": len(sales),
        "unique_products": int(sales["Description"].nunique()),
        "unique_invoices": int(sales["InvoiceNo"].nunique()),
        "known_customers": int(known_customers["CustomerID"].nunique()),
        "total_units_sold": int(sales["Quantity"].sum()),
        "total_revenue_gbp": round(float(sales["Revenue"].sum()), 2),
        "repeat_customer_share_percent_among_known_customers": round(repeat_customer_share, 2) if np.isfinite(repeat_customer_share) else None,
        "date_start": str(sales["InvoiceDate"].min()),
        "date_end": str(sales["InvoiceDate"].max()),
        "top_products_by_units": top_units[["Description", "UnitsSold"]].to_dict(orient="records"),
        "top_products_by_revenue": top_revenue[["Description", "Revenue"]].to_dict(orient="records"),
        "top_countries_by_revenue": country_sales.to_dict(orient="records"),
    }
    pd.Series(summary, dtype=object).to_json(REPORT_DIR / "analysis_summary.json", indent=2, force_ascii=False)
    product_lines.to_csv(REPORT_DIR / "product_summary.csv", index=False)
    country_sales.to_csv(REPORT_DIR / "country_summary.csv", index=False)
    monthly.to_csv(REPORT_DIR / "monthly_revenue.csv", index=False)

    with open(REPORT_DIR / "analysis_summary.txt", "w", encoding="utf-8") as f:
        f.write("EDAV PROJECT - ANALYSIS SUMMARY\n")
        f.write("=" * 38 + "\n")
        for key in ["source_rows", "clean_sales_rows", "unique_products", "unique_invoices",
                    "known_customers", "total_units_sold", "total_revenue_gbp",
                    "repeat_customer_share_percent_among_known_customers", "date_start", "date_end"]:
            f.write(f"{key}: {summary.get(key)}\n")
        f.write("\nTop products by units sold:\n")
        for item in summary["top_products_by_units"][:10]:
            f.write(f"- {item['Description']}: {item['UnitsSold']}\n")
        f.write("\nNote: Product descriptions are not official brand names. The dataset has no rating/satisfaction field.\n")

    print("Analysis complete.")
    print(f"Rows before cleaning: {original_rows:,}")
    print(f"Valid sales rows: {len(sales):,}")
    print(f"Unique products: {sales['Description'].nunique():,}")
    print(f"Unique invoices: {sales['InvoiceNo'].nunique():,}")
    print(f"Total revenue: £{sales['Revenue'].sum():,.2f}")
    print(f"Charts saved to: {OUT_DIR}")
    print(f"Summary saved to: {REPORT_DIR}")

if __name__ == "__main__":
    main()
