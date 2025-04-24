# emirkoc-dsa210-project-proposal
"Analyzing the Relationship Between French Bakery Sales and Diet Motivation Search Trends (2021–2022)"
________________________________________
 Motivation
Weight loss participants change their eating behaviors when their choice of food alters. People show strong interest in sweet treats throughout the period of diet change research. Research data will reveal this answer through its investigative process. Daily customer buying patterns for sweet bakery products at a French establishment are studied based on public interest patterns in weight loss keywords “régime” and “comment maigrir.” Research findings collected by the interview team will strengthen the strategic goals of small businesses.
________________________________________
Data Sources & Collection Strategy

. Primary Data – French Bakery Sales  
- Coverage: Daily product sales from January 1, 2021 to September 30, 2022  
- Rows: 601 (aggregated daily)  
The three columns present in this dataset consist of date, Sweet and Savory together with Other option.  
The three product categories defined by the bakery are Sweet which includes the Croissant and Savory with the Baguette as well as Other products.  
The team performed data cleaning procedures by daily aggregation before eliminating all price data points from the information.


2. Secondary Data – Google Trends (France)  
- Keywords: “régime” and “comment maigrir”  
The research utilizes a search interest value scale which ranges from zero to hundred for daily data measurements.  
A total of 639 rows cover the entire duration from 2021 and significant parts of 2022 within the dataset.  
- Columns: date, keyword, search_index  
The developer used this data through PyTrends Python library.  

A date-based merge operation establishes connections between datasets for evaluations needing chronological correlation analysis.

______________________________________
 Project Scope and Analytical Steps:
1. Data Cleaning  
All dates must be standardized into datetime format and normalized at the same time.  
- Clean missing or inconsistent values  
The products need classification into the three groups of Sweet/Savory/Other.  
The Google Trends data requires forward-filling of gaps to match the data range in the bakery dataset.

2. Exploratory Data Analysis (EDA)  
- Time series plots of sales and search trends  
- Weekly averages and seasonality analysis  
We must investigate periods with maximum interest rates to determine how sales patterns behave.  
An examination of seasonal product categories which reach the top sales ranks should be conducted.

3. Hypothesis Testing  
 H1: Sweet sales significantly drop on high diet-search days  
- H2: Trend search spikes can predict changes in sales 1–3 days in advance  
- H3: Savory products are less affected by dieting periods  
- Tests to be used:  
  - Mann–Whitney U Test  
  - Spearman correlation  
  - Cross-correlation for lag detection


Machine Learning & Prediction
The project uses effective normal machine learning techniques which undergraduate students can program. The research aims to identify the relationship between search activities related to dieting and bakery market sales performance.

Models:

1. Linear Regression  
Three variables including Google Trends scores and weekday indicator and holiday markers are included as input variables in this analysis.
- Output: Predicted quantity of sweet sales

3. Decision Tree Regressor  
- Offers visual and explainable predictions for different trend levels
  This decision model reveals the impact that different conditions have on sweet products sold in the market.

3. Time Series Plot Comparison  
- Visual overlay of Google Trends and daily sales data  
RStudio enables users to observe both the timing of variables as well as the extent of their associated relationships.

Evaluation Metrics:  
- MAE (Mean Absolute Error)  
The visualization confirms complete matching accuracy between actual and predicated sales data points.


Visualization & Reporting

Visuals:
Sales with search trend data merge in Time Series Charts as part of the visual representations.  
The data is illustrated using two bar chart categories which examine weekday and peak period trends.  
- Heatmaps (seasonal concentration of sales behavior)

Reporting:
- Jupyter Notebooks with step-by-step explanations  
- A clear Markdown (README) summary of all findings  
- An optional interactive Streamlit app for public exploration


________________________________________
Intended Outcomes & Benefits:
-Scientific investigations evaluate how digital dieting objectives influence actual sweet consumption behaviors of users.  
-The investigation produces critical information which helps bakeries make production quantity decisions at times of peak resolution popularity.  
-The provided public search information shows how it improves retail predictions as demonstrated by this research.  
- A template for similar research in other industries (fitness, health, e-commerce)
