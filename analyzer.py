import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import re
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_hiring_trends(processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze hiring trends from processed job data.
    
    Args:
        processed_data: Processed job data
    
    Returns:
        List of hiring trend insights
    """
    logger.info("Analyzing hiring trends")
    
    try:
        insights = []
        
        # Analyze hiring velocity
        if "hiring_velocity" in processed_data:
            velocity_data = processed_data["hiring_velocity"]
            
            # Split the data into two halves to compare recent vs earlier
            half_point = len(velocity_data) // 2
            recent_data = velocity_data[half_point:]
            earlier_data = velocity_data[:half_point]
            
            for company in processed_data["companies"]:
                # Calculate total jobs in each period
                recent_count = sum(data[company] for data in recent_data if company in data)
                earlier_count = sum(data[company] for data in earlier_data if company in data)
                
                if earlier_count > 0:
                    percent_change = ((recent_count - earlier_count) / earlier_count) * 100
                    
                    if percent_change > 30:
                        insights.append({
                            "type": "hiring_surge",
                            "company": company,
                            "percent_change": percent_change,
                            "insight": f"Hiring surge detected: {company} has increased hiring by {percent_change:.1f}% compared to the previous period."
                        })
                    elif percent_change < -30:
                        insights.append({
                            "type": "hiring_decline",
                            "company": company,
                            "percent_change": percent_change,
                            "insight": f"Hiring decline detected: {company} has decreased hiring by {abs(percent_change):.1f}% compared to the previous period."
                        })
        
        # Analyze role patterns
        if "roles_by_company" in processed_data:
            for company, roles in processed_data["roles_by_company"].items():
                # Leadership roles often indicate strategic changes
                leadership_roles = ["CEO", "CFO", "CTO", "COO", "CHRO", "CMO", "President", "Director", "VP", "Head"]
                
                leadership_count = sum(count for role, count in roles.items() 
                                     if any(leader in role for leader in leadership_roles))
                
                if leadership_count >= 2:
                    insights.append({
                        "type": "leadership_changes",
                        "company": company,
                        "count": leadership_count,
                        "insight": f"Leadership changes: {company} is hiring for {leadership_count} leadership positions, indicating potential organizational changes."
                    })
                
                # Detect specific technology focus
                tech_categories = {
                    "AI/ML": ["AI", "Machine Learning", "Data Scientist", "NLP", "Computer Vision", "Deep Learning"],
                    "Cloud": ["AWS", "Azure", "GCP", "Cloud", "DevOps", "SRE", "Kubernetes"],
                    "Mobile": ["iOS", "Android", "Mobile", "React Native", "Flutter"],
                    "Frontend": ["Frontend", "UI", "UX", "React", "Angular", "Vue"],
                    "Backend": ["Backend", "API", "Microservices", "Node.js", "Java", "Python", "Go", "Ruby"]
                }
                
                for category, keywords in tech_categories.items():
                    category_count = sum(count for role, count in roles.items() 
                                       if any(keyword.lower() in role.lower() for keyword in keywords))
                    
                    if category_count >= 3:
                        insights.append({
                            "type": "technology_focus",
                            "company": company,
                            "category": category,
                            "count": category_count,
                            "insight": f"Technology focus: {company} is hiring {category_count} roles in {category}, indicating strategic investment in this area."
                        })
        
        # Analyze location patterns
        if "locations_by_company" in processed_data:
            for company, locations in processed_data["locations_by_company"].items():
                remote_count = sum(count for location, count in locations.items() 
                                 if "remote" in location.lower())
                
                total_jobs = sum(locations.values())
                if total_jobs > 0:
                    remote_percentage = (remote_count / total_jobs) * 100
                    
                    if remote_percentage > 50:
                        insights.append({
                            "type": "remote_work",
                            "company": company,
                            "percentage": remote_percentage,
                            "insight": f"Remote work focus: {company} has {remote_percentage:.1f}% remote positions, indicating a strong remote work culture."
                        })
                
                # Geographic expansion
                regions = {
                    "North America": ["US", "USA", "United States", "Canada", "Mexico"],
                    "Europe": ["UK", "United Kingdom", "Germany", "France", "Spain", "Italy", "Netherlands", "Sweden"],
                    "Asia": ["China", "Japan", "India", "Singapore", "Hong Kong"],
                    "Latin America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru"],
                    "Africa": ["South Africa", "Nigeria", "Kenya", "Egypt"],
                    "Australia/Oceania": ["Australia", "New Zealand"]
                }
                
                region_counts = {region: 0 for region in regions}
                for location, count in locations.items():
                    for region, keywords in regions.items():
                        if any(keyword.lower() in location.lower() for keyword in keywords):
                            region_counts[region] += count
                
                # Identify regions with significant presence
                for region, count in region_counts.items():
                    if count >= 3:
                        insights.append({
                            "type": "geographic_expansion",
                            "company": company,
                            "region": region,
                            "count": count,
                            "insight": f"Geographic focus: {company} has {count} positions in {region}, indicating strategic focus or expansion in this region."
                        })
        
        logger.info(f"Generated {len(insights)} hiring trend insights")
        return insights
    
    except Exception as e:
        logger.error(f"Error analyzing hiring trends: {str(e)}")
        return []

def identify_skill_patterns(processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify patterns in skill requirements across companies.
    
    Args:
        processed_data: Processed job data
    
    Returns:
        List of skill pattern insights
    """
    logger.info("Identifying skill patterns")
    
    try:
        insights = []
        
        if "skills_by_company" in processed_data:
            # Get all unique skills
            all_skills = set()
            for company_skills in processed_data["skills_by_company"].values():
                all_skills.update(company_skills.keys())
            
            # Calculate skill prevalence across companies
            skill_prevalence = {}
            for skill in all_skills:
                companies_with_skill = sum(1 for company, skills in processed_data["skills_by_company"].items() 
                                         if skill in skills)
                skill_prevalence[skill] = companies_with_skill / len(processed_data["companies"])
            
            # Identify emerging skills (low prevalence but appearing in multiple companies)
            emerging_skills = []
            for skill, prevalence in skill_prevalence.items():
                if 0.1 <= prevalence <= 0.4:  # In 10-40% of companies
                    total_demand = sum(skills.get(skill, 0) for skills in processed_data["skills_by_company"].values())
                    if total_demand >= 5:  # At least 5 jobs require this skill
                        emerging_skills.append((skill, prevalence, total_demand))
            
            # Sort by total demand and take top 5
            emerging_skills.sort(key=lambda x: x[2], reverse=True)
            for skill, prevalence, demand in emerging_skills[:5]:
                insights.append({
                    "type": "emerging_skill",
                    "skill": skill,
                    "prevalence": prevalence,
                    "demand": demand,
                    "insight": f"Emerging skill: {skill} is appearing in {prevalence*100:.1f}% of companies with {demand} total job postings."
                })
            
            # Identify highly competitive skills (high prevalence across companies)
            competitive_skills = []
            for skill, prevalence in skill_prevalence.items():
                if prevalence >= 0.7:  # In 70%+ of companies
                    total_demand = sum(skills.get(skill, 0) for skills in processed_data["skills_by_company"].values())
                    if total_demand >= 10:  # At least 10 jobs require this skill
                        competitive_skills.append((skill, prevalence, total_demand))
            
            # Sort by total demand and take top 5
            competitive_skills.sort(key=lambda x: x[2], reverse=True)
            for skill, prevalence, demand in competitive_skills[:5]:
                insights.append({
                    "type": "competitive_skill",
                    "skill": skill,
                    "prevalence": prevalence,
                    "demand": demand,
                    "insight": f"Competitive skill: {skill} is in high demand across {prevalence*100:.1f}% of companies with {demand} total job postings."
                })
            
            # Identify company-specific skills (unique to one or few companies)
            for company in processed_data["companies"]:
                if company in processed_data["skills_by_company"]:
                    company_skills = processed_data["skills_by_company"][company]
                    
                    unique_skills = []
                    for skill, count in company_skills.items():
                        other_companies_with_skill = sum(1 for c, skills in processed_data["skills_by_company"].items() 
                                                      if c != company and skill in skills)
                        
                        if other_companies_with_skill == 0 and count >= 2:  # Unique to this company and in multiple jobs
                            unique_skills.append((skill, count))
                    
                    # Sort by count and take top 3
                    unique_skills.sort(key=lambda x: x[1], reverse=True)
                    for skill, count in unique_skills[:3]:
                        insights.append({
                            "type": "unique_skill",
                            "company": company,
                            "skill": skill,
                            "count": count,
                            "insight": f"Unique focus: {company} is the only company hiring for {skill} ({count} positions), indicating a potential competitive advantage."
                        })
        
        logger.info(f"Generated {len(insights)} skill pattern insights")
        return insights
    
    except Exception as e:
        logger.error(f"Error identifying skill patterns: {str(e)}")
        return []

def detect_market_shifts(processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect potential market shifts based on hiring patterns.
    
    Args:
        processed_data: Processed job data
    
    Returns:
        List of market shift insights
    """
    logger.info("Detecting market shifts")
    
    try:
        insights = []
        
        # Analyze role distribution changes
        if "role_distribution" in processed_data:
            # Group roles into categories
            role_categories = {
                "Engineering": ["Engineer", "Developer", "Programmer", "Architect"],
                "Data": ["Data", "Analytics", "Scientist", "Analyst"],
                "Product": ["Product", "Manager", "Owner"],
                "Design": ["Design", "UX", "UI", "User Experience"],
                "Marketing": ["Marketing", "Growth", "SEO", "Content"],
                "Sales": ["Sales", "Account", "Business Development"],
                "Operations": ["Operations", "Support", "Customer Success"]
            }
            
            category_counts = {company: {category: 0 for category in role_categories} 
                              for company in processed_data["companies"]}
            
            for role_data in processed_data["role_distribution"]:
                role = role_data["role"]
                
                # Determine which category this role belongs to
                assigned_category = None
                for category, keywords in role_categories.items():
                    if any(keyword.lower() in role.lower() for keyword in keywords):
                        assigned_category = category
                        break
                
                if assigned_category:
                    for company in processed_data["companies"]:
                        if company in role_data:
                            category_counts[company][assigned_category] += role_data[company]
            
            # Calculate percentage of each category for each company
            category_percentages = {}
            for company, categories in category_counts.items():
                total = sum(categories.values())
                if total > 0:
                    category_percentages[company] = {category: (count / total) * 100 
                                                   for category, count in categories.items()}
            
            # Identify significant category focuses
            for company, percentages in category_percentages.items():
                for category, percentage in percentages.items():
                    if percentage >= 40:  # Company has a strong focus in this category
                        insights.append({
                            "type": "category_focus",
                            "company": company,
                            "category": category,
                            "percentage": percentage,
                            "insight": f"Strategic focus: {company} is heavily investing in {category} ({percentage:.1f}% of hiring), indicating a strategic priority."
                        })
            
            # Compare companies to identify divergent strategies
            if len(category_percentages) >= 2:
                for category in role_categories:
                    company_percentages = [(company, percentages.get(category, 0)) 
                                          for company, percentages in category_percentages.items()]
                    
                    company_percentages.sort(key=lambda x: x[1], reverse=True)
                    
                    if len(company_percentages) >= 2:
                        top_company, top_percentage = company_percentages[0]
                        bottom_company, bottom_percentage = company_percentages[-1]
                        
                        difference = top_percentage - bottom_percentage
                        if difference >= 30 and top_percentage >= 25:  # Significant difference
                            insights.append({
                                "type": "divergent_strategy",
                                "category": category,
                                "top_company": top_company,
                                "top_percentage": top_percentage,
                                "bottom_company": bottom_company,
                                "bottom_percentage": bottom_percentage,
                                "difference": difference,
                                "insight": f"Divergent strategies: {top_company} is investing heavily in {category} ({top_percentage:.1f}%), while {bottom_company} is not ({bottom_percentage:.1f}%), suggesting different market approaches."
                            })
        
        # Analyze geographic shifts
        if "location_distribution" in processed_data:
            # Group locations by region
            regions = {
                "North America": ["US", "USA", "United States", "Canada", "Mexico"],
                "Europe": ["UK", "United Kingdom", "Germany", "France", "Spain", "Italy", "Netherlands", "Sweden"],
                "Asia": ["China", "Japan", "India", "Singapore", "Hong Kong"],
                "Latin America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru"],
                "Remote": ["Remote", "Virtual", "Work from home", "WFH"]
            }
            
            region_counts = {company: {region: 0 for region in regions} 
                            for company in processed_data["companies"]}
            
            for location_data in processed_data["location_distribution"]:
                location = location_data["location"]
                
                # Determine which region this location belongs to
                assigned_region = None
                for region, keywords in regions.items():
                    if any(keyword.lower() in location.lower() for keyword in keywords):
                        assigned_region = region
                        break
                
                if assigned_region:
                    for company in processed_data["companies"]:
                        if company in location_data:
                            region_counts[company][assigned_region] += location_data[company]
            
            # Identify emerging regions
            for company, region_data in region_counts.items():
                total_locations = sum(region_data.values())
                if total_locations > 0:
                    for region, count in region_data.items():
                        percentage = (count / total_locations) * 100
                        
                        if region != "North America" and percentage >= 20:  # Significant non-US focus
                            insights.append({
                                "type": "geographic_shift",
                                "company": company,
                                "region": region,
                                "percentage": percentage,
                                "insight": f"Geographic shift: {company} has {percentage:.1f}% of roles in {region}, indicating international expansion or market focus."
                            })
        
        logger.info(f"Generated {len(insights)} market shift insights")
        return insights
    
    except Exception as e:
        logger.error(f"Error detecting market shifts: {str(e)}")
        return []

def analyze_industry_trends(processed_data: Dict[str, Any], companies_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Analyze trends and patterns specific to each industry.
    
    Args:
        processed_data: Processed job data
        companies_data: List of company data with industry information
    
    Returns:
        Dictionary mapping industries to lists of industry-specific insights
    """
    logger.info("Analyzing industry-specific trends")
    
    try:
        # Group companies by industry
        companies_by_industry = {}
        for company in companies_data:
            industry = company.get("industry")
            if industry:
                if industry not in companies_by_industry:
                    companies_by_industry[industry] = []
                companies_by_industry[industry].append(company.get("name"))
        
        industry_insights = {}
        
        # For each industry, analyze specific trends
        for industry, industry_companies in companies_by_industry.items():
            industry_insights[industry] = []
            
            # Skip if there are too few companies in this industry
            if len(industry_companies) < 2:
                continue
            
            # 1. Analyze hiring velocity within this industry
            if "hiring_velocity" in processed_data:
                velocity_data = processed_data["hiring_velocity"]
                industry_velocity = {}
                
                for company in industry_companies:
                    # Calculate average jobs per period
                    if company in processed_data["companies"] and len(velocity_data) > 0:
                        company_velocity = sum(data.get(company, 0) for data in velocity_data) / len(velocity_data)
                        industry_velocity[company] = company_velocity
                
                if industry_velocity:
                    # Calculate industry average
                    if len(industry_velocity) > 0:
                        industry_avg = sum(industry_velocity.values()) / len(industry_velocity)
                    else:
                        industry_avg = 0  # Default value if no companies have velocity data
                    
                    # Find companies significantly above average (25% or more)
                    above_avg_companies = [(company, vel) for company, vel in industry_velocity.items() 
                                          if vel >= industry_avg * 1.25]
                    
                    if above_avg_companies:
                        # Sort by velocity descending
                        above_avg_companies.sort(key=lambda x: x[1], reverse=True)
                        top_company, velocity = above_avg_companies[0]
                        
                        # Ensure safe division for percentage calculation
                        if industry_avg > 0:
                            percentage_above = ((velocity/industry_avg)-1)*100
                        else:
                            percentage_above = 100  # Default to 100% if industry_avg is zero
                            
                        industry_insights[industry].append({
                            "type": "industry_leader",
                            "company": top_company,
                            "industry": industry,
                            "velocity": velocity,
                            "industry_avg": industry_avg,
                            "insight": f"Industry leader: {top_company} is hiring at {velocity:.1f} jobs per period, {percentage_above:.1f}% above the {industry} industry average."
                        })
            
            # 2. Analyze skill demand specific to this industry
            if "skills_by_company" in processed_data:
                # Collect all skills for companies in this industry
                industry_skills = {}
                for company in industry_companies:
                    if company in processed_data["skills_by_company"]:
                        company_skills = processed_data["skills_by_company"][company]
                        for skill, count in company_skills.items():
                            if skill not in industry_skills:
                                industry_skills[skill] = 0
                            industry_skills[skill] += count
                
                # Find top skills for this industry
                if industry_skills:
                    top_skills = sorted(industry_skills.items(), key=lambda x: x[1], reverse=True)[:5]
                    skill_list = ", ".join([skill for skill, _ in top_skills])
                    
                    industry_insights[industry].append({
                        "type": "industry_skills",
                        "industry": industry,
                        "top_skills": [skill for skill, _ in top_skills],
                        "insight": f"Critical {industry} skills: The most in-demand skills in the {industry} industry are {skill_list}."
                    })
                    
                    # Identify industry-specific skills (more common in this industry than others)
                    other_industries = set(companies_by_industry.keys()) - {industry}
                    other_industry_companies = []
                    for ind in other_industries:
                        other_industry_companies.extend(companies_by_industry[ind])
                    
                    industry_specific = []
                    for skill, industry_count in industry_skills.items():
                        # Calculate what percentage of this industry's companies need this skill
                        # Ensure we don't divide by zero if industry_companies is empty
                        if len(industry_companies) > 0:
                            industry_prevalence = sum(1 for company in industry_companies 
                                                   if company in processed_data["skills_by_company"] and 
                                                   skill in processed_data["skills_by_company"][company]) / len(industry_companies)
                        else:
                            industry_prevalence = 0
                        
                        # Calculate what percentage of other industries' companies need this skill
                        # Ensure we don't divide by zero for empty other_industry_companies
                        if len(other_industry_companies) > 0:
                            other_prevalence = sum(1 for company in other_industry_companies 
                                                if company in processed_data["skills_by_company"] and 
                                                skill in processed_data["skills_by_company"][company]) / len(other_industry_companies)
                        else:
                            other_prevalence = 0
                        
                        # Use a safe division approach to prevent division by zero
                        prevalence_ratio = industry_prevalence / max(0.01, other_prevalence) if other_prevalence > 0 else float('inf')
                        
                        # If much more prevalent in this industry
                        if industry_prevalence >= 0.4 and prevalence_ratio >= 2:
                            industry_specific.append((skill, industry_prevalence, prevalence_ratio))
                    
                    if industry_specific:
                        # Sort by industry-specificity ratio
                        industry_specific.sort(key=lambda x: x[2], reverse=True)
                        specific_skill = industry_specific[0][0]
                        
                        industry_insights[industry].append({
                            "type": "industry_specific_skill",
                            "industry": industry,
                            "skill": specific_skill,
                            "insight": f"Industry specialization: {specific_skill} is a specialized skill particularly important in the {industry} industry."
                        })
            
            # 3. Analyze geographic trends for this industry
            if "locations_by_company" in processed_data:
                # Collect locations across industry
                industry_locations = {}
                for company in industry_companies:
                    if company in processed_data["locations_by_company"]:
                        company_locations = processed_data["locations_by_company"][company]
                        for location, count in company_locations.items():
                            if location not in industry_locations:
                                industry_locations[location] = 0
                            industry_locations[location] += count
                
                if industry_locations:
                    # Find top locations for this industry
                    top_locations = sorted(industry_locations.items(), key=lambda x: x[1], reverse=True)[:3]
                    location_list = ", ".join([location for location, _ in top_locations])
                    
                    industry_insights[industry].append({
                        "type": "industry_hubs",
                        "industry": industry,
                        "top_locations": [location for location, _ in top_locations],
                        "insight": f"Industry hubs: The main hiring locations in the {industry} industry are {location_list}."
                    })
        
        logger.info(f"Generated industry-specific insights for {len(industry_insights)} industries")
        return industry_insights
    
    except Exception as e:
        logger.error(f"Error analyzing industry trends: {str(e)}")
        return {}

def generate_industry_recommendations(industry_insights: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate industry-specific strategic recommendations.
    
    Args:
        industry_insights: Dictionary of industry-specific insights
    
    Returns:
        Dictionary mapping industries to lists of recommendations
    """
    logger.info("Generating industry-specific recommendations")
    
    try:
        industry_recommendations = {}
        
        for industry, insights in industry_insights.items():
            industry_recommendations[industry] = []
            
            # Group insights by type
            insight_types = {}
            for insight in insights:
                insight_type = insight["type"]
                if insight_type not in insight_types:
                    insight_types[insight_type] = []
                insight_types[insight_type].append(insight)
            
            # 1. Skills investment recommendation
            if "industry_skills" in insight_types:
                skills_insight = insight_types["industry_skills"][0]
                top_skills = skills_insight.get("top_skills", [])
                if top_skills:
                    skill_list = ", ".join(top_skills[:3])
                    industry_recommendations[industry].append({
                        "type": "industry_skill_investment",
                        "industry": industry,
                        "skills": top_skills[:3],
                        "priority": "high",
                        "recommendation": f"Focus training on {industry}-critical skills: {skill_list}. These skills are in highest demand across the industry."
                    })
            
            # 2. Location strategy recommendation
            if "industry_hubs" in insight_types:
                hubs_insight = insight_types["industry_hubs"][0]
                top_locations = hubs_insight.get("top_locations", [])
                if top_locations:
                    location = top_locations[0]
                    industry_recommendations[industry].append({
                        "type": "industry_location_strategy",
                        "industry": industry,
                        "location": location,
                        "priority": "medium",
                        "recommendation": f"Consider talent presence in {location}, the primary hiring hub for the {industry} industry."
                    })
            
            # 3. Competitive intelligence recommendation
            if "industry_leader" in insight_types:
                leader_insight = insight_types["industry_leader"][0]
                company = leader_insight.get("company")
                if company:
                    industry_recommendations[industry].append({
                        "type": "industry_competitor_analysis",
                        "industry": industry,
                        "company": company,
                        "priority": "high",
                        "recommendation": f"Monitor {company}'s strategic moves closely. They are the hiring leader in the {industry} industry, which may indicate upcoming market initiatives."
                    })
            
            # 4. Specialization recommendation
            if "industry_specific_skill" in insight_types:
                specific_insight = insight_types["industry_specific_skill"][0]
                skill = specific_insight.get("skill")
                if skill:
                    industry_recommendations[industry].append({
                        "type": "industry_specialization",
                        "industry": industry,
                        "skill": skill,
                        "priority": "medium",
                        "recommendation": f"Develop expertise in {skill}, a specialized skill particularly valuable in the {industry} industry."
                    })
        
        logger.info(f"Generated recommendations for {len(industry_recommendations)} industries")
        return industry_recommendations
    
    except Exception as e:
        logger.error(f"Error generating industry recommendations: {str(e)}")
        return {}

def generate_strategic_recommendations(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate strategic recommendations based on analyzed insights.
    
    Args:
        insights: List of insights from various analysis functions
    
    Returns:
        List of strategic recommendations
    """
    logger.info("Generating strategic recommendations")
    
    try:
        recommendations = []
        
        # Group insights by type
        insight_types = {}
        for insight in insights:
            insight_type = insight["type"]
            if insight_type not in insight_types:
                insight_types[insight_type] = []
            insight_types[insight_type].append(insight)
        
        # Generate recommendations based on emerging skills
        if "emerging_skill" in insight_types:
            emerging_skills = [insight["skill"] for insight in insight_types["emerging_skill"]]
            if emerging_skills:
                skill_list = ", ".join(emerging_skills[:3])
                recommendations.append({
                    "type": "skill_investment",
                    "skills": emerging_skills[:3],
                    "priority": "high",
                    "recommendation": f"Invest in training for emerging skills: {skill_list}. These skills are growing in demand but not yet widespread, providing a competitive advantage window."
                })
        
        # Generate recommendations based on geographic shifts
        if "geographic_shift" in insight_types:
            region_counts = Counter([insight["region"] for insight in insight_types["geographic_shift"]])
            if region_counts:
                top_region, count = region_counts.most_common(1)[0]
                if count >= 2:  # Multiple companies focusing on this region
                    recommendations.append({
                        "type": "geographic_expansion",
                        "region": top_region,
                        "priority": "medium",
                        "recommendation": f"Consider {top_region} market presence. Multiple competitors are expanding hiring in this region, indicating potential market opportunities."
                    })
        
        # Generate recommendations based on hiring surges
        if "hiring_surge" in insight_types:
            surging_companies = [insight["company"] for insight in insight_types["hiring_surge"]]
            if surging_companies:
                companies_list = ", ".join(surging_companies[:3])
                recommendations.append({
                    "type": "competitive_monitoring",
                    "companies": surging_companies[:3],
                    "priority": "high",
                    "recommendation": f"Monitor product launches from {companies_list}. These companies show significant hiring surges, often preceding major product initiatives."
                })
        
        # Generate recommendations based on technology focus
        if "technology_focus" in insight_types:
            tech_counts = Counter([insight["category"] for insight in insight_types["technology_focus"]])
            if tech_counts:
                top_tech, count = tech_counts.most_common(1)[0]
                if count >= 2:  # Multiple companies focusing on this technology
                    recommendations.append({
                        "type": "technology_investment",
                        "technology": top_tech,
                        "priority": "high",
                        "recommendation": f"Strategically evaluate {top_tech} investments. Multiple competitors are heavily investing in this technology area, signaling industry direction."
                    })
        
        # Generate recommendations based on unique skills
        if "unique_skill" in insight_types:
            unique_skills = [(insight["company"], insight["skill"]) for insight in insight_types["unique_skill"]]
            if unique_skills:
                company, skill = unique_skills[0]
                recommendations.append({
                    "type": "competitive_advantage",
                    "company": company,
                    "skill": skill,
                    "priority": "medium",
                    "recommendation": f"Research {company}'s use of {skill}. They're uniquely hiring for this skill, potentially indicating proprietary technology or market differentiation."
                })
        
        # Generate recommendations based on leadership changes
        if "leadership_changes" in insight_types:
            companies_with_leadership_changes = [insight["company"] for insight in insight_types["leadership_changes"]]
            if companies_with_leadership_changes:
                companies_list = ", ".join(companies_with_leadership_changes[:2])
                recommendations.append({
                    "type": "strategic_shift",
                    "companies": companies_with_leadership_changes[:2],
                    "priority": "medium",
                    "recommendation": f"Prepare for potential strategic shifts from {companies_list}. Leadership hiring often precedes major strategic changes or funding events."
                })
        
        # Generate recommendations based on divergent strategies
        if "divergent_strategy" in insight_types:
            for insight in insight_types["divergent_strategy"][:2]:  # Limit to top 2 insights
                recommendations.append({
                    "type": "strategic_positioning",
                    "category": insight["category"],
                    "companies": [insight["top_company"], insight["bottom_company"]],
                    "priority": "low",
                    "recommendation": f"Evaluate your positioning in {insight['category']} relative to competitors. {insight['top_company']} is heavily investing while {insight['bottom_company']} is not, indicating different market bets."
                })
        
        logger.info(f"Generated {len(recommendations)} strategic recommendations")
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating strategic recommendations: {str(e)}")
        return []
