
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
    'CO': 4  # mg/m3 maximum daily 8-hour mean (or your approximation for annual average)
}

@st.cache
def load_data():
    # Make sure this URL is the raw version of the file on GitHub
    url = 'https://raw.githubusercontent.com/JesHP73/plotAQEU/main/eu_dataset_cleaned/aggregated_data_eu_air_quality.csv'
    response = requests.get(url)
    if response.status_code == 200:
        csv_raw = StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_raw)
        df['WHO Guideline'] = df['air_pollutant'].map(lambda x: who_guidelines.get(x, 0))
        return df
    else:
        response.raise_for_status()

try:
    plot_data = load_data()
except requests.exceptions.HTTPError as e:
    st.error(f'Error fetching the CSV file: {e}')

# If the data is loaded correctly, then proceed with plotting
if 'plot_data' in locals():
    # Streamlit app layout
    st.title('Top Countries Exceeding WHO Air Pollutant Levels (AQI)')

    # Create subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar plot for each air pollutant
    for pollutant in plot_data['air_pollutant'].unique():
        subset = plot_data[plot_data['air_pollutant'] == pollutant]
        fig.add_trace(go.Bar(x=subset['country'], 
                             y=subset['AQI_Index'], 
                             name=pollutant),
                      secondary_y=False)

    # Add scatter plot for WHO guidelines
    fig.add_trace(go.Scatter(x=plot_data['country'], 
                             y=plot_data['WHO Guideline'], 
                             mode='lines+markers', 
                             name='WHO Guideline', 
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

