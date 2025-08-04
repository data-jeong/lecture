"""Custom widget components for the dashboard"""

import streamlit as st
from typing import Optional, Any


def create_metric_card(label: str, value: Any, delta: Optional[str] = None, 
                       delta_color: str = "normal", icon: Optional[str] = None):
    """Create a custom metric card with optional icon"""
    
    container = st.container()
    
    with container:
        if icon:
            st.markdown(f"### {icon} {label}")
        else:
            st.markdown(f"### {label}")
        
        st.metric(
            label="",
            value=value,
            delta=delta,
            delta_color=delta_color,
            label_visibility="collapsed"
        )
    
    return container


def create_progress_card(title: str, value: float, max_value: float = 100, 
                        format_str: str = "{:.1f}%", color: str = "blue"):
    """Create a progress card with title and progress bar"""
    
    container = st.container()
    
    with container:
        st.markdown(f"**{title}**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            progress = value / max_value
            st.progress(progress)
        
        with col2:
            st.markdown(format_str.format(value))
    
    return container


def create_notification(message: str, type: str = "info", icon: Optional[str] = None):
    """Create a notification message"""
    
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    if icon is None:
        icon = icons.get(type, "📢")
    
    if type == "info":
        st.info(f"{icon} {message}")
    elif type == "success":
        st.success(f"{icon} {message}")
    elif type == "warning":
        st.warning(f"{icon} {message}")
    elif type == "error":
        st.error(f"{icon} {message}")
    else:
        st.write(f"{icon} {message}")


def create_stat_card(title: str, stats: dict):
    """Create a statistics card with multiple values"""
    
    container = st.container()
    
    with container:
        st.markdown(f"### {title}")
        
        cols = st.columns(len(stats))
        
        for i, (key, value) in enumerate(stats.items()):
            with cols[i]:
                st.metric(key, value)
    
    return container


def create_action_buttons(buttons: list, columns: int = 3):
    """Create a group of action buttons"""
    
    cols = st.columns(columns)
    results = {}
    
    for i, button in enumerate(buttons):
        col_idx = i % columns
        
        with cols[col_idx]:
            btn_type = button.get('type', 'secondary')
            use_container_width = button.get('use_container_width', True)
            
            if btn_type == 'primary':
                results[button['key']] = st.button(
                    button['label'],
                    key=button['key'],
                    type='primary',
                    use_container_width=use_container_width
                )
            else:
                results[button['key']] = st.button(
                    button['label'],
                    key=button['key'],
                    use_container_width=use_container_width
                )
    
    return results


def create_info_box(title: str, content: str, color: str = "#F0F2F6"):
    """Create an info box with custom styling"""
    
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 1rem; border-radius: 0.5rem;">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_kpi_row(kpis: list):
    """Create a row of KPI metrics"""
    
    cols = st.columns(len(kpis))
    
    for i, kpi in enumerate(kpis):
        with cols[i]:
            value = kpi.get('value', 0)
            label = kpi.get('label', '')
            delta = kpi.get('delta', None)
            delta_color = kpi.get('delta_color', 'normal')
            
            st.metric(
                label=label,
                value=value,
                delta=delta,
                delta_color=delta_color
            )


def create_data_table(data, height: int = 400, use_checkbox: bool = False):
    """Create an interactive data table"""
    
    if use_checkbox:
        # Add checkbox column
        data.insert(0, "Select", False)
        
        edited_df = st.data_editor(
            data,
            height=height,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select rows to perform actions",
                    default=False,
                )
            }
        )
        
        selected_rows = edited_df[edited_df["Select"]]
        return selected_rows.drop("Select", axis=1)
    else:
        st.dataframe(
            data,
            height=height,
            use_container_width=True,
            hide_index=True
        )
        return None


def create_tabs_with_badges(tabs_config: dict):
    """Create tabs with badge counts"""
    
    tab_labels = []
    for tab_name, badge_count in tabs_config.items():
        if badge_count and badge_count > 0:
            tab_labels.append(f"{tab_name} ({badge_count})")
        else:
            tab_labels.append(tab_name)
    
    return st.tabs(tab_labels)