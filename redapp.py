import streamlit as st
import pandas as pd
import numpy as np
#import pymysql
import mysql.connector


def create_con():

    return mysql.connector.connect(host='127.0.0.1',user='root',passwd='',database='redbus')
#pymysql.connect(host='127.0.0.1',user='root',passwd='',database='redbus')
# Initialize session state for selected filters
if 'selected_price' not in st.session_state:
    st.session_state.selected_price = 'Anything'
if 'selected_star' not in st.session_state:
    st.session_state.selected_star = 'All'
if 'selected_departure' not in st.session_state:
    st.session_state.selected_departure = 'Anything'
if 'selected_arrival' not in st.session_state:
    st.session_state.selected_arrival = 'Anything'
if 'selected_duration' not in st.session_state:
    st.session_state.selected_duration = 'Anything'

# Function to fetch data from the database
def fetch_data(query,params=None):
    connection = create_con()
    if params is None:
        params=()
    df= pd.read_sql(query,connection,params=None)
    connection.close()
    return df

# Fetch initial data to populate filters
initial_query = "SELECT * FROM redbus.bus_routes"
initial_data = fetch_data(initial_query)

# Handle NaN values in the 'duration' column by filling with 0
initial_data['duration'] = initial_data['duration'].str.extract(r'(\d+)').astype(float).fillna(0).astype(int)

# Streamlit app layout
st.title('Redbus Routes Data Filtering and Analysis')

# Bustype Filter
bustype_options = np.append(['Anything'], initial_data['bustype'].unique())
bustype_filter = st.multiselect('Select Bus Type:', options=bustype_options)

# Route Filter
route_options = np.append(['Anything'], initial_data['route_name'].unique())
route_filter = st.multiselect('Select Route:', options=route_options)

# Price Range Filter
st.write('Select Price Range:')
price_columns = st.columns(6)
price_range = st.session_state.selected_price
price_options = ['Anything', '0-250', '250-500', '500-1000', '1000-1500', '1500+']
for i, price_option in enumerate(price_options):
    button_style = 'background-color: lightgreen;' if price_option == price_range else ''
    if price_columns[i].button(price_option, key=f'price_{price_option}', help=f'Select {price_option}', on_click=lambda p=price_option: setattr(st.session_state, 'selected_price', p)):
        st.session_state.selected_price = price_option

price_filter_map = {
    'Anything': (initial_data['price'].min(), initial_data['price'].max()),
    '0-250': (0, 250),
    '250-500': (250, 500),
    '500-1000': (500, 1000),
    '1000-1500': (1000, 1500),
    '1500+': (1500, initial_data['price'].max())
}
price_filter = price_filter_map[st.session_state.selected_price]

# Star Rating Filter
st.write('Select Star Rating:')
star_rating_filter = st.slider('Star Rating', 0.0, 5.0, (0.0, 5.0), 0.1)
star_filter = None if star_rating_filter == (0.0, 5.0) else star_rating_filter

# Seat Availability Filter
availability_options = ['Anything'] + [str(i) for i in range(0, int(initial_data['seats_available'].max()) + 1)]
availability_filter = st.selectbox('Select Minimum Seat Availability:', availability_options, key='seat_availability_filter')
availability_filter = None if availability_filter == 'Anything' else int(availability_filter)

# Departure Time Filter
st.write('Select Departure Time Range:')
departure_time_columns = st.columns(5)
departure_time_range = st.session_state.selected_departure
departure_options = ['Anything', '0-6', '6-12', '12-18', '18-24']
for i, departure_option in enumerate(departure_options):
    button_style = 'background-color: lightgreen;' if departure_option == departure_time_range else ''
    if departure_time_columns[i].button(departure_option, key=f'departure_{departure_option}', help=f'Select {departure_option}', on_click=lambda d=departure_option: setattr(st.session_state, 'selected_departure', d)):
        st.session_state.selected_departure = departure_option

departure_time_map = {
    'Anything': (0, 24),
    '0-6': (0, 6),
    '6-12': (6, 12),
    '12-18': (12, 18),
    '18-24': (18, 24)
}
departure_filter = departure_time_map[st.session_state.selected_departure]

# Arrival Time Filter
st.write('Select Arrival Time Range:')
arrival_time_columns = st.columns(5)
arrival_time_range = st.session_state.selected_arrival
arrival_options = ['Anything', '0-6', '6-12', '12-18', '18-24']
for i, arrival_option in enumerate(arrival_options):
    button_style = 'background-color: lightgreen;' if arrival_option == arrival_time_range else ''
    if arrival_time_columns[i].button(arrival_option, key=f'arrival_{arrival_option}', help=f'Select {arrival_option}', on_click=lambda a=arrival_option: setattr(st.session_state, 'selected_arrival', a)):
        st.session_state.selected_arrival = arrival_option

arrival_time_map = {
    'Anything': (0, 24),
    '0-6': (0, 6),
    '6-12': (6, 12),
    '12-18': (12, 18),
    '18-24': (18, 24)
}
arrival_filter = arrival_time_map[st.session_state.selected_arrival]

# Duration Filter
st.write('Select Duration Range (in hours):')
duration_columns = st.columns(5)
duration_range = st.session_state.selected_duration
duration_options = ['Anything', '0-2', '2-4', '4-6', '6+']
for i, duration_option in enumerate(duration_options):
    button_style = 'background-color: lightgreen;' if duration_option == duration_range else ''
    if duration_columns[i].button(duration_option, key=f'duration_{duration_option}', help=f'Select {duration_option}', on_click=lambda d=duration_option: setattr(st.session_state, 'selected_duration', d)):
        st.session_state.selected_duration = duration_option

duration_map = {
    'Anything': (0, initial_data['duration'].max()),
    '0-2': (0, 2),
    '2-4': (2, 4),
    '4-6': (4, 6),
    '6+': (6, initial_data['duration'].max())
}
duration_filter = duration_map[st.session_state.selected_duration]

# Build the query based on filters
query = "SELECT * FROM bus_routes WHERE 1=1"

if bustype_filter and 'Anything' not in bustype_filter:
    bustype_filter_str = ",".join([f"'{b}'" for b in bustype_filter])
    query += f" AND bustype IN ({bustype_filter_str})"

if route_filter and 'Anything' not in route_filter:
    route_filter_str = ",".join([f"'{r}'" for r in route_filter])
    query += f" AND route_name IN ({route_filter_str})"

query += f" AND price BETWEEN {price_filter[0]} AND {price_filter[1]}"

if availability_filter is not None:
    query += f" AND seats_available >= {availability_filter}"

if star_filter is not None:
    query += f" AND star_rating BETWEEN {star_filter[0]} AND {star_filter[1]}"

query += f" AND HOUR(departing_time) BETWEEN {departure_filter[0]} AND {departure_filter[1]}"
query += f" AND HOUR(reaching_time) BETWEEN {arrival_filter[0]} AND {arrival_filter[1]}"
query += f" AND duration BETWEEN {duration_filter[0]} AND {duration_filter[1]}"

# Fetch filtered data
filtered_data = fetch_data(query)

# Display filtered data
st.write('Filtered Data:')
st.dataframe(filtered_data)

# Add a download button to export the filtered data
if not filtered_data.empty:
    st.download_button(
        label="Download Filtered Data",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv"
    )
else:
    st.warning("No data available with the selected filters.")
