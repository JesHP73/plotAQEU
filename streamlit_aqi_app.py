
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import requests
from io import StringIO

# Load your data
plot_aqi_df = pd.read_csv('https://raw.githubusercontent.com/JesHP73/plotAQEU/2cd8420dd7027b74a520eb8eac04a36ca9cb705b/plot_aqi_df.csv')

# Calculate the mean AQI per year for each country
mean_aqi_per_country = plot_aqi_df.groupby(['year', 'country'])['AQI'].mean().reset_index()
mean_aqi_per_country['year'] = pd.to_datetime(mean_aqi_per_country['year'], format='%Y')

# List of all countries
all_countries = mean_aqi_per_country['country'].unique().tolist()

# Streamlit app layout
st.title('Air Quality Index 1990-2023')
st.write('Select country:')

# Dropdown for country selection
selected_countries = st.multiselect(
    'Select country',
    options=['All'] + all_countries,
    default=['All']
)

# Function to filter data based on selection
def filter_data(selection):
    if 'All' in selection:
        filtered_data = mean_aqi_per_country.groupby('year')['AQI'].mean().reset_index()
        filtered_data['country'] = 'All Countries'
    else:
        filtered_data = mean_aqi_per_country[mean_aqi_per_country['country'].isin(selection)]
    return filtered_data

# Display the chart
def display_chart(data):
    fig = px.line(data, x='year', y='AQI', color='country',
                  title='Average EU AQI per Year by Selected Country(s)')
    st.plotly_chart(fig, use_container_width=True)

# Filter and display data
filtered_data = filter_data(selected_countries)
display_chart(filtered_data)


# Define the WHO guideline values
who_guidelines = {
    'NO2': 10,  # µg/m3 annual average
    'PM10': 15,  # µg/m3 annual average
    'O3': 60,  # µg/m3 maximum daily 8-hour mean
    'PM2.5': 5,  # µg/m3 annual average
    'CO': 4  # mg/m3 maximum daily 8-hour mean
}

@st.cache(show_spinner=False)
def load_data():
    url = 'https://raw.githubusercontent.com/JesHP73/plotAQEU/main/eu_dataset_cleaned/aggregated_data_eu_air_quality.csv'
    data = pd.read_csv(url)
    data['WHO Guideline'] = data['air_pollutant'].map(lambda x: who_guidelines.get(x, 0))
    return data

# Load your data
try:
    df = load_data()
except Exception as e:
    st.error(f"An error occurred while loading the data: {e}")
    st.stop()

# Check if the dataframe is loaded and has the expected columns
if df is not None and all(col in df.columns for col in ['country', 'air_pollutant', 'AQI_Index']):
    # Streamlit app layout
    st.title('Top Countries Exceeding WHO Air Pollutant Levels (AQI)')

    # Create subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar plot for each air pollutant
    for pollutant in df['air_pollutant'].unique():
        subset = df[df['air_pollutant'] == pollutant]
        fig.add_trace(go.Bar(x=subset['country'], 
                             y=subset['AQI_Index'], 
                             name=pollutant),
                      secondary_y=False)

    # Add scatter plot for WHO guidelines
    # Note that this will add a line for each country, you might need to adjust this logic
    for country in df['country'].unique():
        country_data = df[df['country'] == country]
        fig.add_trace(go.Scatter(x=country_data['country'], 
                                 y=country_data['WHO Guideline'], 
                                 mode='lines+markers', 
                                 name='WHO Guideline - ' + country,
                                 marker=dict(color='red', size=10)),
                      secondary_y=False)

    # Update layout
    fig.update_layout(title_text='Top Countries Exceeding WHO Air Pollutant Levels (AQI)',
                      xaxis_title='Country',
                      yaxis_title='Air Quality Index (AQI)',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # Rotate x-axis labels
    fig.update_xaxes(tickangle=45)

    # Display the plot in the Streamlit app
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("The data frame is empty or the necessary columns are missing.")


