import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from openai import OpenAI, OpenAIError
     
client = OpenAI(api_key='your-api-key-here')
import time
         
# Replace with your OpenAI API key

# Set the title and introduction
st.set_page_config(page_title="📈 Mutual Fund Data Analysis", page_icon=":bar_chart:")
st.title("📊 Mutual Fund Data Analysis")
st.write("Upload 5 CSV files and do Analysis on them")

# Upload CSV files
uploaded_files = st.file_uploader("Choose 5 CSV files", type=["csv"], accept_multiple_files=True)

dfs = []
file_names = []
for uploaded_file in uploaded_files:
    dfs.append(pd.read_csv(uploaded_file))
    file_names.append(uploaded_file.name)

if uploaded_files:
    # Calculate geometric and arithmetic means
    gm_values = []
    am_values = []
    for df in dfs:
        adj_close_values = df['Adj Close']
        gm = np.exp(np.mean(np.log(adj_close_values)))
        am = np.mean(adj_close_values)
        gm_values.append(gm)
        am_values.append(am)

    # Find the highest means
    max_gm_index = np.argmax(gm_values)
    max_am_index = np.argmax(am_values)
    highest_file_name_gm = file_names[max_gm_index]
    highest_file_name_am = file_names[max_am_index]

    # Create an input box for user prompts
    st.write("## 🤖 Chat with AI")
    user_prompt = st.text_area("Enter a prompt for analysis:", value="Calculate the trend in the data.")
    generate_button = st.button("Generate Analysis")

    # Add loading animation when Generate Analysis button is clicked
    if generate_button:
        with st.spinner("Generating analysis..."):
            time.sleep(6)

        # Combine user prompt with uploaded data information
        prompt = f"User Prompt: {user_prompt}\n"
        data_info = ""
        for file_name, gm, am in zip(file_names, gm_values, am_values):
            data_info += f"{file_name[:-4]} - Geometric Mean: {gm:.4f}, Arithmetic Mean: {am:.2f}\n"

        # Combine user prompt and data information for OpenAI
        combined_prompt = prompt + "Data Information:\n" + data_info

        try:
            # Generate response from OpenAI
            response = client.completions.create(model="text-davinci-003",
                                                 prompt=combined_prompt,
                                                 max_tokens=500)

            # Display OpenAI response
            st.subheader("AI Output")
            st.write(response.choices[0].text)

        except OpenAIError as e:
            if e.error_code == "insufficient_quota":
                st.error("OpenAI API usage limit exceeded. Please try again later.")
            else:
                st.error(f"OpenAI API error: {e}")

    # Display the highest means and Adj Close price in colored boxes
    st.sidebar.title("🔝 Top Fund")

    highest_name_html = f'<p style="text-align: left; font-size: 26px; color: green; font-weight: bold;">{highest_file_name_gm[:-4]}</p>'
    st.sidebar.markdown(highest_name_html, unsafe_allow_html=True)
    st.sidebar.markdown(f"**Geometric Mean:** {gm_values[max_gm_index]:.4f}")
    st.sidebar.markdown(f"**Arithmetic Mean:** {am_values[max_gm_index]:.2f}")

    highest_price = dfs[max_gm_index]['Adj Close'].max()
    st.sidebar.markdown(f"**Adj Close Price:** {highest_price:.2f}")

    # Create buttons to display means for all companies
    display_geometric = st.sidebar.button("📈 Display Geometric Means")
    display_arithmetic = st.sidebar.button("📊 Display Arithmetic Means")

    unique_file_names = list(set(file_names))
    unique_file_names.sort()

    if display_geometric:
        st.sidebar.subheader("Geometric Means for All Companies")
        for file_name in unique_file_names:
            idx = file_names.index(file_name)
            st.sidebar.write(f"{file_name[:-4]}: Geometric Mean: {gm_values[idx]:.4f}")

    if display_arithmetic:
        st.sidebar.subheader("Arithmetic Means for All Companies")
        for file_name in unique_file_names:
            idx = file_names.index(file_name)
            st.sidebar.write(f"{file_name[:-4]}: Arithmetic Mean: {am_values[idx]:.2f}")

    # Create a line chart for Adj Close prices
    st.write(f"## {highest_file_name_gm[:-4]}")
    fig = px.line(dfs[max_gm_index], x='Date', y='Adj Close', title=f'📈 Adj Close Prices in {highest_file_name_gm[:-4]}')
    st.plotly_chart(fig, use_container_width=True)

    # Create donut chart for geometric mean of all companies
    gm_data = pd.DataFrame({'Company': [name[:-4] for name in unique_file_names], 'Geometric Mean': gm_values})
    gm_chart = px.pie(gm_data, values='Geometric Mean', names='Company', hole=0.5, title=" Geometric Mean Distribution")

    # Create donut chart for arithmetic mean of all companies
    am_data = pd.DataFrame({'Company': [name[:-4] for name in unique_file_names], 'Arithmetic Mean': am_values})
    am_chart = px.pie(am_data, values='Arithmetic Mean', names='Company', hole=0.5, title=" Arithmetic Mean Distribution")

    # Display donut charts side by side with space in between
    st.write("## ✨ Mean Distribution")
    col1, spacer, col2 = st.columns([1, 0.2, 1])  # Divide the space into three columns
    with col1:
        st.plotly_chart(gm_chart, use_container_width=True)

    with spacer:
        st.write("")

    with col2:
        st.plotly_chart(am_chart, use_container_width=True)

    # Create bar chart for average Adj Close price of each company
    st.write("## 📊 Average Return for Each Company")
    avg_adj_close_per_company = [np.mean(df['Adj Close']) for df in dfs]
    avg_per_company_data = pd.DataFrame(
        {'Company': [name[:-4] for name in unique_file_names], 'Average Adj Close Price': avg_adj_close_per_company})
    avg_per_company_chart = px.bar(avg_per_company_data, x='Company', y='Average Adj Close Price',
                                   title=" Average Adj Close Price for Each Company")
    st.plotly_chart(avg_per_company_chart, use_container_width=True)
