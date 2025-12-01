import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Streamlit app configuration
st.set_page_config(page_title="NDMC Hackathon Screening", layout="wide")
st.title("🏥 NDMC Hackathon Applicant Screening Tool")
st.markdown("**Ethiopia Public Health Policy Hackathon - Applicant Evaluation System**")

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

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

# Upload Excel file
uploaded_file = st.file_uploader(
    "📁 Upload NDMC Hackathon Excel File", 
    type=["xlsx", "xls"],
    help="Upload the Excel file exported from Google Forms"
)

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

def calculate_technical_score(expertise_list, languages_list):
    """Calculate technical score based on expertise and languages"""
    score = 0
    
    # Medical/Public Health keywords (high value)
    medical_keywords = [
        'public health', 'epidemiology', 'biostatistics', 'health informatics',
        'clinical', 'medical', 'healthcare', 'immunization', 'vaccine',
        'maternal health', 'child health', 'infectious disease', 'nutrition'
    ]
    
    # Data Science/Technical keywords
    tech_keywords = [
        'data science', 'machine learning', 'ai', 'artificial intelligence',
        'statistics', 'data analysis', 'data visualization', 'python',
        'r programming', 'sql', 'gis', 'geospatial', 'biostatistics'
    ]
    
    # Programming languages scores
    programming_languages = {
        'python': 3, 'r': 3, 'sql': 2, 'javascript': 1, 'java': 1,
        'c++': 1, 'matlab': 2, 'sas': 2, 'stata': 2, 'spss': 1
    }
    
    # Check expertise
    if expertise_list:
        expertise_text = ' '.join([str(item).lower() for item in expertise_list])
        for keyword in medical_keywords + tech_keywords:
            if keyword in expertise_text:
                score += 2 if keyword in medical_keywords else 1
    
    # Check programming languages
    if languages_list:
        languages_text = ' '.join([str(lang).lower() for lang in languages_list])
        for lang, lang_score in programming_languages.items():
            if lang in languages_text:
                score += lang_score
    
    return score

def calculate_hackathon_score(row):
    """Calculate comprehensive score for each candidate"""
    score = 0
    
    # Experience (30% of total)
    if not pd.isna(row['experience_numeric']):
        experience_score = min(row['experience_numeric'] * 3, 15)  # Max 15 points
        score += experience_score
    
    # Technical skills (30% of total)
    tech_score = calculate_technical_score(row['expertise_list'], row['languages_list'])
    score += min(tech_score, 15)  # Max 15 points
    
    # Hackathon experience (15% of total)
    hackathon_col = COLUMN_MAPPING['hackathon_before']
    if hackathon_col in row and pd.notna(row[hackathon_col]):
        hackathon_response = str(row[hackathon_col]).lower()
        if 'yes' in hackathon_response:
            score += 10
            # Bonus for detailed experience
            exp_col = COLUMN_MAPPING['hackathon_experience']
            if exp_col in row and pd.notna(row[exp_col]) and len(str(row[exp_col]).strip()) > 20:
                score += 5
    
    # Policy interest & reflection (15% of total)
    reflection_col = COLUMN_MAPPING['reflection']
    if reflection_col in row and pd.notna(row[reflection_col]):
        reflection_text = str(row[reflection_col])
        if len(reflection_text.strip()) > 50:  # Meaningful reflection
            score += 10
            if len(reflection_text.strip()) > 150:  # Detailed reflection
                score += 5
    
    # Availability for full event (10% of total)
    availability_col = COLUMN_MAPPING['availability']
    if availability_col in row and pd.notna(row[availability_col]):
        availability_response = str(row[availability_col]).lower()
        if 'yes' in availability_response or 'available' in availability_response:
            score += 10
    
    return round(score, 1)

def main():
    if uploaded_file:
        try:
            # Read the Excel file
            st.info(f"📊 Loading file: {uploaded_file.name}")
            
            # Read Excel file
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            except:
                df = pd.read_excel(uploaded_file, engine='xlrd')
            
            # Verify columns
            missing_columns = [col for col in COLUMN_MAPPING.values() if col not in df.columns]
            
            if missing_columns:
                st.warning(f"Some expected columns are missing: {', '.join(missing_columns[:5])}...")
                st.write("Found columns:", list(df.columns))
            
            # Process the data
            with st.spinner("🔍 Processing applicant data..."):
                # Create processed dataframe
                df_processed = df.copy()
                
                # Extract experience
                exp_col = COLUMN_MAPPING['experience']
                df_processed['experience_numeric'] = df_processed[exp_col].apply(extract_numeric_experience)
                
                # Parse multi-select fields
                df_processed['expertise_list'] = df_processed[COLUMN_MAPPING['expertise']].apply(parse_multiselect_field)
                df_processed['languages_list'] = df_processed[COLUMN_MAPPING['languages']].apply(parse_multiselect_field)
                
                # Calculate scores
                df_processed['technical_score'] = df_processed.apply(
                    lambda x: calculate_technical_score(x['expertise_list'], x['languages_list']), axis=1
                )
                df_processed['total_score'] = df_processed.apply(calculate_hackathon_score, axis=1)
                
                # Store in session state
                st.session_state.processed_data = df_processed
            
            # Display overview
            st.success(f"✅ Successfully processed {len(df_processed)} applicants")
            
            # Overview metrics
            st.subheader("📊 Applicant Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Applicants", len(df_processed))
            
            with col2:
                valid_exp = df_processed['experience_numeric'].notna().sum()
                st.metric("Experience Data Available", valid_exp)
            
            with col3:
                hackathon_col = COLUMN_MAPPING['hackathon_before']
                if hackathon_col in df_processed.columns:
                    hackathon_experienced = df_processed[hackathon_col].apply(
                        lambda x: 'yes' in str(x).lower() if pd.notna(x) else False
                    ).sum()
                    st.metric("Previous Hackathon Experience", hackathon_experienced)
            
            with col4:
                availability_col = COLUMN_MAPPING['availability']
                if availability_col in df_processed.columns:
                    fully_available = df_processed[availability_col].apply(
                        lambda x: 'yes' in str(x).lower() if pd.notna(x) else False
                    ).sum()
                    st.metric("Fully Available", fully_available)
            
            # Filters Section
            st.subheader("🎛️ Screening Filters")
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Experience filter
                min_exp = st.slider(
                    "Minimum Years of Experience",
                    min_value=0,
                    max_value=20,
                    value=1,
                    help="Filter by minimum work experience"
                )
                
                # Availability filter
                availability_filter = st.selectbox(
                    "Availability for Full Event",
                    ["All", "Available", "Not Available"],
                    help="Filter by availability Dec 21-25, 2025"
                )
            
            with filter_col2:
                # Institution type filter
                institution_col = COLUMN_MAPPING['institution']
                if institution_col in df_processed.columns:
                    institutions = sorted(df_processed[institution_col].dropna().unique().tolist())
                    selected_institutions = st.multiselect(
                        "Institution/Organization",
                        institutions,
                        help="Filter by specific institutions"
                    )
                
                # Hackathon experience filter
                hackathon_filter = st.selectbox(
                    "Previous Hackathon Experience",
                    ["All", "Yes", "No"],
                    help="Filter by previous hackathon participation"
                )
            
            with filter_col3:
                # Programming languages filter
                all_languages = []
                for lang_list in df_processed['languages_list'].dropna():
                    all_languages.extend([lang.lower() for lang in lang_list])
                
                unique_languages = sorted(set([lang for lang in all_languages if lang]))
                selected_languages = st.multiselect(
                    "Programming Languages",
                    unique_languages[:20],
                    help="Filter by programming language proficiency"
                )
                
                # Expertise area filter
                all_expertise = []
                for exp_list in df_processed['expertise_list'].dropna():
                    all_expertise.extend([exp.lower() for exp in exp_list])
                
                unique_expertise = sorted(set([exp for exp in all_expertise if exp]))
                selected_expertise = st.multiselect(
                    "Areas of Expertise",
                    unique_expertise[:20],
                    help="Filter by areas of expertise"
                )
            
            # Apply filters
            filtered_df = df_processed.copy()
            
            # Experience filter
            filtered_df = filtered_df[filtered_df['experience_numeric'] >= min_exp]
            
            # Availability filter
            if availability_filter != "All":
                availability_col = COLUMN_MAPPING['availability']
                if availability_col in filtered_df.columns:
                    if availability_filter == "Available":
                        filtered_df = filtered_df[filtered_df[availability_col].str.lower().str.contains('yes', na=False)]
                    else:
                        filtered_df = filtered_df[~filtered_df[availability_col].str.lower().str.contains('yes', na=False)]
            
            # Institution filter
            if selected_institutions and institution_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[institution_col].isin(selected_institutions)]
            
            # Hackathon experience filter
            if hackathon_filter != "All":
                hackathon_col = COLUMN_MAPPING['hackathon_before']
                if hackathon_col in filtered_df.columns:
                    if hackathon_filter == "Yes":
                        filtered_df = filtered_df[filtered_df[hackathon_col].str.lower().str.contains('yes', na=False)]
                    else:
                        filtered_df = filtered_df[~filtered_df[hackathon_col].str.lower().str.contains('yes', na=False)]
            
            # Languages filter
            if selected_languages:
                def has_languages(lang_list):
                    if not isinstance(lang_list, list):
                        return False
                    lang_list_lower = [lang.lower() for lang in lang_list]
                    return any(lang in lang_list_lower for lang in selected_languages)
                
                filtered_df = filtered_df[filtered_df['languages_list'].apply(has_languages)]
            
            # Expertise filter
            if selected_expertise:
                def has_expertise(exp_list):
                    if not isinstance(exp_list, list):
                        return False
                    exp_list_lower = [exp.lower() for exp in exp_list]
                    return any(exp in exp_list_lower for exp in selected_expertise)
                
                filtered_df = filtered_df[filtered_df['expertise_list'].apply(has_expertise)]
            
            # Store filtered data
            st.session_state.filtered_data = filtered_df
            
            # Display filtered results
            st.subheader(f"✅ Filtered Results: {len(filtered_df)} applicants")
            
            # Display options
            display_option = st.radio(
                "View:",
                ["Summary View", "Detailed View", "Scoring Details"],
                horizontal=True
            )
            
            if display_option == "Summary View":
                # Summary columns
                summary_cols = [
                    COLUMN_MAPPING['name'],
                    COLUMN_MAPPING['email'],
                    COLUMN_MAPPING['institution'],
                    COLUMN_MAPPING['position'],
                    'experience_numeric',
                    'technical_score',
                    'total_score'
                ]
                
                summary_df = filtered_df[summary_cols].copy()
                summary_df.columns = ['Name', 'Email', 'Institution', 'Position', 'Experience (Years)', 'Tech Score', 'Total Score']
                summary_df = summary_df.sort_values('Total Score', ascending=False)
                
                st.dataframe(
                    summary_df.reset_index(drop=True),
                    use_container_width=True,
                    height=400
                )
            
            elif display_option == "Detailed View":
                # Detailed columns
                detail_cols = [
                    COLUMN_MAPPING['name'],
                    COLUMN_MAPPING['email'],
                    COLUMN_MAPPING['institution'],
                    COLUMN_MAPPING['position'],
                    COLUMN_MAPPING['expertise'],
                    COLUMN_MAPPING['languages'],
                    COLUMN_MAPPING['hackathon_before'],
                    COLUMN_MAPPING['availability'],
                    'total_score'
                ]
                
                detail_df = filtered_df[detail_cols].copy()
                detail_df.columns = ['Name', 'Email', 'Institution', 'Position', 'Expertise', 'Languages', 'Hackathon Before', 'Available', 'Score']
                detail_df = detail_df.sort_values('Score', ascending=False)
                
                st.dataframe(
                    detail_df.reset_index(drop=True),
                    use_container_width=True,
                    height=400
                )
            
            else:  # Scoring Details
                scoring_df = filtered_df.copy()
                scoring_cols = [
                    COLUMN_MAPPING['name'],
                    'experience_numeric',
                    'technical_score',
                    'total_score'
                ]
                
                # Add score breakdown
                scoring_df['Exp Score'] = scoring_df['experience_numeric'].apply(lambda x: min(x * 3, 15) if pd.notna(x) else 0)
                scoring_df['Hackathon Bonus'] = scoring_df.apply(
                    lambda row: 15 if ('yes' in str(row.get(COLUMN_MAPPING['hackathon_before'], '')).lower() and 
                                     len(str(row.get(COLUMN_MAPPING['hackathon_experience'], '')).strip()) > 20) 
                                 else (10 if 'yes' in str(row.get(COLUMN_MAPPING['hackathon_before'], '')).lower() else 0),
                    axis=1
                )
                
                scoring_df = scoring_df[[COLUMN_MAPPING['name'], 'Exp Score', 'technical_score', 'Hackathon Bonus', 'total_score']]
                scoring_df.columns = ['Name', 'Experience Score', 'Technical Score', 'Hackathon Bonus', 'Total Score']
                scoring_df = scoring_df.sort_values('Total Score', ascending=False)
                
                st.dataframe(
                    scoring_df.reset_index(drop=True),
                    use_container_width=True,
                    height=400
                )
            
            # Top Candidates Section
            st.subheader("🏆 Top Candidates Ranking")
            
            top_n = st.slider(
                "Number of top candidates to select",
                min_value=5,
                max_value=min(50, len(filtered_df)),
                value=20,
                help="Select number of top candidates for the hackathon"
            )
            
            # Get top candidates
            top_candidates = filtered_df.nlargest(top_n, 'total_score').copy()
            
            # Display top candidates with detailed info
            top_display_cols = [
                COLUMN_MAPPING['name'],
                COLUMN_MAPPING['email'],
                COLUMN_MAPPING['institution'],
                COLUMN_MAPPING['position'],
                'experience_numeric',
                COLUMN_MAPPING['expertise'],
                COLUMN_MAPPING['languages'],
                COLUMN_MAPPING['hackathon_before'],
                COLUMN_MAPPING['availability'],
                'total_score'
            ]
            
            top_display = top_candidates[top_display_cols].copy()
            top_display.columns = [
                'Name', 'Email', 'Institution', 'Position', 'Exp (Yrs)', 
                'Expertise', 'Languages', 'Hackathon Exp', 'Available', 'Score'
            ]
            top_display = top_display.sort_values('Score', ascending=False).reset_index(drop=True)
            
            # Add rank column
            top_display.insert(0, 'Rank', range(1, len(top_display) + 1))
            
            st.dataframe(
                top_display,
                use_container_width=True,
                height=500
            )
            
            # Download Section
            st.subheader("📥 Export Results")
            
            col1, col2, col3 = st.columns(3)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with col1:
                # CSV - All filtered applicants
                csv_all = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📊 All Filtered Applicants",
                    data=csv_all,
                    file_name=f"ndmc_filtered_applicants_{timestamp}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # CSV - Top candidates
                csv_top = top_candidates.to_csv(index=False)
                st.download_button(
                    label="🏅 Top Candidates",
                    data=csv_top,
                    file_name=f"ndmc_top_{top_n}_candidates_{timestamp}.csv",
                    mime="text/csv"
                )
            
            with col3:
                # Excel report
                output = pd.ExcelWriter(f"ndmc_report_{timestamp}.xlsx", engine='openpyxl')
                filtered_df.to_excel(output, sheet_name='All Filtered', index=False)
                top_candidates.to_excel(output, sheet_name=f'Top {top_n}', index=False)
                
                # Summary statistics
                summary_stats = pd.DataFrame({
                    'Metric': ['Total Applicants', 'Filtered Applicants', 'Top Candidates Selected',
                              'Average Experience', 'Average Technical Score', 'Average Total Score',
                              'Hackathon Experienced (%)', 'Fully Available (%)'],
                    'Value': [
                        len(df_processed),
                        len(filtered_df),
                        top_n,
                        f"{filtered_df['experience_numeric'].mean():.1f} years",
                        f"{filtered_df['technical_score'].mean():.1f}",
                        f"{filtered_df['total_score'].mean():.1f}",
                        f"{(filtered_df[COLUMN_MAPPING['hackathon_before']].str.lower().str.contains('yes').sum() / len(filtered_df) * 100):.1f}%",
                        f"{(filtered_df[COLUMN_MAPPING['availability']].str.lower().str.contains('yes').sum() / len(filtered_df) * 100):.1f}%"
                    ]
                })
                summary_stats.to_excel(output, sheet_name='Summary', index=False)
                output.close()
                
                with open(f"ndmc_report_{timestamp}.xlsx", "rb") as file:
                    st.download_button(
                        label="📋 Full Excel Report",
                        data=file,
                        file_name=f"ndmc_hackathon_report_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            # Statistics Section
            st.subheader("📈 Selection Statistics")
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                selection_rate = (len(filtered_df) / len(df_processed)) * 100
                st.metric("Initial Filter Rate", f"{selection_rate:.1f}%")
            
            with stat_col2:
                top_selection_rate = (top_n / len(df_processed)) * 100
                st.metric("Final Selection Rate", f"{top_selection_rate:.1f}%")
            
            with stat_col3:
                avg_exp = filtered_df['experience_numeric'].mean()
                st.metric("Avg Experience", f"{avg_exp:.1f} years")
            
            with stat_col4:
                avg_score = filtered_df['total_score'].mean()
                st.metric("Avg Score", f"{avg_score:.1f}")
            
            # Diversity Metrics
            with st.expander("🌍 Diversity Metrics"):
                div_col1, div_col2, div_col3 = st.columns(3)
                
                with div_col1:
                    if COLUMN_MAPPING['institution'] in filtered_df.columns:
                        unique_institutions = filtered_df[COLUMN_MAPPING['institution']].nunique()
                        st.metric("Unique Institutions", unique_institutions)
                
                with div_col2:
                    if COLUMN_MAPPING['position'] in filtered_df.columns:
                        positions = filtered_df[COLUMN_MAPPING['position']].value_counts()
                        st.write("**Top Positions:**")
                        for position, count in positions.head(5).items():
                            st.write(f"• {position}: {count}")
                
                with div_col3:
                    if COLUMN_MAPPING['city'] in filtered_df.columns:
                        cities = filtered_df[COLUMN_MAPPING['city']].value_counts()
                        st.write("**Top Cities:**")
                        for city, count in cities.head(5).items():
                            st.write(f"• {city}: {count}")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("""
            **Common issues and solutions:**
            1. **File format:** Ensure it's a valid Excel file (.xlsx or .xls)
            2. **Column names:** The file should have the exact Google Forms column names
            3. **Encoding:** Try saving the file as UTF-8 encoded
            4. **Data structure:** Ensure data starts from row 1, column A
            
            **For quick fix:**
            - Open the file in Excel
            - Save as .xlsx format
            - Re-upload the file
            """)
    
    else:
        # Instructions
        st.info("👆 **Upload the NDMC Hackathon Excel file** to start screening applicants!")
        
        with st.expander("📋 About this Screening Tool"):
            st.markdown("""
            ### **NDMC Hackathon Applicant Screening Tool**
            
            **Purpose:**
            This tool is specifically designed for screening applicants for the Ethiopia Public Health Policy Hackathon (Dec 21-25, 2025).
            
            **Scoring Criteria:**
            1. **Experience (30%)** - Work experience in years
            2. **Technical Skills (30%)** - Expertise and programming languages
            3. **Hackathon Experience (15%)** - Previous participation and learnings
            4. **Policy Reflection (15%)** - Quality of reflection on challenge areas
            5. **Availability (10%)** - Confirmed availability for full event
            
            **Expected Columns:**
            - Full Name, Email, Phone Number
            - Institution, Position, Work Experience
            - Areas of Expertise, Programming Languages
            - Hackathon experience, Availability
            - Policy challenge reflections
            
            **Output:**
            - Ranked list of top candidates
            - Filtered applicant pool
            - Detailed scoring breakdown
            - Export options (CSV, Excel)
            
            **Developed for:** National Data Management Center (NDMC) Ethiopia
            """)

# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.caption("🏥 National Data Management Center (NDMC) Ethiopia | Public Health Policy Hackathon 2025")