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
import hashlib
warnings.filterwarnings('ignore')

# Streamlit app configuration
st.set_page_config(
    page_title="NDMC Hackathon Screening",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E3A8A !important;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #3B82F6 !important;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .critical-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px solid #FF6B6B;
    }
    .candidate-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3B82F6;
    }
    .skill-tag {
        background: #10B981;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 500;
    }
    .ml-tag {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 600;
    }
    .dl-tag {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 600;
    }
    .math-tag {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 600;
    }
    .critical-tag {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 700;
        box-shadow: 0 2px 4px rgba(239,68,68,0.3);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
    }
    .stSelectbox > div > div {
        border-radius: 10px !important;
    }
    .stSlider > div > div {
        border-radius: 10px !important;
    }
    .highlight {
        background-color: #FFFBEB;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #F59E0B;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #F59E0B;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🏥 NDMC Hackathon Applicant Screening Tool</h1>', unsafe_allow_html=True)
st.markdown("**Ethiopia Public Health Policy Hackathon - Advanced ML/DL & Mathematical Modeling Screening**")

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
    'experience': ['experience', 'work experience', 'years of experience', 'years'],
    'institution': ['institution', 'organization', 'company', 'university', 'employer'],
    'position': ['position', 'title', 'role', 'designation', 'current position'],
    'expertise': ['expertise', 'skills', 'area of expertise', 'specialization'],
    'languages': ['programming languages', 'languages', 'programming skills', 'coding'],
    'hackathon_before': ['hackathon before', 'participated in hackathon', 'previous hackathon'],
    'availability': ['available', 'availability', 'attend', 'december 21-25'],
    'city': ['city', 'residence', 'location', 'region']
}

# CRITICAL SKILLS DEFINITIONS
CRITICAL_DOMAINS = {
    'epidemiology': {
        'keywords': ['epidemiology', 'epidemiological', 'public health', 'biostatistics', 
                    'clinical research', 'healthcare analytics', 'disease surveillance',
                    'health informatics', 'medical statistics', 'health data'],
        'weight': 4,
        'color': '#3B82F6'
    },
    'data_science': {
        'keywords': ['data science', 'data analysis', 'analytics', 'data mining',
                    'predictive modeling', 'statistical analysis', 'business intelligence',
                    'data visualization', 'big data', 'data engineering'],
        'weight': 3,
        'color': '#10B981'
    },
    'machine_learning': {
        'keywords': ['machine learning', 'ml', 'predictive analytics', 'supervised learning',
                    'unsupervised learning', 'classification', 'regression', 'clustering',
                    'feature engineering', 'model selection', 'xgboost', 'random forest',
                    'ensemble methods', 'model evaluation'],
        'weight': 5,
        'color': '#F59E0B'
    },
    'deep_learning': {
        'keywords': ['deep learning', 'dl', 'neural networks', 'cnn', 'convolutional neural network',
                    'rnn', 'recurrent neural network', 'lstm', 'transformer', 'attention mechanism',
                    'computer vision', 'natural language processing', 'nlp', 'image recognition',
                    'time series forecasting', 'generative models', 'gan', 'autoencoder'],
        'weight': 6,
        'color': '#8B5CF6'
    },
    'mathematical_modeling': {
        'keywords': ['mathematical modeling', 'mathematical model', 'simulation', 'optimization',
                    'operations research', 'numerical analysis', 'differential equations',
                    'stochastic modeling', 'statistical modeling', 'bayesian statistics',
                    'monte carlo simulation', 'agent-based modeling', 'system dynamics',
                    'computational modeling', 'quantitative modeling'],
        'weight': 5,
        'color': '#EC4899'
    },
    'programming_critical': {
        'keywords': ['python', 'r programming', 'r language', 'r studio'],
        'weight': 10,  # Very high weight - MANDATORY
        'color': '#EF4444',
        'mandatory': True
    }
}

def extract_numeric_experience(experience_str):
    """Extract numeric experience from various formats"""
    if pd.isna(experience_str) or experience_str == "":
        return np.nan
    
    experience_str = str(experience_str).lower()
    
    # Remove any non-numeric characters except decimal point and plus/minus
    clean_str = re.sub(r'[^\d.+\-]', ' ', experience_str)
    
    # Look for patterns
    patterns = [
        r'(\d+\.?\d*)\s*[-+]\s*(\d+\.?\d*)',  # Range like "3-5" or "2+"
        r'(\d+\.?\d*)\s*years?',  # "5 years"
        r'(\d+\.?\d*)\s*yr',  # "5 yr"
        r'(\d+\.?\d*)\s*\+',  # "5+"
        r'(\d+\.?\d*)'  # Just a number
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, clean_str)
        if matches:
            if isinstance(matches[0], tuple):
                # For ranges, take the higher value
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
    
    # Clean and split
    field_str = str(field_value)
    # Replace common separators with commas
    field_str = re.sub(r'[;|/\n]', ',', field_str)
    # Split by comma and clean
    items = [item.strip() for item in field_str.split(',') if item.strip()]
    return items

def analyze_critical_skills(text, skills_list=None):
    """
    Analyze text for critical skills and return detailed analysis
    Returns: (total_score, skills_found, missing_critical)
    """
    if pd.isna(text) or text == "":
        return 0, [], True
    
    text_lower = str(text).lower()
    skills_found = []
    total_score = 0
    missing_critical = False
    
    # Check each critical domain
    for domain, config in CRITICAL_DOMAINS.items():
        for keyword in config['keywords']:
            if keyword in text_lower:
                skills_found.append({
                    'domain': domain,
                    'keyword': keyword,
                    'weight': config['weight'],
                    'color': config['color']
                })
                total_score += config['weight']
                break  # Count each domain only once
    
    # Check for Python/R specifically (MANDATORY)
    mandatory_keywords = ['python', 'r programming', 'r language']
    has_mandatory = any(keyword in text_lower for keyword in mandatory_keywords)
    
    if not has_mandatory:
        missing_critical = True
    
    # Also check skills list if provided
    if skills_list:
        for skill in skills_list:
            skill_lower = str(skill).lower()
            for domain, config in CRITICAL_DOMAINS.items():
                for keyword in config['keywords']:
                    if keyword in skill_lower:
                        # Check if not already counted
                        if not any(s['domain'] == domain for s in skills_found):
                            skills_found.append({
                                'domain': domain,
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
    
    # Analyze expertise text
    exp_score, exp_skills, exp_missing = analyze_critical_skills(expertise_text, expertise_list)
    score += exp_score * 2  # Double weight for expertise
    
    # Analyze languages text
    lang_score, lang_skills, lang_missing = analyze_critical_skills(languages_text, languages_list)
    score += lang_score * 1.5  # 1.5x weight for languages
    
    # Combine all skills found
    all_skills = exp_skills + lang_skills
    
    # Penalty for missing Python/R
    if exp_missing and lang_missing:
        score -= 20  # Significant penalty for missing mandatory skills
    
    return score, all_skills

def calculate_hackathon_score(row, column_mapping):
    """Calculate comprehensive score for each candidate with advanced ML/DL focus"""
    score = 0
    skill_details = []
    
    # Experience (20% of total - reduced from 30%)
    if not pd.isna(row.get('experience_numeric', np.nan)):
        experience_score = min(row['experience_numeric'] * 2, 10)  # Max 10 points (reduced)
        score += experience_score
    
    # ADVANCED Technical skills (40% of total - increased from 30%)
    expertise_text = str(row.get(column_mapping.get('expertise', ''), ''))
    languages_text = str(row.get(column_mapping.get('languages', ''), ''))
    expertise_list = row.get('expertise_list', [])
    languages_list = row.get('languages_list', [])
    
    tech_score, tech_skills = calculate_advanced_technical_score(
        expertise_text, languages_text, expertise_list, languages_list
    )
    score += min(tech_score, 20)  # Max 20 points
    skill_details.extend(tech_skills)
    
    # Check for Python/R (MANDATORY - Auto-reject if missing)
    combined_text = (expertise_text + ' ' + languages_text).lower()
    has_python = 'python' in combined_text
    has_r = any(r_keyword in combined_text for r_keyword in ['r programming', 'r language', 'r studio'])
    
    if not (has_python or has_r):
        score -= 50  # Massive penalty - effectively rejects candidate
    
    # Hackathon experience (15% of total)
    hackathon_col = column_mapping.get('hackathon_before')
    if hackathon_col and hackathon_col in row and pd.notna(row[hackathon_col]):
        hackathon_response = str(row[hackathon_col]).lower()
        if 'yes' in hackathon_response:
            score += 10
            # Bonus for detailed experience
            exp_col = column_mapping.get('hackathon_experience')
            if exp_col and exp_col in row and pd.notna(row[exp_col]) and len(str(row[exp_col]).strip()) > 20:
                score += 5
    
    # Policy interest & reflection with ML/DL focus (15% of total)
    reflection_col = column_mapping.get('reflection')
    if reflection_col and reflection_col in row and pd.notna(row[reflection_col]):
        reflection_text = str(row[reflection_col]).lower()
        
        # Check for modeling keywords in reflection
        modeling_keywords = ['model', 'modeling', 'simulation', 'predict', 'forecast', 
                           'algorithm', 'machine learning', 'deep learning', 'ai']
        modeling_count = sum(1 for keyword in modeling_keywords if keyword in reflection_text)
        
        if len(reflection_text.strip()) > 50:
            score += 8  # Base score
            score += min(modeling_count, 5)  # Bonus for modeling terms
            if len(reflection_text.strip()) > 150:
                score += 2
    
    # Availability for full event (10% of total)
    availability_col = column_mapping.get('availability')
    if availability_col and availability_col in row and pd.notna(row[availability_col]):
        availability_response = str(row[availability_col]).lower()
        if 'yes' in availability_response or 'available' in availability_response:
            score += 10
    
    return max(score, 0), skill_details  # Ensure non-negative score

def find_best_column_match(df_columns, target_key):
    """Find the best matching column in the dataframe for a target key"""
    df_columns_lower = [str(col).lower() for col in df_columns]
    
    # First check exact mapping
    if target_key in COLUMN_MAPPING:
        exact_col = COLUMN_MAPPING[target_key]
        if exact_col in df_columns:
            return exact_col
    
    # Then check alternative names
    if target_key in ALTERNATIVE_COLUMN_NAMES:
        for alt_name in ALTERNATIVE_COLUMN_NAMES[target_key]:
            for i, col in enumerate(df_columns_lower):
                if alt_name in col:
                    return df_columns[i]
    
    return None

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
            with st.expander("📄 Extracted PDF Text"):
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
    
    # Create column mapping
    column_mapping = {}
    
    if file_type == 'excel':
        for key, exact_col in COLUMN_MAPPING.items():
            if exact_col in df_processed.columns:
                column_mapping[key] = exact_col
    else:
        for key in COLUMN_MAPPING.keys():
            found_col = find_best_column_match(df_processed.columns, key)
            if found_col:
                column_mapping[key] = found_col
    
    # Display column mapping
    with st.expander("🔍 Column Mapping Results"):
        for key, mapped_col in column_mapping.items():
            st.write(f"**{key}**: `{mapped_col}`")
        
        missing_keys = [key for key in ['name', 'email', 'experience', 'expertise', 'languages'] 
                       if key not in column_mapping]
        if missing_keys:
            st.warning(f"⚠️ Missing important columns: {', '.join(missing_keys)}")
    
    # Extract experience
    if 'experience' in column_mapping:
        exp_col = column_mapping['experience']
        df_processed['experience_numeric'] = df_processed[exp_col].apply(extract_numeric_experience)
    else:
        df_processed['experience_numeric'] = np.nan
    
    # Parse multi-select fields
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
        
        # Analyze skills
        tech_score, tech_skills = calculate_advanced_technical_score(
            expertise_text, languages_text, expertise_list, languages_list
        )
        
        # Check for Python/R
        combined_text = (expertise_text + ' ' + languages_text).lower()
        has_python = 'python' in combined_text
        has_r = any(r_keyword in combined_text for r_keyword in ['r programming', 'r language', 'r studio'])
        
        critical_skills_data.append({
            'index': idx,
            'technical_score': tech_score,
            'skills_found': tech_skills,
            'has_python': has_python,
            'has_r': has_r,
            'has_critical_language': has_python or has_r
        })
    
    # Store critical skills data
    st.session_state.critical_skills_data = critical_skills_data
    
    # Calculate technical score
    df_processed['technical_score'] = [data['technical_score'] for data in critical_skills_data]
    df_processed['has_python'] = [data['has_python'] for data in critical_skills_data]
    df_processed['has_r'] = [data['has_r'] for data in critical_skills_data]
    df_processed['has_critical_language'] = [data['has_critical_language'] for data in critical_skills_data]
    
    # Calculate total score
    df_processed['total_score'] = df_processed.apply(
        lambda x: calculate_hackathon_score(x, column_mapping)[0],
        axis=1
    )
    
    return df_processed, column_mapping

def create_fancy_candidate_card(candidate, rank, column_mapping):
    """Create a fancy visual card for a candidate with ML/DL emphasis"""
    with st.container():
        # Determine card color based on critical skills
        has_critical_lang = candidate.get('has_critical_language', False)
        card_style = "candidate-card" if has_critical_lang else "candidate-card"
        
        st.markdown(f"<div class='{card_style}'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            # Rank and critical language indicator
            rank_color = "#F59E0B" if has_critical_lang else "#6B7280"
            st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 2rem; color: {rank_color}; font-weight: bold;'>#{rank}</div>
                <div style='font-size: 1.5rem; color: #10B981;'>{candidate.get('total_score', 0):.1f}</div>
                <div style='font-size: 0.8rem; color: #6B7280;'>Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Name and basic info
            name = candidate.get(column_mapping.get('name', ''), 'N/A')
            position = candidate.get(column_mapping.get('position', ''), 'N/A')
            institution = candidate.get(column_mapping.get('institution', ''), 'N/A')
            
            st.markdown(f"**{name}**")
            st.markdown(f"*{position}*")
            st.markdown(f"🏛️ {institution}")
            
            # Experience
            exp = candidate.get('experience_numeric', 'N/A')
            if not pd.isna(exp):
                st.markdown(f"📅 {exp:.1f} years experience")
            
            # Critical language indicators
            if candidate.get('has_python', False):
                st.markdown("🐍 **Python**", help="Has Python experience")
            if candidate.get('has_r', False):
                st.markdown("📊 **R**", help="Has R programming experience")
            
            if not candidate.get('has_critical_language', False):
                st.markdown("❌ **Missing Python/R**", help="Critical requirement missing")
        
        with col3:
            # Quick stats
            st.markdown("""
            <div style='text-align: right;'>
                <div style='font-size: 0.9rem;'>Tech Score</div>
                <div style='font-size: 1.2rem; color: #F59E0B;'>{:.1f}</div>
            </div>
            """.format(candidate.get('technical_score', 0)), unsafe_allow_html=True)
            
            # Availability indicator
            if 'availability' in column_mapping:
                avail_col = column_mapping['availability']
                if avail_col in candidate and pd.notna(candidate[avail_col]):
                    availability = str(candidate[avail_col]).lower()
                    if 'yes' in availability:
                        st.markdown("✅ **Available**")
                    else:
                        st.markdown("❌ **Not Available**")
        
        st.markdown("</div>", unsafe_allow_html=True)

def create_critical_skills_analysis(df_processed, prefix=""):
    """Create visual analysis of critical skills across candidates"""
    if df_processed is None or df_processed.empty:
        return
    
    st.markdown('<h3 class="sub-header">🔍 Critical Skills Analysis</h3>', unsafe_allow_html=True)
    
    # Calculate critical skills statistics
    total_candidates = len(df_processed)
    has_python = df_processed['has_python'].sum()
    has_r = df_processed['has_r'].sum()
    has_critical_lang = df_processed['has_critical_language'].sum()
    
    # Display critical metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='critical-card'>
            <div style='font-size: 2rem;'>{has_python}</div>
            <div>Python Experts</div>
            <div style='font-size: 0.8rem;'>{has_python/total_candidates*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='critical-card'>
            <div style='font-size: 2rem;'>{has_r}</div>
            <div>R Programming</div>
            <div style='font-size: 0.8rem;'>{has_r/total_candidates*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size: 2rem;'>{has_critical_lang}</div>
            <div>Has Python/R</div>
            <div style='font-size: 0.8rem;'>{has_critical_lang/total_candidates*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        missing_critical = total_candidates - has_critical_lang
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);'>
            <div style='font-size: 2rem;'>{missing_critical}</div>
            <div>Missing Critical</div>
            <div style='font-size: 0.8rem;'>{missing_critical/total_candidates*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills distribution chart
    if st.session_state.critical_skills_data:
        all_skills = []
        for data in st.session_state.critical_skills_data:
            all_skills.extend([skill['domain'] for skill in data['skills_found']])
        
        if all_skills:
            skill_counts = Counter(all_skills)
            
            # Create horizontal bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=list(skill_counts.values()),
                    y=list(skill_counts.keys()),
                    orientation='h',
                    marker_color=['#F59E0B' if 'machine' in skill else 
                                 '#8B5CF6' if 'deep' in skill else
                                 '#EC4899' if 'math' in skill else
                                 '#3B82F6' if 'epidemiology' in skill else
                                 '#10B981' for skill in skill_counts.keys()],
                    text=list(skill_counts.values()),
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='Critical Skills Distribution Across All Applicants',
                xaxis_title='Number of Applicants',
                yaxis_title='Skill Domain',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            # Generate unique key for this chart
            chart_key = generate_chart_key(f"skills_dist_{prefix}")
            st.plotly_chart(fig, use_container_width=True, key=chart_key)

def create_ml_dl_expertise_filter():
    """Create specialized ML/DL expertise filter"""
    st.markdown("""
    <div class='warning-box'>
        <h4>🔬 Advanced ML/DL & Mathematical Modeling Filter</h4>
        <p><strong>Note:</strong> Python or R programming experience is <span style='color: #EF4444; font-weight: bold;'>MANDATORY</span> for all selected candidates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mandatory programming language filter
        prog_filter = st.radio(
            "Programming Language (MANDATORY):",
            ["Python or R Required", "Python Only", "R Only", "Both Preferred", "Any"],
            help="Filter candidates based on mandatory programming language requirements",
            key="prog_filter_radio"
        )
        
        # ML/DL expertise level
        ml_expertise = st.select_slider(
            "ML/DL Expertise Level:",
            options=["Basic", "Intermediate", "Advanced", "Expert"],
            value="Intermediate",
            help="Required level of Machine Learning/Deep Learning expertise",
            key="ml_expertise_slider"
        )
    
    with col2:
        # Specific ML/DL techniques
        ml_techniques = st.multiselect(
            "Required ML/DL Techniques:",
            ["Supervised Learning", "Unsupervised Learning", "Deep Learning", 
             "Computer Vision", "NLP", "Time Series", "Ensemble Methods",
             "Reinforcement Learning", "Generative Models"],
            help="Select specific ML/DL techniques required",
            key="ml_techniques_select"
        )
        
        # Mathematical modeling requirements
        math_modeling = st.multiselect(
            "Mathematical Modeling Expertise:",
            ["Statistical Modeling", "Simulation", "Optimization", 
             "Stochastic Processes", "Bayesian Methods", "System Dynamics",
             "Agent-Based Modeling", "Differential Equations"],
            help="Select required mathematical modeling expertise",
            key="math_modeling_select"
        )
    
    return {
        'prog_filter': prog_filter,
        'ml_expertise': ml_expertise,
        'ml_techniques': ml_techniques,
        'math_modeling': math_modeling
    }

def apply_advanced_filters(df, ml_filters):
    """Apply advanced ML/DL filters to dataframe"""
    filtered_df = df.copy()
    
    # Apply programming language filter
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
    
    return filtered_df

def main():
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Applicant File", 
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
        
        # Display file info
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Successfully loaded {file_type.upper()} file: {uploaded_file.name}")
            with col2:
                st.info(f"📊 {len(df)} records")
        
        # Preprocess data
        with st.spinner("🔍 Analyzing critical skills and processing applicants..."):
            df_processed, column_mapping = preprocess_dataframe(df, file_type)
        
        if df_processed is None or df_processed.empty:
            st.error("No data could be processed.")
            return
        
        st.session_state.processed_data = df_processed
        st.session_state.column_mapping = column_mapping
        
        # Display critical skills analysis
        create_critical_skills_analysis(df_processed, "all_applicants")
        
        # Advanced ML/DL Filters
        st.markdown('<h3 class="sub-header">🔬 Advanced ML/DL & Mathematical Modeling Filters</h3>', unsafe_allow_html=True)
        ml_filters = create_ml_dl_expertise_filter()
        
        # Basic Filters Section
        st.markdown('<h3 class="sub-header">🎛️ Basic Screening Filters</h3>', unsafe_allow_html=True)
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            min_exp = st.slider(
                "Minimum Years of Experience",
                min_value=0, max_value=20, value=1,
                key="min_exp_slider"
            )
            
            if 'availability' in column_mapping:
                availability_filter = st.selectbox(
                    "Availability",
                    ["All", "Available", "Not Available"],
                    key="availability_select"
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
                    key="hackathon_select"
                )
        
        with filter_col3:
            if 'languages_list' in df_processed.columns:
                all_languages = []
                for lang_list in df_processed['languages_list'].dropna():
                    if isinstance(lang_list, list):
                        all_languages.extend([lang.lower() for lang in lang_list])
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
                        all_expertise.extend([exp.lower() for exp in exp_list])
                unique_expertise = sorted(set([exp for exp in all_expertise if exp]))
                selected_expertise = st.multiselect(
                    "Areas of Expertise",
                    unique_expertise[:20],
                    key="expertise_multiselect"
                )
        
        # Apply all filters
        filtered_df = df_processed.copy()
        
        # Apply advanced ML/DL filters
        filtered_df = apply_advanced_filters(filtered_df, ml_filters)
        
        # Apply basic filters
        filtered_df = filtered_df[filtered_df['experience_numeric'] >= min_exp]
        
        if availability_filter != "All" and 'availability' in column_mapping:
            availability_col = column_mapping['availability']
            if availability_filter == "Available":
                filtered_df = filtered_df[filtered_df[availability_col].str.lower().str.contains('yes', na=False)]
            else:
                filtered_df = filtered_df[~filtered_df[availability_col].str.lower().str.contains('yes', na=False)]
        
        # Store filtered data
        st.session_state.filtered_data = filtered_df
        
        # Display results
        st.markdown(f'<h3 class="sub-header">✅ Filtered Results: {len(filtered_df)} applicants</h3>', unsafe_allow_html=True)
        
        if len(filtered_df) > 0:
            # Top Candidates Selection
            st.markdown('<h3 class="sub-header">🏆 Top Candidates Selection</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                top_n = st.slider(
                    "Number of top candidates",
                    min_value=5,
                    max_value=min(50, len(filtered_df)),
                    value=min(20, len(filtered_df)),
                    key="top_n_slider"
                )
            
            with col2:
                if st.button("🔄 Refresh Selection", use_container_width=True, key="refresh_button"):
                    st.rerun()
            
            # Get top candidates
            if 'total_score' in filtered_df.columns:
                top_candidates = filtered_df.nlargest(top_n, 'total_score').copy()
                st.session_state.top_candidates = top_candidates
                
                # Display candidates
                view_tab1, view_tab2, view_tab3 = st.tabs(["🎯 Cards View", "📋 Table View", "📊 Analytics"])
                
                with view_tab1:
                    st.markdown(f'<h4>🎖️ Top {top_n} Ranked Candidates</h4>', unsafe_allow_html=True)
                    for idx, (_, candidate) in enumerate(top_candidates.iterrows(), 1):
                        create_fancy_candidate_card(candidate, idx, column_mapping)
                
                with view_tab2:
                    # Table view with critical columns
                    display_cols = []
                    if 'name' in column_mapping:
                        display_cols.append(column_mapping['name'])
                    if 'institution' in column_mapping:
                        display_cols.append(column_mapping['institution'])
                    display_cols.extend(['total_score', 'technical_score', 'experience_numeric', 
                                       'has_python', 'has_r', 'has_critical_language'])
                    
                    display_df = top_candidates[display_cols].copy()
                    display_df.columns = ['Name', 'Institution', 'Total Score', 'Tech Score', 
                                         'Experience', 'Python', 'R', 'Has Critical Lang']
                    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
                    
                    st.dataframe(display_df, use_container_width=True, height=500, key="top_candidates_table")
                
                with view_tab3:
                    # Analytics
                    create_critical_skills_analysis(top_candidates, "top_candidates")
                    
                    # Score distribution with unique key
                    fig = px.histogram(top_candidates, x='total_score', nbins=15,
                                     title='Score Distribution of Top Candidates')
                    
                    chart_key = generate_chart_key("score_dist_top")
                    st.plotly_chart(fig, use_container_width=True, key=chart_key)
                
                # Export Section
                st.markdown('<h3 class="sub-header">📥 Export Results</h3>', unsafe_allow_html=True)
                
                export_col1, export_col2 = st.columns(2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                with export_col1:
                    csv_all = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📊 All Filtered (CSV)",
                        data=csv_all,
                        file_name=f"ndmc_filtered_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_all_csv"
                    )
                
                with export_col2:
                    if file_type == 'excel':
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            filtered_df.to_excel(writer, sheet_name='Filtered Applicants', index=False)
                            top_candidates.to_excel(writer, sheet_name=f'Top {top_n}', index=False)
                        st.download_button(
                            label="📋 Excel Report",
                            data=output.getvalue(),
                            file_name=f"ndmc_report_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_excel"
                        )
                
                # Statistics
                st.markdown('<h3 class="sub-header">📈 Selection Statistics</h3>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    selection_rate = (len(filtered_df) / len(df_processed)) * 100
                    st.metric("Filter Rate", f"{selection_rate:.1f}%", key="filter_rate_metric")
                
                with col2:
                    python_rate = (filtered_df['has_python'].sum() / len(filtered_df)) * 100
                    st.metric("Python %", f"{python_rate:.1f}%", key="python_rate_metric")
                
                with col3:
                    r_rate = (filtered_df['has_r'].sum() / len(filtered_df)) * 100
                    st.metric("R %", f"{r_rate:.1f}%", key="r_rate_metric")
                
                with col4:
                    avg_score = filtered_df['total_score'].mean()
                    st.metric("Avg Score", f"{avg_score:.1f}", key="avg_score_metric")
            
            else:
                st.warning("No scoring data available.")
        else:
            st.warning("No applicants match the selected filters.")
    
    else:
        # Instructions
        st.info("👆 **Upload applicant file** to start screening!")
        
        with st.expander("📋 Advanced ML/DL Screening Criteria", expanded=True):
            st.markdown("""
            ### **🎯 CRITICAL REQUIREMENTS FOR NDMC HACKATHON**
            
            **🔴 MANDATORY REQUIREMENTS (Auto-reject if missing):**
            1. **Python or R programming experience** - Must have at least one
            2. **Minimum screening score** - Based on comprehensive evaluation
            
            **📊 SPECIALIZED SKILLS WEIGHTING:**
            | Skill Category | Weight | Examples |
            |---------------|--------|----------|
            | **Deep Learning** | ⭐⭐⭐⭐⭐⭐ (6) | Neural Networks, CNN, RNN, Transformers |
            | **Machine Learning** | ⭐⭐⭐⭐⭐ (5) | Supervised/Unsupervised, XGBoost, Random Forest |
            | **Mathematical Modeling** | ⭐⭐⭐⭐⭐ (5) | Simulation, Optimization, Statistical Modeling |
            | **Epidemiology** | ⭐⭐⭐⭐ (4) | Public Health, Biostatistics, Disease Surveillance |
            | **Data Science** | ⭐⭐⭐ (3) | Analytics, Visualization, Data Mining |
            | **Python/R (MANDATORY)** | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ (10) | Programming Language Requirement |
            
            **🎯 SCORING BREAKDOWN:**
            - **Technical Skills (40%)** - ML/DL/Mathematical Modeling expertise
            - **Experience (20%)** - Work experience in relevant fields
            - **Hackathon Experience (15%)** - Previous participation
            - **Policy Reflection (15%)** - Modeling-focused analysis
            - **Availability (10%)** - Full event attendance
            
            **🚀 EXPECTED EXPERTISE AREAS:**
            - **Machine Learning**: Classification, Regression, Ensemble Methods
            - **Deep Learning**: Neural Networks, Computer Vision, NLP
            - **Mathematical Modeling**: Simulation, Optimization, Statistical Analysis
            - **Epidemiology**: Public Health Analytics, Disease Modeling
            - **Programming**: Python (Pandas, Scikit-learn, TensorFlow/PyTorch) or R (tidyverse)
            
            **⚠️ AUTO-REJECTION CRITERIA:**
            - Missing Python/R programming experience
            - Insufficient technical score
            - No relevant modeling/analytics background
            
            **Developed for:** National Data Management Center (NDMC) Ethiopia
            """)

# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280;'>
    <p>🏥 <strong>National Data Management Center (NDMC) Ethiopia</strong> | Public Health Policy Hackathon 2025</p>
    <p>🤖 <strong>Advanced ML/DL & Mathematical Modeling Screening</strong> | Python/R Mandatory</p>
</div>
""", unsafe_allow_html=True)