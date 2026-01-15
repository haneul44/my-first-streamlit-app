#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:23:35 2026

@author: dina
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# dashboard page and title creation
st.set_page_config(page_title="US Agricaltural Exports 2011", 
                   page_icon=":seedling:", layout="wide")
st.title(":seedling: US Agricaltural Exports in 2011")

#reading the data 
link = "https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv"
df=pd.read_csv(link)

# create a download button for the original dataset
st.download_button("Download the data in csv format", data=df.to_csv(),
                   file_name='us_agg_2011.csv')

# cleaning the data
df.drop("category", axis=1, inplace=True)
df.rename(columns={'total fruits':'fruits', 'total veggies':'veggies', 
                   'total exports': 'total'}, 
          inplace=True)
categories = ['beef', 'pork', 'poultry', 'dairy', 'fruits', 'veggies', 
              'corn', 'wheat', 'cotton']
df['misc.'] = df['total'] - df[categories].sum(axis=1)
#df.sort_values('code', inplace=True)
categories.append('misc.')
df_cat = pd.melt(frame=df, id_vars=['code', 'state'], 
                value_vars=categories, var_name='category', value_name='export')


# adding a sidebar for the filters with a title
# Sidebar for choropleth category selection

st.sidebar.header("Filter Data by Export Category: ")

# Filter functionality for choropleth using a select box in the side bar
# Create a new list of categories with 'total exports' as the first element
choropleth_categories = ['total'] + categories
choropleth_category = st.sidebar.selectbox("Select Category for Choropleth Map:",
                                            choropleth_categories,
                                            index=0  # this is my default setting; first element is total imports
                                          )

# figure 1: choropleth
fig = px.choropleth(data_frame=df,
                    locationmode='USA-states',
                    locations='code',
                    scope="usa",
                    color=choropleth_category,
                    hover_name="state",
                    hover_data= choropleth_category,
                    color_continuous_scale=px.colors.sequential.Greens,
                    height=700
                    )

# creating a dynamic title
coro_title = choropleth_category.title()+' Exports in Million USD'

# customization of choropleth color bar
fig.update_layout(coloraxis_colorbar= dict(title=coro_title, len=0.7, thickness=50))

# display figure in dashboard
st.plotly_chart(fig, use_container_width=True)


# Add another side bar header
st.sidebar.header("Filter Data by State(s): ")

# Add multi-select filter for states
states = ['All States'] + df['state'].tolist()
state_list = st.sidebar.multiselect("Choose State(s) for Tree Chart, Bar Chart", 
                                    options=states, 
                                    default=['All States'])
formatted_states = ", ".join(state_list)

# logic for the state selection: filter the wide and long dataframes by chosen states
if state_list==['All States']:
    df_states=df.copy() # wide format
    df_cat_states = df_cat.copy() # long format
else:
    df_states=df.loc[df["state"].isin(state_list), :]
    df_cat_states = df_cat.loc[df_cat['state'].isin(state_list), :]
 


# Figure 2: Treemap of selected states 
#st.subheader("Exports Breakdown By Category - "+formatted_states)
tree_title = "Exports Breakdown By Category - "+formatted_states

# connecting the front end state selection with the treemap


fig = px.treemap(data_frame=df_cat_states, 
                 path=['state', 'category'], values='export', 
                 color='category',
                 title=tree_title,
                 height=700, 
                 color_discrete_sequence=px.colors.qualitative.Safe)
# display figure in dashboard
st.plotly_chart(fig, use_container_width=True)



# Figures 3 and 4

# dasboard columns creation
col1, col2 = st.columns((2))

# Figure 2: total exports by state in a bar chart for chosen states
with col1:
    st.subheader("Total Exports - "+formatted_states)
    df_states.sort_values('total', inplace=True)
    
    fig=px.bar(data_frame=df_states, y='code', x="total", hover_name="state",
               color_discrete_sequence=px.colors.qualitative.Safe,
               labels={'code': 'State', 'total':'Total Exports in Million USD'},
               height=700)
    st.plotly_chart(fig, use_container_width=True)
