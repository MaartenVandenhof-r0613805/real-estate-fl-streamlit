from pathlib import Path
import pandas as pd
import streamlit as st
import pickle
import numpy as np
from sklearn.metrics import mean_squared_error as MSE

# Import models and data
reg_model_app = pickle.load(open(Path(__file__).parents[1] / 'models' / 'lasso_reg_app.pkl', "rb"))
dt_model_app = pickle.load(open(Path(__file__).parents[1] / 'models' / 'decision_tree_app.pkl', "rb"))
ridge_model_app = pickle.load(open(Path(__file__).parents[1] / 'models' / 'ridge_reg_app.pkl', "rb"))
app_model_df = pd.read_csv(Path(__file__).parents[1] / 'data' / 'app_model.csv')
app_model_df = app_model_df.sort_values(by="year:period")

# Layout
# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

# Set title
'''
# Predict the increase in apartment price % for the next quartile in the Flanders region, Belgium
'''

# Create predictions
data = np.array(app_model_df.drop(columns=["next_q_lvl_app", "year:period"]))

# Lasso regression predictions
y_reg_pred = reg_model_app.predict(data)

y_pred_reg_chart_df = app_model_df[["next_q_lvl_app", "year:period"]].copy()
y_pred_reg_chart_df["Price prediction"] = y_reg_pred
y_pred_reg_chart_df = y_pred_reg_chart_df.rename(columns={"next_q_lvl_app": "Actual price increase"})
y_pred_reg_chart_df = y_pred_reg_chart_df.set_index("year:period")

'''
### Lasso regression predictions:
'''
st.write('''MSE: {}'''.format(MSE(y_reg_pred, app_model_df["next_q_lvl_app"])))

st.line_chart(y_pred_reg_chart_df)

# Ridge regression predictions
y_ridge_pred = ridge_model_app.predict(data)

y_pred_ridge_chart_df = app_model_df[["next_q_lvl_app", "year:period"]].copy()
y_pred_ridge_chart_df["Price prediction"] = y_ridge_pred
y_pred_ridge_chart_df = y_pred_ridge_chart_df.rename(columns={"next_q_lvl_app": "Actual price increase"})
y_pred_ridge_chart_df = y_pred_ridge_chart_df.set_index("year:period")

'''
### Ridge regression predictions:
'''
st.write('''MSE: {}'''.format(MSE(y_ridge_pred, app_model_df["next_q_lvl_app"])))

st.line_chart(y_pred_ridge_chart_df)

# Decision tree predictions
y_dt_pred = dt_model_app.predict(data)

y_pred_chart_df = app_model_df[["next_q_lvl_app", "year:period"]].copy()
y_pred_chart_df["Price prediction"] = y_dt_pred
y_pred_chart_df = y_pred_chart_df.rename(columns={"next_q_lvl_app": "Actual price increase"})
y_pred_chart_df = y_pred_chart_df.set_index("year:period")

'''
### Decision tree predictions:
'''
st.write('''MSE: {}'''.format(MSE(y_dt_pred, app_model_df["next_q_lvl_app"])))
st.line_chart(y_pred_chart_df)

# Combined model predictions

y_pred_comb = (y_ridge_pred + y_dt_pred) / 2

y_pred_comb_chart_df = app_model_df[["next_q_lvl_app", "year:period"]].copy()
y_pred_comb_chart_df["Price prediction"] = y_pred_comb
y_pred_comb_chart_df = y_pred_comb_chart_df.rename(columns={"next_q_lvl_app": "Actual price increase"})
y_pred_comb_chart_df = y_pred_comb_chart_df.set_index("year:period")

'''
### Ridge and Decision tree combined predictions:
'''
st.write('''MSE: {}'''.format(MSE(y_pred_comb, app_model_df["next_q_lvl_app"])))
st.line_chart(y_pred_comb_chart_df)

# Create sidebar
sd_model = reg_model_app
with st.sidebar:
    '''# Predict price increase using the selected model:'''
    if st.button("Lasso regression"):
        sd_model = reg_model_app
    if st.button("Ridge regression"):
        sd_model = ridge_model_app
    if st.button("Decision tree"):
        sd_model = dt_model_app
    interest = st.number_input("Current interest rate:", value=data[0, 0])
    permits = st.number_input("Amount of new permits:", value=int(data[0, 1]))
    prev_q_permits = st.number_input("Amount of previous quartile new permits:", value=int(data[0, 2]))
    transactions = st.number_input("Amount of transactions:", value=int(data[0, 3]))
    current_increase = st.number_input("Last increase in price in %:", value=data[0, 4])
    st.write('''# Predicted result: {}'''.format(sd_model.predict(
        np.array([interest, permits, prev_q_permits, transactions, current_increase]).reshape(1, -1))[0]) + '''%''')
