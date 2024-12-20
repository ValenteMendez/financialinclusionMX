import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# Set page configuration
st.set_page_config(page_title="Financial Inclusion MX", page_icon="💸", layout="centered")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'State-Level_Consolidated_Dataset.csv')
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    percentage_columns = [col for col in df.columns if col.startswith('%')]
    for col in percentage_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '.').astype(float)
        else:
            df[col] = df[col].astype(float)
    df.set_index('Estado', inplace=True)
    # Filter out "Sin identificar"
    df = df[df.index != 'Sin identificar']
    return df

df = load_data()

st.title('Financial Inclusion Analysis - Mexico, June 2024')

# 1. Population Demographics
st.header('1. Population demographics')
df['Adult_Population_Percentage'] = df['Poblacion_adulta'] / df['Poblacion'] * 100
df['Superficie_km2'] = df['Superficie_km2'].fillna(df['Superficie_km2'].median())

fig = px.scatter(df, x='Poblacion', y='Adult_Population_Percentage', 
                 size='Superficie_km2', hover_name=df.index, 
                 labels={'Poblacion': 'total population', 
                         'Adult_Population_Percentage': 'adult population as (%)', 
                         'Superficie_km2': 'Area (km²)'},
                 title='Population demographics by state; size represents area')
st.plotly_chart(fig)

# 2. Banking Infrastructure Availability
st.header('2. Banking infrastructure availability')

# Add a dictionary for friendly names
infrastructure_labels = {
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial bank branches',
    'Cajeros_10mil_adultos': 'ATMs',
    'Corresponsales_10mil_adultos': 'Banking agents (corresponsales)'
}

infrastructure_metrics = {
    'Sucursales_banca_comercial_10mil_adultos': '#1f77b4',
    'Cajeros_10mil_adultos': '#2ca02c',
    'Corresponsales_10mil_adultos': '#d62728'
}

selected_metric = st.selectbox('Select infrastructure type:', 
                             list(infrastructure_metrics.keys()),
                             format_func=lambda x: infrastructure_labels[x],
                             key='infrastructure')

fig = px.bar(df.sort_values(selected_metric, ascending=False), 
             y=selected_metric, 
             title=f'{infrastructure_labels[selected_metric]} per 10,000 Adults',
             color_discrete_sequence=[infrastructure_metrics[selected_metric]])

fig.update_layout(
    xaxis_title='state', 
    yaxis_title='number per 10,000 adults', 
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig)

# 3. Account Ownership by Type
st.header('3. Account ownership by type')
account_columns = [
    'Cuentas_Nivel1_10mil_adultos_Banca', 
    'Cuentas_Nivel2_10mil_adultos_Banca', 
    'Cuentas_Nivel3_10mil_adultos_Banca', 
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca'
]

account_labels = {
    'Cuentas_Nivel1_10mil_adultos_Banca': 'Cuentas nivel 1',
    'Cuentas_Nivel2_10mil_adultos_Banca': 'Cuentas nivel 2',
    'Cuentas_Nivel3_10mil_adultos_Banca': 'Cuentas nivel 3',
    'Cuentas_cuentas_transaccionales_tradicionales_10mil_adultos_Banca': 'Cuentas transaccionales tradicionales'
}

view_type = st.radio('Select view type', ['Absolute numbers', 'Percentage'])

if view_type == 'Absolute numbers':
    account_data_abs = df[account_columns]
    account_data_renamed = account_data_abs.rename(columns=account_labels)
    fig = px.bar(
        account_data_renamed.sort_values(list(account_labels.values())[0], ascending=False),
        y=list(account_labels.values()),
        title='Account ownership by type per 10,000 adults'
    )
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='accounts per 10,000 adults', 
        barmode='stack', 
        height=700
    )
else:
    account_data_percentage = df[account_columns].div(df[account_columns].sum(axis=1), axis=0) * 100
    account_data_renamed = account_data_percentage.rename(columns=account_labels)
    fig = px.bar(
        account_data_renamed.sort_values(list(account_labels.values())[0], ascending=False),
        y=list(account_labels.values()),
        title='Account Ownership by Type (Percentage)'
    )
    fig.update_layout(
        xaxis_title='State', 
        yaxis_title='Percentage', 
        barmode='stack', 
        height=700
    )

fig.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=10)
    ),
    margin=dict(l=50, r=300, t=80, b=200),
    xaxis_tickangle=-45,
    height=700
)
st.plotly_chart(fig, use_container_width=True)

# 4. Credit Product Penetration
st.header('4. Credit product penetration')
credit_columns = [
    'Creditos_hipotecarios_10mil_adultos_Banca', 
    'Creditos_personales_10mil_adultos_Banca', 
    'Creditos_nomina_10mil_adultos_Banca', 
    'Creditos_automotrices_10mil_adultos_Banca', 
    'Creditos_ABCD_10mil_adultos_Banca'
]

credit_labels = {
    'Creditos_hipotecarios_10mil_adultos_Banca': 'Mortgage (Hipotecarios)',
    'Creditos_personales_10mil_adultos_Banca': 'Personal (Personales)',
    'Creditos_nomina_10mil_adultos_Banca': 'Salary (Nómina)',
    'Creditos_automotrices_10mil_adultos_Banca': 'Automotive (Automotriz)',
    'Creditos_ABCD_10mil_adultos_Banca': 'ABCD'
}

credit_data_renamed = df[credit_columns].rename(columns=credit_labels)
fig = px.bar(
    credit_data_renamed.sort_values('Mortgage (Hipotecarios)', ascending=False), 
    y=list(credit_labels.values()),
    title='Credit product penetration per 10,000 adults'
)
fig.update_layout(
    xaxis_title='state', 
    yaxis_title='credits per 10,000 adults', 
    barmode='stack', 
    height=700,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=10)
    ),
    margin=dict(l=50, r=300, t=80, b=200),
    xaxis_tickangle=-45
)
st.plotly_chart(fig, use_container_width=True)

# 5. Mobile Banking Adoption
st.header('5. Mobile banking adoption')
df['Mobile_Banking_Penetration'] = df['Contratos_celular_10mil_adultos'] / 10000

fig = px.bar(
    df.sort_values('Mobile_Banking_Penetration', ascending=False), 
    y='Mobile_Banking_Penetration', 
    title='Mobile banking adoption by state'
)
fig.update_layout(
    xaxis_title='state', 
    yaxis_title='mobile banking contracts per adult', 
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig)

# 6. Comparison of different financial institutions
st.header('6. Comparison of different financial institutions')
institution_columns = ['Sucursales_banca_comercial_10mil_adultos', 
                       'Sucursales_banca_desarrollo_10mil_adultos', 
                       'Sucursales_cooperativas_10mil_adultos', 
                       'Sucursales_microfinancieras_10mil_adultos']
institution_data = df[institution_columns]

institution_colors = {
    'Sucursales_banca_comercial_10mil_adultos': '#1f77b4',
    'Sucursales_banca_desarrollo_10mil_adultos': '#ff7f0e',
    'Sucursales_cooperativas_10mil_adultos': '#2ca02c',
    'Sucursales_microfinancieras_10mil_adultos': '#d62728'
}

institution_view = st.radio('Select view', ['Individual institutions', 'Total branches'])

institution_labels = {
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial banks',
    'Sucursales_banca_desarrollo_10mil_adultos': 'Development banks',
    'Sucursales_cooperativas_10mil_adultos': 'Cooperatives',
    'Sucursales_microfinancieras_10mil_adultos': 'Microfinance institutions',
    'variable': 'Institution type'
}

if institution_view == 'Individual institutions':
    selected_institution = st.selectbox('Select institution type', 
                                      institution_columns,
                                      format_func=lambda x: institution_labels[x])
    fig = px.bar(df.sort_values(selected_institution, ascending=False), 
                 y=selected_institution,
                 title=f'{institution_labels[selected_institution]} per 10,000 adults',
                 color_discrete_sequence=[institution_colors[selected_institution]],
                 labels={
                     selected_institution: institution_labels[selected_institution],
                     "variable": ""  # This removes the "Institution type" label
                 })
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='branches per 10,000 adults', 
        height=700,
        width=1200,
        showlegend=False,  # This hides the legend for individual view
        margin=dict(l=50, r=300, t=80, b=200),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig)
else:
    df['Total_Branches'] = institution_data.sum(axis=1)
    
    # Create a new DataFrame with renamed columns for plotting
    plot_data = df[institution_columns].copy()
    plot_data.columns = [institution_labels[col] for col in institution_columns]
    
    fig = px.bar(plot_data.sort_values('Commercial banks', ascending=False), 
                 y=list(institution_labels.values())[:4],  # Only take the first 4 values (excluding 'variable')
                 title='Total financial institution branches per 10,000 adults',
                 color_discrete_map={
                     'Commercial banks': '#1f77b4',
                     'Development banks': '#ff7f0e',
                     'Cooperatives': '#2ca02c',
                     'Microfinance institutions': '#d62728'
                 })
    fig.update_layout(
        xaxis_title='state', 
        yaxis_title='branches per 10,000 adults', 
        barmode='stack', 
        height=700,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=300, t=80, b=200),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

# 7. Relationships between Various Indicators and Financial Inclusion
st.header('7. Relationships between various indicators and financial inclusion index')
df['FI_Index'] = (
    df['Sucursales_banca_comercial_10mil_adultos'] + 
    df['Cajeros_10mil_adultos'] + 
    df['Corresponsales_10mil_adultos'] +
    df[account_columns].sum(axis=1) / 1000 +
    df[credit_columns].sum(axis=1) / 1000
) / 5

df['Poblacion'] = df['Poblacion'].fillna(df['Poblacion'].median())

indicators = [
    'TPV_10mil_adultos', 
    'Sucursales_banca_comercial_10mil_adultos', 
    'Cajeros_10mil_adultos', 
    'Corresponsales_10mil_adultos', 
    'Contratos_celular_10mil_adultos'
]

indicator_labels = {
    'TPV_10mil_adultos': 'POS',
    'Sucursales_banca_comercial_10mil_adultos': 'Commercial bank branches', 
    'Cajeros_10mil_adultos': 'ATMs',
    'Corresponsales_10mil_adultos': 'Banking agents',
    'Contratos_celular_10mil_adultos': 'Mobile banking contracts'
}

for indicator in indicators:
    fig = px.scatter(
        df, 
        x=indicator, 
        y='FI_Index', 
        size='Poblacion', 
        hover_name=df.index, 
        labels={
            indicator: f'{indicator_labels[indicator]} per 10,000 adults', 
            'FI_Index': 'Financial Inclusion Index',
            'Poblacion': 'Population'
        },
        title=f'Relationship between {indicator_labels[indicator]} and Financial Inclusion Index; size = population'
    )
    st.plotly_chart(fig)

    correlation = df[indicator].corr(df['FI_Index'])
    st.write(f"*Correlation between {indicator_labels[indicator]} and Financial Inclusion Index: {correlation:.2f}*")

# 8. Top and Bottom States in Financial Inclusion
st.header('8. Financial Inclusion Index by state')

# Filter out "Sin identificar"
df_filtered = df[df.index != 'Sin identificar']

top_3_fi = df_filtered['FI_Index'].nlargest(3)
bottom_3_fi = df_filtered['FI_Index'].nsmallest(3)

st.write("Top 3 states with highest financial inclusion:")
st.write(top_3_fi)
st.write("Bottom 3 states with lowest financial inclusion:")
st.write(bottom_3_fi)

# Add bar chart for all states (excluding "Sin identificar")
fig = px.bar(df_filtered.sort_values('FI_Index', ascending=False), 
             y='FI_Index',
             title='Financial Inclusion Index by state',
             color_discrete_sequence=['#90EE90'])  # Light green color

fig.update_layout(
    xaxis_title='State',
    yaxis_title='Financial Inclusion Index',
    height=600,
    xaxis_tickangle=-45,
    showlegend=False
)

st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("Base_de_Datos_de_Inclusion_Financiera_202406 - Hoja 1.csv")
    return df

df = load_data()

year_col = "Periodo_Año"
quarter_col = "Periodo_Trimestre"

# Filter data according to rules:
df_filtered = pd.DataFrame()
for year in df[year_col].unique():
    if year == 2024:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "2T")]
    else:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "4T")]
    df_filtered = pd.concat([df_filtered, df_year], ignore_index=True)

df_filtered = df_filtered.sort_values(by=year_col)

# Convert year to string for categorical x-axis in bar charts
df_filtered[year_col] = df_filtered[year_col].astype(str)

# Adjust column selections (modify indices as per your actual data structure)
infrastructure_cols = df_filtered.columns[3:11]
infra_map = {
    "Branches": infrastructure_cols[0],
    "ATMs": infrastructure_cols[1],
    "POS": infrastructure_cols[2],
    "Places with POS": infrastructure_cols[3],
    "Banking agents (corresponsales)": infrastructure_cols[4],
    "Mobile banking contracts": infrastructure_cols[5],
    "Transactions in ATMs": infrastructure_cols[6],
    "Transactions in POS": infrastructure_cols[7]
}

captacion_types = df_filtered.columns[11:18]
captacion_total = df_filtered.columns[18]
captacion_map = {
    "Ahorro": captacion_types[0],
    "Plazo": captacion_types[1],
    "N1": captacion_types[2],
    "N2": captacion_types[3],
    "N3": captacion_types[4],
    "Tradicionales": captacion_types[5],
    "Simplificadas": captacion_types[6],
    "Total": captacion_total
}

credit_start_col = "Crédito\nBanca_Tarjeta de crédito"
credit_end_col = "Crédito\nBanca_Total"
credit_cols = df_filtered.loc[:, credit_start_col:credit_end_col].columns[:-1]
credit_total_col = df_filtered.loc[:, credit_start_col:credit_end_col].columns[-1]

credit_map = {}
for c in credit_cols:
    short_label = c.replace("Crédito\nBanca_", "").strip()
    credit_map[short_label] = c
credit_map["Total"] = credit_total_col

# EACP Captación mapping
captacion_eacp_cols = df_filtered.columns[19:23]  # Columns T to W
captacion_eacp_map = {
    "Ahorro EACP": captacion_eacp_cols[0],
    "Plazo EACP": captacion_eacp_cols[1],
    "Otras EACP": captacion_eacp_cols[2],
    "Total EACP": captacion_eacp_cols[3]
}

# EACP Crédito mapping
credito_eacp_cols = df_filtered.columns[31:37]  # Columns AF to AK
credito_eacp_map = {}
for c in credito_eacp_cols[:-1]:  # Exclude the total
    short_label = c.replace("Crédito\nEACP_", "").strip()
    credito_eacp_map[short_label] = c
credito_eacp_map["Total"] = credito_eacp_cols[-1]  # Add total separately

st.title("Financial Inclusion Analysis - Mexico, historical data")

###################################
# Infrastructure (Single Dropdown)
###################################
st.header("Infrastructure trends")
infra_choice = st.selectbox("Select type of infrastructure:", list(infra_map.keys()), index=0)

infra_col = infra_map[infra_choice]
infra_df = df_filtered[[year_col, infra_col]].copy()
# Single type: just show a bar chart with year on x and the value on y
fig_infra = px.bar(infra_df, x=year_col, y=infra_col, 
                   title=f"Infrastructure: {infra_choice}", 
                   color_discrete_sequence=["#CCCCCC"])  # Changed to light grey
fig_infra.update_layout(
    barmode='group',
    xaxis_title='year',
    yaxis_title='number of units'
)
st.plotly_chart(fig_infra, use_container_width=True)

###################################
# Captación (Single Dropdown)
###################################
st.header("Trends for 'Captación' - Banca")
capt_choice = st.selectbox("Select a type of 'Captación' (or total):", list(captacion_map.keys()), index=0)

if capt_choice == "Total":
    # Use total column directly (column S)
    capt_total_df = df_filtered[[year_col, captacion_total]].copy()
    fig_capt = px.bar(capt_total_df, x=year_col, y=captacion_total, 
                      title="Total Captación Banca",
                      color_discrete_sequence=["#1f77b4"])
    fig_capt.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt, use_container_width=True)
    st.markdown("""
        **Note:** The total is composed of:
        - Ahorro (Savings)
        - Plazo (Term deposits)
        - Tradicionales (Traditional)
        - Simplificadas (Simplified)
        
        Where N1, N2, and N3 accounts make up the Simplified accounts category.
    """)
else:
    # Single type chart remains the same
    capt_col = captacion_map[capt_choice]
    capt_df = df_filtered[[year_col, capt_col]].copy()
    fig_capt = px.bar(capt_df, x=year_col, y=capt_col, 
                      title=f"Captación: {capt_choice}",
                      color_discrete_sequence=["#1f77b4"])
    fig_capt.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt, use_container_width=True)

###################################
# Captación EACP (Single Dropdown)
###################################
st.header("Trends for 'Captación' - Entidades de Ahorro y Crédito Popular")
capt_eacp_choice = st.selectbox("Select a type of 'Captación' (or total):", list(captacion_eacp_map.keys()), index=0)

if capt_eacp_choice == "Total EACP":
    # Use column W directly
    capt_eacp_total_df = df_filtered[[year_col, captacion_eacp_map["Total EACP"]]].copy()
    fig_capt_eacp = px.bar(capt_eacp_total_df, x=year_col, y=captacion_eacp_map["Total EACP"],
                          title="Total Captación EACP",
                          color_discrete_sequence=['#2ca02c'])
    fig_capt_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt_eacp, use_container_width=True)
else:
    # Single type remains the same
    capt_eacp_col = captacion_eacp_map[capt_eacp_choice]
    capt_eacp_df = df_filtered[[year_col, capt_eacp_col]].copy()
    fig_capt_eacp = px.bar(capt_eacp_df, x=year_col, y=capt_eacp_col,
                          title=f"Captación EACP: {capt_eacp_choice}",
                          color_discrete_sequence=['#2ca02c'])
    fig_capt_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of accounts'
    )
    st.plotly_chart(fig_capt_eacp, use_container_width=True)

###################################
# Crédito (Single Dropdown)
###################################
st.header("Trends for 'Crédito' - Banca")
credit_choice = st.selectbox("Select a type of 'Crédito' (or total):", list(credit_map.keys()), index=0)

if credit_choice == "Total":
    # Use column AE directly
    credit_total_df = df_filtered[[year_col, credit_total_col]].copy()
    fig_credit = px.bar(credit_total_df, x=year_col, y=credit_total_col,
                       title="Total Crédito Banca",
                       color_discrete_sequence=["#1f77b4"])
    fig_credit.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit, use_container_width=True)
else:
    # Single type remains the same
    credit_col = credit_map[credit_choice]
    credit_df = df_filtered[[year_col, credit_col]].copy()
    fig_credit = px.bar(credit_df, x=year_col, y=credit_col,
                       title=f"Crédito: {credit_choice}",
                       color_discrete_sequence=["#1f77b4"])
    fig_credit.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit, use_container_width=True)

###################################
# Crédito EACP (Single Dropdown)
###################################
st.header("Trends for 'Crédito' - Entidades de Ahorro y Crédito Popular")
# Modify the map to only include AF to AI and total AJ
credito_eacp_map = {}
for c in credito_eacp_cols[0:4]:  # Only take AF to AI
    short_label = c.replace("Crédito\nEACP_", "").strip() + " EACP"
    credito_eacp_map[short_label] = c
credito_eacp_map["Total EACP"] = credito_eacp_cols[-2]  # Add AJ as total

credit_eacp_choice = st.selectbox("Select a type of 'Crédito' (or total):", list(credito_eacp_map.keys()), index=0)

if credit_eacp_choice == "Total EACP":
    # Use column AJ directly
    credit_eacp_total_col = credito_eacp_cols[-2]  # This is column AJ
    credit_eacp_total_df = df_filtered[[year_col, credit_eacp_total_col]].copy()
    fig_credit_eacp = px.bar(credit_eacp_total_df, x=year_col, y=credit_eacp_total_col,
                            title="Total Crédito EACP",
                            color_discrete_sequence=['#2ca02c'])
    fig_credit_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit_eacp, use_container_width=True)
else:
    # Single type remains the same
    credit_eacp_col = credito_eacp_map[credit_eacp_choice]
    credit_eacp_df = df_filtered[[year_col, credit_eacp_col]].copy()
    fig_credit_eacp = px.bar(credit_eacp_df, x=year_col, y=credit_eacp_col,
                            title=f"Crédito: {credit_eacp_choice}",
                            color_discrete_sequence=['#2ca02c'])
    fig_credit_eacp.update_layout(
        xaxis_title='year',
        yaxis_title='number of credits'
    )
    st.plotly_chart(fig_credit_eacp, use_container_width=True)

###################################
# Gender Analysis - Cards
###################################
st.header("Gender Analysis - Debit and Credit Cards")

# Filter data according to rules (4T except 2024 which is 2T)
df_gender = pd.DataFrame()
for year in df[year_col].unique():
    if year == 2024:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "2T")]
    else:
        df_year = df[(df[year_col] == year) & (df[quarter_col] == "4T")]
    df_gender = pd.concat([df_gender, df_year], ignore_index=True)

# Create DataFrames for debit and credit cards
debit_data = pd.DataFrame({
    'Year': df_gender[year_col],
    'Women': df_gender.iloc[:, 46].str.replace(',', '').astype(float),
    'Men': df_gender.iloc[:, 47].str.replace(',', '').astype(float)
})

credit_data = pd.DataFrame({
    'Year': df_gender[year_col],
    'Women': df_gender.iloc[:, 49].str.replace(',', '').astype(float),
    'Men': df_gender.iloc[:, 50].str.replace(',', '').astype(float)
})

# Filter from 2018 onwards and sort
debit_data = debit_data[debit_data['Year'] >= 2018].sort_values('Year')
credit_data = credit_data[credit_data['Year'] >= 2018].sort_values('Year')

# Calculate percentages for debit cards
debit_data['Total'] = debit_data['Men'] + debit_data['Women']
debit_data['Men %'] = (debit_data['Men'] / debit_data['Total'] * 100).round(1)
debit_data['Women %'] = (debit_data['Women'] / debit_data['Total'] * 100).round(1)

# Calculate percentages for credit cards
credit_data['Total'] = credit_data['Men'] + credit_data['Women']
credit_data['Men %'] = (credit_data['Men'] / credit_data['Total'] * 100).round(1)
credit_data['Women %'] = (credit_data['Women'] / credit_data['Total'] * 100).round(1)

# Debit Cards Analysis
st.subheader("Debit cards by gender")

# Line chart for debit cards (separate lines for men and women)
fig_debit_line = px.line(debit_data, x='Year', y=['Women', 'Men'],
                    title='Debit cards by gender over time',
                    color_discrete_map={'Women': '#ff7f0e', 'Men': '#1f77b4'})
fig_debit_line.update_layout(
    xaxis_title='year',
    yaxis_title='number of cards',
    legend_title='gender'
)
st.plotly_chart(fig_debit_line, use_container_width=True)

# Stacked bar chart for debit cards (percentages)
fig_debit_bar = px.bar(debit_data, x='Year', y=['Women %', 'Men %'],
                       title='Debit cards by gender over time (% distribution)',
                       color_discrete_map={'Women %': '#ff7f0e', 'Men %': '#1f77b4'})
fig_debit_bar.update_layout(
    xaxis_title='year',
    yaxis_title='percentage',
    barmode='stack',
    legend_title='gender',
    yaxis_range=[0, 100]  # Force y-axis to be 0-100%
)
st.plotly_chart(fig_debit_bar, use_container_width=True)

# Credit Cards Analysis
st.subheader("Credit cards by gender")

# Line chart for credit cards (separate lines for men and women)
fig_credit_line = px.line(credit_data, x='Year', y=['Women', 'Men'],
                     title='Credit cards by gender over time',
                     color_discrete_map={'Women': '#ff7f0e', 'Men': '#1f77b4'})
fig_credit_line.update_layout(
    xaxis_title='year',
    yaxis_title='number of cards',
    legend_title='gender'
)
st.plotly_chart(fig_credit_line, use_container_width=True)

# Stacked bar chart for credit cards (percentages)
fig_credit_bar = px.bar(credit_data, x='Year', y=['Women %', 'Men %'],
                        title='Credit cards by gender over time (% distribution)',
                        color_discrete_map={'Women %': '#ff7f0e', 'Men %': '#1f77b4'})
fig_credit_bar.update_layout(
    xaxis_title='year',
    yaxis_title='percentage',
    barmode='stack',
    legend_title='gender',
    yaxis_range=[0, 100]  # Force y-axis to be 0-100%
)
st.plotly_chart(fig_credit_bar, use_container_width=True)
# Footer
st.markdown(
    'Made by [Valentin Mendez](https://www.linkedin.com/in/valentemendez/) using information from the [CNBV](https://datos.gob.mx/busca/organization/2a93da6c-8c17-4671-a334-984536ac9d61?tags=inclusion)'
)

# Hide the "Made with Streamlit" footer
hide_streamlit_style = """
<style>
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)