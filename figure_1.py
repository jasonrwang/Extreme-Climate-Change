# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 13:32:12 2020

@author: Florian Jehn and Jason R. Wang
"""

import pandas as pd
import altair as alt
import numpy as np
from scipy import interpolate
import os

# # Import Wagner and Weitzmann Data

dfWW2015 = pd.DataFrame();

# def importWagnerWeitzmann():
#     '''
#     Simple function to append a formatted Wagner-Weitzmann curve to a Pandas df.
#     '''

# Generate list with all the relevant files
dataFolder = './Data/'
files = [file for file in os.listdir(dataFolder)]

for file in files:
    # Extract the PPM value
    print(file)
    ppm = file.split('.csv')[0].split('_')[-1].split('ppm')[0]
    df = pd.read_csv(dataFolder+file,';')
    df['ppm'] = ppm
    dfWW2015 = dfWW2015.append(df)

dfWW2015 = dfWW2015.rename(columns={'x':'Temperature Change','y':'Probability'})

dfWW2015 = dfWW2015.reset_index(drop=True)

# ## Import Counts and Format

# +
# Read in the data
ipcc_counts = pd.read_csv("Results" + os.sep + "temp_counts_all.csv", sep=";", index_col=0)
counts_1_5_report = pd.read_csv("Results" + os.sep + "counts_SR15_Full_Report_High_Res.csv", sep=";",index_col=0)
    
# Replace the spaces in the temperature description
ipcc_counts.index = ipcc_counts.index.str.replace(" ","").str.replace('°C','')
counts_1_5_report.index = counts_1_5_report.index.str.replace(" ","").str.replace('°C','')

ipcc_counts = ipcc_counts.reset_index().rename(columns={'index':'Temperature Change','0':'Count'})
counts_1_5_report = counts_1_5_report.reset_index().rename(columns={'index':'Temperature Change','0':'Count'})

dfCounts = pd.DataFrame(ipcc_counts)
dfCounts['Type'] = 'All'

dfSR15 = pd.DataFrame(counts_1_5_report)
dfSR15['Type'] = 'SR15'

# Subtract out results with SR15 from all
dfnoSR15 = pd.DataFrame(dfCounts.set_index('Temperature Change')['Count'] - dfSR15.set_index('Temperature Change')['Count'])
dfnoSR15['Type'] = 'NoSR15'
dfnoSR15 = dfnoSR15.reset_index()

# Merge all types
dfCounts = dfCounts.append(dfSR15).append(dfnoSR15)
# -

# ## Plot

# Combine data from counts and probability.

dfCounts['ppm'] = np.nan
dfCounts['Probability'] = np.nan
dfWW2015['Type'] = np.nan
dfWW2015['Count'] = np.nan

dfCombined = dfCounts.append(dfWW2015)

dfCombined['ppm'] = dfCombined['ppm'].astype('float')

dfCombined['Temperature Change'] = dfCombined['Temperature Change'].astype('float')

# +
base = alt.Chart(dfCombined).mark_bar().encode(
    x=alt.X('Temperature Change:O',title='Temperature Change (ºC)'),
    y='Count:Q'
).transform_filter(
    alt.datum.Type=='All'
)

line = alt.Chart(dfCombined).mark_line(opacity=0.6).encode(
    x=alt.X('Temperature Change:Q', axis=None),
    y=alt.Y('Probability:Q',sort=['-ppm']),
    color=alt.Color('ppm:N',scale=alt.Scale(scheme='dark2')),
).transform_filter(
    alt.datum.Type!='All'
)

alt.layer(base, line).resolve_scale(
    y='independent'
).properties(width=600)
# -
# Again without SR1.5

# +
base = alt.Chart(dfCombined).mark_bar().encode(
    x=alt.X('Temperature Change:O',title='Temperature Change (ºC)'),
    y='Count:Q'
).transform_filter(
    alt.datum.Type=='NoSR15'
)

line = alt.Chart(dfCombined).mark_line(opacity=0.6).encode(
    x=alt.X('Temperature Change:Q', axis=None),
    y=alt.Y('Probability:Q',sort=['-ppm']),
    color=alt.Color('ppm:N',scale=alt.Scale(scheme='dark2')),
).transform_filter(
    alt.datum.Type!='All'
)

alt.layer(base, line).resolve_scale(
    y='independent'
).properties(width=600)
# -

# And now with SR15 and without stacked

dfCombined['Type'].unique()

# +
base = alt.Chart(dfCombined).mark_bar().encode(
    x=alt.X('Temperature Change:O',title='Temperature Change (ºC)'),
    y='Count:Q',
    color=alt.Color('Type:N',legend=alt.Legend(orient='left'))
).transform_filter(
    (alt.datum.Type=='NoSR15') | (alt.datum.Type=='SR15')
)
base

line = alt.Chart(dfCombined).mark_line(opacity=0.6).encode(
    x=alt.X('Temperature Change:Q', axis=None),
    y=alt.Y('Probability:Q',sort=['-ppm']),
    color=alt.Color('ppm:N',scale=alt.Scale(scheme='dark2'),legend=alt.Legend(orient='right')),
).transform_filter(
    alt.datum.Type!='All'
)

alt.layer(base, line).resolve_scale(
    y='independent'
).properties(width=600)
# -


