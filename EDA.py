import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ===== Load the macroeconomic data and SPY price data =====
df = pd.read_csv('macro_data_25yrs.csv', parse_dates=['Date'])
spy = yf.download('SPY', start='2018-01-01', end='2025-07-01')
spy_price = pd.Series(spy[('Close', 'SPY')], index=spy.index)
spy_price.name = 'Close'
spy_price = pd.DataFrame(spy_price)
spy_price['F1M_Return'] = spy_price.pct_change(25).shift(-25)
spy_price.to_csv('SPY_close.csv')

# ===== data quality check =====
# Display the first few rows
print('First few rows of the dataset:')
print(df.head())

# Basic info about the dataset
print('\nDataset info:')
df.info()

# Check for missing values
print('\nMissing value counts:')
print(df.isnull().sum())

# ===== Forward fill missing values =====
# Select numeric columns only
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print('Numeric columns:', numeric_cols)

# Instantiate a simple imputer to replace missing values with the mean
for col in numeric_cols:
    df[col] = df[col].ffill()

# Verify that there are no missing values in numeric columns now
print('\nMissing value counts after imputation:')
print(df[numeric_cols].isnull().sum())

# ===== Visualize the macroeconomic data =====
# line plot to easily visualize the trend of macro data
fig = make_subplots(rows = 2, cols = 3, subplot_titles = tuple(df.columns[1:].to_list()))
for i, col in enumerate(df.columns[1:], start=1):
    fig.add_trace(
        go.Scatter(
            x = df['Date'],
            y = df[col],
            mode = 'lines',
            name = col),
        row = i//4+1, col = (i-3 if i>3 else i))
fig.update_layout(
    title = go.layout.Title(text = "Macro Data", x = 0.5),
    showlegend = False)
fig.show()

# historgram to visualize the distribution of macro data
fig_hist = make_subplots(rows = 2, cols = 3, subplot_titles = tuple(df.columns[1:].to_list()))
for i, col in enumerate(df.columns[1:], start=1):
    fig_hist.add_trace(
        go.Histogram(
            x = df[col],
            name = col,
            nbinsx = 20),
        row = i//4+1, col = (i-3 if i>3 else i))
fig_hist.update_layout(
    title = go.layout.Title(text = "Macro Data Distribution", x = 0.5),
    showlegend = False)
fig_hist.show()

# Boxplot to check outliers in macro data
fig_box = make_subplots(rows = 2, cols = 3, subplot_titles = tuple(df.columns[1:].to_list()))
for i, col in enumerate(df.columns[1:], start=1):
    fig_box.add_trace(
        go.Box(
            y = df[col],
            name = col,
            boxmean = True),
        row = i//4+1, col = (i-3 if i>3 else i)) 
fig_box.update_layout(
    title = go.layout.Title(text = "Macro Data Boxplot", x = 0.5),
    showlegend = False)
fig_box.show()

# Correlation heatmap to visualize the correlation between macro data
fig_corr = px.imshow(
    df[df.columns.to_list()[1:]].corr(),
    color_continuous_scale='RdBu',
    zmin=-1, zmax=1,
    title='Correlation Heatmap of Macro Data',
    labels=dict(x="Variables", y="Variables", color="Correlation Coefficient")
)
fig_corr.update_xaxes(side="top")
fig_corr.show()

corr_mat = df[df.columns.to_list()[1:]].corr()
high_corr_cols = corr_mat[abs(corr_mat['Inflation_Rate_%'])>0.3].index.to_list()
print(df[df.columns[1:]].corr())

fig_scatter = px.scatter_matrix(
    df[high_corr_cols],
    title='Scatter Matrix of Macro Data',
    labels={col: col for col in high_corr_cols},
    dimensions=high_corr_cols,
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_scatter.update_traces(diagonal_visible=False)
fig_scatter.show()

# ===== Analysis on SPY vs Inflation Rate and Treasury Yield =====
df2 = df.merge(spy_price, left_on='Date', right_on='Date', how='left')
cols = list((set(df.columns[1:]) - set(high_corr_cols)) | set(['Inflation_Rate_%']))
#
# correlation heatmap
fig_corr2 = px.imshow(
    df2[df2.columns[1:-2].to_list() + ['F1M_Return']].corr(),
    color_continuous_scale='RdBu',
    zmin=-1, zmax=1,
    title='Correlation Heatmap of Macro Data',
    labels=dict(x="Variables", y="Variables", color="Correlation Coefficient")
)
fig_corr2.update_xaxes(side="top")
fig_corr2.show()

# F1M_Return is the most correlated with Inflation_Rate_%
fig_ols1 = px.scatter(df2, x = 'Inflation_Rate_%', y = "F1M_Return", trendline = "ols")
fig_ols1.show()

# F1M_Return is the sencond correlated with 10Y Treasury Yield'
fig_ols2 = px.scatter(df2, x = '10Y Treasury Yield', y = "F1M_Return", trendline = "ols")
fig_ols2.show()

# F1M Return corresponding to inflation range and treasury yield range
df3 = df2.copy()
bins = [-0.01, 2, 4, 6, 8, np.inf]
names = ['(0,2]', '(2,4]', '(4,6]', '(6,8]', '8+']
df3['InflationRange'] = pd.cut(df3['Inflation_Rate_%'], bins, labels = names)

bins = [-0.01, 1, 2, 3, 4, np.inf]
names = ['(0,1]', '(1,2]', '(2,3]', '(3,4]', '4+']
df3['TYRange'] = pd.cut(df3['10Y Treasury Yield'], bins, labels = names)

print('Return by Inflation Range', df3.groupby('InflationRange')['F1M_Return'].mean())
print('Return by Treasury Yield Range', df3.groupby('TYRange')['F1M_Return'].mean())
# %%
