import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_hiring_trend_chart(hiring_velocity_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a line chart showing hiring velocity over time for different companies.
    
    Args:
        hiring_velocity_data: List of dictionaries with hiring data by date
    
    Returns:
        Plotly figure object
    """
    try:
        # Convert to DataFrame for Plotly
        df = pd.DataFrame(hiring_velocity_data)
        
        # Set date as index
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        
        # Get company columns (all columns except 'date')
        company_cols = [col for col in df.columns if col != "date"]
        
        # Create line chart
        fig = go.Figure()
        
        for company in company_cols:
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df[company],
                mode="lines+markers",
                name=company,
                hovertemplate=f"{company}: %{{y}} jobs<br>%{{x|%Y-%m-%d}}<extra></extra>"
            ))
        
        # Layout customization
        fig.update_layout(
            title="Hiring Velocity by Company",
            xaxis_title="Date",
            yaxis_title="Number of New Job Postings",
            legend_title="Companies",
            hovermode="x unified",
            height=500,
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating hiring trend chart: {str(e)}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            text="Error creating chart: Data format issue",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

def create_skill_heatmap(skills_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a heatmap showing skill demand across companies.
    
    Args:
        skills_data: List of dictionaries with skill demand data
    
    Returns:
        Plotly figure object
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(skills_data)
        
        # Pivot the data to create a matrix of skills vs companies
        pivot_df = pd.pivot_table(
            df, 
            values="count", 
            index="skill", 
            columns="company", 
            aggfunc="sum", 
            fill_value=0
        )
        
        # Select top skills by total count
        pivot_df["total"] = pivot_df.sum(axis=1)
        top_skills = pivot_df.sort_values("total", ascending=False).head(15).drop("total", axis=1)
        
        # Create heatmap
        fig = px.imshow(
            top_skills,
            labels=dict(x="Company", y="Skill", color="Job Count"),
            x=top_skills.columns,
            y=top_skills.index,
            color_continuous_scale="YlGnBu",
            aspect="auto"
        )
        
        # Customize layout
        fig.update_layout(
            title="In-Demand Skills Across Companies",
            height=600,
            xaxis={'side': 'bottom'}
        )
        
        # Add text annotations
        for i, skill in enumerate(top_skills.index):
            for j, company in enumerate(top_skills.columns):
                value = top_skills.iloc[i, j]
                if value > 0:
                    fig.add_annotation(
                        x=company,
                        y=skill,
                        text=str(value),
                        showarrow=False,
                        font=dict(color="black" if value < 8 else "white")
                    )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating skill heatmap: {str(e)}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            text="Error creating heatmap: Data format issue",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

def create_geo_expansion_map(location_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a geographic bubble map showing hiring focus across regions.
    
    Args:
        location_data: List of dictionaries with location data
    
    Returns:
        Plotly figure object
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(location_data)
        
        # Create geographical mapping
        geo_mapping = {
            "San Francisco": {"lat": 37.7749, "lon": -122.4194, "region": "North America"},
            "New York": {"lat": 40.7128, "lon": -74.0060, "region": "North America"},
            "Seattle": {"lat": 47.6062, "lon": -122.3321, "region": "North America"},
            "Austin": {"lat": 30.2672, "lon": -97.7431, "region": "North America"},
            "Boston": {"lat": 42.3601, "lon": -71.0589, "region": "North America"},
            "Chicago": {"lat": 41.8781, "lon": -87.6298, "region": "North America"},
            "Toronto": {"lat": 43.6532, "lon": -79.3832, "region": "North America"},
            "London": {"lat": 51.5074, "lon": -0.1278, "region": "Europe"},
            "Berlin": {"lat": 52.5200, "lon": 13.4050, "region": "Europe"},
            "Paris": {"lat": 48.8566, "lon": 2.3522, "region": "Europe"},
            "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "region": "Europe"},
            "Singapore": {"lat": 1.3521, "lon": 103.8198, "region": "Asia"},
            "Tokyo": {"lat": 35.6762, "lon": 139.6503, "region": "Asia"},
            "Sydney": {"lat": -33.8688, "lon": 151.2093, "region": "Australia"},
            "São Paulo": {"lat": -23.5505, "lon": -46.6333, "region": "Latin America"},
            "Mexico City": {"lat": 19.4326, "lon": -99.1332, "region": "Latin America"},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946, "region": "Asia"},
            "Dublin": {"lat": 53.3498, "lon": -6.2603, "region": "Europe"},
            "Remote": {"lat": 0, "lon": 0, "region": "Remote"}  # Placeholder for remote
        }
        
        # Prepare data for map
        map_data = []
        
        for location_entry in df.to_dict('records'):
            location = location_entry.get("location", "")
            
            # Find matching location in geo_mapping
            matched_location = None
            for geo_location in geo_mapping:
                if geo_location.lower() in location.lower():
                    matched_location = geo_location
                    break
            
            if matched_location:
                for company in [c for c in location_entry.keys() if c != "location"]:
                    count = location_entry[company]
                    if count > 0:
                        map_data.append({
                            "company": company,
                            "location": matched_location,
                            "count": count,
                            "lat": geo_mapping[matched_location]["lat"],
                            "lon": geo_mapping[matched_location]["lon"],
                            "region": geo_mapping[matched_location]["region"]
                        })
            elif "remote" in location.lower():
                # Add Remote as a special category (will be handled separately)
                for company in [c for c in location_entry.keys() if c != "location"]:
                    count = location_entry[company]
                    if count > 0:
                        map_data.append({
                            "company": company,
                            "location": "Remote",
                            "count": count,
                            "lat": None,  # Will be handled in visualization
                            "lon": None,
                            "region": "Remote"
                        })
        
        # Convert to DataFrame for visualization
        map_df = pd.DataFrame(map_data)
        
        # Handle the case where geo mapping didn't work well
        if len(map_df) == 0 or map_df["lat"].isna().all():
            # Fall back to a bar chart of regions
            region_counts = df.melt(
                id_vars=["location"],
                var_name="company",
                value_name="count"
            )
            region_counts = region_counts[region_counts["count"] > 0]
            
            fig = px.bar(
                region_counts, 
                x="location", 
                y="count", 
                color="company",
                title="Job Postings by Location",
                labels={"location": "Location", "count": "Number of Jobs"}
            )
            return fig
        
        # For actual geo map with matched locations
        non_remote = map_df[map_df["region"] != "Remote"]
        
        fig = px.scatter_geo(
            non_remote,
            lat="lat",
            lon="lon",
            color="company",
            size="count",
            hover_name="location",
            hover_data={"company": True, "count": True, "region": True, "lat": False, "lon": False},
            title="Geographic Distribution of Job Postings",
            size_max=30,
            projection="natural earth"
        )
        
        # Add annotations for remote jobs
        remote_jobs = map_df[map_df["region"] == "Remote"]
        if not remote_jobs.empty:
            remote_by_company = remote_jobs.groupby("company")["count"].sum().reset_index()
            
            remote_text = "Remote Jobs: " + ", ".join(
                f"{row['company']}: {row['count']}" for _, row in remote_by_company.iterrows()
            )
            
            fig.add_annotation(
                x=0.5,
                y=0.95,
                xref="paper",
                yref="paper",
                text=remote_text,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.3)",
                borderwidth=1,
                borderpad=4
            )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating geo expansion map: {str(e)}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            text="Error creating geographic map: Data format issue",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

def create_company_comparison_chart(companies_data: Dict[str, Any]) -> go.Figure:
    """
    Create a radar chart comparing different aspects of companies.
    
    Args:
        companies_data: Dictionary with company comparison data
    
    Returns:
        Plotly figure object
    """
    try:
        categories = ["Engineering", "Data Science", "Product", "Design", "Marketing", "Remote Work"]
        
        fig = go.Figure()
        
        for company, values in companies_data.items():
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=company
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Company Hiring Focus Comparison"
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating company comparison chart: {str(e)}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            text="Error creating comparison chart: Data format issue",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

def create_role_distribution_chart(role_data: List[Dict[str, Any]], company: str = None) -> go.Figure:
    """
    Create a pie or bar chart showing role distribution for a specific company or overall.
    
    Args:
        role_data: List of dictionaries with role distribution data
        company: Optional company to filter for
    
    Returns:
        Plotly figure object
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(role_data)
        
        if company:
            # Filter for specific company and create pie chart
            if company in df.columns:
                company_roles = df[["role", company]].copy()
                company_roles = company_roles[company_roles[company] > 0]
                
                if len(company_roles) == 0:
                    raise ValueError(f"No role data for {company}")
                
                # Sort by count and take top 10
                company_roles = company_roles.sort_values(company, ascending=False).head(10)
                
                fig = px.pie(
                    company_roles,
                    values=company,
                    names="role",
                    title=f"Role Distribution for {company}",
                    hole=0.4
                )
                
                # Customize layout
                fig.update_layout(
                    height=500,
                    legend_title="Roles"
                )
                
                return fig
            else:
                raise ValueError(f"Company {company} not found in data")
        else:
            # Create a stacked bar chart for all companies
            companies = [col for col in df.columns if col != "role"]
            
            # Melt the DataFrame for plotly
            melted_df = df.melt(
                id_vars=["role"],
                value_vars=companies,
                var_name="company",
                value_name="count"
            )
            
            # Filter out zero counts
            melted_df = melted_df[melted_df["count"] > 0]
            
            # Sum by role and get top roles
            role_totals = melted_df.groupby("role")["count"].sum().reset_index()
            top_roles = role_totals.sort_values("count", ascending=False).head(10)["role"].tolist()
            
            # Filter for top roles
            melted_df = melted_df[melted_df["role"].isin(top_roles)]
            
            fig = px.bar(
                melted_df,
                x="role",
                y="count",
                color="company",
                title="Top Roles Across Companies",
                labels={"role": "Role", "count": "Number of Jobs", "company": "Company"}
            )
            
            # Customize layout
            fig.update_layout(
                height=500,
                xaxis_title="Role",
                yaxis_title="Number of Job Postings",
                legend_title="Companies",
                xaxis={'categoryorder': 'total descending'}
            )
            
            return fig
    
    except Exception as e:
        logger.error(f"Error creating role distribution chart: {str(e)}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating role chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
