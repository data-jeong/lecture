"""Chart components for the dashboard"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pandas as pd
import numpy as np


def create_line_chart(data, x_col, y_col, title="Line Chart", height=400):
    """Create a line chart using Plotly"""
    
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        title=title,
        height=height
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig


def create_bar_chart(data, x_col, y_col, title="Bar Chart", orientation='v', height=400):
    """Create a bar chart using Plotly"""
    
    if orientation == 'v':
        fig = px.bar(data, x=x_col, y=y_col, title=title, height=height)
    else:
        fig = px.bar(data, x=y_col, y=x_col, title=title, orientation='h', height=height)
    
    fig.update_layout(
        xaxis_title=x_col if orientation == 'v' else y_col,
        yaxis_title=y_col if orientation == 'v' else x_col,
        showlegend=True
    )
    
    return fig


def create_pie_chart(values, names, title="Pie Chart", height=400):
    """Create a pie chart using Plotly"""
    
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        height=height
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    return fig


def create_heatmap(data, title="Heatmap", height=400):
    """Create a heatmap using Plotly"""
    
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


def create_scatter_plot(data, x_col, y_col, color_col=None, size_col=None, 
                        title="Scatter Plot", height=400):
    """Create a scatter plot using Plotly"""
    
    fig = px.scatter(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        height=height
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=True if color_col else False
    )
    
    return fig


def create_area_chart(data, x_col, y_cols, title="Area Chart", height=400):
    """Create an area chart using Plotly"""
    
    fig = go.Figure()
    
    for y_col in y_cols:
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines',
            name=y_col,
            fill='tonexty',
            stackgroup='one'
        ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=x_col,
        yaxis_title="Value",
        hovermode='x unified'
    )
    
    return fig


def create_gauge_chart(value, max_value=100, title="Gauge", height=300):
    """Create a gauge chart using Plotly"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "lightgray"},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=height)
    
    return fig


def create_candlestick_chart(data, date_col, open_col, high_col, low_col, close_col,
                            title="Candlestick Chart", height=400):
    """Create a candlestick chart for financial data"""
    
    fig = go.Figure(data=[go.Candlestick(
        x=data[date_col],
        open=data[open_col],
        high=data[high_col],
        low=data[low_col],
        close=data[close_col]
    )])
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=date_col,
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    
    return fig


def create_box_plot(data, x_col=None, y_col=None, title="Box Plot", height=400):
    """Create a box plot using Plotly"""
    
    fig = px.box(
        data,
        x=x_col,
        y=y_col,
        title=title,
        height=height
    )
    
    fig.update_layout(
        xaxis_title=x_col if x_col else "",
        yaxis_title=y_col if y_col else "",
        showlegend=False
    )
    
    return fig


def create_3d_scatter(data, x_col, y_col, z_col, color_col=None, 
                      title="3D Scatter Plot", height=600):
    """Create a 3D scatter plot using Plotly"""
    
    fig = px.scatter_3d(
        data,
        x=x_col,
        y=y_col,
        z=z_col,
        color=color_col,
        title=title,
        height=height
    )
    
    fig.update_layout(
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_col
        )
    )
    
    return fig