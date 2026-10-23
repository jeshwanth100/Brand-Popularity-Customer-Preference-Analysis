# Brand Popularity and Customer Preference Analysis

**Course:** EDAV – Python Course-End Project  
**Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook

## Project overview
This project explores product popularity and customer purchasing patterns using the **UCI Online Retail** transactional dataset. It analyzes units sold, product transaction frequency, revenue by product, revenue by country, monthly sales, and repeat purchasing among customers with an available CustomerID.

> **Scope note:** UCI Online Retail is a real transaction dataset. It does not contain explicit brand names or customer satisfaction ratings. Therefore, product descriptions are used as a proxy for popularity, and purchase behavior is analyzed instead of claiming direct survey-based customer preferences or ratings.

## Dataset
- Official source: https://archive.ics.uci.edu/dataset/352/online+retail
- Citation: Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
- License: CC BY 4.0; credit the source when redistributing or adapting the dataset.
- Original dataset: 541,909 transaction rows; dates cover 1 December 2010 to 9 December 2011.

Download `Online Retail.xlsx` from the UCI page and place it in `data/`. The script also attempts to fetch the dataset using `ucimlrepo` if the local file is not present.

## Setup (Windows / VS Code)
```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python src/analyze_retail.py
```

If automatic download fails, download the official Excel file manually and put it at `data/Online Retail.xlsx`, then rerun the script.

## Outputs
The script creates:
- `visualizations/top_products_units.png`
- `visualizations/top_products_revenue.png`
- `visualizations/country_revenue.png`
- `visualizations/monthly_revenue.png`
- `report/analysis_summary.txt`
- `report/analysis_summary.json`
- CSV summary tables in `report/`

## Research questions
1. Which products have the highest units sold?
2. Which products generate the most revenue?
3. Which countries account for the largest revenue?
4. How does revenue change month to month?
5. Among customers with a recorded CustomerID, what share placed more than one distinct order?

## Data cleaning
The script parses dates and numeric fields, removes rows without essential values, excludes cancelled invoices (invoice numbers beginning with `C`), and excludes non-positive quantities/prices from sales-based analysis. Returns are therefore not counted in the positive-sales charts.

## Limitations
The dataset does not identify product manufacturers/brands or customer satisfaction ratings. Revenue and sales volume are not the same as popularity, and transaction data cannot by itself explain why a customer chose a product. Findings should be reported as patterns in the observed transactions.

## Suggested report sections
Abstract, Introduction, Problem Statement, Objectives, Dataset Description, Methodology, Data Cleaning, Exploratory Analysis, Visualizations, Findings (generated from your run), Limitations, Conclusion, Future Scope, References.

## Author
[Your Name]  
Department of Information Technology  
Chaitanya Bharathi Institute of Technology, Hyderabad
