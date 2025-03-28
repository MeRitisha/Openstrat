import streamlit as st
import plotly.express as px
import pandas as pd
import json
import datetime
import time
import io
import logging
from scraper import (
    scrape_job_listings, 
    load_companies_data, 
    get_companies_by_industry, 
    get_companies_by_priority,
    get_industry_hiring_trends,
    get_real_time_job_updates
)
from data_processor import process_job_data
from analyzer import (
    analyze_hiring_trends, 
    identify_skill_patterns, 
    detect_market_shifts, 
    analyze_industry_trends,
    generate_industry_recommendations
)
from visualizer import create_hiring_trend_chart, create_skill_heatmap, create_geo_expansion_map
from notifier import setup_email_preferences
from database import get_db_connection, save_company_to_watch, get_watched_companies
from utils import get_demo_data
from resume_analyzer import extract_resume_content, analyze_resume_vs_company_jobs, generate_resume_insights, get_career_opportunity_score
from talent_analyzer import analyze_talent_availability, get_top_cities_for_talent, get_skill_prevalence, get_competing_companies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Competitive Hiring Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'email_preferences' not in st.session_state:
    st.session_state.email_preferences = {
        'enabled': False,
        'email': '',
        'frequency': 'daily',
        'alert_threshold': 20
    }

if 'watched_companies' not in st.session_state:
    # Load watched companies from database
    st.session_state.watched_companies = get_watched_companies()
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

if 'current_view' not in st.session_state:
    st.session_state.current_view = "dashboard"

if 'uploaded_resume' not in st.session_state:
    st.session_state.uploaded_resume = None
    
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
    
# Initialize achievements and gamification data
if 'achievements' not in st.session_state:
    st.session_state.achievements = {
        'companies_tracked': {
            'name': 'Company Tracker',
            'description': 'Track multiple competitor companies',
            'levels': [
                {'name': 'Beginner', 'threshold': 1, 'badge': '🥉', 'unlocked': False},
                {'name': 'Intermediate', 'threshold': 5, 'badge': '🥈', 'unlocked': False},
                {'name': 'Advanced', 'threshold': 10, 'badge': '🥇', 'unlocked': False},
                {'name': 'Expert', 'threshold': 25, 'badge': '👑', 'unlocked': False}
            ],
            'current_level': 0,
            'progress': 0,
            'max': 25
        },
        'industries_analyzed': {
            'name': 'Industry Analyst',
            'description': 'Analyze different industries for hiring trends',
            'levels': [
                {'name': 'Beginner', 'threshold': 1, 'badge': '🥉', 'unlocked': False},
                {'name': 'Intermediate', 'threshold': 3, 'badge': '🥈', 'unlocked': False},
                {'name': 'Advanced', 'threshold': 5, 'badge': '🥇', 'unlocked': False},
                {'name': 'Expert', 'threshold': 7, 'badge': '👑', 'unlocked': False}
            ],
            'current_level': 0,
            'progress': 0,
            'max': 7
        },
        'talent_searches': {
            'name': 'Talent Scout',
            'description': 'Search for talent in various locations',
            'levels': [
                {'name': 'Beginner', 'threshold': 1, 'badge': '🥉', 'unlocked': False},
                {'name': 'Intermediate', 'threshold': 5, 'badge': '🥈', 'unlocked': False},
                {'name': 'Advanced', 'threshold': 15, 'badge': '🥇', 'unlocked': False},
                {'name': 'Expert', 'threshold': 30, 'badge': '👑', 'unlocked': False}
            ],
            'current_level': 0,
            'progress': 0,
            'max': 30
        },
        'resumes_analyzed': {
            'name': 'Resume Expert',
            'description': 'Analyze resumes against job requirements',
            'levels': [
                {'name': 'Beginner', 'threshold': 1, 'badge': '🥉', 'unlocked': False},
                {'name': 'Intermediate', 'threshold': 5, 'badge': '🥈', 'unlocked': False},
                {'name': 'Advanced', 'threshold': 10, 'badge': '🥇', 'unlocked': False},
                {'name': 'Expert', 'threshold': 20, 'badge': '👑', 'unlocked': False}
            ],
            'current_level': 0,
            'progress': 0,
            'max': 20
        },
        'insights_generated': {
            'name': 'Insight Generator',
            'description': 'Generate hiring insights from data',
            'levels': [
                {'name': 'Beginner', 'threshold': 5, 'badge': '🥉', 'unlocked': False},
                {'name': 'Intermediate', 'threshold': 15, 'badge': '🥈', 'unlocked': False},
                {'name': 'Advanced', 'threshold': 30, 'badge': '🥇', 'unlocked': False},
                {'name': 'Expert', 'threshold': 50, 'badge': '👑', 'unlocked': False}
            ],
            'current_level': 0,
            'progress': 0, 
            'max': 50
        }
    }
    
if 'gamification_stats' not in st.session_state:
    st.session_state.gamification_stats = {
        'recruitment_score': 0,
        'total_actions': 0,
        'streak_days': 0,
        'last_active_date': None
    }

# Helper functions for achievements
def update_achievement_progress(achievement_key, increment=1, check_unlocks=True):
    """Update achievement progress and check for unlocks"""
    if achievement_key in st.session_state.achievements:
        achievement = st.session_state.achievements[achievement_key]
        achievement['progress'] += increment
        
        # Check for level unlocks
        if check_unlocks:
            current_progress = achievement['progress']
            for i, level in enumerate(achievement['levels']):
                if current_progress >= level['threshold'] and not level['unlocked']:
                    level['unlocked'] = True
                    achievement['current_level'] = i
                    return True, level  # Return unlock info
        
        return False, None
    return False, None

def calculate_recruitment_score():
    """Calculate overall recruitment strategy score based on achievements"""
    total_score = 0
    achievement_weights = {
        'companies_tracked': 25,
        'industries_analyzed': 20,
        'talent_searches': 15,
        'resumes_analyzed': 15,
        'insights_generated': 25
    }
    
    for key, achievement in st.session_state.achievements.items():
        # Calculate percentage completion for this achievement
        max_value = achievement['max']
        current_value = achievement['progress']
        completion_pct = min(1.0, current_value / max_value)
        
        # Add weighted score
        total_score += completion_pct * achievement_weights.get(key, 10)
    
    return round(total_score)

# Application functions
def add_company():
    """Add a company to the watch list"""
    # Check if we're adding from the sidebar or the company page
    company_name = ""
    if "sidebar_new_company" in st.session_state and st.session_state.sidebar_new_company:
        company_name = st.session_state.sidebar_new_company
    elif "new_company" in st.session_state and st.session_state.new_company:
        company_name = st.session_state.new_company
    
    # Add the company if name is provided and not already in the list
    if company_name and company_name not in st.session_state.watched_companies:
        with st.spinner(f"Adding {company_name} to your watch list..."):
            # Save to database
            success = save_company_to_watch(company_name)
            if success:
                st.session_state.watched_companies.append(company_name)
                st.success(f"Added {company_name} to your watch list!")
                
                # Update achievements for tracking companies
                if 'achievements' in st.session_state:
                    unlocked, level = update_achievement_progress('companies_tracked')
                    if unlocked:
                        st.balloons()
                        st.success(f"🎉 Achievement Unlocked: Company Tracker - {level['name']} {level['badge']}")
                    
                    # Increment total actions
                    if 'gamification_stats' in st.session_state:
                        st.session_state.gamification_stats['total_actions'] += 1
            else:
                st.error("Failed to add company. Please try again.")
                
def add_top_companies(count=50):
    """Add top companies to the watchlist"""
    try:
        # List of predefined top tech companies
        top_tech_companies = [
            "Apple", "Microsoft", "Google", "Amazon", "Meta", 
            "Tesla", "NVIDIA", "Samsung", "Intel", "IBM",
            "Oracle", "Salesforce", "Adobe", "SAP", "OpenAI",
            "Palantir", "Snowflake", "Databricks", "Cisco", "ServiceNow",
            "Sony", "LG Electronics", "Dell Technologies", "HP", "Lenovo",
            "ASUS", "Xiaomi", "OnePlus", "Huawei", "Razer",
            "Stripe", "PayPal", "Square", "Robinhood", "Coinbase", 
            "CrowdStrike", "Darktrace", "Cloudflare", "Okta", "Zscaler",
            "SpaceX", "Rivian", "Waymo", "ByteDance", "Epic Games",
            "DeepMind", "Anduril", "QuantumScape", "Boston Dynamics", "Cruise"
        ]
        
        # Limit to the requested count
        companies_to_add = top_tech_companies[:count]
        added_count = 0
        
        with st.spinner(f"Adding {len(companies_to_add)} top companies to your watchlist..."):
            for company_name in companies_to_add:
                if company_name and company_name not in st.session_state.watched_companies:
                    # Save to database
                    success = save_company_to_watch(company_name)
                    if success:
                        st.session_state.watched_companies.append(company_name)
                        added_count += 1
                        
                        # Update achievements for tracking companies (without notifications for each company)
                        if 'achievements' in st.session_state:
                            update_achievement_progress('companies_tracked', check_unlocks=False)
            
            # Now check for level unlocks once at the end
            if 'achievements' in st.session_state and added_count > 0:
                unlocked, level = update_achievement_progress('companies_tracked', increment=0, check_unlocks=True)
                if unlocked:
                    st.balloons()
                    st.success(f"🎉 Achievement Unlocked: Company Tracker - {level['name']} {level['badge']}")
                
                # Increment total actions
                if 'gamification_stats' in st.session_state:
                    st.session_state.gamification_stats['total_actions'] += 1
                    
            return added_count
    except Exception as e:
        st.error(f"Error adding top companies: {str(e)}")
        return 0

def refresh_data():
    """Refresh the data from all sources"""
    with st.spinner("Fetching latest hiring data..."):
        # Get real-time job updates for watched companies
        if st.session_state.watched_companies:
            # Use the real-time job updates function
            job_updates = get_real_time_job_updates(st.session_state.watched_companies)
            
            # Store the job updates in session state
            if 'real_time_job_data' not in st.session_state:
                st.session_state.real_time_job_data = {}
            
            st.session_state.real_time_job_data = job_updates
            
            # Count new jobs
            new_jobs_count = sum(
                len([job for job in jobs if job.get('status') == 'new']) 
                for jobs in job_updates.values()
            )
            
            # Show the count of new jobs
            if new_jobs_count > 0:
                st.info(f"Found {new_jobs_count} new job postings!")
                
        # Update the timestamp
        st.session_state.last_update = datetime.datetime.now()
    st.success("Data refreshed successfully!")
    
def change_view(view):
    """Change the current view/tab"""
    st.session_state.current_view = view
    
# Sidebar
with st.sidebar:
    st.title("🔍 Competitive Hiring Intel")
    
    # Navigation
    st.subheader("Navigation")
    if st.button("📊 Dashboard", use_container_width=True):
        change_view("dashboard")
    if st.button("🔎 Company Intelligence", use_container_width=True):
        change_view("company")
    if st.button("📄 Resume Analyzer", use_container_width=True):
        change_view("resume")
    if st.button("🔍 Talent Demand", use_container_width=True):
        change_view("talent")
    if st.button("🎮 Gamification", use_container_width=True):
        change_view("gamification")
    if st.button("⚙️ Settings", use_container_width=True):
        change_view("settings")
    
    # Company watchlist
    st.subheader("Companies Watchlist")
    
    # Add company form
    st.text_input("Add a company:", key="sidebar_new_company")
    st.button("Add Company", on_click=add_company)
    
    # List of watched companies
    if st.session_state.watched_companies:
        for company in st.session_state.watched_companies:
            st.write(f"• {company}")
    else:
        st.info("No companies in your watchlist. Add one to get started!")
    
    # Data refresh
    st.subheader("Data Controls")
    st.button("🔄 Refresh Data", on_click=refresh_data)
    
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.caption("Not yet updated")

# Main content area
if st.session_state.current_view == "dashboard":
    st.title("Competitive Hiring Intelligence Dashboard")
    
    # Add automatic refresh option
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh Interval (minutes)", min_value=1, max_value=60, value=5)
        st.sidebar.caption(f"Data will refresh every {refresh_interval} minutes")
        
        # Auto-refresh logic
        if 'last_auto_refresh' not in st.session_state:
            st.session_state.last_auto_refresh = time.time()
            
        # Check if it's time to refresh
        current_time = time.time()
        if current_time - st.session_state.last_auto_refresh >= refresh_interval * 60:
            # Trigger refresh
            refresh_data()
            st.session_state.last_auto_refresh = current_time
    
    if not st.session_state.watched_companies:
        st.info("Add companies to your watchlist to see hiring intelligence.")
        st.write("This tool helps you:")
        st.write("• Predict market shifts based on hiring patterns")
        st.write("• Identify skill gaps in your industry")
        st.write("• Anticipate new product launches from competitors")
        st.write("• Track real-time job updates with timestamps")
        
        # Sample visualization to show what the dashboard will look like
        st.subheader("Sample Dashboard Preview")
        # Using demo data for visualization
        demo_data = get_demo_data()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Hiring Velocity (Sample)")
            fig = create_hiring_trend_chart(demo_data["hiring_velocity"])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Skill Demand (Sample)")
            fig = create_skill_heatmap(demo_data["skill_demand"])
            st.plotly_chart(fig, use_container_width=True)
            
        st.caption("⚠️ This is sample data. Add companies to your watchlist to see real insights.")
        
    else:
        # Real dashboard with data from watched companies
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric(
                label="Companies Tracked", 
                value=len(st.session_state.watched_companies),
                delta=None
            )
        
        # Display real-time job metrics if available
        if 'real_time_job_data' in st.session_state and st.session_state.real_time_job_data:
            # Calculate total jobs and new jobs
            total_jobs = sum(len(jobs) for jobs in st.session_state.real_time_job_data.values())
            new_jobs = sum(
                len([job for job in jobs if job.get('status') == 'new']) 
                for jobs in st.session_state.real_time_job_data.values()
            )
            
            with col2:
                st.metric(
                    label="Roles Monitored", 
                    value=total_jobs,
                    delta=f"+{new_jobs} new"
                )
        else:
            with col2:
                st.metric(
                    label="Roles Monitored", 
                    value="0",
                    delta=None
                )
        
        with col3:
            # In a real app, we would calculate this from actual data
            st.metric(
                label="Detected Trends", 
                value="4",
                delta="+2 new"
            )
        
        # Main dashboard components
        st.subheader("Hiring Velocity")
        
        # For this example, we'll use the demo data
        # In a real app, this would be replaced with actual scraped and analyzed data
        demo_data = get_demo_data()
        
        # Hiring Trends Chart
        fig = create_hiring_trend_chart(demo_data["hiring_velocity"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Real-time job updates section
        st.subheader("Real-Time Job Updates")
        
        if 'real_time_job_data' in st.session_state and st.session_state.real_time_job_data:
            # Display the latest job postings with timestamps
            for company, jobs in st.session_state.real_time_job_data.items():
                if jobs:  # Only show companies that have jobs
                    st.write(f"### {company}")
                    
                    # Create a table of job listings
                    job_df = pd.DataFrame([
                        {
                            "Job Title": job.get("title", ""),
                            "Location": job.get("location", ""),
                            "Status": job.get("status", "").upper(),
                            "Posted": job.get("posted_time", ""),
                            "Timestamp": job.get("timestamp", "")
                        }
                        for job in jobs[:5]  # Show only the first 5 jobs for each company
                    ])
                    
                    # Apply styling based on job status
                    def highlight_new(val):
                        if val == "NEW":
                            return 'background-color: #d4f7dc; font-weight: bold'
                        elif val == "UPDATED":
                            return 'background-color: #f7f3d4; font-weight: bold'
                        else:
                            return ''
                    
                    # Display the styled dataframe
                    st.dataframe(
                        job_df.style.applymap(highlight_new, subset=["Status"]), 
                        use_container_width=True
                    )
                    
                    # Show a view more option if there are more than 5 jobs
                    if len(jobs) > 5:
                        st.caption(f"Showing 5 of {len(jobs)} jobs. View Company Intelligence for more.")
        else:
            st.info("No real-time job data available yet. Click 'Refresh Data' to fetch the latest job listings.")
            
        # Insights from the data
        st.subheader("Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📈 **Hiring Surge Detected**: Google has increased hiring for AI engineers by 35% in the last month, suggesting a strategic focus on AI capabilities.")
            st.info("🌎 **Geographic Expansion**: Shopify is hiring more remote roles focused on Latin America, indicating potential market expansion.")
        
        with col2:
            st.warning("⚠️ **Leadership Changes**: 3 competitors have posted new CFO positions, potentially indicating preparation for funding rounds or IPO.")
            st.success("✅ **Opportunity**: Decline in frontend developer hiring across competitors suggests an opportunity to gain UI/UX advantage.")
        
        # Skills heatmap
        st.subheader("In-Demand Skills Across Competitors")
        fig = create_skill_heatmap(demo_data["skill_demand"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Geographic distribution
        st.subheader("Geographic Hiring Focus")
        fig = create_geo_expansion_map(demo_data["geo_distribution"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Strategic recommendations
        st.subheader("Strategic Recommendations")
        st.markdown("""
        Based on current hiring patterns:
        
        1. **Consider investing in AI capabilities** - Multiple competitors are building AI teams
        2. **Focus on Latin America market** - Hiring patterns suggest market opportunity
        3. **Prepare for competitive funding events** - CFO hiring indicates upcoming financial activities
        4. **Leverage UI/UX as differentiator** - Competitors are under-investing in frontend talent
        """)

elif st.session_state.current_view == "company":
    st.title("Company Intelligence")
    
    if not st.session_state.watched_companies:
        st.info("Add companies to your watchlist to see detailed intelligence.")
        
        # Add company form
        st.subheader("Add a Company")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            with st.form("add_company_form"):
                st.text_input("Company name", key="new_company", 
                             placeholder="e.g., Google, Microsoft, Amazon")
                submitted = st.form_submit_button("Add to Watchlist")
                if submitted:
                    add_company()
                    st.rerun()
        
        with col2:
            if st.button("Add Top 50 Companies", use_container_width=True):
                added_count = add_top_companies(50)
                if added_count > 0:
                    st.success(f"Added {added_count} top companies to your watchlist!")
                    st.rerun()
        
        if not st.session_state.watched_companies:
            st.stop()
    
    # Company selector
    selected_company = st.selectbox(
        "Select a company to analyze:",
        options=st.session_state.watched_companies
    )
    
    if selected_company:
        st.subheader(f"{selected_company} Hiring Intelligence")
        
        # Using demo data for now
        demo_data = get_demo_data()
        company_data = demo_data["company_specific"].get(selected_company, demo_data["company_specific"]["Google"])
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Active Job Postings", 
                value=company_data["active_jobs"],
                delta=company_data["jobs_delta"]
            )
        with col2:
            st.metric(
                label="Hiring Velocity", 
                value=f"{company_data['velocity']}%",
                delta=f"{company_data['velocity_delta']}%"
            )
        with col3:
            st.metric(
                label="New Role Types", 
                value=company_data["new_roles"],
                delta=company_data["roles_delta"]
            )
        
        # Job role breakdown
        st.subheader("Job Roles Breakdown")
        
        # Create a pie chart of job roles
        fig = px.pie(
            values=list(company_data["roles"].values()),
            names=list(company_data["roles"].keys()),
            title=f"Job Distribution at {selected_company}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Real-time job postings
        st.subheader("Real-Time Job Postings")
        
        if 'real_time_job_data' in st.session_state and st.session_state.real_time_job_data and selected_company in st.session_state.real_time_job_data:
            # Get real-time job data for this company
            real_time_jobs = st.session_state.real_time_job_data[selected_company]
            
            if real_time_jobs:
                # Show a toggle to filter by status
                show_only_new = st.checkbox("Show only new job postings", value=False)
                
                # Filter jobs if requested
                if show_only_new:
                    filtered_jobs = [job for job in real_time_jobs if job.get('status') == 'new']
                else:
                    filtered_jobs = real_time_jobs
                
                if filtered_jobs:
                    # Display jobs in expandable sections
                    for job in filtered_jobs:
                        # Create an expander with the job title and status badge
                        status = job.get('status', '').upper()
                        status_color = {
                            'NEW': '🟢',
                            'UPDATED': '🟡',
                            'ACTIVE': '🔵',
                            'CLOSING SOON': '🟠'
                        }.get(status, '⚪')
                        
                        with st.expander(f"{status_color} {job.get('title', 'No Title')} - {job.get('location', 'No Location')}"):
                            # Two columns for job details
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Posted:** {job.get('timestamp', 'Unknown')}")
                                if 'department' in job:
                                    st.write(f"**Department:** {job['department']}")
                                st.write("**Description:**")
                                st.write(job.get('description', 'No description available'))
                                
                                # Key requirements
                                if 'requirements' in job and job['requirements']:
                                    st.write("**Key Requirements:**")
                                    for req in job['requirements']:
                                        st.write(f"• {req}")
                            
                            with col2:
                                # Status information
                                st.info(f"**Status:** {status}")
                                
                                # Salary information if available
                                if 'salary_range' in job:
                                    st.write(f"**Salary Range:** {job['salary_range']}")
                                
                                # Application link
                                if 'url' in job:
                                    st.markdown(f"[Apply for this position]({job['url']})")
                else:
                    st.info("No new job postings found with the current filter.")
            else:
                st.info(f"No real-time job data available for {selected_company}. Click 'Refresh Data' in the sidebar to fetch the latest job listings.")
        else:
            # No real-time data, show sample job postings instead
            st.caption("Showing sample job listings. Click 'Refresh Data' in the sidebar to fetch real-time job updates.")
            
            # Recent job postings from demo data
            for job in company_data["recent_jobs"]:
                with st.expander(f"{job['title']} - {job['location']}"):
                    st.write(f"**Posted:** {job['date']}")
                    st.write(f"**Department:** {job['department']}")
                    st.write("**Description:**")
                    st.write(job['description'])
                    
                    # Key requirements
                    st.write("**Key Requirements:**")
                    for req in job['requirements']:
                        st.write(f"• {req}")
        
        # Strategic insights
        st.subheader("Strategic Insights")
        
        for insight in company_data["insights"]:
            if insight["type"] == "warning":
                st.warning(insight["text"])
            elif insight["type"] == "info":
                st.info(insight["text"])
            elif insight["type"] == "success":
                st.success(insight["text"])

elif st.session_state.current_view == "resume":
    st.title("Resume Analyzer")
    
    st.write("""
    Upload your resume to analyze how it matches with job requirements from companies you're tracking.
    This tool helps you:
    
    - Identify skills that match current market demand
    - Discover skill gaps for targeted roles
    - Get personalized recommendations to improve your resume
    """)
    
    # Resume upload section
    # Enhanced alternative input options for resume analysis
    upload_method = st.radio("Choose input method:", ["Upload File", "Paste Text", "LinkedIn URL", "Resume Template"])
    
    # Initialize session state for resume data if it doesn't exist
    if 'uploaded_resume' not in st.session_state:
        st.session_state.uploaded_resume = None
    
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
        
    # Add help text to explain options
    with st.expander("📋 How to use Resume Analysis"):
        st.markdown("""
        ### Resume Analysis Options:
        
        1. **Upload File**: Upload your resume document directly (Note: currently has limitations in this environment)
        2. **Paste Text**: Copy and paste the content of your resume directly into the text box
        3. **LinkedIn URL**: Enter your LinkedIn profile URL to automatically extract your professional information
        4. **Resume Template**: Use our template to quickly create a structured resume for analysis
        
        For best results in this environment, we recommend using the **Paste Text** or **Resume Template** options.
        """)
    
    # Check if we should display analysis results
    show_analysis = False
    resume_text = None
    
    # Handle file upload method
    if upload_method == "Upload File":
        uploaded_file = st.file_uploader("Upload your resume (PDF or TXT file)", type=["pdf", "txt"])
        
        if uploaded_file:
            try:
                # Read the content of the uploaded file
                if uploaded_file.type == "application/pdf":
                    st.warning("PDF parsing is limited in this demo. For best results, use a text file.")
                    # In a full application, we would use a PDF parser like PyPDF2 or pdfminer
                    resume_text = "Sample resume content for demonstration"
                else:  # Text file
                    resume_text = uploaded_file.getvalue().decode("utf-8")
                
                # Store the resume text in session state
                st.session_state.uploaded_resume = resume_text
                
                # Process the resume right away
                with st.spinner("Analyzing your resume..."):
                    resume_data = extract_resume_content(resume_text)
                    st.session_state.resume_data = resume_data
                    show_analysis = True
            except Exception as e:
                st.error(f"Error processing file: {str(e)}. Try using the 'Paste Text' option instead.")
    
    # Handle text input method
    elif upload_method == "Paste Text":
        resume_text = st.text_area("Paste your resume text here:", height=300)
        
        if st.button("Analyze Pasted Text"):
            if resume_text.strip():
                # Store the resume text in session state
                st.session_state.uploaded_resume = resume_text
                
                # Process the resume right away
                with st.spinner("Analyzing your resume..."):
                    resume_data = extract_resume_content(resume_text)
                    st.session_state.resume_data = resume_data
                    show_analysis = True
            else:
                st.warning("Please paste your resume text before analyzing.")
                
    # Handle LinkedIn URL method        
    elif upload_method == "LinkedIn URL":
        linkedin_url = st.text_input("Enter your LinkedIn profile URL:", placeholder="https://www.linkedin.com/in/yourprofile/")
        
        if st.button("Analyze LinkedIn Profile"):
            if linkedin_url.strip():
                st.session_state.uploaded_resume = linkedin_url
                
                with st.spinner("Extracting and analyzing LinkedIn profile data..."):
                    try:
                        # In a real application, we would use LinkedIn API or web scraping
                        # For this demo, we'll simulate extracting profile data
                        st.info("⚠️ LinkedIn profile extraction is simulated in this demo environment.")
                        
                        # Generate sample data based on URL
                        profile_name = linkedin_url.split("/")[-1].replace("-", " ").title()
                        if not profile_name or profile_name == "":
                            profile_name = "Demo Profile"
                            
                        # Create simulated resume content
                        resume_text = f"""
                        {profile_name}
                        
                        SKILLS
                        Python, Data Analysis, Machine Learning, JavaScript, React, SQL, AWS, Leadership
                        
                        EXPERIENCE
                        Senior Data Analyst at TechCorp (2019 - Present)
                        - Led data analysis initiatives for enterprise clients
                        - Developed predictive models using machine learning
                        
                        Data Scientist at Innovation Labs (2017 - 2019)
                        - Built data pipelines for processing large datasets
                        - Collaborated with cross-functional teams on AI projects
                        
                        EDUCATION
                        M.S. in Computer Science, Stanford University (2015-2017)
                        B.S. in Statistics, UC Berkeley (2011-2015)
                        
                        PROJECTS
                        Smart City Data Analysis
                        Customer Segmentation Algorithm
                        """
                        
                        # Store and process the resume
                        st.session_state.uploaded_resume = resume_text
                        resume_data = extract_resume_content(resume_text)
                        st.session_state.resume_data = resume_data
                        show_analysis = True
                        
                    except Exception as e:
                        st.error(f"Error processing LinkedIn profile: {str(e)}. Try using the 'Paste Text' option instead.")
            else:
                st.warning("Please enter a LinkedIn profile URL.")
                
    # Handle Resume Template method
    elif upload_method == "Resume Template":
        st.subheader("Resume Template")
        st.write("Fill out this template to quickly create and analyze a structured resume.")
        
        with st.form("resume_template_form"):
            # Personal information
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
            with col2:
                title = st.text_input("Professional Title", placeholder="e.g., Software Engineer")
                location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
            
            # Skills section
            st.subheader("Skills")
            skills_input = st.text_area("Enter skills (comma-separated)", 
                                       placeholder="Python, JavaScript, Machine Learning, Leadership, Project Management")
            
            # Experience
            st.subheader("Experience")
            with st.expander("Add Job #1", expanded=True):
                job1_title = st.text_input("Job Title", key="job1_title")
                job1_company = st.text_input("Company", key="job1_company")
                job1_dates = st.text_input("Dates", placeholder="e.g., 2020-Present", key="job1_dates")
                job1_description = st.text_area("Description", placeholder="Key responsibilities and achievements", key="job1_desc")
            
            with st.expander("Add Job #2"):
                job2_title = st.text_input("Job Title", key="job2_title")
                job2_company = st.text_input("Company", key="job2_company")
                job2_dates = st.text_input("Dates", placeholder="e.g., 2018-2020", key="job2_dates")
                job2_description = st.text_area("Description", placeholder="Key responsibilities and achievements", key="job2_desc")
            
            # Education
            st.subheader("Education")
            with st.expander("Add Education", expanded=True):
                edu_degree = st.text_input("Degree", placeholder="e.g., Bachelor of Science in Computer Science")
                edu_school = st.text_input("School", placeholder="e.g., University of California, Berkeley")
                edu_dates = st.text_input("Dates", placeholder="e.g., 2014-2018")
            
            # Projects (optional)
            st.subheader("Projects (Optional)")
            projects = st.text_area("Enter projects (one per line)", placeholder="Project name: Brief description")
            
            # Submit button
            submitted = st.form_submit_button("Generate and Analyze Resume")
        
        if submitted:
            if name and title and skills_input:
                # Create structured resume from template
                skills_list = [skill.strip() for skill in skills_input.split(",")]
                
                resume_text = f"""
                {name}
                {title}
                {location}
                {email}
                
                SKILLS
                {skills_input}
                
                EXPERIENCE
                """
                
                # Add Job #1
                if job1_title and job1_company:
                    resume_text += f"\n{job1_title} at {job1_company} ({job1_dates})\n"
                    if job1_description:
                        # Use safer string manipulation to add bullet points
                        bullet_text = "- " + job1_description.replace("\n", "\n- ")
                        resume_text += bullet_text + "\n"
                
                # Add Job #2
                if job2_title and job2_company:
                    resume_text += f"\n{job2_title} at {job2_company} ({job2_dates})\n"
                    if job2_description:
                        # Use safer string manipulation to add bullet points
                        bullet_text = "- " + job2_description.replace("\n", "\n- ")
                        resume_text += bullet_text + "\n"
                
                # Add Education
                if edu_degree and edu_school:
                    resume_text += f"\nEDUCATION\n{edu_degree}, {edu_school} ({edu_dates})\n"
                
                # Add Projects
                if projects:
                    resume_text += f"\nPROJECTS\n{projects}\n"
                
                # Store and process the resume
                st.session_state.uploaded_resume = resume_text
                
                with st.spinner("Analyzing your resume..."):
                    resume_data = extract_resume_content(resume_text)
                    st.session_state.resume_data = resume_data
                    show_analysis = True
            else:
                st.warning("Please fill in the required fields (Name, Title, and Skills).")
    
    # Display analysis results if available
    if st.session_state.resume_data:
        # Get the resume data from session state
        resume_data = st.session_state.resume_data
        
        # Update achievements for analyzing resumes
        if 'achievements' in st.session_state and show_analysis:
            unlocked, level = update_achievement_progress('resumes_analyzed')
            if unlocked:
                st.balloons()
                st.success(f"🎉 Achievement Unlocked: Resume Expert - {level['name']} {level['badge']}")
            
            # Increment total actions
            if 'gamification_stats' in st.session_state:
                st.session_state.gamification_stats['total_actions'] += 1
        
        # Display extracted skills
        st.subheader("Skills Extracted from Your Resume")
        skill_cols = st.columns(3)
        skills_per_col = len(resume_data["skills"]) // 3 + 1
        
        for i, skill in enumerate(resume_data["skills"]):
            col_idx = i // skills_per_col
            with skill_cols[min(col_idx, 2)]:
                st.write(f"✓ {skill}")
        
        # Match against company job listings
        if st.session_state.watched_companies:
            st.subheader("Resume Match Analysis")
            
            # Get demo data for now (in a real app, this would use actual job listings)
            demo_data = get_demo_data()
            
            # Create tabs for each watched company
            company_tabs = st.tabs(st.session_state.watched_companies)
            
            for i, company in enumerate(st.session_state.watched_companies):
                with company_tabs[i]:
                    # Get company job data
                    company_data = demo_data["company_specific"].get(company, demo_data["company_specific"]["Google"])
                    
                    # Analyze resume against company jobs
                    job_matches = analyze_resume_vs_company_jobs(resume_data, company_data["recent_jobs"])
                    
                    # Show overall match score
                    opportunity_score = get_career_opportunity_score(job_matches)
                    
                    st.metric(
                        label=f"Overall Match with {company}", 
                        value=f"{opportunity_score:.1f}%"
                    )
                    
                    # Display top matches with enhanced visualization
                    st.subheader("Top Job Matches")
                    for job_match in job_matches[:3]:  # Show top 3 matches
                        # Set color based on match quality
                        match_quality = job_match.get("match_quality", "")
                        if match_quality == "Excellent":
                            quality_color = "green"
                        elif match_quality == "Good":
                            quality_color = "blue"
                        elif match_quality == "Fair": 
                            quality_color = "orange"
                        else:
                            quality_color = "red"
                            
                        # Create an expander with colored heading
                        with st.expander(f"{job_match['job_title']} ({job_match['match_percentage']:.1f}% match)"):
                            # Top metrics for the job match
                            cols = st.columns(3)
                            with cols[0]:
                                st.metric("Match Quality", job_match.get("match_quality", "N/A"))
                            
                            with cols[1]:
                                skill_coverage = job_match.get("skill_coverage", {})
                                ratio = skill_coverage.get("skill_match_ratio", "0/0") if skill_coverage else "0/0"
                                st.metric("Skills Match", ratio)
                            
                            with cols[2]:
                                posted_date = job_match.get("posted_date", "")
                                posted_text = f"Posted {posted_date}" if posted_date else "Recent"
                                st.metric("Status", posted_text)
                                
                            # Job details
                            st.markdown("---")
                            st.write(f"**Department:** {job_match['job_department']}")
                            st.write(f"**Location:** {job_match['job_location']}")
                            
                            if job_match.get("salary_range"):
                                st.write(f"**Salary Range:** {job_match['salary_range']}")
                                
                            # Skills section with columns
                            st.markdown("---")
                            st.subheader("Skills Analysis")
                            
                            skill_cols = st.columns(3)
                            
                            with skill_cols[0]:
                                st.write("**✓ Matching Skills:**")
                                for skill in job_match["matching_skills"]:
                                    st.markdown(f"<span style='color:green'>✓ {skill}</span>", unsafe_allow_html=True)
                            
                            with skill_cols[1]:
                                if job_match.get("partial_matching_skills"):
                                    st.write("**~ Partial Matches:**")
                                    for skill in job_match["partial_matching_skills"]:
                                        st.markdown(f"<span style='color:orange'>~ {skill}</span>", unsafe_allow_html=True)
                            
                            with skill_cols[2]:
                                if job_match["missing_skills"]:
                                    st.write("**○ Skills to Develop:**")
                                    for skill in job_match["missing_skills"][:5]:  # Limit to 5 to avoid overwhelming
                                        st.markdown(f"<span style='color:red'>○ {skill}</span>", unsafe_allow_html=True)
                                        
                            # Add visual skill coverage meter if available
                            if job_match.get("skill_coverage"):
                                sc = job_match["skill_coverage"]
                                st.markdown("---")
                                st.subheader("Skill Coverage Metrics")
                                
                                # Create a progress bar for skill coverage
                                exact = sc.get("exact_match_count", 0)
                                partial = sc.get("partial_match_count", 0)
                                total = sc.get("total_required", 1)  # Avoid division by zero
                                
                                coverage_pct = min(100, int((exact + (partial * 0.5)) / total * 100)) if total > 0 else 0
                                st.progress(coverage_pct / 100)
                                
                                # Display skill metrics
                                metric_cols = st.columns(4)
                                with metric_cols[0]:
                                    st.metric("Exact Matches", exact)
                                with metric_cols[1]:
                                    st.metric("Partial Matches", partial)
                                with metric_cols[2]:
                                    st.metric("Missing Skills", sc.get("missing_count", 0))
                                with metric_cols[3]:
                                    st.metric("Total Required", total)
                    
                    # Generate and display insights
                    insights = generate_resume_insights(resume_data, job_matches)
                    if insights:
                        st.subheader("Career Insights")
                        for insight in insights:
                            st.info(insight)
            
            # Overall recommendations across companies with enhanced visualization
            st.subheader("Strategic Career Development Plan")
            
            # Collect all missing skills across top matches
            all_missing_skills = {}
            for company in st.session_state.watched_companies:
                company_data = demo_data["company_specific"].get(company, demo_data["company_specific"]["Google"])
                job_matches = analyze_resume_vs_company_jobs(resume_data, company_data["recent_jobs"])
                
                for job_match in job_matches[:2]:  # Consider top 2 matches from each company
                    for skill in job_match["missing_skills"]:
                        if skill in all_missing_skills:
                            all_missing_skills[skill] += 1
                        else:
                            all_missing_skills[skill] = 1
            
            # Sort by frequency and display top skills to develop
            if all_missing_skills:
                sorted_skills = sorted(all_missing_skills.items(), key=lambda x: x[1], reverse=True)
                
                # Display skills to develop in a visually appealing way
                st.markdown("""
                <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:15px;">
                    <h3 style="color:#0066cc;">🎯 Priority Skills to Develop</h3>
                    <p>Based on your resume analysis across all companies, these skills would most significantly improve your marketability:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a skill priority table
                skill_data = []
                for skill, count in sorted_skills[:5]:  # Top 5
                    priority = "High" if count > 2 else ("Medium" if count > 1 else "Normal")
                    priority_color = "#ff4b4b" if count > 2 else ("#ff9d45" if count > 1 else "#2986cc")
                    skill_data.append({
                        "Skill": skill,
                        "Demand": f"{count} roles",
                        "Priority": priority,
                        "color": priority_color
                    })
                
                # Display as custom HTML table
                st.markdown("<table width='100%' style='text-align:left; border-collapse:separate; border-spacing:0 8px;'>", unsafe_allow_html=True)
                st.markdown("<tr><th>Skill</th><th>Demand</th><th>Priority</th><th>Learning Resources</th></tr>", unsafe_allow_html=True)
                
                for item in skill_data:
                    # Generate simulated learning resource suggestion based on skill
                    learning_resource = "Online Course" if "python" in item["Skill"].lower() or "javascript" in item["Skill"].lower() else (
                        "Certification" if "aws" in item["Skill"].lower() or "cloud" in item["Skill"].lower() else 
                        "Workshop/Practice"
                    )
                    
                    st.markdown(f"""
                    <tr style="background-color:#f8f9fa;">
                        <td style="padding:10px;"><b>{item["Skill"]}</b></td>
                        <td style="padding:10px;">{item["Demand"]}</td>
                        <td style="padding:10px;"><span style="color:{item["color"]}; font-weight:bold;">{item["Priority"]}</span></td>
                        <td style="padding:10px;">{learning_resource}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</table>", unsafe_allow_html=True)
                
                # Create a development timeline
                st.markdown("""
                <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin:20px 0;">
                    <h3 style="color:#0066cc;">📅 Development Timeline</h3>
                    <p>A suggested timeline for skill acquisition based on priority:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create columns for timeline visualization
                timeline_cols = st.columns(3)
                
                with timeline_cols[0]:
                    st.markdown("""
                    <div style="border-left:3px solid #ff4b4b; padding-left:10px; margin-bottom:15px;">
                        <h4>Short-term (1-3 months)</h4>
                        <ul style="padding-left:15px;">
                    """, unsafe_allow_html=True)
                    
                    # Add high priority skills
                    for item in skill_data:
                        if item["Priority"] == "High":
                            st.markdown(f"<li>{item['Skill']}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                
                with timeline_cols[1]:
                    st.markdown("""
                    <div style="border-left:3px solid #ff9d45; padding-left:10px; margin-bottom:15px;">
                        <h4>Mid-term (3-6 months)</h4>
                        <ul style="padding-left:15px;">
                    """, unsafe_allow_html=True)
                    
                    # Add medium priority skills
                    for item in skill_data:
                        if item["Priority"] == "Medium":
                            st.markdown(f"<li>{item['Skill']}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                
                with timeline_cols[2]:
                    st.markdown("""
                    <div style="border-left:3px solid #2986cc; padding-left:10px; margin-bottom:15px;">
                        <h4>Long-term (6+ months)</h4>
                        <ul style="padding-left:15px;">
                    """, unsafe_allow_html=True)
                    
                    # Add normal priority skills
                    for item in skill_data:
                        if item["Priority"] == "Normal":
                            st.markdown(f"<li>{item['Skill']}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                
                # General career development recommendations
                st.markdown("""
                <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin:20px 0;">
                    <h3 style="color:#0066cc;">📋 General Career Development Recommendations</h3>
                </div>
                """, unsafe_allow_html=True)
                
                rec_cols = st.columns(2)
                
                with rec_cols[0]:
                    st.markdown("""
                    <div style="background-color:#ffffff; padding:15px; border-radius:10px; height:100%;">
                        <h4>Resume Enhancement</h4>
                        <ul>
                            <li>Tailor your resume for specific job applications</li>
                            <li>Quantify achievements with metrics where possible</li>
                            <li>Highlight projects that demonstrate your skills</li>
                            <li>Use action verbs and industry keywords</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with rec_cols[1]:
                    st.markdown("""
                    <div style="background-color:#ffffff; padding:15px; border-radius:10px; height:100%;">
                        <h4>Professional Development</h4>
                        <ul>
                            <li>Focus on developing the most in-demand skills</li>
                            <li>Build a portfolio showcasing your abilities</li>
                            <li>Network with professionals in target companies</li>
                            <li>Contribute to open-source or community projects</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Add companies to your watchlist to see how your resume matches against their job requirements.")
    else:
        st.info("Upload your resume to see how it matches with job requirements from companies you're tracking.")

elif st.session_state.current_view == "talent":
    st.title("Talent Demand & Availability")
    
    st.write("""
    Analyze the talent market for specific job roles and skills. This tool helps you:
    
    - Find out how many candidates are available for a specific role
    - Discover which cities have the most talent for your needs
    - Identify skill prevalence and opportunities
    - Understand competing companies hiring for similar roles
    - Analyze industry hiring trends from company data
    """)
    
    # Industry analysis option
    tabs = st.tabs(["Job Role Analysis", "Industry Hiring Trends"])
    
    with tabs[0]:
        # Job Role Analysis functionality
        st.subheader("Job Role Talent Analysis")
        st.write("Analyze talent availability for specific job roles and skills.")
        
        # Input form for talent analysis
        with st.form("talent_analysis_form_tab"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_role = st.text_input("Job Role", placeholder="e.g., Software Engineer, Marketing Manager")
                
            with col2:
                location = st.text_input("Location", placeholder="e.g., San Francisco, Remote")
            
            # Skill input
            st.subheader("Required Skills")
            skills_input = st.text_area("Enter skills (one per line)", placeholder="Python\nSQL\nReact\nData Analysis")
            
            # Parse skills
            skills = [skill.strip() for skill in skills_input.split("\n") if skill.strip()]
            
            # Submit button
            submitted = st.form_submit_button("Analyze Talent Market")
            
        # Process the form when submitted
        if submitted and job_role and location:
            # Store unique locations searched
            if 'talent_locations_searched' not in st.session_state:
                st.session_state.talent_locations_searched = set()
            
            # Show results
            with st.spinner(f"Analyzing talent market for {job_role} in {location}..."):
                # Add to set of locations searched
                st.session_state.talent_locations_searched.add(location)
                
                # Update achievements for talent searches
                if 'achievements' in st.session_state:
                    # Only count unique locations
                    if len(st.session_state.talent_locations_searched) > st.session_state.achievements['talent_searches']['progress']:
                        unlocked, level = update_achievement_progress('talent_searches')
                        
                        if unlocked:
                            st.balloons()
                            st.success(f"🎉 Achievement Unlocked: Talent Scout - {level['name']} {level['badge']}")
                        
                        # Increment total actions
                        if 'gamification_stats' in st.session_state:
                            st.session_state.gamification_stats['total_actions'] += 1
                
                # Get talent availability data
                if not skills:
                    # Default skills if none provided
                    skills = ["Programming", "Communication", "Problem Solving"]
                    
                talent_data = analyze_talent_availability(job_role, location, skills)
                
                # Display key metrics
                st.subheader("Talent Availability")
                
                # Create three metrics at the top
                metric_cols = st.columns(3)
                
                with metric_cols[0]:
                    st.metric(
                        label="Available Candidates", 
                        value=f"{talent_data['total_candidates']:,}"
                    )
                
                with metric_cols[1]:
                    st.metric(
                        label="Annual Growth Rate", 
                        value=f"{talent_data['talent_growth_rate']['current_growth_rate']}%"
                    )
                
                with metric_cols[2]:
                    # Calculate remote percentage
                    remote_pct = talent_data["remote_availability"]["remote_percentage"]
                    hybrid_pct = talent_data["remote_availability"]["hybrid_percentage"]
                    st.metric(
                        label="Remote Work Preference", 
                        value=f"{remote_pct}% Remote, {hybrid_pct}% Hybrid"
                    )
                
                # Create tabs for different analyses
                talent_tabs = st.tabs(["Top Cities", "Skill Analysis", "Competing Companies", "Demographics"])
                
                # Tab 1: Geographic Analysis (Top Cities)
                with talent_tabs[0]:
                    st.subheader(f"Top Cities for {job_role} Talent")
                    
                    # Create a table of top cities
                    city_data = pd.DataFrame(talent_data["top_cities"])
                    
                    # Format the numbers with commas
                    city_data["talent_count"] = city_data["talent_count"].apply(lambda x: f"{x:,}")
                    
                    # Rename columns for display
                    city_data.columns = ["City", "Available Talent", "Annual Growth (%)"]
                    
                    # Display as a table
                    st.table(city_data)
                    
                    # Add a note about talent mobility
                    st.info(f"💡 **Insight:** {talent_data['top_cities'][0]['city']} has the highest concentration of {job_role} talent with a growth rate of {talent_data['top_cities'][0]['growth_rate']}% annually.")
                
                # Tab 2: Skill Analysis
                with talent_tabs[1]:
                    st.subheader("Skill Prevalence Analysis")
                    
                    # Create a DataFrame for the skills
                    skill_data = pd.DataFrame(talent_data["skill_prevalence"])
                    
                    # Sort by prevalence (highest first)
                    skill_data = skill_data.sort_values(by="prevalence", ascending=False)
                    
                    # Create a horizontal bar chart
                    fig = px.bar(
                        skill_data,
                        y="skill",
                        x="prevalence",
                        title=f"Skill Prevalence for {job_role} (% of candidates)",
                        labels={"prevalence": "% of Candidates", "skill": "Skill"},
                        orientation='h',
                        color="prevalence",
                        color_continuous_scale="Viridis",
                        range_color=[0, 100]
                    )
                    
                    # Update layout
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Identify skill gaps (skills with low prevalence = opportunity)
                    rare_skills = skill_data[skill_data["prevalence"] < 40].sort_values(by="prevalence")
                    if not rare_skills.empty:
                        rare_skill_names = ", ".join(rare_skills["skill"].tolist())
                        st.success(f"💡 **Opportunity:** The skills '{rare_skill_names}' are in demand but less common among candidates, potentially making them valuable differentiators for your company.")
                
                # Tab 3: Competing Companies
                with talent_tabs[2]:
                    st.subheader("Companies Competing for Same Talent")
                    
                    # Create a DataFrame for competing companies
                    competing_companies = pd.DataFrame(talent_data["competing_companies"])
                    
                    # Create bar chart for hiring volume
                    fig = px.bar(
                        competing_companies,
                        x="name",
                        y="role_count",
                        title=f"Companies Hiring {job_role} Talent",
                        labels={"name": "Company", "role_count": "Monthly Job Postings"},
                        color="role_count",
                        color_continuous_scale="Viridis",
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display competitor details
                    st.subheader("Competitor Hiring Details")
                    
                    # Calculate market share percentages based on role count
                    total_roles = competing_companies["role_count"].sum()
                    competing_companies["market_share"] = (competing_companies["role_count"] / total_roles * 100).round(1)
                    competing_companies["market_share"] = competing_companies["market_share"].apply(lambda x: f"{x}%")
                    
                    # Rename columns for display
                    display_companies = competing_companies.copy()
                    display_companies.columns = ["Company", "Hiring Velocity", "Monthly Job Postings", "Market Share (%)"]
                    
                    # Display as a table
                    st.table(display_companies)
                    
                    # Add insights
                    top_competitor = talent_data["competing_companies"][0]["name"]
                    top_volume = talent_data["competing_companies"][0]["role_count"]
                    st.info(f"💡 **Insight:** {top_competitor} is the most active competitor hiring for {job_role} positions with approximately {top_volume} new job postings per month.")
                
                # Tab 4: Demographics
                with talent_tabs[3]:
                    st.subheader("Talent Demographics")
                    
                    # Create two columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Education breakdown pie chart
                        education_df = pd.DataFrame(talent_data["education_breakdown"])
                        
                        fig = px.pie(
                            education_df,
                            values="percentage",
                            names="level",  # Changed from "education_level" to "level" to match the column name
                            title=f"Education Level Distribution for {job_role}",
                            hole=0.4,
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Experience distribution pie chart
                        experience_df = pd.DataFrame(talent_data["experience_levels"])
                        
                        fig = px.pie(
                            experience_df,
                            values="percentage",
                            names="level",  # Changed from "experience_level" to "level" to match the column name
                            title=f"Experience Level Distribution for {job_role}",
                            hole=0.4,
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Remote work availability
                    st.subheader("Remote Work Preferences")
                    
                    # Create data for the remote work pie chart
                    remote_data = {
                        "Work Type": ["Remote", "Hybrid", "On-site"],
                        "Percentage": [
                            talent_data["remote_availability"]["remote_percentage"],
                            talent_data["remote_availability"]["hybrid_percentage"],
                            talent_data["remote_availability"]["onsite_percentage"]
                        ]
                    }
                    
                    remote_df = pd.DataFrame(remote_data)
                    
                    fig = px.pie(
                        remote_df,
                        values="Percentage",
                        names="Work Type",
                        title=f"Work Location Preferences for {job_role} Talent",
                        color="Work Type",
                        color_discrete_map={
                            "Remote": "#1f77b4",
                            "Hybrid": "#ff7f0e",
                            "On-site": "#2ca02c"
                        }
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add insights
                    # For the trend text, we'll use a descriptive phrase based on the 'trend' value
                    trend_text = "an increasing" if talent_data['remote_availability']['trend'] == "increasing" else "a stable"
                    st.info(f"💡 **Insight:** {talent_data['remote_availability']['remote_percentage']}% of {job_role} professionals prefer fully remote roles, with {trend_text} trend in remote work preferences.")
        
    with tabs[1]:
        # Industry Hiring Trends from loaded company data
        st.subheader("Industry Hiring Trends Analysis")
        st.write("Analyze hiring trends based on company data from the companies database.")
        
        # Load company data
        with st.spinner("Loading company data..."):
            companies_data = load_companies_data()
            
            if not companies_data:
                st.error("No company data found. Please make sure the companies data file is available.")
            else:
                st.success(f"Loaded data for {len(companies_data)} companies across multiple industries.")
                
                # Get unique industries
                industries = sorted(list(set([company.get("industry") for company in companies_data if company.get("industry")])))
                
                # Industry filter
                # Store the previous industry
                if 'previous_industry' not in st.session_state:
                    st.session_state.previous_industry = None
                
                selected_industry = st.selectbox(
                    "Select an industry to analyze:",
                    options=["All Industries"] + industries
                )
                
                # Check if industry changed and update achievement
                if selected_industry != "All Industries" and selected_industry != st.session_state.previous_industry:
                    st.session_state.previous_industry = selected_industry
                    
                    # Update achievements for industry analysis
                    if 'achievements' in st.session_state:
                        unlocked, level = update_achievement_progress('industries_analyzed')
                        if unlocked:
                            st.balloons()
                            st.success(f"🎉 Achievement Unlocked: Industry Analyst - {level['name']} {level['badge']}")
                        
                        # Increment total actions
                        if 'gamification_stats' in st.session_state:
                            st.session_state.gamification_stats['total_actions'] += 1
                
                # Priority filter
                priorities = ["All Priorities", "Critical", "High", "Medium"]
                selected_priority = st.selectbox(
                    "Filter by priority:",
                    options=priorities
                )
                
                # Apply filters
                if selected_industry != "All Industries" and selected_priority != "All Priorities":
                    filtered_companies = [c for c in companies_data if c.get("industry") == selected_industry and c.get("priority") == selected_priority]
                elif selected_industry != "All Industries":
                    filtered_companies = [c for c in companies_data if c.get("industry") == selected_industry]
                elif selected_priority != "All Priorities":
                    filtered_companies = [c for c in companies_data if c.get("priority") == selected_priority]
                else:
                    filtered_companies = companies_data
                
                # Display filtering results
                st.write(f"Showing data for {len(filtered_companies)} companies")
                
                # Get industry trends
                with st.spinner("Analyzing industry hiring trends..."):
                    industry_trends = get_industry_hiring_trends()
                    
                    # Generate processed data for deeper analysis
                    if 'real_time_job_data' in st.session_state:
                        processed_data = process_job_data(st.session_state.real_time_job_data)
                    else:
                        # Create simulated processed data for demo use
                        processed_data = {
                            "companies": [company.get("name") for company in companies_data if company.get("name")],
                            "hiring_velocity": industry_trends.get(selected_industry, {}).get("hiring_velocity", []),
                            "roles_by_company": {company.get("name"): {"Software Engineer": 5, "Data Scientist": 3} for company in companies_data if company.get("name")},
                            "skills_by_company": {company.get("name"): {"Python": 4, "JavaScript": 3, "Cloud": 2} for company in companies_data if company.get("name")},
                            "locations_by_company": {company.get("name"): {"San Francisco": 3, "New York": 2, "Remote": 5} for company in companies_data if company.get("name")}
                        }
                    
                    # Get industry-specific insights from analyzer
                    industry_insights = analyze_industry_trends(processed_data, companies_data)
                    
                    # Generate industry-specific recommendations
                    industry_recommendations = generate_industry_recommendations(industry_insights)
                    
                    if selected_industry != "All Industries" and selected_industry in industry_trends:
                        # Show just the selected industry
                        industry_data = industry_trends[selected_industry]
                        
                        # Metrics
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric("Companies in Industry", industry_data["total_companies"])
                        with cols[1]:
                            st.metric("Avg. Hiring Velocity", f"{industry_data['hiring_velocity']} jobs/week")
                        with cols[2]:
                            st.metric("Growth Rate", f"{industry_data['growth_rate']}%")
                        
                        # Add tabs for different industry insights
                        industry_tabs = st.tabs(["Roles & Skills", "Industry Insights", "Strategic Recommendations"])
                        
                        with industry_tabs[0]:
                            # Top roles in industry
                            st.subheader(f"Top Roles in {selected_industry}")
                            
                            # Convert to DataFrame for visualization
                            roles_df = pd.DataFrame(industry_data["top_roles"])
                            
                        with industry_tabs[1]:
                            st.subheader(f"Industry-Specific Insights for {selected_industry}")
                            
                            # Display industry-specific insights if available
                            if selected_industry in industry_insights and industry_insights[selected_industry]:
                                for insight in industry_insights[selected_industry]:
                                    with st.container(border=True):
                                        insight_type = insight["type"]
                                        
                                        # Create an icon based on insight type
                                        if insight_type == "industry_leader":
                                            icon = "🏆"
                                            title = "Industry Leader"
                                        elif insight_type == "industry_skills":
                                            icon = "🔧"
                                            title = "Critical Skills"
                                        elif insight_type == "industry_specific_skill":
                                            icon = "⭐"
                                            title = "Specialized Skill"
                                        elif insight_type == "industry_hubs":
                                            icon = "📍"
                                            title = "Industry Hubs"
                                        else:
                                            icon = "💡"
                                            title = "Industry Insight"
                                            
                                        st.markdown(f"### {icon} {title}")
                                        st.write(insight["insight"])
                                        
                                        # Add additional context based on insight type
                                        if insight_type == "industry_leader":
                                            st.progress(min(1.0, insight["velocity"] / (insight["industry_avg"] * 2)), "Hiring Velocity vs Industry Average")
                                        elif insight_type == "industry_skills" and "top_skills" in insight:
                                            skills = insight["top_skills"]
                                            for i, skill in enumerate(skills[:5], 1):
                                                st.write(f"{i}. {skill}")
                                        elif insight_type == "industry_hubs" and "top_locations" in insight:
                                            locations = insight["top_locations"]
                                            st.write("Major talent hubs:")
                                            for location in locations[:3]:
                                                st.write(f"• {location}")
                            else:
                                st.info(f"No specific insights available for the {selected_industry} industry yet. Add more companies from this industry to generate insights.")
                            
                        with industry_tabs[2]:
                            st.subheader(f"Strategic Recommendations for {selected_industry}")
                            
                            # Display industry-specific recommendations if available
                            if selected_industry in industry_recommendations and industry_recommendations[selected_industry]:
                                for recommendation in industry_recommendations[selected_industry]:
                                    with st.container(border=True):
                                        priority = recommendation["priority"]
                                        
                                        # Create an icon and color based on priority
                                        if priority == "high":
                                            priority_color = "red"
                                            priority_label = "High Priority"
                                        elif priority == "medium":
                                            priority_color = "orange"
                                            priority_label = "Medium Priority"
                                        else:
                                            priority_color = "blue"
                                            priority_label = "Low Priority"
                                            
                                        st.markdown(f"<span style='color: {priority_color};'><b>{priority_label}</b></span>", unsafe_allow_html=True)
                                        st.write(recommendation["recommendation"])
                                        
                                        # Add additional context based on recommendation type
                                        if recommendation["type"] == "industry_skill_investment" and "skills" in recommendation:
                                            st.write("**Skills to invest in:**")
                                            for skill in recommendation["skills"]:
                                                st.write(f"• {skill}")
                                        elif recommendation["type"] == "industry_competitor_analysis" and "company" in recommendation:
                                            st.write(f"**Key competitor to monitor:** {recommendation['company']}")
                            else:
                                st.info(f"No specific recommendations available for the {selected_industry} industry yet.")
                        
                        # Create a horizontal bar chart
                        fig = px.bar(
                            roles_df,
                            y="role",
                            x="count",
                            color="growth",
                            orientation='h',
                            title=f"Most In-Demand Roles in {selected_industry}",
                            labels={"role": "Role", "count": "Open Positions", "growth": "YoY Growth (%)"},
                            color_continuous_scale="Viridis",
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Skill demand in industry
                        st.subheader(f"Skill Demand in {selected_industry}")
                        
                        # Convert to DataFrame for visualization
                        skills_df = pd.DataFrame(industry_data["skill_demand"])
                        
                        # Create a horizontal bar chart
                        fig = px.bar(
                            skills_df,
                            y="skill",
                            x="demand_score",
                            color="growth",
                            orientation='h',
                            title=f"Most In-Demand Skills in {selected_industry}",
                            labels={"skill": "Skill", "demand_score": "Demand Score", "growth": "YoY Growth (%)"},
                            color_continuous_scale="Viridis",
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Top hiring companies
                        st.subheader("Top Hiring Companies")
                        st.write(f"Companies with the highest hiring velocity in {selected_industry}:")
                        
                        for i, company in enumerate(industry_data["top_hiring_companies"]):
                            st.write(f"{i+1}. {company}")
                            
                    else:
                        # Show comparison across industries
                        st.subheader("Industry Comparison")
                        
                        # Prepare data for charts
                        industry_names = []
                        hiring_velocities = []
                        growth_rates = []
                        company_counts = []
                        
                        for industry, data in industry_trends.items():
                            industry_names.append(industry)
                            hiring_velocities.append(data["hiring_velocity"])
                            growth_rates.append(data["growth_rate"])
                            company_counts.append(data["total_companies"])
                        
                        # Create a DataFrame for industry comparison
                        industry_df = pd.DataFrame({
                            "Industry": industry_names,
                            "Hiring Velocity": hiring_velocities,
                            "Growth Rate": growth_rates,
                            "Companies": company_counts
                        })
                        
                        # Create charts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Hiring velocity chart
                            fig = px.bar(
                                industry_df,
                                y="Industry",
                                x="Hiring Velocity",
                                orientation='h',
                                title="Hiring Velocity by Industry",
                                color="Hiring Velocity",
                                color_continuous_scale="Viridis",
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Growth rate chart
                            fig = px.bar(
                                industry_df,
                                y="Industry",
                                x="Growth Rate",
                                orientation='h',
                                title="Hiring Growth Rate by Industry",
                                color="Growth Rate",
                                color_continuous_scale="Viridis",
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Company breakdown
                        st.subheader("Company Breakdown by Industry")
                        fig = px.pie(
                            industry_df,
                            values="Companies",
                            names="Industry",
                            title="Distribution of Companies by Industry"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                # Display raw company data
                with st.expander("View Raw Company Data"):
                    st.dataframe(filtered_companies)
    # End of talent analysis functionality

# Gamification view
elif st.session_state.current_view == "gamification":
    st.title("🎮 Recruitment Strategy Gamification")
    
    # Update the recruitment score
    st.session_state.gamification_stats['recruitment_score'] = calculate_recruitment_score()
    
    # Dashboard header with current score
    score_col, streak_col = st.columns(2)
    with score_col:
        score = st.session_state.gamification_stats['recruitment_score']
        st.metric("Recruitment Strategy Score", value=f"{score}/100")
        
        # Score interpretation
        if score < 20:
            st.caption("Beginner: You're just getting started!")
        elif score < 40:
            st.caption("Novice: Building your recruitment strategy")
        elif score < 60:
            st.caption("Advanced: Solid strategy in development")
        elif score < 80:
            st.caption("Expert: Sophisticated recruitment approach")
        else:
            st.caption("Master Strategist: Exceptional recruitment intelligence")
    
    with streak_col:
        streak = st.session_state.gamification_stats['streak_days']
        st.metric("Activity Streak", value=f"{streak} days")
        
        # Show total actions
        total_actions = st.session_state.gamification_stats['total_actions']
        st.caption(f"Total actions: {total_actions}")
    
    # Main achievements display
    st.subheader("Achievements & Badges")
    
    # Create achievement cards in a grid
    col1, col2 = st.columns(2)
    
    # List to alternate columns
    columns = [col1, col2]
    
    for i, (key, achievement) in enumerate(st.session_state.achievements.items()):
        # Alternate between columns
        col = columns[i % 2]
        
        with col:
            # Create achievement card
            with st.container(border=True):
                # Header with badge for current level
                current_level = achievement['current_level']
                if current_level < len(achievement['levels']):
                    badge = achievement['levels'][current_level]['badge']
                    level_name = achievement['levels'][current_level]['name']
                else:
                    badge = "🏆"
                    level_name = "Master"
                
                st.subheader(f"{badge} {achievement['name']}")
                st.caption(achievement['description'])
                
                # Progress bar
                progress_pct = min(100, (achievement['progress'] / achievement['max']) * 100)
                st.progress(int(progress_pct))
                
                # Progress text
                st.write(f"{achievement['progress']}/{achievement['max']} • Level: {level_name}")
                
                # Show unlocked badges
                badges_html = ""
                for level in achievement['levels']:
                    if level['unlocked']:
                        badges_html += f"<span style='font-size:24px;margin-right:10px;'>{level['badge']}</span>"
                    else:
                        badges_html += f"<span style='font-size:24px;margin-right:10px;opacity:0.3;'>{level['badge']}</span>"
                
                st.markdown(badges_html, unsafe_allow_html=True)
    
    # Actions to earn achievements
    st.subheader("Ways to Unlock Achievements")
    
    with st.expander("How to Level Up Your Recruitment Strategy"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Company Tracker**
            - Add companies to your watchlist
            - Track competitors across industries
            - Monitor hiring across diverse company sizes
            
            **Industry Analyst**
            - Analyze different industry segments
            - Compare hiring patterns between industries
            - Track industry-specific skill trends
            """)
        
        with col2:
            st.markdown("""
            **Talent Scout**
            - Search for talent in various locations
            - Analyze candidate availability for different roles
            - Identify cities with specific talent concentrations
            
            **Resume Expert**
            - Analyze resumes against job requirements
            - Match candidate skills to job openings
            - Identify skill gaps and opportunities
            """)
    
    # Add some gamified actions
    st.subheader("Recruitment Challenges")
    
    challenge1, challenge2 = st.columns(2)
    
    with challenge1:
        with st.container(border=True):
            st.markdown("### 🎯 Quick Win Challenge")
            st.markdown("**Track 5 companies in the same industry**")
            st.caption("Unlock: Company Tracker - Intermediate Badge")
            if st.button("Begin Challenge", key="challenge1"):
                st.session_state.current_view = "company"
                st.rerun()
    
    with challenge2:
        with st.container(border=True):
            st.markdown("### 🏆 Advanced Challenge")
            st.markdown("**Analyze talent availability in 3 different cities**")
            st.caption("Unlock: Talent Scout - Intermediate Badge")
            if st.button("Begin Challenge", key="challenge2"):
                st.session_state.current_view = "talent"
                st.rerun()
    
    # Recent achievements
    st.subheader("Recent Achievements")
    if any(any(level['unlocked'] for level in achievement['levels']) for achievement in st.session_state.achievements.values()):
        for key, achievement in st.session_state.achievements.items():
            for level in achievement['levels']:
                if level['unlocked']:
                    st.success(f"🎉 Unlocked: {achievement['name']} - {level['name']} {level['badge']}")
    else:
        st.info("Complete actions in the platform to earn achievements!")

elif st.session_state.current_view == "settings":
    st.title("Settings & Preferences")
    
    # Email notification settings
    st.subheader("Email Notifications")
    
    # Email settings form
    with st.form("email_settings"):
        enable_email = st.checkbox("Enable email notifications", value=st.session_state.email_preferences["enabled"])
        email_address = st.text_input("Email address", value=st.session_state.email_preferences["email"])
        
        frequency = st.radio(
            "Notification frequency",
            options=["daily", "weekly", "significant changes only"],
            index=0 if st.session_state.email_preferences["frequency"] == "daily" else 
                  1 if st.session_state.email_preferences["frequency"] == "weekly" else 2
        )
        
        alert_threshold = st.slider(
            "Alert me when hiring changes by at least (%)",
            min_value=5,
            max_value=50,
            value=st.session_state.email_preferences["alert_threshold"],
            step=5
        )
        
        submitted = st.form_submit_button("Save Email Preferences")
        
        if submitted:
            st.session_state.email_preferences = {
                "enabled": enable_email,
                "email": email_address,
                "frequency": frequency,
                "alert_threshold": alert_threshold
            }
            
            # In a real app, we would save these preferences to the database
            st.success("Email preferences saved!")
            
            # Set up the email system with the new preferences
            if enable_email and email_address:
                setup_email_preferences(
                    email_address, 
                    enable_email, 
                    frequency, 
                    alert_threshold
                )
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear All Watched Companies"):
            st.session_state.watched_companies = []
            # In a real app, we would also clear this from the database
            st.success("Watchlist cleared!")
    
    with col2:
        if st.button("Reset Application Data"):
            # Reset all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Reinitialize required session state variables
            st.session_state.email_preferences = {
                'enabled': False,
                'email': '',
                'frequency': 'daily',
                'alert_threshold': 20
            }
            st.session_state.watched_companies = []
            st.session_state.last_update = None
            st.session_state.current_view = "dashboard"
            
            st.success("Application data reset!")
            st.rerun()
