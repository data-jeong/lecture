"""
Streamlit Dashboard Examples
Example code snippets for various dashboard features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def example_basic_layout():
    """Basic layout example"""
    st.title("Dashboard Layout Example")
    
    # Columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Revenue", "$45,231", "12%")
    
    with col2:
        st.metric("Users", "1,234", "-2%")
    
    with col3:
        st.metric("Performance", "98.5%", "1.2%")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Chart", "Data", "Analysis"])
    
    with tab1:
        st.line_chart(np.random.randn(20, 3))
    
    with tab2:
        st.dataframe(pd.DataFrame(np.random.randn(10, 5)))
    
    with tab3:
        st.write("Analysis content here")


def example_interactive_charts():
    """Interactive charts example"""
    st.title("Interactive Charts")
    
    # Generate sample data
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=30),
        'sales': np.random.randint(100, 500, 30),
        'profit': np.random.randint(50, 200, 30)
    })
    
    # Plotly line chart
    fig = px.line(df, x='date', y=['sales', 'profit'], 
                  title='Sales and Profit Trend')
    st.plotly_chart(fig, use_container_width=True)
    
    # Plotly bar chart
    fig2 = px.bar(df.tail(7), x='date', y='sales', 
                  title='Last 7 Days Sales')
    st.plotly_chart(fig2, use_container_width=True)


def example_real_time_update():
    """Real-time update example"""
    st.title("Real-time Updates")
    
    placeholder = st.empty()
    
    for i in range(10):
        with placeholder.container():
            st.metric("Current Value", f"{np.random.randint(100, 200)}")
            st.line_chart(np.random.randn(20, 3))
        
        import time
        time.sleep(1)


def example_file_operations():
    """File operations example"""
    st.title("File Operations")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        
        # Process data
        st.subheader("Data Summary")
        st.write(df.describe())
        
        # Download processed data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download processed data",
            data=csv,
            file_name="processed_data.csv",
            mime="text/csv"
        )


def example_forms():
    """Forms example"""
    st.title("User Forms")
    
    with st.form("my_form"):
        st.write("User Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
        
        with col2:
            age = st.number_input("Age", min_value=1, max_value=100)
            country = st.selectbox("Country", ["USA", "UK", "Canada", "Other"])
        
        interests = st.multiselect(
            "Interests",
            ["Technology", "Sports", "Music", "Travel", "Reading"]
        )
        
        subscribe = st.checkbox("Subscribe to newsletter")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.success(f"Form submitted for {name}!")


def example_sidebar():
    """Sidebar example"""
    with st.sidebar:
        st.title("Settings")
        
        # Theme selector
        theme = st.radio("Theme", ["Light", "Dark", "Auto"])
        
        # Date range
        st.subheader("Date Range")
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        
        # Filters
        st.subheader("Filters")
        categories = st.multiselect(
            "Categories",
            ["Sales", "Marketing", "Development", "Support"]
        )
        
        # Actions
        if st.button("Apply Settings"):
            st.success("Settings applied!")
        
        if st.button("Reset"):
            st.warning("Settings reset!")


def example_custom_components():
    """Custom components example"""
    st.title("Custom Components")
    
    # Progress indicator
    progress = st.progress(0)
    for i in range(100):
        progress.progress(i + 1)
    
    # Status indicator
    status = st.status("Running analysis...", expanded=True)
    status.write("Processing data...")
    status.write("Generating charts...")
    status.update(label="Analysis complete!", state="complete")
    
    # Expander
    with st.expander("See details"):
        st.write("Detailed information here")
        st.line_chart(np.random.randn(10, 3))
    
    # Info boxes
    st.info("This is an info message")
    st.success("This is a success message")
    st.warning("This is a warning message")
    st.error("This is an error message")


def example_session_state():
    """Session state example"""
    st.title("Session State Management")
    
    # Initialize session state
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Display counter
    st.write(f"Counter value: {st.session_state.counter}")
    
    # Buttons to modify state
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Increment"):
            st.session_state.counter += 1
            st.session_state.history.append(
                f"Incremented to {st.session_state.counter}"
            )
    
    with col2:
        if st.button("Decrement"):
            st.session_state.counter -= 1
            st.session_state.history.append(
                f"Decremented to {st.session_state.counter}"
            )
    
    with col3:
        if st.button("Reset"):
            st.session_state.counter = 0
            st.session_state.history = ["Reset to 0"]
    
    # Display history
    if st.session_state.history:
        st.subheader("History")
        for item in st.session_state.history[-5:]:  # Show last 5
            st.write(f"- {item}")


def example_caching():
    """Caching example"""
    st.title("Data Caching")
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def load_data():
        # Simulate expensive computation
        import time
        time.sleep(2)
        return pd.DataFrame(
            np.random.randn(1000, 5),
            columns=['A', 'B', 'C', 'D', 'E']
        )
    
    @st.cache_resource
    def init_model():
        # Cache resource (like ML model)
        return {"model": "initialized"}
    
    # Load cached data
    with st.spinner("Loading data..."):
        df = load_data()
        model = init_model()
    
    st.success("Data loaded from cache!")
    st.dataframe(df.head())
    
    # Clear cache button
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")


def example_multipage():
    """Multi-page navigation example"""
    st.title("Multi-page Navigation")
    
    # Page selector
    page = st.selectbox(
        "Select Page",
        ["Home", "Analytics", "Reports", "Settings"]
    )
    
    # Display selected page
    if page == "Home":
        st.header("Welcome to Dashboard")
        st.write("This is the home page")
        
    elif page == "Analytics":
        st.header("Analytics")
        st.line_chart(np.random.randn(20, 3))
        
    elif page == "Reports":
        st.header("Reports")
        st.dataframe(pd.DataFrame(np.random.randn(10, 5)))
        
    elif page == "Settings":
        st.header("Settings")
        st.checkbox("Enable notifications")
        st.slider("Refresh rate", 1, 60, 5)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Dashboard Examples",
        page_icon="📊",
        layout="wide"
    )
    
    st.sidebar.title("Examples")
    
    example = st.sidebar.radio(
        "Select Example",
        [
            "Basic Layout",
            "Interactive Charts",
            "Real-time Updates",
            "File Operations",
            "Forms",
            "Custom Components",
            "Session State",
            "Caching",
            "Multi-page"
        ]
    )
    
    if example == "Basic Layout":
        example_basic_layout()
    elif example == "Interactive Charts":
        example_interactive_charts()
    elif example == "Real-time Updates":
        example_real_time_update()
    elif example == "File Operations":
        example_file_operations()
    elif example == "Forms":
        example_forms()
    elif example == "Custom Components":
        example_custom_components()
    elif example == "Session State":
        example_session_state()
    elif example == "Caching":
        example_caching()
    elif example == "Multi-page":
        example_multipage()