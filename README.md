# FUEL DEMAND ANALYSIS IN BRAZIL WITH DATA FROM ANP

## Description:

This script performs an exploratory data analysis of fuel sales data (diesel, gasoline, ethanol) from Brazil's National Petroleum Agency (ANP). The goal is to identify trends, seasonal patterns, and consumption differences among Brazilian states (DF, GO, MA, MT, MG, PA, SP, TO.)

**Analysis Structure:**

- Loading and Preparation: Reads data from an Excel file, then cleans and consolidates it into a single dataframe.

- Seasonality Analysis: Decomposes the time series to understand monthly consumption patterns for Brazil as a whole and for each state. (Multiplicative sazonality decomposition)

- State-Level Analysis: Compares the evolution of consumption and the fuel mix (diesel, gasoline, ethanol) across states.

Recent Analysis and Conclusions: Focuses on the trend of the last 5 years and summarizes key insights.


**Tools Used:**

- Python

- Pandas

- Matplotlib

- Statsmodels


**How to run**:

1. Install the required libraries (pip install pandas matplotlib statsmodels).

2. Make sure the file vendas_distribuidoras_anp 1 (3).xlsx is located in a subfolder/data

3. Run the Script
