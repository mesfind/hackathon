import streamlit as st
import pandas as pd
import numpy as np
import re
import io
from datetime import datetime
import PyPDF2
from io import BytesIO
import warnings
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import streamlit.components.v1 as components
warnings.filterwarnings('ignore')

# Streamlit app configuration
st.set_page_config(
    page_title="NDMC Hackathon Screening",
    layout="wide",
    page_icon="",
    initial_sidebar_state="expanded"
)

# CSS with modern design
st.markdown("""
<style>
    /* Main App Styling - Enhanced */
    .main-header {
        font-size: 3rem !important;
        color: #1E3A8A !important;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #8B5CF6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(30, 58, 138, 0.15);
        padding: 0.5rem 0;
        position: relative;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 25%;
        width: 50%;
        height: 4px;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #8B5CF6);
        border-radius: 2px;
    }
    
    .sub-header {
        font-size: 1.8rem !important;
        color: #3B82F6 !important;
        border-bottom: 4px solid;
        border-image: linear-gradient(90deg, #3B82F6, #8B5CF6) 1;
        padding-bottom: 0.7rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        display: inline-block;
    }
    
    .sub-header::before {
        content: '✦';
        margin-right: 10px;
        color: #8B5CF6;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95));
        padding: 1.8rem;
        border-radius: 20px;
        color: #1F2937;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08), 0 4px 12px rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.8);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        border-radius: 20px 20px 0 0;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 8px 20px rgba(59, 130, 246, 0.1);
    }
    
    .critical-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 15px 35px rgba(245, 87, 108, 0.25);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .critical-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .critical-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(245, 87, 108, 0.35);
    }
    
    /* ENHANCED CANDIDATE CARD WITH WHITE BACKGROUND - IMPROVED */
    .candidate-card-container {
        border-radius: 24px;
        padding: 3px;
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #F59E0B 70%, #EF4444 100%);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .candidate-card-container:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
    }
    
    .candidate-card-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #F59E0B, #EF4444, #10B981);
        border-radius: 24px 24px 0 0;
        z-index: 2;
    }
    
    .candidate-card {
        background: white !important;
        border-radius: 21px;
        padding: 2.2rem;
        position: relative;
        height: 100%;
        border: 1px solid rgba(229, 231, 235, 0.8);
        backdrop-filter: blur(5px);
    }
    
    /* Rank Badge - Premium Design */
    .rank-badge {
        position: absolute;
        top: -25px;
        left: 30px;
        color: white;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        font-weight: 900;
        box-shadow: 0 8px 25px rgba(0,0,0,0.25), inset 0 4px 8px rgba(255,255,255,0.3);
        z-index: 2;
        border: 5px solid white;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .candidate-card-container:hover .rank-badge {
        transform: scale(1.15) rotate(10deg);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4), inset 0 6px 12px rgba(255,255,255,0.4);
    }
    
    /* Score Badge - Premium Design */
    .score-badge {
        position: absolute;
        top: -22px;
        right: 30px;
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 900;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2), inset 0 4px 8px rgba(255,255,255,0.3);
        z-index: 2;
        border: 4px solid white;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Candidate Name - Luxury Design */
    .candidate-name {
        font-size: 1.8rem;
        font-weight: 900;
        color: #1F2937;
        margin-top: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #F3F4F6, #E5E7EB, #F3F4F6) 1;
        position: relative;
    }
    
    .candidate-name::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        border-radius: 2px;
    }
    
    .candidate-title {
        color: #3B82F6;
        font-size: 1.2rem;
        margin: 0.3rem 0 0.5rem 0;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.5rem 0;
    }
    
    .candidate-title span {
        font-size: 1.3rem;
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .candidate-institution {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        padding: 0.8rem 0;
    }
    
    .candidate-institution span:first-child {
        font-size: 1.2rem;
        color: #3B82F6;
    }
    
    /* Contact Info - Luxury Card */
    .contact-info {
        background: linear-gradient(135deg, rgba(248, 250, 252, 0.9), rgba(241, 245, 249, 0.9));
        border-radius: 18px;
        padding: 1.5rem;
        margin: 2rem 0;
        border-left: 6px solid #0EA5E9;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(229, 231, 235, 0.6);
        position: relative;
        overflow: hidden;
    }
    
    .contact-info::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.05), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .contact-info:hover::before {
        transform: translateX(100%);
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0.8rem 0;
        color: #1E40AF;
        font-size: 1rem;
        padding: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .contact-item:hover {
        transform: translateX(5px);
        color: #1E3A8A;
    }
    
    .contact-icon {
        width: 28px;
        text-align: center;
        font-size: 1.3rem;
        color: #3B82F6;
        background: rgba(59, 130, 246, 0.1);
        padding: 0.5rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .contact-item:hover .contact-icon {
        background: rgba(59, 130, 246, 0.2);
        transform: scale(1.1);
    }
    
    /* Stats Panel - Premium Design */
    .stats-panel {
        background: linear-gradient(135deg, rgba(255, 251, 235, 0.9), rgba(254, 243, 199, 0.9));
        padding: 1.5rem;
        border-radius: 18px;
        margin: 1.8rem 0;
        border-left: 6px solid #F59E0B;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(229, 231, 235, 0.6);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        text-align: center;
    }
    
    .stat-item {
        padding: 0.8rem;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 14px;
        transition: all 0.3s ease;
    }
    
    .stat-item:hover {
        background: rgba(255, 255, 255, 0.9);
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 900;
        color: #1E40AF;
        margin-bottom: 0.4rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        opacity: 0.9;
    }
    
    /* Skills Container - Premium Design */
    .skills-container {
        margin: 2rem 0;
        padding-top: 1.5rem;
        border-top: 3px solid rgba(229, 231, 235, 0.5);
        position: relative;
    }
    
    .skills-container::before {
        content: '🛠️';
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 0 1rem;
        font-size: 1.5rem;
        color: #3B82F6;
    }
    
    .skill-tag {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        margin: 0.4rem;
        display: inline-block;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.25);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .skill-tag::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.2) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .skill-tag:hover::before {
        transform: translateX(100%);
    }
    
    .skill-tag:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
    }
    
    .ml-tag {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .dl-tag {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    
    .math-tag {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3);
    }
    
    .critical-tag {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.35);
        font-weight: 800;
    }
    
    .health-tag {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .other-tag {
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%);
        box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
    }
    
    /* CV Section - Luxury Design */
    .cv-section {
        background: linear-gradient(135deg, rgba(248, 250, 255, 0.9), rgba(237, 242, 255, 0.9));
        padding: 1.5rem;
        border-radius: 18px;
        margin: 2rem 0;
        border-left: 6px solid #8B5CF6;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(229, 231, 235, 0.6);
    }
    
    /* Link Buttons - Luxury Design */
    .link-button {
        display: inline-flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem 1.5rem;
        color: white;
        border-radius: 15px;
        text-decoration: none;
        font-size: 0.9rem;
        margin: 0.4rem;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .link-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.2) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
        z-index: -1;
    }
    
    .link-button:hover::before {
        transform: translateX(100%);
    }
    
    .link-button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .cv-button {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    }
    
    .github-button {
        background: linear-gradient(135deg, #333333 0%, #000000 100%);
    }
    
    .linkedin-button {
        background: linear-gradient(135deg, #0077B5 0%, #004471 100%);
    }
    
    .kaggle-button {
        background: linear-gradient(135deg, #20BEFF 0%, #0087B5 100%);
    }
    
    .portfolio-button {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
    }
    
    /* Action Buttons - Enhanced */
    .action-button {
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border: 2px solid #E5E7EB;
        color: #4B5563;
        padding: 0.9rem;
        border-radius: 15px;
        cursor: pointer;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        font-weight: 700;
        position: relative;
        overflow: hidden;
    }
    
    .action-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .action-button:hover::before {
        transform: translateX(100%);
    }
    
    .action-button:hover {
        background: linear-gradient(135deg, #F1F5F9, #E5E7EB);
        border-color: #D1D5DB;
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .email-button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .email-button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
        color: white;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
    }
    
    /* Indicators - Enhanced */
    .python-indicator {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 16px;
        height: 16px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 50%;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.8), inset 0 2px 4px rgba(255,255,255,0.5);
        z-index: 1;
        border: 3px solid white;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    .cv-indicator {
        position: absolute;
        top: 20px;
        left: 100px;
        width: 16px;
        height: 16px;
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        border-radius: 50%;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.8), inset 0 2px 4px rgba(255,255,255,0.5);
        z-index: 1;
        border: 3px solid white;
        animation: pulse-purple 2s infinite;
    }
    
    @keyframes pulse-purple {
        0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(139, 92, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
    }
    
    .verified-badge {
        font-size: 0.9rem;
        color: #10B981;
        margin-left: 0.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        backdrop-filter: blur(5px);
    }
    
    .section-title {
        display: flex;
        align-items: center;
        margin-bottom: 1.2rem;
        font-size: 1.1rem;
        color: #1F2937;
        font-weight: 800;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(229, 231, 235, 0.5);
    }
    
    .section-icon {
        font-size: 1.5rem;
        margin-right: 0.8rem;
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2));
    }
    
    /* Enhanced shadow for cards */
    .candidate-card-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.5s ease;
        pointer-events: none;
        border-radius: 24px;
    }
    
    .candidate-card-container:hover::after {
        opacity: 1;
    }
    
    /* Glass morphism effect for metrics */
    .metric-card.glass {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Scrollbar enhancements */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(180deg, #F3F4F6, #E5E7EB);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        border-radius: 10px;
        border: 2px solid #F3F4F6;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
    }
    
    /* Enhanced table styling */
    .stDataFrame {
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08) !important;
        border: 1px solid rgba(229, 231, 235, 0.8) !important;
    }
    
    /* Enhanced download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        padding: 1rem 2rem !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px 15px 0 0 !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        margin: 0 5px !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9) !important;
        border: 1px solid #E5E7EB !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #F1F5F9, #E5E7EB) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        color: white !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Loading spinner enhancement */
    .stSpinner > div {
        border: 3px solid rgba(59, 130, 246, 0.1) !important;
        border-top: 3px solid #3B82F6 !important;
        border-radius: 50% !important;
        animation: spin 1s linear infinite !important;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced input fields */
    .stTextInput > div > div {
        border-radius: 15px !important;
        border: 2px solid #E5E7EB !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput > div > div:hover {
        border-color: #3B82F6 !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Gradient overlay for page */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        background: linear-gradient(135deg, rgba(248, 250, 252, 0.3), rgba(241, 245, 249, 0.3));
        min-height: 100vh;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'top_candidates' not in st.session_state:
    st.session_state.top_candidates = None
if 'file_type' not in st.session_state:
    st.session_state.file_type = None
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}
if 'critical_skills_data' not in st.session_state:
    st.session_state.critical_skills_data = None
if 'chart_counter' not in st.session_state:
    st.session_state.chart_counter = 0
if 'cv_view_mode' not in st.session_state:
    st.session_state.cv_view_mode = " Basic View"

def generate_chart_key(prefix=""):
    """Generate a unique key for Plotly charts"""
    st.session_state.chart_counter += 1
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_chart_{st.session_state.chart_counter}_{timestamp}"

# Hardcoded column mapping based on your file structure
COLUMN_MAPPING = {
    'timestamp': 'Timestamp',
    'email': 'Email address',
    'name': 'Full Name [First Name, Middle Name, Last Name]',
    'email2': 'Email Address2',
    'phone': 'Phone Number (with country code e.g. +2519123456**)',
    'institution': 'Institution / Organization',
    'position': 'Current Position / Title',
    'gender': 'Gender',
    'city': 'City of Residence,  Region',
    'age_range': 'Age Range in Years',
    'expertise': 'Area(s) of Expertise (Select all that apply)',
    'experience': 'Work Experience in Years',
    'languages': 'Programming Languages Familiarity (Select all that apply)',
    'portfolio': 'Link to your GitHub, Kaggle, or professional portfolio',
    'hackathon_before': 'Have you participated in a hackathon before? ',
    'hackathon_experience': 'If yes, briefly describe your experience (100 words max)',
    'interest': 'Why are you interested in participating in this hackathon? (max 200 words)',
    'contribution': 'What do you hope to contribute or learn from this event? (max 150 words)',
    'challenge_area': 'Preferred Policy Challenge Area (Select your top one or two)',
    'reflection': 'Instruction: Reflect on one of the following hackathon challenge areas: \n1. How can data-driven modelling improve immunization coverage and identify zero-dose children in Ethiopia? \n 2. What models or visualization tools can help the Ministry of Health fo',
    'policy_question': 'Describe one public health policy question you are personally interested in exploring during the hackathon.\n1. What is the problem or policy question? \n2. Why is it important? \n3. What data and modelling approach might be used to address it?',
    'availability': 'Are you available to attend the full hackathon in Addis Ababa from December 21–25, 2025?',
    'travel_support': 'Do you require travel support (for participants outside Addis Ababa)?',
    'consent': 'Do you consent to your information being used for participant selection and event communications? ',
    'cv': 'Upload your short CV ( PDF or DOCX only)'
}

# Alternative column names for CSV/PDF
ALTERNATIVE_COLUMN_NAMES = {
    'name': ['full name', 'name', 'applicant name', 'first name', 'last name'],
    'email': ['email', 'email address', 'e-mail', 'mail'],
    'phone': ['phone', 'mobile', 'contact', 'whatsapp', 'number'],
    'experience': ['experience', 'work experience', 'years of experience', 'years'],
    'institution': ['institution', 'organization', 'company', 'university', 'employer'],
    'position': ['position', 'title', 'role', 'designation', 'current position'],
    'expertise': ['expertise', 'skills', 'area of expertise', 'specialization'],
    'languages': ['programming languages', 'languages', 'programming skills', 'coding'],
    'portfolio': ['portfolio', 'github', 'kaggle', 'linkedin', 'website', 'cv', 'resume'],
    'hackathon_before': ['hackathon before', 'participated in hackathon', 'previous hackathon'],
    'availability': ['available', 'availability', 'attend', 'december 21-25'],
    'city': ['city', 'residence', 'location', 'region'],
    'cv': ['cv', 'resume', 'curriculum vitae', 'upload cv', 'cv upload', 'short cv']
}

# CRITICAL SKILLS DEFINITIONS
CRITICAL_DOMAINS = {
    'epidemiology': {
        'keywords': ['epidemiology', 'epidemiological', 'public health', 'biostatistics', 
                    'clinical research', 'healthcare analytics', 'disease surveillance',
                    'health informatics', 'medical statistics', 'health data'],
        'weight': 4,
        'color': '#3B82F6',
        'display_name': 'Epidemiology & Public Health'
    },
    'data_science': {
        'keywords': ['data science', 'data analysis', 'analytics', 'data mining',
                    'predictive modeling', 'statistical analysis', 'business intelligence',
                    'data visualization', 'big data', 'data engineering'],
        'weight': 3,
        'color': '#10B981',
        'display_name': 'Data Science'
    },
    'machine_learning': {
        'keywords': ['machine learning', 'ml', 'predictive analytics', 'supervised learning',
                    'unsupervised learning', 'classification', 'regression', 'clustering',
                    'feature engineering', 'model selection', 'xgboost', 'random forest',
                    'ensemble methods', 'model evaluation'],
        'weight': 5,
        'color': '#F59E0B',
        'display_name': 'Machine Learning'
    },
    'deep_learning': {
        'keywords': ['deep learning', 'dl', 'neural networks', 'cnn', 'convolutional neural network',
                    'rnn', 'recurrent neural network', 'lstm', 'transformer', 'attention mechanism',
                    'computer vision', 'natural language processing', 'nlp', 'image recognition',
                    'time series forecasting', 'generative models', 'gan', 'autoencoder'],
        'weight': 6,
        'color': '#8B5CF6',
        'display_name': 'Deep Learning'
    },
    'mathematical_modeling': {
        'keywords': ['mathematical modeling', 'mathematical model', 'simulation', 'optimization',
                    'operations research', 'numerical analysis', 'differential equations',
                    'stochastic modeling', 'statistical modeling', 'bayesian statistics',
                    'monte carlo simulation', 'agent-based modeling', 'system dynamics',
                    'computational modeling', 'quantitative modeling'],
        'weight': 5,
        'color': '#EC4899',
        'display_name': 'Mathematical Modeling'
    },
    'programming_critical': {
        'keywords': ['python', 'r programming', 'r language', 'r studio'],
        'weight': 10,
        'color': '#EF4444',
        'mandatory': True,
        'display_name': 'Python/R Programming'
    },
    'cv_present': {
        'keywords': ['cv', 'resume', 'curriculum vitae'],
        'weight': 15,
        'color': '#8B5CF6',
        'display_name': 'CV Uploaded'
    }
}

def extract_portfolio_links(portfolio_text, cv_column_value=None):
    """Extract and categorize portfolio links from text with CV priority - USE ORIGINAL LINKS"""
    if pd.isna(portfolio_text):
        portfolio_text = ""
    
    portfolio_text = str(portfolio_text)
    
    # Start with links dictionary
    links = {
        'cv': None,
        'github': None,
        'linkedin': None,
        'kaggle': None,
        'other': []
    }
    
    # First, check the dedicated CV column (highest priority)
    if cv_column_value and pd.notna(cv_column_value):
        cv_text = str(cv_column_value)
        
        # Look for URLs in the CV column - handle multiple URLs
        url_pattern = r'https?://[^\s]+'
        cv_urls = re.findall(url_pattern, cv_text)
        
        for url in cv_urls:
            url_lower = url.lower()
            
            # Check for Google Drive links - USE ORIGINAL URL
            if 'drive.google.com' in url_lower:
                links['cv'] = url.strip()
                break  # Stop after first valid CV link
            
            # Also check for direct file links
            elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx']):
                links['cv'] = url.strip()
                break
    
    # Then check portfolio text for all links (if CV not found in CV column)
    if not links['cv']:
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, portfolio_text)
        
        for url in urls:
            # Only set CV if not already found
            if not links['cv']:
                url_lower = url.lower()
                
                # Check for Google Drive links - USE ORIGINAL URL
                if 'drive.google.com' in url_lower:
                    links['cv'] = url.strip()
                    break  # Stop after first valid CV link
                
                # Check for direct file links
                elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx', 'onedrive', 'dropbox']):
                    links['cv'] = url.strip()
                    break
    
    # Extract other links from portfolio text
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, portfolio_text)
    
    for url in urls:
        url_lower = url.lower()
        url_clean = url.strip()
        
        # Skip if this is the CV URL we already found
        if links['cv'] and url_clean == links['cv']:
            continue
            
        # Other link types
        if 'github.com' in url_lower:
            links['github'] = url_clean
        elif 'linkedin.com' in url_lower:
            links['linkedin'] = url_clean
        elif 'kaggle.com' in url_lower:
            links['kaggle'] = url_clean
        else:
            # Don't add Google Drive links to "other" - they're CVs
            if 'drive.google.com' not in url_lower:
                links['other'].append(url_clean)
    
    return links

def extract_numeric_experience(experience_str):
    """Extract numeric experience from various formats"""
    if pd.isna(experience_str) or experience_str == "":
        return np.nan
    
    experience_str = str(experience_str).lower()
    clean_str = re.sub(r'[^\d.+\-]', ' ', experience_str)
    
    patterns = [
        r'(\d+\.?\d*)\s*[-+]\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*years?',
        r'(\d+\.?\d*)\s*yr',
        r'(\d+\.?\d*)\s*\+',
        r'(\d+\.?\d*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, clean_str)
        if matches:
            if isinstance(matches[0], tuple):
                nums = [float(x) for x in matches[0] if x]
                return max(nums) if nums else np.nan
            else:
                try:
                    return float(matches[0])
                except:
                    continue
    
    return np.nan

def parse_multiselect_field(field_value):
    """Parse comma/semicolon separated multi-select fields"""
    if pd.isna(field_value):
        return []
    
    field_str = str(field_value)
    field_str = re.sub(r'[;|/\n]', ',', field_str)
    items = [item.strip() for item in field_str.split(',') if item.strip()]
    return items

def analyze_critical_skills(text, skills_list=None):
    """Analyze text for critical skills and return detailed analysis"""
    if pd.isna(text) or text == "":
        return 0, [], True
    
    text_lower = str(text).lower()
    skills_found = []
    total_score = 0
    missing_critical = False
    
    for domain, config in CRITICAL_DOMAINS.items():
        for keyword in config['keywords']:
            if keyword in text_lower:
                skills_found.append({
                    'domain': domain,
                    'display_name': config['display_name'],
                    'keyword': keyword,
                    'weight': config['weight'],
                    'color': config['color']
                })
                total_score += config['weight']
                break
    
    mandatory_keywords = ['python', 'r programming', 'r language']
    has_mandatory = any(keyword in text_lower for keyword in mandatory_keywords)
    
    if not has_mandatory:
        missing_critical = True
    
    if skills_list:
        for skill in skills_list:
            skill_lower = str(skill).lower()
            for domain, config in CRITICAL_DOMAINS.items():
                for keyword in config['keywords']:
                    if keyword in skill_lower:
                        if not any(s['domain'] == domain for s in skills_found):
                            skills_found.append({
                                'domain': domain,
                                'display_name': config['display_name'],
                                'keyword': keyword,
                                'weight': config['weight'],
                                'color': config['color']
                            })
                            total_score += config['weight']
                        break
    
    return total_score, skills_found, missing_critical

def calculate_advanced_technical_score(expertise_text, languages_text, expertise_list, languages_list):
    """Calculate advanced technical score with critical skills emphasis"""
    score = 0
    
    exp_score, exp_skills, exp_missing = analyze_critical_skills(expertise_text, expertise_list)
    score += exp_score * 2
    
    lang_score, lang_skills, lang_missing = analyze_critical_skills(languages_text, languages_list)
    score += lang_score * 1.5
    
    all_skills = exp_skills + lang_skills
    
    if exp_missing and lang_missing:
        score -= 20
    
    return score, all_skills

def calculate_hackathon_score(row, column_mapping):
    """Calculate comprehensive score for each candidate with advanced ML/DL focus and CV bonus"""
    score = 0
    skill_details = []
    
    if not pd.isna(row.get('experience_numeric', np.nan)):
        experience_score = min(row['experience_numeric'] * 2, 10)
        score += experience_score
    
    expertise_text = str(row.get(column_mapping.get('expertise', ''), ''))
    languages_text = str(row.get(column_mapping.get('languages', ''), ''))
    expertise_list = row.get('expertise_list', [])
    languages_list = row.get('languages_list', [])
    
    tech_score, tech_skills = calculate_advanced_technical_score(
        expertise_text, languages_text, expertise_list, languages_list
    )
    score += min(tech_score, 20)
    skill_details.extend(tech_skills)
    
    combined_text = (expertise_text + ' ' + languages_text).lower()
    has_python = 'python' in combined_text
    has_r = any(r_keyword in combined_text for r_keyword in ['r programming', 'r language', 'r studio'])
    
    if not (has_python or has_r):
        score -= 50  # Still penalize heavily for missing Python/R
    
    # CV BONUS: Strong bonus for having a CV
    portfolio_links = row.get('portfolio_links', {})
    if portfolio_links.get('cv'):
        score += 15  # Significant bonus for having CV
        # Extra bonus for Google Drive CV (easier to access)
        cv_url = portfolio_links['cv']
        if any(gdrive in cv_url.lower() for gdrive in ['drive.google.com', 'docs.google.com']):
            score += 5
    
    hackathon_col = column_mapping.get('hackathon_before')
    if hackathon_col and hackathon_col in row and pd.notna(row[hackathon_col]):
        hackathon_response = str(row[hackathon_col]).lower()
        if 'yes' in hackathon_response:
            score += 10
            exp_col = column_mapping.get('hackathon_experience')
            if exp_col and exp_col in row and pd.notna(row[exp_col]) and len(str(row[exp_col]).strip()) > 20:
                score += 5
    
    reflection_col = column_mapping.get('reflection')
    if reflection_col and reflection_col in row and pd.notna(row[reflection_col]):
        reflection_text = str(row[reflection_col]).lower()
        modeling_keywords = ['model', 'modeling', 'simulation', 'predict', 'forecast', 
                           'algorithm', 'machine learning', 'deep learning', 'ai']
        modeling_count = sum(1 for keyword in modeling_keywords if keyword in reflection_text)
        
        if len(reflection_text.strip()) > 50:
            score += 8
            score += min(modeling_count, 5)
            if len(reflection_text.strip()) > 150:
                score += 2
    
    availability_col = column_mapping.get('availability')
    if availability_col and availability_col in row and pd.notna(row[availability_col]):
        availability_response = str(row[availability_col]).lower()
        if 'yes' in availability_response or 'available' in availability_response:
            score += 10
    
    return max(score, 0), skill_details

def find_best_column_match(df_columns, target_key):
    """Find the best matching column in the dataframe for a target key"""
    df_columns_lower = [str(col).lower() for col in df_columns]
    
    if target_key in COLUMN_MAPPING:
        exact_col = COLUMN_MAPPING[target_key]
        if exact_col in df_columns:
            return exact_col
    
    if target_key in ALTERNATIVE_COLUMN_NAMES:
        for alt_name in ALTERNATIVE_COLUMN_NAMES[target_key]:
            for i, col in enumerate(df_columns_lower):
                if alt_name in col:
                    return df_columns[i]
    
    return None

def filter_ethiopia_candidates(df, column_mapping):
    """Filter candidates who are likely from Ethiopia based on location data"""
    filtered_df = df.copy()
    
    # Keywords indicating Ethiopian location
    ethiopia_keywords = ['ethiopia', 'ethiopian', 'addis', 'addis ababa', 'addisababa',
                        'bahir dar', 'mekelle', 'dire dawa', 'hawassa', 'gondar',
                        'jimma', 'debre markos', 'assela', 'wollo', 'tigray',
                        'amhara', 'oromia', 'somali', 'afar', 'sidama']
    
    location_columns = []
    
    # Try to find location-related columns
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['city', 'location', 'region', 'country', 'residence', 'address']):
            location_columns.append(col)
    
    # Also check mapped columns
    if 'city' in column_mapping:
        location_columns.append(column_mapping['city'])
    
    # Remove duplicates
    location_columns = list(set(location_columns))
    
    if not location_columns:
        st.warning("No location columns found. Cannot filter by Ethiopia location.")
        return filtered_df
    
    # Filter function
    def is_ethiopian(row):
        for col in location_columns:
            if col in row and pd.notna(row[col]):
                cell_value = str(row[col]).lower()
                if any(keyword in cell_value for keyword in ethiopia_keywords):
                    return True
                # Check for Ethiopian phone codes
                if col.lower().find('phone') != -1 or col.lower().find('mobile') != -1:
                    if '+251' in str(row[col]) or '251' in str(row[col]):
                        return True
        return False
    
    # Apply filter
    ethiopia_mask = filtered_df.apply(is_ethiopian, axis=1)
    ethiopian_count = ethiopia_mask.sum()
    non_ethiopian_count = len(filtered_df) - ethiopian_count
    
    if non_ethiopian_count > 0:
        st.info(f"Filtered out {non_ethiopian_count} non-Ethiopian candidates. Keeping {ethiopian_count} Ethiopian candidates.")
    
    return filtered_df[ethiopia_mask]

# File processing functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def parse_pdf_to_dataframe(pdf_text):
    """Attempt to parse PDF text into structured data"""
    lines = pdf_text.split('\n')
    data = []
    current_record = {}
    
    for line in lines:
        line = line.strip()
        if line and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                for target_key in ALTERNATIVE_COLUMN_NAMES:
                    for alt_name in ALTERNATIVE_COLUMN_NAMES[target_key]:
                        if alt_name in key.lower():
                            current_record[target_key] = value
                            break
        
        elif not line and current_record:
            data.append(current_record)
            current_record = {}
    
    if current_record:
        data.append(current_record)
    
    return pd.DataFrame(data) if data else pd.DataFrame()

def load_excel_file(uploaded_file):
    """Load data from Excel file"""
    try:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except:
            df = pd.read_excel(uploaded_file, engine='xlrd')
        return df, 'excel'
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None, None

def load_csv_file(uploaded_file):
    """Load data from CSV file"""
    try:
        content = uploaded_file.read()
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                return df, 'csv'
            except UnicodeDecodeError:
                continue
        
        st.error("Could not decode CSV file with any supported encoding.")
        return None, None
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None, None

def load_pdf_file(uploaded_file):
    """Load data from PDF file"""
    try:
        pdf_text = extract_text_from_pdf(uploaded_file)
        
        if not pdf_text:
            st.error("Could not extract text from PDF")
            return None, None
        
        df = parse_pdf_to_dataframe(pdf_text)
        
        if df.empty:
            st.warning("PDF parsed but no structured data found.")
            with st.expander("Extracted PDF Text"):
                st.text(pdf_text[:2000] + "..." if len(pdf_text) > 2000 else pdf_text)
            return None, None
        
        return df, 'pdf'
    except Exception as e:
        st.error(f"Error processing PDF file: {e}")
        return None, None

def preprocess_dataframe(df, file_type):
    """Preprocess DataFrame from any file type with critical skills analysis"""
    if df is None or df.empty:
        return None, {}
    
    df_processed = df.copy()
    column_mapping = {}
    
    # Try to map columns
    for key in COLUMN_MAPPING.keys():
        found_col = find_best_column_match(df_processed.columns, key)
        if found_col:
            column_mapping[key] = found_col
    
    # Debug column mapping
    with st.expander("Column Mapping Results"):
        st.write("**Critical columns found:**")
        critical_columns = ['name', 'email', 'phone', 'institution', 'position', 'city', 'portfolio', 'experience', 'expertise', 'languages', 'cv']
        for key in critical_columns:
            if key in column_mapping:
                st.write(f"**{key}**: '{column_mapping[key]}'")
                # Show sample data for this column
                if len(df_processed) > 0:
                    sample = df_processed[column_mapping[key]].iloc[0] if column_mapping[key] in df_processed.columns else "COLUMN NOT FOUND"
                    st.write(f"   Sample value (first 200 chars): '{str(sample)[:200]}...'")
            else:
                st.write(f"**{key}**: NOT FOUND")
    
    # Portfolio links extraction including CV column - USE ORIGINAL URLS
    if 'portfolio' in column_mapping or 'cv' in column_mapping:
        port_col = column_mapping.get('portfolio')
        cv_col = column_mapping.get('cv')
        
        def extract_links_with_cv(row):
            portfolio_text = ""
            cv_value = None
            
            # Get portfolio text
            if port_col and port_col in row and pd.notna(row[port_col]):
                portfolio_text = str(row[port_col])
            
            # Get CV value - this is where the Google Drive links are
            if cv_col and cv_col in row and pd.notna(row[cv_col]):
                cv_value = str(row[cv_col])
            
            return extract_portfolio_links(portfolio_text, cv_value)
        
        df_processed['portfolio_links'] = df_processed.apply(extract_links_with_cv, axis=1)
    else:
        df_processed['portfolio_links'] = [{} for _ in range(len(df_processed))]
    
    # Debug extracted links
    with st.expander("Extracted Links Sample (First 5 Rows)"):
        for i, row in df_processed.head(5).iterrows():
            st.write(f"**Row {i}:**")
            if 'portfolio_links' in row:
                st.write(f"  portfolio_links: {row['portfolio_links']}")
            if 'cv' in column_mapping:
                cv_value = row[column_mapping['cv']] if column_mapping['cv'] in row else None
                st.write(f"  CV column value (first 100 chars): {str(cv_value)[:100]}...")
    
    # Process experience
    if 'experience' in column_mapping:
        exp_col = column_mapping['experience']
        df_processed['experience_numeric'] = df_processed[exp_col].apply(extract_numeric_experience)
    else:
        df_processed['experience_numeric'] = np.nan
    
    # Process multi-select fields
    for field in ['expertise', 'languages']:
        if field in column_mapping:
            col = column_mapping[field]
            df_processed[f'{field}_list'] = df_processed[col].apply(parse_multiselect_field)
        else:
            df_processed[f'{field}_list'] = [[] for _ in range(len(df_processed))]
    
    # Analyze critical skills
    critical_skills_data = []
    
    for idx, row in df_processed.iterrows():
        expertise_text = str(row.get(column_mapping.get('expertise', ''), ''))
        languages_text = str(row.get(column_mapping.get('languages', ''), ''))
        expertise_list = row.get('expertise_list', [])
        languages_list = row.get('languages_list', [])
        
        tech_score, tech_skills = calculate_advanced_technical_score(
            expertise_text, languages_text, expertise_list, languages_list
        )
        
        combined_text = (expertise_text + ' ' + languages_text).lower()
        has_python = 'python' in combined_text
        has_r = any(r_keyword in combined_text for r_keyword in ['r programming', 'r language', 'r studio'])
        
        # Check for CV
        portfolio_links = row.get('portfolio_links', {})
        has_cv = portfolio_links.get('cv') is not None
        
        critical_skills_data.append({
            'index': idx,
            'technical_score': tech_score,
            'skills_found': tech_skills,
            'has_python': has_python,
            'has_r': has_r,
            'has_critical_language': has_python or has_r,
            'has_cv': has_cv
        })
    
    st.session_state.critical_skills_data = critical_skills_data
    
    # Add calculated columns
    df_processed['technical_score'] = [data['technical_score'] for data in critical_skills_data]
    df_processed['has_python'] = [data['has_python'] for data in critical_skills_data]
    df_processed['has_r'] = [data['has_r'] for data in critical_skills_data]
    df_processed['has_critical_language'] = [data['has_critical_language'] for data in critical_skills_data]
    df_processed['has_cv'] = [data['has_cv'] for data in critical_skills_data]
    
    # Calculate total score
    df_processed['total_score'] = df_processed.apply(
        lambda x: calculate_hackathon_score(x, column_mapping)[0],
        axis=1
    )
    
    return df_processed, column_mapping

def extract_cv_links(candidate, portfolio_links, column_mapping):
    """Extract all possible CV links from candidate data"""
    cv_links = []
    
    # First priority: CV from portfolio_links
    if portfolio_links.get('cv'):
        cv_url = portfolio_links['cv']
        cv_links.append({
            'url': cv_url,
            'type': 'google_drive' if 'drive.google.com' in cv_url.lower() else 'direct_file',
            'source': 'Google Drive CV' if 'drive.google.com' in cv_url.lower() else 'Direct CV Link',
            'icon': ''
        })
    
    return cv_links[:3]

def create_enhanced_candidate_card(candidate, rank, column_mapping, cv_view_mode):
    """Create an enhanced visual card for a candidate with CV integration"""
    
    # Extract candidate information
    name = "N/A"
    position = "N/A"
    institution = "N/A"
    email = ""
    phone = ""
    city = ""
    
    if 'name' in column_mapping:
        name_val = candidate.get(column_mapping['name'])
        if pd.notna(name_val):
            name = str(name_val).strip()
    
    if 'position' in column_mapping:
        position_val = candidate.get(column_mapping['position'])
        if pd.notna(position_val):
            position = str(position_val).strip()
    
    if 'institution' in column_mapping:
        institution_val = candidate.get(column_mapping['institution'])
        if pd.notna(institution_val):
            institution = str(institution_val).strip()
    
    if 'email' in column_mapping:
        email_val = candidate.get(column_mapping['email'])
        if pd.notna(email_val):
            email = str(email_val).strip()
    
    if 'phone' in column_mapping:
        phone_val = candidate.get(column_mapping['phone'])
        if pd.notna(phone_val):
            phone = str(phone_val).strip()
    
    if 'city' in column_mapping:
        city_val = candidate.get(column_mapping['city'])
        if pd.notna(city_val):
            city = str(city_val).strip()
    
    portfolio_links = candidate.get('portfolio_links', {})
    cv_links = extract_cv_links(candidate, portfolio_links, column_mapping)
    
    expertise_list = candidate.get('expertise_list', [])
    languages_list = candidate.get('languages_list', [])
    
    experience = candidate.get('experience_numeric', np.nan)
    total_score = candidate.get('total_score', 0)
    technical_score = candidate.get('technical_score', 0)
    has_python = candidate.get('has_python', False)
    has_critical_lang = candidate.get('has_critical_language', False)
    has_cv = candidate.get('has_cv', False)
    
    # Escape for JavaScript
    email_js = email.replace("'", "\\'").replace('"', '\\"') if email else ''
    
    # Create beautiful card with proper styling
    card_html = f"""
    <div class="candidate-card-container">
        <div class="candidate-card">
            <!-- Rank Badge with Gradient -->
            <div class="rank-badge" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                #{rank}
            </div>
            
            <!-- Score Badge -->
            <div class="score-badge">
                {total_score:.0f}<span style="font-size: 0.9rem; opacity: 0.9;">pts</span>
            </div>
            
            <!-- Python Indicator -->
            {f'<div class="python-indicator" title="Python Expert"></div>' if has_python else ''}
            
            <!-- CV Indicator -->
            {f'<div class="cv-indicator" title="CV Available"></div>' if has_cv else ''}
            
            <!-- Candidate Name -->
            <div class="candidate-name">
                {name}
                {f'<span class="verified-badge">Verified</span>' if email and '@' in email else ''}
            </div>
            
            <!-- Position -->
            <div class="candidate-title">
                <span style="color: #8B5CF6;"></span> {position}
            </div>
            
            <!-- Institution -->
            <div class="candidate-institution">
                <span style="color: #3B82F6;"></span> {institution}
                {f'<span style="margin-left: auto; background: linear-gradient(135deg, #F59E0B, #D97706); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;"> {city}</span>' if city and city.lower() not in ['not provided', 'nan', 'na', ''] else ''}
            </div>
            
            <!-- Contact Info Card -->
            <div class="contact-info">
                <div class="section-title">
                    <span class="section-icon"></span>
                    Contact Information
                </div>
                <div class="contact-item">
                    <span class="contact-icon"></span>
                    <span style="font-weight: 600; color: #1E40AF;">{email if email and email.lower() != 'nan' else 'Not provided'}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon"></span>
                    <span style="font-weight: 600; color: #1E40AF;">{phone if phone and phone.lower() != 'nan' else 'Not provided'}</span>
                </div>
            </div>
            
            <!-- Stats Panel -->
            <div class="stats-panel">
                <div class="section-title">
                    <span class="section-icon"></span>
                    Performance Metrics
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">
                            {f'{experience:.0f}+' if not pd.isna(experience) else 'N/A'}
                        </div>
                        <div class="stat-label">Years Exp</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="color: #3B82F6;">{technical_score:.0f}</div>
                        <div class="stat-label">Tech Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="color: {'#10B981' if has_critical_lang else '#EF4444'}; font-size: 1.4rem;">
                            {'YES' if has_critical_lang else 'NO'}
                        </div>
                        <div class="stat-label">Python/R</div>
                    </div>
                </div>
            </div>
            
            <!-- Skills Section -->
            <div class="skills-container">
                <div class="section-title">
                    <span class="section-icon"></span>
                    Technical Expertise
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
    """
    
    # Add colorful skill tags
    all_skills = expertise_list + languages_list
    if all_skills:
        skill_count = 0
        for skill in all_skills:
            if skill and skill_count < 10:
                skill_str = str(skill)
                skill_lower = skill_str.lower()
                skill_display = skill_str[:20] + "..." if len(skill_str) > 20 else skill_str
                
                # Color code skills
                if any(kw in skill_lower for kw in ['epidemiology', 'public health', 'health']):
                    card_html += f'<span class="health-tag" title="{skill_str}">{skill_display}</span>'
                elif 'python' in skill_lower or 'r programming' in skill_lower:
                    card_html += f'<span class="critical-tag" title="{skill_str}">{skill_display}</span>'
                elif any(kw in skill_lower for kw in ['machine learning', 'ml', 'ai', 'artificial intelligence']):
                    card_html += f'<span class="ml-tag" title="{skill_str}">{skill_display}</span>'
                elif any(kw in skill_lower for kw in ['data science', 'analytics', 'visualization']):
                    card_html += f'<span class="skill-tag" title="{skill_str}">{skill_display}</span>'
                elif any(kw in skill_lower for kw in ['mathematical', 'statistical', 'modeling']):
                    card_html += f'<span class="math-tag" title="{skill_str}">{skill_display}</span>'
                elif 'stata' in skill_lower:
                    card_html += f'<span class="dl-tag" title="{skill_str}">{skill_display}</span>'
                else:
                    card_html += f'<span class="other-tag" title="{skill_str}">{skill_display}</span>'
                
                skill_count += 1
    
    card_html += """
                </div>
            </div>
            
            <!-- Portfolio Links -->
            <div style="margin-top: 1.8rem; padding-top: 1.2rem; border-top: 2px solid #E5E7EB;">
                <div class="section-title">
                    <span class="section-icon"></span>
                    Professional Links
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
    """
    
    # Add portfolio links - USE ORIGINAL URLS
    if portfolio_links.get('cv'):
        cv_url = portfolio_links["cv"]
        # Display original Google Drive URL
        card_html += f'''
            <a href="{cv_url}" target="_blank" class="link-button cv-button" title="Click to open CV in Google Drive">
                <span></span> View CV on Google Drive
            </a>
        '''
    
    if portfolio_links.get('github'):
        github_url = portfolio_links["github"]
        card_html += f'''
            <a href="{github_url}" target="_blank" class="link-button github-button">
                <span></span> GitHub
            </a>
        '''
    
    if portfolio_links.get('linkedin'):
        linkedin_url = portfolio_links["linkedin"]
        card_html += f'''
            <a href="{linkedin_url}" target="_blank" class="link-button linkedin-button">
                <span></span> LinkedIn
            </a>
        '''
    
    if not any([portfolio_links.get('cv'), portfolio_links.get('github'), portfolio_links.get('linkedin')]):
        card_html += '''
            <div style="color: #9CA3AF; font-size: 0.9rem; padding: 0.8rem; 
                      background: #F9FAFB; border-radius: 12px; width: 100%; text-align: center; 
                      border: 1px dashed #D1D5DB; font-style: italic;">
                No portfolio links provided
            </div>
        '''
    
    # Action Buttons
    card_html += f"""
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E5E7EB;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <button onclick="copyToClipboard('{email_js}')" 
                            style="background: linear-gradient(135deg, #F3F4F6, #E5E7EB); 
                                   border: 1px solid #D1D5DB; color: #4B5563; padding: 0.6rem; 
                                   border-radius: 8px; cursor: pointer; font-size: 0.85rem; 
                                   display: flex; align-items: center; justify-content: center; 
                                   gap: 0.3rem; font-weight: 600; transition: all 0.2s ease;">
                        <span></span> Copy Email
                    </button>
                    <button onclick="window.open('mailto:{email}?subject=NDMC%20Hackathon%20Invitation')" 
                            style="background: linear-gradient(135deg, #3B82F6, #1D4ED8); 
                                   color: white; border: none; padding: 0.6rem; border-radius: 8px; 
                                   cursor: pointer; font-size: 0.85rem; display: flex; 
                                   align-items: center; justify-content: center; gap: 0.3rem; 
                                   font-weight: 600; transition: all 0.2s ease;">
                        <span></span> Email Now
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function copyToClipboard(text) {{
        if (text && text !== 'Not provided' && text !== 'nan') {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('Copied email: ' + text);
            }});
        }} else {{
            alert('No email available to copy');
        }}
    }}
    </script>
    """
    
    return card_html

def create_top20_selection_report(top_candidates, column_mapping):
    """Create comprehensive top 20 selection report with complete contact info - NO EMOJIS"""
    if top_candidates is None or top_candidates.empty:
        return None
    
    top_20 = top_candidates.head(20).copy()
    report_data = []
    
    for idx, (_, candidate) in enumerate(top_20.iterrows(), 1):
        candidate_info = {
            'Rank': idx,
            'Score': round(candidate.get('total_score', 0), 1),
            'Technical Score': round(candidate.get('technical_score', 0), 1),
            'Experience (Years)': candidate.get('experience_numeric', 'N/A'),
            'CV Available': 'YES' if candidate.get('has_cv', False) else 'NO'
        }
        
        for field in ['name', 'email', 'phone', 'institution', 'position', 
                     'city', 'availability']:
            if field in column_mapping:
                col = column_mapping[field]
                if col in candidate and pd.notna(candidate[col]):
                    display_name = field.replace('_', ' ').title()
                    candidate_info[display_name] = str(candidate[col])
                else:
                    candidate_info[field.replace('_', ' ').title()] = 'Not Provided'
        
        portfolio_links = candidate.get('portfolio_links', {})
        if portfolio_links:
            if portfolio_links.get('cv'):
                candidate_info['CV Link'] = portfolio_links['cv']
            if portfolio_links.get('github'):
                candidate_info['GitHub'] = portfolio_links['github']
            if portfolio_links.get('linkedin'):
                candidate_info['LinkedIn'] = portfolio_links['linkedin']
            if portfolio_links.get('kaggle'):
                candidate_info['Kaggle'] = portfolio_links['kaggle']
            if portfolio_links.get('other'):
                candidate_info['Other Links'] = ', '.join(portfolio_links['other'][:3])
        
        candidate_info['Python'] = 'YES' if candidate.get('has_python', False) else 'NO'
        candidate_info['R'] = 'YES' if candidate.get('has_r', False) else 'NO'
        candidate_info['Critical Language'] = 'YES' if candidate.get('has_critical_language', False) else 'NO'
        
        report_data.append(candidate_info)
    
    report_df = pd.DataFrame(report_data)
    
    preferred_order = ['Rank', 'Name', 'Email', 'Phone', 'Institution', 'Position', 
                      'Experience (Years)', 'Score', 'Technical Score', 'CV Available',
                      'CV Link', 'GitHub', 'LinkedIn', 'Kaggle', 'Other Links',
                      'City', 'Availability', 'Python', 'R', 'Critical Language']
    
    existing_columns = [col for col in preferred_order if col in report_df.columns]
    remaining_columns = [col for col in report_df.columns if col not in existing_columns]
    
    report_df = report_df[existing_columns + remaining_columns]
    
    return report_df

def create_formatted_critical_skills_chart(df_processed, prefix=""):
    """Create a well-formatted critical skills distribution bar plot"""
    if df_processed is None or df_processed.empty:
        return
    
    if st.session_state.critical_skills_data:
        all_skills = []
        for data in st.session_state.critical_skills_data:
            all_skills.extend([skill['display_name'] for skill in data['skills_found']])
        
        if all_skills:
            skill_counts = Counter(all_skills)
            
            skills_df = pd.DataFrame({
                'Skill Domain': list(skill_counts.keys()),
                'Number of Applicants': list(skill_counts.values())
            })
            
            skills_df = skills_df.sort_values('Number of Applicants', ascending=True)
            
            # Create custom colors based on skill type
            colors = []
            for skill in skills_df['Skill Domain']:
                if 'Machine Learning' in skill:
                    colors.append('#F59E0B')
                elif 'Deep Learning' in skill:
                    colors.append('#8B5CF6')
                elif 'Mathematical' in skill:
                    colors.append('#EC4899')
                elif 'Epidemiology' in skill:
                    colors.append('#3B82F6')
                elif 'Data Science' in skill:
                    colors.append('#10B981')
                elif 'Python/R' in skill:
                    colors.append('#EF4444')
                elif 'CV Uploaded' in skill:
                    colors.append('#8B5CF6')
                else:
                    colors.append('#4facfe')
            
            fig = go.Figure(data=[
                go.Bar(
                    x=skills_df['Number of Applicants'],
                    y=skills_df['Skill Domain'],
                    orientation='h',
                    marker_color=colors,
                    text=skills_df['Number of Applicants'],
                    textposition='outside',
                    textfont=dict(size=12, color='black', family="Arial, sans-serif"),
                    hovertemplate='<b>%{y}</b><br>Applicants: %{x}<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='rgba(255,255,255,0.3)'),
                        opacity=0.9
                    )
                )
            ])
            
            total_applicants = len(df_processed)
            
            annotations = []
            for i, (skill, count) in enumerate(zip(skills_df['Skill Domain'], skills_df['Number of Applicants'])):
                percentage = (count / total_applicants) * 100
                annotations.append(dict(
                    x=count + (max(skills_df['Number of Applicants']) * 0.02),
                    y=i,
                    text=f'{percentage:.1f}%',
                    showarrow=False,
                    font=dict(size=11, color='#6B7280', family="Arial, sans-serif"),
                    xanchor='left'
                ))
            
            fig.update_layout(
                title=dict(
                    text='<b>Critical Skills Distribution</b><br><span style="font-size:14px; color:#6B7280">Number of Applicants by Skill Domain</span>',
                    font=dict(size=20, family="Arial, sans-serif", weight="bold"),
                    x=0.5,
                    xanchor='center',
                    y=0.95
                ),
                xaxis_title='<b>Number of Applicants</b>',
                yaxis_title='<b>Skill Domain</b>',
                plot_bgcolor='rgba(248, 250, 252, 1)',
                paper_bgcolor='rgba(248, 250, 252, 1)',
                height=max(400, len(skills_df) * 45),
                margin=dict(l=10, r=10, t=120, b=50),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(229, 231, 235, 0.5)',
                    zeroline=False,
                    showline=True,
                    linecolor='rgba(156, 163, 175, 0.3)',
                    tickfont=dict(size=11, family="Arial, sans-serif")
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showline=True,
                    linecolor='rgba(156, 163, 175, 0.3)',
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                    automargin=True
                ),
                annotations=annotations,
                showlegend=False
            )
            
            chart_key = generate_chart_key(f"formatted_skills_{prefix}")
            st.plotly_chart(fig, use_container_width=True, key=chart_key)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Skills Detected", sum(skill_counts.values()))
            with col2:
                st.metric("Unique Skill Domains", len(skill_counts))
            with col3:
                avg_skills = sum(skill_counts.values()) / total_applicants
                st.metric("Avg Skills per Applicant", f"{avg_skills:.1f}")

def create_critical_skills_analysis(df_processed, prefix=""):
    """Create visual analysis of critical skills across candidates"""
    if df_processed is None or df_processed.empty:
        return
    
    st.markdown('<h3 class="sub-header">Critical Skills Analysis</h3>', unsafe_allow_html=True)
    
    total_candidates = len(df_processed)
    has_python = df_processed['has_python'].sum()
    has_r = df_processed['has_r'].sum()
    has_critical_lang = df_processed['has_critical_language'].sum()
    has_cv = df_processed['has_cv'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='critical-card'>
            <div style='font-size: 2.2rem; font-weight: 800;'>{has_python}</div>
            <div style='font-size: 1rem; font-weight: 600;'>Python Experts</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem;'>{has_python/total_candidates*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='critical-card'>
            <div style='font-size: 2.2rem; font-weight: 800;'>{has_r}</div>
            <div style='font-size: 1rem; font-weight: 600;'>R Programming</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem;'>{has_r/total_candidates*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size: 2.2rem; font-weight: 800; color: #8B5CF6;'>{has_cv}</div>
            <div style='font-size: 1rem; font-weight: 600;'>CV Uploaded</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; color: #6B7280;'>{has_cv/total_candidates*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        missing_critical = total_candidates - has_critical_lang
        st.markdown(f"""
        <div class='metric-card' style='background: white; border: 2px solid #EF4444;'>
            <div style='font-size: 2.2rem; font-weight: 800; color: #EF4444;'>{missing_critical}</div>
            <div style='font-size: 1rem; font-weight: 600; color: #EF4444;'>Missing Python/R</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; color: #DC2626;'>{missing_critical/total_candidates*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    
    create_formatted_critical_skills_chart(df_processed, prefix)

def create_ml_dl_expertise_filter():
    """Create specialized ML/DL expertise filter"""
    st.markdown("""
    <div class='warning-box'>
        <h4>Advanced ML/DL & Mathematical Modeling Filter</h4>
        <p><strong>Note:</strong> Python or R programming experience is <span style='color: #EF4444; font-weight: bold;'>MANDATORY</span> for all selected candidates.</p>
        <p><strong>CV Priority:</strong> Candidates with uploaded CVs receive +15 bonus points.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        prog_filter = st.radio(
            "Programming Language (MANDATORY):",
            ["Python or R Required", "Python Only", "R Only", "Both Preferred", "Any"],
            help="Filter candidates based on mandatory programming language requirements",
            key="prog_filter_radio"
        )
        
        cv_filter = st.selectbox(
            "CV Requirement:",
            ["Any", "CV Required", "CV Preferred", "No CV Required"],
            help="Filter candidates based on CV availability",
            key="cv_filter_select"
        )
    
    with col2:
        ml_techniques = st.multiselect(
            "Required ML/DL Techniques:",
            ["Supervised Learning", "Unsupervised Learning", "Deep Learning", 
             "Computer Vision", "NLP", "Time Series", "Ensemble Methods",
             "Reinforcement Learning", "Generative Models"],
            help="Select specific ML/DL techniques required",
            key="ml_techniques_multiselect"
        )
        
        math_modeling = st.multiselect(
            "Mathematical Modeling Expertise:",
            ["Statistical Modeling", "Simulation", "Optimization", 
             "Stochastic Processes", "Bayesian Methods", "System Dynamics",
             "Agent-Based Modeling", "Differential Equations"],
            help="Select required mathematical modeling expertise",
            key="math_modeling_multiselect"
        )
    
    return {
        'prog_filter': prog_filter,
        'cv_filter': cv_filter,
        'ml_techniques': ml_techniques,
        'math_modeling': math_modeling
    }

def apply_advanced_filters(df, ml_filters):
    """Apply advanced ML/DL filters to dataframe"""
    filtered_df = df.copy()
    
    prog_filter = ml_filters['prog_filter']
    if prog_filter != "Any":
        if prog_filter == "Python or R Required":
            filtered_df = filtered_df[filtered_df['has_critical_language']]
        elif prog_filter == "Python Only":
            filtered_df = filtered_df[filtered_df['has_python']]
        elif prog_filter == "R Only":
            filtered_df = filtered_df[filtered_df['has_r']]
        elif prog_filter == "Both Preferred":
            filtered_df = filtered_df[filtered_df['has_python'] & filtered_df['has_r']]
    
    cv_filter = ml_filters['cv_filter']
    if cv_filter == "CV Required":
        filtered_df = filtered_df[filtered_df['has_cv']]
    elif cv_filter == "CV Preferred":
        # Keep all but sort CV holders higher
        filtered_df = filtered_df.sort_values('has_cv', ascending=False)
    
    return filtered_df

def main():
    # App Header
    st.markdown('<h1 class="main-header">NDMC Hackathon Applicant Screening Tool</h1>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Applicant File", 
        type=["xlsx", "xls", "csv", "pdf"],
        help="Supports Excel (recommended), CSV, and PDF files",
        key="file_uploader"
    )
    
    if uploaded_file:
        # Determine file type
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith(('.xlsx', '.xls')):
            df, file_type = load_excel_file(uploaded_file)
        elif file_name.endswith('.csv'):
            df, file_type = load_csv_file(uploaded_file)
        elif file_name.endswith('.pdf'):
            df, file_type = load_pdf_file(uploaded_file)
        else:
            st.error("Unsupported file format.")
            return
        
        if df is None:
            return
        
        st.session_state.file_type = file_type
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"Successfully loaded {file_type.upper()} file: {uploaded_file.name}")
            with col2:
                st.info(f"{len(df)} records")
        
        with st.expander("Raw Data Preview"):
            st.dataframe(df.head(), use_container_width=True)
        
        with st.spinner("Analyzing critical skills and processing applicants..."):
            df_processed, column_mapping = preprocess_dataframe(df, file_type)
        
        if df_processed is None or df_processed.empty:
            st.error("No data could be processed.")
            return
        
        # Ethiopia Filter
        st.markdown('<h3 class="sub-header">Ethiopia Location Filter</h3>', unsafe_allow_html=True)
        
        ethiopia_filter = st.checkbox(
            "Filter to Ethiopian candidates only",
            value=True,
            help="Filter candidates based on location data (city, region, phone codes)",
            key="ethiopia_filter_checkbox"
        )
        
        if ethiopia_filter:
            df_processed = filter_ethiopia_candidates(df_processed, column_mapping)
            if len(df_processed) == 0:
                st.error("No Ethiopian candidates found. Please check your data or disable the Ethiopia filter.")
                return
        
        st.session_state.processed_data = df_processed
        st.session_state.column_mapping = column_mapping
        
        # Show CV extraction results
        cv_count = df_processed['has_cv'].sum()
        total_count = len(df_processed)
        st.info(f"CV Extraction Results: {cv_count}/{total_count} candidates have CV links ({cv_count/total_count*100:.1f}%)")
        
        create_critical_skills_analysis(df_processed, "all_applicants")
        
        st.markdown('<h3 class="sub-header">Advanced ML/DL & Mathematical Modeling Filters</h3>', unsafe_allow_html=True)
        ml_filters = create_ml_dl_expertise_filter()
        
        st.markdown('<h3 class="sub-header">Basic Screening Filters</h3>', unsafe_allow_html=True)
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            min_exp = st.slider(
                "Minimum Years of Experience",
                min_value=0, max_value=20, value=1,
                key="min_exp_slider"
            )
            
            # Ethiopia filter
            ethiopia_only = st.checkbox(
                "Ethiopian candidates only",
                value=True,
                key="ethiopia_only_checkbox",
                help="Filter candidates based on location data"
            )
            
            if 'availability' in column_mapping:
                availability_filter = st.selectbox(
                    "Availability",
                    ["All", "Available", "Not Available"],
                    key="availability_selectbox"
                )
            else:
                availability_filter = "All"
        
        with filter_col2:
            if 'institution' in column_mapping:
                institution_col = column_mapping['institution']
                if institution_col in df_processed.columns:
                    institutions = sorted(df_processed[institution_col].dropna().unique().tolist())
                    selected_institutions = st.multiselect(
                        "Institution/Organization",
                        institutions,
                        key="institution_multiselect"
                    )
            
            if 'hackathon_before' in column_mapping:
                hackathon_filter = st.selectbox(
                    "Previous Hackathon",
                    ["All", "Yes", "No"],
                    key="hackathon_selectbox"
                )
        
        with filter_col3:
            if 'languages_list' in df_processed.columns:
                all_languages = []
                for lang_list in df_processed['languages_list'].dropna():
                    if isinstance(lang_list, list):
                        all_languages.extend([str(lang).lower() for lang in lang_list])
                unique_languages = sorted(set([lang for lang in all_languages if lang]))
                selected_languages = st.multiselect(
                    "Programming Languages",
                    unique_languages[:20],
                    key="languages_multiselect"
                )
            
            if 'expertise_list' in df_processed.columns:
                all_expertise = []
                for exp_list in df_processed['expertise_list'].dropna():
                    if isinstance(exp_list, list):
                        all_expertise.extend([str(exp).lower() for exp in exp_list])
                unique_expertise = sorted(set([exp for exp in all_expertise if exp]))
                selected_expertise = st.multiselect(
                    "Areas of Expertise",
                    unique_expertise[:20],
                    key="expertise_multiselect"
                )
        
        # Apply all filters
        filtered_df = df_processed.copy()
        
        # Apply Ethiopia filter if checked
        if ethiopia_only:
            filtered_df = filter_ethiopia_candidates(filtered_df, column_mapping)
        
        filtered_df = apply_advanced_filters(filtered_df, ml_filters)
        filtered_df = filtered_df[filtered_df['experience_numeric'] >= min_exp]
        
        if availability_filter != "All" and 'availability' in column_mapping:
            availability_col = column_mapping['availability']
            if availability_filter == "Available":
                filtered_df = filtered_df[filtered_df[availability_col].astype(str).str.lower().str.contains('yes', na=False)]
            else:
                filtered_df = filtered_df[~filtered_df[availability_col].astype(str).str.lower().str.contains('yes', na=False)]
        
        if selected_institutions:
            institution_col = column_mapping['institution']
            filtered_df = filtered_df[filtered_df[institution_col].isin(selected_institutions)]
        
        if hackathon_filter != "All":
            hackathon_col = column_mapping['hackathon_before']
            if hackathon_filter == "Yes":
                filtered_df = filtered_df[filtered_df[hackathon_col].astype(str).str.lower().str.contains('yes', na=False)]
            else:
                filtered_df = filtered_df[~filtered_df[hackathon_col].astype(str).str.lower().str.contains('yes', na=False)]
        
        if selected_languages:
            filtered_df = filtered_df[filtered_df['languages_list'].apply(
                lambda langs: any(str(lang).lower() in [l.lower() for l in selected_languages] for lang in langs if isinstance(lang, str))
            )]
        
        if selected_expertise:
            filtered_df = filtered_df[filtered_df['expertise_list'].apply(
                lambda exps: any(str(exp).lower() in [e.lower() for e in selected_expertise] for exp in exps if isinstance(exp, str))
            )]
        
        st.session_state.filtered_data = filtered_df
        
        st.markdown(f'<h3 class="sub-header">Filtered Results: {len(filtered_df)} applicants</h3>', unsafe_allow_html=True)
        
        if len(filtered_df) > 0:
            # Top Candidates Selection
            st.markdown('<h3 class="sub-header">Top 20 Candidates Selection</h3>', unsafe_allow_html=True)
            
            top_n = 20
            
            if 'total_score' in filtered_df.columns:
                top_candidates = filtered_df.nlargest(top_n, 'total_score').copy()
                st.session_state.top_candidates = top_candidates
                
                top20_report = create_top20_selection_report(top_candidates, column_mapping)
                
                view_tab1, view_tab2, view_tab3 = st.tabs(["Top 20 Report", "Cards View", "Analytics"])
                
                with view_tab1:
                    st.markdown("""
                    <div class='top20-report'>
                        <h3 style='color: white; margin: 0;'>Top 20 Candidates - Complete Contact Information</h3>
                        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                            This report includes all contact information for the top 20 candidates for further analysis.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if top20_report is not None:
                        st.dataframe(top20_report, use_container_width=True, height=600)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            csv_top20 = top20_report.to_csv(index=False)
                            st.download_button(
                                label="Download Top 20 Report (CSV)",
                                data=csv_top20,
                                file_name=f"ndmc_top20_report_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True,
                                key="download_csv_top20"
                            )
                        
                        with col2:
                            if file_type == 'excel':
                                output = BytesIO()
                                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                    top20_report.to_excel(writer, sheet_name='Top 20 Candidates', index=False)
                                st.download_button(
                                    label="Download Top 20 Report (Excel)",
                                    data=output.getvalue(),
                                    file_name=f"ndmc_top20_report_{timestamp}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True,
                                    key="download_excel_top20"
                                )
                
                with view_tab2:
                    st.markdown(f'<h4 style="color: #1F2937; margin-bottom: 1.5rem;">Top {top_n} Ranked Candidates with Complete Contact Info</h4>', unsafe_allow_html=True)
                    
                    # Google Drive integration instructions
                    with st.expander("Google Drive CV Integration Setup", expanded=False):
                        st.markdown("""
                        ### How Google Drive CV links work:
                        1. **Original URLs**: The tool uses the original Google Drive URLs exactly as provided in your data
                        2. **Format**: `https://drive.google.com/open?id=FILE_ID`
                        3. **Access**: Users will click the "View CV on Google Drive" button to open the CV
                        4. **Requirements**: Files must be publicly shared or accessible to reviewers
                        """)
                    
                    # CV View Mode Toggle
                    cv_view_mode = st.radio(
                        "CV Display Mode:",
                        [" Basic View", "CV Preview Mode"],
                        horizontal=True,
                        key="cv_view_mode_radio",
                        help="Choose whether to show CV previews directly in cards"
                    )
                    
                    # Create columns for card display
                    col1, col2 = st.columns(2)
                    
                    for idx, (_, candidate) in enumerate(top_candidates.iterrows(), 1):
                        # Alternate between columns
                        if idx % 2 == 1:
                            with col1:
                                card_html = create_enhanced_candidate_card(candidate, idx, column_mapping, cv_view_mode)
                                components.html(card_html, height=750, scrolling=False)
                        else:
                            with col2:
                                card_html = create_enhanced_candidate_card(candidate, idx, column_mapping, cv_view_mode)
                                components.html(card_html, height=750, scrolling=False)
                        
                        # Add spacing between cards
                        if idx < len(top_candidates):
                            if idx % 2 == 1:
                                with col1:
                                    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                            else:
                                with col2:
                                    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                    
                    # Add interactive JavaScript for better user experience
                    components.html("""
                    <script>
                    // Add hover effects to cards
                    document.addEventListener('DOMContentLoaded', function() {
                        const cards = document.querySelectorAll('.candidate-card-container');
                        cards.forEach(card => {
                            card.addEventListener('mouseenter', function() {
                                this.style.transform = 'translateY(-8px) scale(1.02)';
                                this.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)';
                            });
                            
                            card.addEventListener('mouseleave', function() {
                                this.style.transform = 'translateY(0) scale(1)';
                                this.style.boxShadow = '0 12px 35px rgba(0, 0, 0, 0.1)';
                            });
                        });
                    });
                    </script>
                    """, height=0)
                
                with view_tab3:
                    st.markdown('<h4 style="color: #1F2937; margin-bottom: 1.5rem;">Top 20 Candidates Analytics</h4>', unsafe_allow_html=True)
                    
                    # CV Statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        cv_count = top_candidates['has_cv'].sum()
                        st.metric("CV Available", f"{cv_count}", f"{cv_count/len(top_candidates)*100:.1f}%")
                    with col2:
                        gdrive_cv_count = sum(1 for _, row in top_candidates.iterrows() 
                                             if row.get('portfolio_links', {}).get('cv') and 
                                             'drive.google.com' in str(row['portfolio_links']['cv']).lower())
                        st.metric("Google Drive CVs", f"{gdrive_cv_count}", f"{gdrive_cv_count/cv_count*100:.1f}%" if cv_count > 0 else "0%")
                    with col3:
                        avg_cv_score = top_candidates[top_candidates['has_cv']]['total_score'].mean() if cv_count > 0 else 0
                        st.metric("Avg Score with CV", f"{avg_cv_score:.1f}")
                    with col4:
                        avg_exp = top_candidates['experience_numeric'].mean()
                        st.metric("Avg Experience", f"{avg_exp:.1f} years")
                    
                    # Score distribution
                    fig = px.histogram(top_candidates, x='total_score', nbins=10,
                                     title='<b>Score Distribution of Top 20 Candidates</b>',
                                     color_discrete_sequence=['#3B82F6'],
                                     opacity=0.8)
                    fig.update_layout(
                        plot_bgcolor='rgba(248, 250, 252, 1)',
                        paper_bgcolor='rgba(248, 250, 252, 1)',
                        font=dict(family="Arial, sans-serif")
                    )
                    
                    chart_key = generate_chart_key("score_dist_top20")
                    st.plotly_chart(fig, use_container_width=True, key=chart_key)
                    
                    # Experience distribution
                    fig2 = px.histogram(top_candidates, x='experience_numeric', nbins=10,
                                      title='<b>Experience Distribution of Top 20 Candidates</b>',
                                      color_discrete_sequence=['#10B981'],
                                      opacity=0.8)
                    fig2.update_layout(
                        plot_bgcolor='rgba(248, 250, 252, 1)',
                        paper_bgcolor='rgba(248, 250, 252, 1)',
                        font=dict(family="Arial, sans-serif")
                    )
                    
                    chart_key2 = generate_chart_key("exp_dist_top20")
                    st.plotly_chart(fig2, use_container_width=True, key=chart_key2)
                    
                    # CV vs No CV comparison
                    if cv_count > 0 and cv_count < len(top_candidates):
                        cv_comparison = pd.DataFrame({
                            'Group': ['With CV', 'Without CV'],
                            'Average Score': [
                                top_candidates[top_candidates['has_cv']]['total_score'].mean(),
                                top_candidates[~top_candidates['has_cv']]['total_score'].mean()
                            ],
                            'Average Experience': [
                                top_candidates[top_candidates['has_cv']]['experience_numeric'].mean(),
                                top_candidates[~top_candidates['has_cv']]['experience_numeric'].mean()
                            ],
                            'Count': [cv_count, len(top_candidates) - cv_count]
                        })
                        
                        st.markdown("### CV Availability Impact Analysis")
                        
                        fig3 = px.bar(cv_comparison, x='Group', y=['Average Score', 'Average Experience'],
                                    title='<b>CV vs No CV: Performance Comparison</b>',
                                    barmode='group',
                                    color_discrete_sequence=['#8B5CF6', '#10B981'])
                        fig3.update_layout(
                            plot_bgcolor='rgba(248, 250, 252, 1)',
                            paper_bgcolor='rgba(248, 250, 252, 1)',
                            font=dict(family="Arial, sans-serif")
                        )
                        
                        chart_key3 = generate_chart_key("cv_comparison_top20")
                        st.plotly_chart(fig3, use_container_width=True, key=chart_key3)
                        
                        st.dataframe(cv_comparison, use_container_width=True)
            
            else:
                st.warning("Total score column not found. Cannot rank candidates.")
                top_candidates = filtered_df.copy()
                st.session_state.top_candidates = top_candidates
        
        else:
            st.warning("No candidates match the selected filters. Please adjust your filter criteria.")
    
    else:
        # Show demo/instructions when no file is uploaded
        st.markdown("""
        <div class="metric-card glass" style="text-align: center; padding: 3rem;">
            <h2 style="color: #1E3A8A; margin-bottom: 1rem;">Welcome to NDMC Hackathon Screening Tool</h2>
            <p style="color: #6B7280; font-size: 1.1rem; line-height: 1.6;">
                This tool helps you screen and rank applicants for the NDMC Hackathon with advanced analytics.<br>
                Upload an Excel, CSV, or PDF file containing applicant data to get started.
            </p>
        """, unsafe_allow_html=True)
        
        # ADD THE KEY FEATURES HTML HERE - RIGHT AFTER THE WELCOME MESSAGE
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)); 
              padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: left;">
            <h4 style="color: #1E3A8A; margin-bottom: 1rem;">Key Features:</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #3B82F6;">
                    <div style="font-weight: 600; color: #1E3A8A; margin-bottom: 0.5rem;">Critical Skills Analysis</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Identify Python/R experts, ML/DL skills, and CV availability</div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #10B981;">
                    <div style="font-weight: 600; color: #1E3A8A; margin-bottom: 0.5rem;">Google Drive CV Integration</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Direct access to CVs via Google Drive links with preview mode</div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #F59E0B;">
                    <div style="font-weight: 600; color: #1E3A8A; margin-bottom: 0.5rem;">Advanced Ranking</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Comprehensive scoring system with Ethiopia location filtering</div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #8B5CF6;">
                    <div style="font-weight: 600; color: #1E3A8A; margin-bottom: 0.5rem;">Top 20 Selection</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Generate detailed reports with complete contact information</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ADD THE IMPORTANT NOTES HTML HERE - AFTER THE KEY FEATURES
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(245, 158, 11, 0.1)); 
              padding: 1.5rem; border-radius: 15px; margin-top: 2rem; text-align: left;">
            <h5 style="color: #DC2626; margin-bottom: 0.5rem;">Important Notes:</h5>
            <ul style="color: #6B7280; padding-left: 1.5rem; margin: 0;">
                <li>Python or R programming experience is <strong>MANDATORY</strong> for successful candidates</li>
                <li>Candidates with uploaded CVs receive <strong>+15 bonus points</strong></li>
                <li>Ethiopia location filter is enabled by default</li>
                <li>Google Drive CV links are prioritized for easy access</li>
            </ul>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # # Add example file structure
        # with st.expander("Expected File Structure (Excel/CSV Columns)", expanded=False):
        #     st.markdown("""
        #     ### Recommended Column Names:
            
        #     **Critical Columns (Required for Best Results):**
        #     - `Full Name [First Name, Middle Name, Last Name]` - Applicant's full name
        #     - `Email address` - Email address
        #     - `Phone Number (with country code e.g. +2519123456**)` - Phone number
        #     - `Institution / Organization` - Current institution
        #     - `Current Position / Title` - Job title/position
        #     - `City of Residence, Region` - Location information
        #     - `Area(s) of Expertise (Select all that apply)` - Skills and expertise
        #     - `Programming Languages Familiarity (Select all that apply)` - Programming languages
        #     - `Work Experience in Years` - Years of experience
        #     - `Upload your short CV ( PDF or DOCX only)` - CV file upload or link
        #     - `Link to your GitHub, Kaggle, or professional portfolio` - Portfolio links
            
        #     **Important Columns:**
        #     - `Have you participated in a hackathon before?` - Previous hackathon experience
        #     - `Are you available to attend the full hackathon in Addis Ababa from December 21–25, 2025?` - Availability
        #     - `Preferred Policy Challenge Area (Select your top one or two)` - Interest areas
        #     - `Gender` - Gender information
        #     - `Age Range in Years` - Age range
            
        #     ### Google Drive CV Format:
        #     - Include Google Drive links in the CV upload column
        #     - Format: `https://drive.google.com/open?id=FILE_ID`
        #     - Files should be publicly accessible or shared with reviewers
        #     """)
        
        # # Add sample data download
        # with st.expander("Download Sample Template", expanded=False):
        #     st.markdown("""
        #     ### Download a sample Excel template to understand the expected format:
            
        #     1. **Basic Template**: Contains all necessary columns with example data
        #     2. **Google Drive Integration**: Includes sample Google Drive CV links
        #     3. **Format Guide**: Shows how to structure your data
        #     """)
            
        #     # Create sample data
        #     sample_data = {
        #         'Full Name [First Name, Middle Name, Last Name]': ['John Doe', 'Jane Smith'],
        #         'Email address': ['john.doe@example.com', 'jane.smith@example.com'],
        #         'Phone Number (with country code e.g. +2519123456**)': ['+251911234567', '+251922345678'],
        #         'Institution / Organization': ['Addis Ababa University', 'Ethiopian AI Institute'],
        #         'Current Position / Title': ['Data Scientist', 'ML Researcher'],
        #         'City of Residence, Region': ['Addis Ababa', 'Addis Ababa'],
        #         'Area(s) of Expertise (Select all that apply)': ['Machine Learning, Data Science', 'Deep Learning, Epidemiology'],
        #         'Programming Languages Familiarity (Select all that apply)': ['Python, R', 'Python, SQL'],
        #         'Work Experience in Years': ['3-5 years', '5+ years'],
        #         'Upload your short CV ( PDF or DOCX only)': [
        #             'https://drive.google.com/open?id=EXAMPLE_CV_ID_1',
        #             'https://drive.google.com/open?id=EXAMPLE_CV_ID_2'
        #         ],
        #         'Link to your GitHub, Kaggle, or professional portfolio': [
        #             'https://github.com/johndoe, https://linkedin.com/in/johndoe',
        #             'https://github.com/janesmith, https://kaggle.com/janesmith'
        #         ],
        #         'Have you participated in a hackathon before?': ['Yes', 'No'],
        #         'Are you available to attend the full hackathon in Addis Ababa from December 21–25, 2025?': ['Yes', 'Yes'],
        #         'Gender': ['Male', 'Female'],
        #         'Age Range in Years': ['25-30', '30-35']
        #     }
            
        #     sample_df = pd.DataFrame(sample_data)
            
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         csv_sample = sample_df.to_csv(index=False)
        #         st.download_button(
        #             label="Download Sample CSV",
        #             data=csv_sample,
        #             file_name="ndmc_sample_template.csv",
        #             mime="text/csv",
        #             use_container_width=True,
        #             key="download_sample_csv"
        #         )
            
        #     with col2:
        #         output = BytesIO()
        #         with pd.ExcelWriter(output, engine='openpyxl') as writer:
        #             sample_df.to_excel(writer, sheet_name='Sample Data', index=False)
        #         st.download_button(
        #             label="Download Sample Excel",
        #             data=output.getvalue(),
        #             file_name="ndmc_sample_template.xlsx",
        #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #             use_container_width=True,
        #             key="download_sample_excel"
        #         )

# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 1.5rem 0;'>
    <p style='font-size: 1.1rem; font-weight: 700; color: #1E3A8A;'><strong>National Data Management Center (NDMC)-EPHI, Ethiopia</strong></p>
    <p style='font-size: 1rem;'>Public Health Policy Hackathon 2025</p>
    <p style='font-size: 0.9rem; margin-top: 1rem; color: #4B5563;'>
         <strong>Advanced ML/DL & Mathematical Modeling Screening | Python/R Mandatory </strong>
    </p>
</div>
""", unsafe_allow_html=True)