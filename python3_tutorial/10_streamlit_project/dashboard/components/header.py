"""Header component for the dashboard"""

import streamlit as st
from datetime import datetime


def create_header():
    """Create the main header of the dashboard"""
    
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        # Logo or branding
        st.markdown("## 📊 Dashboard v1.0")
    
    with col2:
        # Search bar
        search_query = st.text_input(
            "Search",
            placeholder="🔍 Search anything...",
            label_visibility="collapsed"
        )
        if search_query:
            st.session_state.search_query = search_query
    
    with col3:
        # Current time and date
        now = datetime.now()
        st.markdown(f"**{now.strftime('%Y-%m-%d')}**")
        st.markdown(f"**{now.strftime('%H:%M:%S')}**")
    
    # Divider
    st.divider()
    
    # Breadcrumb (if needed)
    if 'current_page' in st.session_state:
        st.caption(f"Home > {st.session_state.current_page}")
    
    # Alert banner (if any)
    if 'alert' in st.session_state and st.session_state.alert:
        alert = st.session_state.alert
        if alert['type'] == 'error':
            st.error(alert['message'])
        elif alert['type'] == 'warning':
            st.warning(alert['message'])
        elif alert['type'] == 'info':
            st.info(alert['message'])
        elif alert['type'] == 'success':
            st.success(alert['message'])