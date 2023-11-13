
import streamlit as st
import pandas as pd
import plotly.express as px

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
