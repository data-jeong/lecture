"""Sidebar component for the dashboard"""

import streamlit as st
from datetime import datetime


def create_sidebar():
    """Create and configure the sidebar"""
    
    # User info
    if 'user' in st.session_state and st.session_state.user:
        st.sidebar.markdown(f"### 👤 {st.session_state.user.get('username', 'Guest')}")
        st.sidebar.markdown(f"Role: {st.session_state.user.get('role', 'User')}")
        st.sidebar.divider()
    
    # Quick stats
    st.sidebar.markdown("### 📊 Quick Stats")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric("Active", "89", "5↑")
    
    with col2:
        st.metric("Alerts", "3", "-2↓")
    
    st.sidebar.divider()
    
    # Notifications
    if 'notifications' in st.session_state and st.session_state.notifications:
        st.sidebar.markdown("### 🔔 Notifications")
        
        for notif in st.session_state.notifications[:3]:  # Show latest 3
            with st.sidebar.expander(notif.get('title', 'Notification')):
                st.write(notif.get('message', ''))
                st.caption(notif.get('time', ''))
    
    # Theme toggle
    st.sidebar.divider()
    theme = st.sidebar.radio(
        "🎨 Theme",
        ["Light", "Dark"],
        horizontal=True,
        index=0 if st.session_state.get('theme', 'light') == 'light' else 1
    )
    
    if theme != st.session_state.get('theme'):
        st.session_state.theme = theme.lower()
        st.rerun()
    
    # Footer
    st.sidebar.divider()
    st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()