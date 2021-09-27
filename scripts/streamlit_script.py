import pandas as pd
import streamlit as st
import altair as at
from pathlib import Path

# Import csv files
price_df = pd.read_csv(Path(__file__).parents[1] / 'data' / 'annual_prices.csv')
request_df = pd.read_csv(Path(__file__).parents[1] / 'data' / 'permits_reg.csv')
mean_interest_df = pd.read_csv(Path(__file__).parents[1] / 'data' / 'mean_interest_q.csv')

# Select correct rows from df
price_df_q = price_df[price_df["CD_PERIOD"].isin(['Q1', 'Q2', 'Q3', 'Q4'])].sort_values(by=["year:period"])
price_df_q = price_df_q[price_df_q["CD_REFNIS_NL"] == "VLAAMS GEWEST"]

# Layout
# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

# Add intro
'''
# Analysis of the real estate market in the region of Flanders, Belgium
Select the housing type by pressing the correct button in the sidebar.

Click [here](https://real-estate-fl-ml.herokuapp.com) to go to the price prediction model.
'''

# Create buttons for housing type
en_name = "Apartments"
housing_type = "Appartementen"
housing_type_perm = "appartments"
with st.sidebar:
    st.write('''# Select housing type''')
    if st.button("Apartments"):
        housing_type = "Appartementen"
        housing_type_perm = "appartments"
        en_name = "Apartments"
    if st.button("Detached buildings"):
        housing_type = "Huizen met 4 of meer gevels (open bebouwing)"
        housing_type_perm = "one-dwelling buildings"
        en_name = "Detached buildings"
    if st.button("Closed + semi-detached buildings"):
        housing_type = "Huizen met 2 of 3 gevels (gesloten + halfopen bebouwing)"
        housing_type_perm = "dwellings"
        en_name = "Closed + semi-detached buildings"

# Write housing type to intro
st.write('''### Selected housing type: ''' + en_name)

# Create the year:quartile slider
start_p, end_p = st.select_slider("Select a timeframe: ",
                                  options=price_df_q["year:period"],
                                  value=("2010:Q1", "2020:Q4"))

# Make 2 columns
col1, col2 = st.columns(2)

# Add price chart
price_chart_df = pd.DataFrame(price_df_q[(price_df_q["CD_TYPE_NL"] == housing_type)]
                              [["MS_P_75", "year:period"]])
min_index = price_chart_df.index[price_chart_df["year:period"] == start_p][0]
max_index = price_chart_df.index[price_chart_df["year:period"] == end_p][0]
price_chart_df = price_chart_df[(price_chart_df.index >= min_index) & (price_chart_df.index <= max_index)]
price_chart_df = price_chart_df.set_index("year:period")
price_chart_df.rename(columns={"MS_P_75": "Median price 75th percentile"}, inplace=True)
col1.write('''### Median price for the 75th percentile for each period''')
col1.line_chart(price_chart_df)

# Add transaction chart
transaction_chart_df = pd.DataFrame(price_df_q[(price_df_q["CD_TYPE_NL"] == housing_type)]
                              [["MS_TOTAL_TRANSACTIONS", "year:period"]])
min_index = transaction_chart_df.index[transaction_chart_df["year:period"] == start_p][0]
max_index = transaction_chart_df.index[transaction_chart_df["year:period"] == end_p][0]
transaction_chart_df = transaction_chart_df[(transaction_chart_df.index >= min_index) & (transaction_chart_df.index <= max_index)]
transaction_chart_df = transaction_chart_df.set_index("year:period")
transaction_chart_df.rename(columns={"MS_TOTAL_TRANSACTIONS": "Total amount of transactions"}, inplace=True)
col2.write('''### Total amount of transactions for each period''')
col2.line_chart(transaction_chart_df)

# Add Building permits chart
bp_chart_df = request_df[request_df["Year"] >= 2010].groupby(["year:period", "Year"]).sum().reset_index()
bp_chart_df = pd.DataFrame(bp_chart_df[[housing_type_perm, "year:period"]])

if int(start_p.split(":")[0]) < 2012:
    min_index = bp_chart_df.index[bp_chart_df["year:period"] == "2012:Q1"][0]
else:
    min_index = bp_chart_df.index[bp_chart_df["year:period"] == start_p][0]
max_index = bp_chart_df.index[bp_chart_df["year:period"] == end_p][0]

bp_chart_df = bp_chart_df[(bp_chart_df.index >= min_index) & (bp_chart_df.index <= max_index)]
bp_chart_df = bp_chart_df.set_index("year:period")
col1.write('''### Total amount of building permits per period (starting in 2012)''')
col1.bar_chart(bp_chart_df)

# Add lending chart
lending_chart_df = pd.DataFrame(mean_interest_df[["Value", "year:period"]])
min_index = lending_chart_df.index[lending_chart_df["year:period"] == start_p][0]
max_index = lending_chart_df.index[lending_chart_df["year:period"] == end_p][0]
lending_chart_df = lending_chart_df[(lending_chart_df.index >= min_index) & (lending_chart_df.index <= max_index)]
lending_chart_df = lending_chart_df.set_index("year:period")
lending_chart_df.rename(columns={"MS_TOTAL_TRANSACTIONS": "Total amount of transactions"}, inplace=True)
col2.write('''### Long term interest per period''')
col2.line_chart(lending_chart_df)
