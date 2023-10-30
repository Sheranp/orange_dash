import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime
from google.oauth2.service_account import Credentials
import gspread

st.set_page_config(layout="wide")
st.title('Inbound_DashBoard1')

# Load your data
creds = Credentials.from_service_account_file('orange-dashboard23-55c5d80f6565.json')
gc = gspread.service_account(filename='orange-dashboard23-55c5d80f6565.json')
sh = gc.open('Orange_dashboard')
worksheet = sh.get_worksheet(0)  # You may need to specify the correct worksheet

data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Date Range Selector
start_date = st.date_input('Start Date', datetime.date(2023, 10, 7))
end_date = st.date_input('End Date', datetime.date(2023, 10, 7))

start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date)
df['date'] = pd.to_datetime(df['date'])

# Filter the data
filtered_data = df[(df['date'] >= start_datetime) & (df['date'] <= end_datetime)]
#filtered_data['Unnamed: 60'] = pd.to_datetime(filtered_data['Unnamed: 60'], errors='coerce')

# Handle non-numeric values in 'day cbm' column
filtered_data['day cbm'] = pd.to_numeric(filtered_data['day cbm'], errors='coerce')
day_cbm = filtered_data['day cbm'].sum()

# Create a row with three columns for the pie charts
#st.subheader('Difference in vehicle arrivals, Planning Unloading Time, Planning Separate Time')
col1, col2, col3 = st.columns(3)

# Vehicle Pie Chart
vehicle_pie_chart_data = filtered_data['arrived Crossed or Within time'].value_counts()
col1.subheader('Difference in vehicle arrivals')
col1.plotly_chart(go.Figure(data=[go.Pie(labels=vehicle_pie_chart_data.index, values=vehicle_pie_chart_data.values)], layout={'height': 450, 'width': 350}))

# Unloading Pie Chart
unloading_pie_chart_data = filtered_data['unloading Crossed or Within time'].value_counts()
col2.subheader('Planning Unloading Time')
col2.plotly_chart(go.Figure(data=[go.Pie(labels=unloading_pie_chart_data.index, values=unloading_pie_chart_data.values)], layout={'height': 450, 'width': 350}))

# Separate Pie Chart
separate_pie_chart_data = filtered_data['Separate Crossed or Within time'].value_counts()
col3.subheader('Planning Separate Time')
col3.plotly_chart(go.Figure(data=[go.Pie(labels=separate_pie_chart_data.index, values=separate_pie_chart_data.values)], layout={'height': 450, 'width': 350}))


col4, col5,col6, = st.columns(3)

# Putaway Pie Chart
putaway_pie_chart_data = filtered_data['Putaway Crossed or Within time'].value_counts()
col4.subheader('Planning Putaway Time')
col4.plotly_chart(go.Figure(data=[go.Pie(labels=putaway_pie_chart_data.index, values=putaway_pie_chart_data.values)], layout={'height': 450, 'width': 350}))

# Job Finish Pie Chart
jobfinish_pie_chart_data = filtered_data['Job Crossed or Within time'].value_counts()
col5.subheader('Planning Job Finish Time')
col5.plotly_chart(go.Figure(data=[go.Pie(labels=jobfinish_pie_chart_data.index, values=jobfinish_pie_chart_data.values)], layout={'height': 450, 'width': 350}))


full_cbm = filtered_data['full cbm'].sum()
actual_cbm = filtered_data['Actual CBM'].sum()
day_cbm = filtered_data['day cbm'].sum()
value12 = (full_cbm - actual_cbm) / day_cbm
colors = ['#FF5733', '#33FF57']
fig = go.Figure(data=[go.Pie(
    labels=['Planning CBM', 'Received CBM'],
    values=[full_cbm - actual_cbm, actual_cbm],
    hole=0.4,
    marker=dict(colors=colors) 
)])
fig.update_layout(height=450, width=350)  
col6.subheader('Receiving Planning CBM')
center_text = f"<span style='font-size: 18px; font-weight: bold;'>{value12:.2f}</span>"
fig.add_annotation(
    text=center_text,
    x=0.5,  
    y=0.5, 
    showarrow=False,
)
formatted_value = f"<span style='font-size: 18px; font-weight: bold;'>Need to days: {value12:.2f}</span>"
col6.plotly_chart(fig)
col6.write(formatted_value, unsafe_allow_html=True)






# Your data table
st.subheader('Daily Summary Table')
def highlight_crossed_rows(s):
    is_crossed = s == 'Crossed'
    return [f"background-color: red" if crossed else "" for crossed in is_crossed]

styled_data = filtered_data.style.apply(highlight_crossed_rows, subset=['arrived Crossed or Within time',\
'unloading Crossed or Within time','Separate Crossed or Within time','Putaway Crossed or Within time',\
'Job Crossed or Within time'], axis=1)
st.dataframe(styled_data)

# Check the app theme
theme = st.get_option("theme.primaryColor")

# Define the CSS based on the theme
css = f"""
<style>
    /* Light mode header color */
    .streamlit-dataframe th {{
        background-color: {'lightblue' if theme == 'light' else 'darkgray'};
        color: {'black' if theme == 'light' else 'white'};
    }}
</style>
"""

# Inject the CSS
st.markdown(css, unsafe_allow_html=True)



# Button to toggle visibility
if st.button("More Details"):
    st.session_state.show_details = not st.session_state.show_details if 'show_details' in st.session_state else True



# Hockey Stats Chart and Summary Table
if st.session_state.get('show_details', False):
    date_values = filtered_data['Type of lorry']
    delay_point = filtered_data['Delay point']
    customer_schedule = filtered_data['Customer schedule']
    dock_in_time = filtered_data['Dock in time']

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(x=date_values, y=delay_point, name='Delay point', marker_color='orange'))
    fig.add_trace(go.Bar(x=date_values, y=customer_schedule, name='Customer schedule', marker_color='blue'))
    fig.add_trace(go.Bar(x=date_values, y=dock_in_time, name='Dock in time', marker_color='green'))

    fig.update_xaxes(title_text='Type of Lorry')
    fig.update_yaxes(title_text='Time')
    fig.update_layout(
        barmode='group',
        height=400,
        width=600,
        margin=dict(l=10, r=10, b=10, t=80),
        title_text='Difference in vehicle arrivals Table',
        title_font=dict(size=20, color='black')
    )

    st.subheader('Hockey Stats')
    st.plotly_chart(fig)

    # Summary Table
    table_data = filtered_data.groupby('Type of lorry').agg({'Delay point': 'sum', 'unloading reson': 'first'}).reset_index()
    st.subheader('Summary Table')
    st.dataframe(table_data)



# Define the custom footer HTML
custom_footer_html = """
                <style>
                footer {visibility: hidden;}
                footer:after{
                content:'Shey_int @ 2023 All right reserved';
                display:block;
                position:relative;
                color:tomato;
                }
                </style>
                """

# Display the custom footer
st.markdown(custom_footer_html, unsafe_allow_html=True)
