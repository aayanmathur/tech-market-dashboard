import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# Page config
st.set_page_config(
    page_title="Tech Job Analytics",
    page_icon="🚀",
    layout="wide"
)

# Simple, working CSS
st.markdown("""
<style>
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .section-title {
        font-size: 24px;
        color: #2E86AB;
        font-weight: bold;
        margin: 30px 0 15px 0;
    }
    .insight-card {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2E86AB;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/jobs_data.csv')
        df['date_posted'] = pd.to_datetime(df['date_posted'])
        
        # Process keywords - simple and reliable
        df['keywords_list'] = df['keywords'].fillna('').apply(
            lambda x: [k.strip().lower() for k in str(x).split(',') if k.strip()]
        )
        
        # Simple remote detection
        df['is_remote'] = df['location'].fillna('').str.lower().str.contains('remote')
        
        # Simple salary detection
        df['has_salary'] = df['job_description'].fillna('').str.contains(r'\$\d', case=False)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def get_top_skills(df, n=20):
    all_skills = []
    for skills in df['keywords_list']:
        all_skills.extend(skills)
    return Counter(all_skills).most_common(n)

def main():
    # Header - simple and visible
    st.markdown('<p class="big-font"> Tech Job Market Analytics</p>', unsafe_allow_html=True)
    st.markdown("### Analysis of 5,466 current tech job postings")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category filter
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Job Category", categories)
    
    # Remote filter
    remote_option = st.sidebar.selectbox("Work Type", ["All", "Remote Only", "On-site Only"])
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if remote_option == "Remote Only":
        filtered_df = filtered_df[filtered_df['is_remote'] == True]
    elif remote_option == "On-site Only":
        filtered_df = filtered_df[filtered_df['is_remote'] == False]
    
    if len(filtered_df) == 0:
        st.warning("No jobs match your filters. Please adjust your selection.")
        return
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #2E86AB; margin: 0;">{len(filtered_df):,}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Total Jobs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #2E86AB; margin: 0;">{filtered_df['company'].nunique():,}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Companies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        all_skills = get_top_skills(filtered_df, 1000)
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #2E86AB; margin: 0;">{len(all_skills):,}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Unique Skills</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        remote_pct = (filtered_df['is_remote'].sum() / len(filtered_df) * 100)
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #2E86AB; margin: 0;">{remote_pct:.1f}%</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Remote Jobs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        salary_pct = (filtered_df['has_salary'].sum() / len(filtered_df) * 100)
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #2E86AB; margin: 0;">{salary_pct:.1f}%</h2>
            <p style="margin: 5px 0 0 0; color: #666;">With Salary</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills Analysis
    st.markdown('<p class="section-title"> Most In-Demand Skills</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_skills = get_top_skills(filtered_df, 20)
        if top_skills:
            skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
            
            fig = px.bar(
                skills_df, 
                x='Count', 
                y='Skill',
                orientation='h',
                title='Top 20 Technical Skills',
                color='Count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Remote vs On-site
        remote_counts = filtered_df['is_remote'].value_counts()
        labels = ['On-site', 'Remote']
        values = [remote_counts.get(False, 0), remote_counts.get(True, 0)]
        
        fig = px.pie(
            values=values,
            names=labels,
            title='Remote vs On-site Jobs',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top skill combinations
        st.markdown("**Top Skill Pairs**")
        skill_pairs = []
        for skills in filtered_df['keywords_list']:
            if len(skills) >= 2:
                for i in range(len(skills)):
                    for j in range(i+1, len(skills)):
                        pair = tuple(sorted([skills[i], skills[j]]))
                        skill_pairs.append(pair)
        
        pair_counts = Counter(skill_pairs).most_common(10)
        
        for pair, count in pair_counts:
            st.write(f"**{pair[0]} + {pair[1]}**: {count} jobs")
    
    # Company and Location Analysis
    st.markdown('<p class="section-title"> Company & Location Insights</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top companies
        company_counts = filtered_df['company'].value_counts().head(15)
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title='Top 15 Hiring Companies',
            color=company_counts.values,
            color_continuous_scale='oranges'
        )
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Job categories
        category_counts = filtered_df['category'].value_counts()
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Job Categories Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top locations (excluding remote)
        non_remote_df = filtered_df[~filtered_df['is_remote']]
        if len(non_remote_df) > 0:
            location_counts = non_remote_df['location'].value_counts().head(10)
            
            fig = px.bar(
                x=location_counts.values,
                y=location_counts.index,
                orientation='h',
                title='Top On-site Locations',
                color=location_counts.values,
                color_continuous_scale='blues'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Key Insights
    st.markdown('<p class="section-title"> Key Market Insights</p>', unsafe_allow_html=True)
    
    # Generate insights
    top_skill = get_top_skills(filtered_df, 1)[0] if get_top_skills(filtered_df, 1) else ('N/A', 0)
    top_company = filtered_df['company'].value_counts().index[0] if len(filtered_df) > 0 else 'N/A'
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <strong>🔥 Hottest Skill:</strong> {top_skill[0].upper()} appears in {top_skill[1]} job postings 
            ({top_skill[1]/len(filtered_df)*100:.1f}% of all jobs)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>🏠 Remote Work:</strong> {filtered_df['is_remote'].sum()} jobs ({remote_pct:.1f}%) 
            offer remote work opportunities
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <strong>🏢 Top Employer:</strong> {top_company} is actively hiring with 
            {filtered_df['company'].value_counts().iloc[0]} job postings
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>💰 Salary Transparency:</strong> {filtered_df['has_salary'].sum()} jobs ({salary_pct:.1f}%) 
            mention salary information
        </div>
        """, unsafe_allow_html=True)
    
    # Job Listings Table
    st.markdown('<p class="section-title"> Sample Job Listings</p>', unsafe_allow_html=True)
    
    # Create display dataframe - simple and foolproof
    display_data = []
    for _, row in filtered_df.head(100).iterrows():
        display_data.append({
            'Company': row['company'],
            'Category': row['category'], 
            'Location': row['location'],
            'Remote': '✅ Yes' if row['is_remote'] else '❌ No',
            'Salary Info': '💰 Yes' if row['has_salary'] else '❌ No',
            'Date Posted': row['date_posted'].strftime('%Y-%m-%d') if pd.notna(row['date_posted']) else 'N/A'
        })
    
    display_df = pd.DataFrame(display_data)
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Footer
    st.markdown("---")

if __name__ == "__main__":
    main()