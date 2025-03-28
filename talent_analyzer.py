import re
import json
from typing import Dict, List, Any, Tuple
import pandas as pd

def analyze_talent_availability(job_role: str, location: str, skills: List[str]) -> Dict[str, Any]:
    """
    Analyze talent availability for a specific job role, location, and skills.
    
    Args:
        job_role: The job role to analyze
        location: The location to search for talent
        skills: List of required skills
        
    Returns:
        Dictionary with talent availability insights
    """
    # In a real application, this would call APIs for LinkedIn, Indeed, Glassdoor, etc.
    # For this demo, we'll return sample data based on the inputs
    
    # Calculate availability based on role and location
    availability_data = {
        "total_candidates": calculate_candidate_estimate(job_role, location),
        "top_cities": get_top_cities_for_talent(job_role, skills),
        "skill_prevalence": get_skill_prevalence(job_role, skills),
        "talent_growth_rate": calculate_talent_growth_rate(job_role, location),
        "competing_companies": get_competing_companies(job_role, location),
        "education_breakdown": get_education_breakdown(job_role),
        "experience_levels": get_experience_distribution(job_role, location),
        "remote_availability": calculate_remote_availability(job_role, skills)
    }
    
    return availability_data

def calculate_candidate_estimate(job_role: str, location: str) -> int:
    """
    Estimate the number of candidates available for a role in a location.
    
    In a real implementation, this would query job platforms' APIs.
    """
    # Base estimate ranges by common roles
    role_estimates = {
        "software engineer": 5000,
        "data scientist": 3000,
        "product manager": 2500,
        "marketing manager": 4000,
        "sales representative": 6000,
        "ux designer": 2000,
        "data analyst": 3500,
        "project manager": 4500,
        "graphic designer": 3200,
        "content writer": 5500
    }
    
    # Location multipliers
    location_multipliers = {
        "san francisco": 1.5,
        "new york": 1.4,
        "seattle": 1.2,
        "austin": 1.1,
        "boston": 1.1,
        "chicago": 1.2,
        "los angeles": 1.3,
        "denver": 0.9,
        "atlanta": 1.0,
        "remote": 2.0
    }
    
    # Get base estimate for the role or use default
    base_estimate = 3000  # Default value
    for key, value in role_estimates.items():
        if key in job_role.lower():
            base_estimate = value
            break
    
    # Apply location multiplier if found
    multiplier = 1.0
    for key, value in location_multipliers.items():
        if key in location.lower():
            multiplier = value
            break
    
    # Calculate and add some variability
    import random
    estimate = int(base_estimate * multiplier * random.uniform(0.9, 1.1))
    
    return estimate

def get_top_cities_for_talent(job_role: str, skills: List[str]) -> List[Dict[str, Any]]:
    """
    Get top cities with the highest concentration of talent for a role.
    """
    tech_cities = [
        {"city": "San Francisco, CA", "talent_count": 12500, "growth_rate": 5.2},
        {"city": "New York, NY", "talent_count": 11000, "growth_rate": 4.8},
        {"city": "Seattle, WA", "talent_count": 9500, "growth_rate": 7.1},
        {"city": "Austin, TX", "talent_count": 7200, "growth_rate": 9.3},
        {"city": "Boston, MA", "talent_count": 6800, "growth_rate": 4.2},
        {"city": "Denver, CO", "talent_count": 5400, "growth_rate": 8.7},
        {"city": "Chicago, IL", "talent_count": 6100, "growth_rate": 3.8},
        {"city": "Los Angeles, CA", "talent_count": 7800, "growth_rate": 5.1},
        {"city": "Atlanta, GA", "talent_count": 5900, "growth_rate": 6.4},
        {"city": "Raleigh, NC", "talent_count": 4200, "growth_rate": 7.9}
    ]
    
    marketing_cities = [
        {"city": "New York, NY", "talent_count": 14500, "growth_rate": 5.8},
        {"city": "Chicago, IL", "talent_count": 8900, "growth_rate": 4.1},
        {"city": "Los Angeles, CA", "talent_count": 12300, "growth_rate": 6.2},
        {"city": "Atlanta, GA", "talent_count": 7600, "growth_rate": 7.3},
        {"city": "San Francisco, CA", "talent_count": 9200, "growth_rate": 5.6},
        {"city": "Dallas, TX", "talent_count": 6800, "growth_rate": 6.9},
        {"city": "Miami, FL", "talent_count": 5900, "growth_rate": 8.4},
        {"city": "Boston, MA", "talent_count": 7100, "growth_rate": 4.5},
        {"city": "Seattle, WA", "talent_count": 6300, "growth_rate": 6.1},
        {"city": "Denver, CO", "talent_count": 4800, "growth_rate": 7.7}
    ]
    
    design_cities = [
        {"city": "New York, NY", "talent_count": 10500, "growth_rate": 6.1},
        {"city": "Los Angeles, CA", "talent_count": 9800, "growth_rate": 5.9},
        {"city": "San Francisco, CA", "talent_count": 8700, "growth_rate": 5.2},
        {"city": "Chicago, IL", "talent_count": 6200, "growth_rate": 4.3},
        {"city": "Austin, TX", "talent_count": 5500, "growth_rate": 8.1},
        {"city": "Portland, OR", "talent_count": 4800, "growth_rate": 7.2},
        {"city": "Seattle, WA", "talent_count": 5900, "growth_rate": 6.3},
        {"city": "Boston, MA", "talent_count": 4600, "growth_rate": 4.8},
        {"city": "Miami, FL", "talent_count": 4200, "growth_rate": 7.6},
        {"city": "Denver, CO", "talent_count": 3900, "growth_rate": 7.1}
    ]
    
    # Determine which city list to use based on job role
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        cities = tech_cities
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        cities = marketing_cities
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        cities = design_cities
    else:
        # Use average of all lists as default
        cities = []
        for i in range(len(tech_cities)):
            avg_count = (tech_cities[i]["talent_count"] + marketing_cities[i]["talent_count"] + design_cities[i]["talent_count"]) // 3
            avg_growth = (tech_cities[i]["growth_rate"] + marketing_cities[i]["growth_rate"] + design_cities[i]["growth_rate"]) / 3
            cities.append({
                "city": tech_cities[i]["city"],
                "talent_count": avg_count,
                "growth_rate": round(avg_growth, 1)
            })
    
    # Sort by talent count and return top cities
    return sorted(cities, key=lambda x: x["talent_count"], reverse=True)

def get_skill_prevalence(job_role: str, skills: List[str]) -> List[Dict[str, Any]]:
    """
    Get prevalence of requested skills among talent for the specified job role.
    """
    # Tech skills prevalence (percentages)
    tech_skills_prevalence = {
        "python": 65,
        "java": 58,
        "javascript": 72,
        "sql": 62,
        "react": 48,
        "aws": 53,
        "docker": 42,
        "kubernetes": 35,
        "machine learning": 38,
        "data science": 42,
        "c++": 45,
        "golang": 28,
        "typescript": 44,
        "node.js": 51,
        "git": 75,
        "agile": 67,
        "jira": 58,
        "tableau": 32,
        "power bi": 29,
        "tensorflow": 26
    }
    
    # Marketing skills prevalence
    marketing_skills_prevalence = {
        "seo": 58,
        "social media": 72,
        "content marketing": 65,
        "google analytics": 63,
        "email marketing": 61,
        "ppc": 48,
        "sem": 52,
        "adobe creative suite": 55,
        "canva": 67,
        "hubspot": 49,
        "salesforce": 51,
        "market research": 62,
        "copywriting": 59,
        "google ads": 54,
        "facebook ads": 56,
        "influencer marketing": 44,
        "brand strategy": 58,
        "campaign management": 63,
        "mailchimp": 57,
        "conversion optimization": 48
    }
    
    # Design skills prevalence
    design_skills_prevalence = {
        "adobe photoshop": 75,
        "adobe illustrator": 68,
        "figma": 62,
        "sketch": 54,
        "ui design": 65,
        "ux design": 63,
        "adobe xd": 59,
        "typography": 72,
        "color theory": 78,
        "responsive design": 66,
        "user research": 58,
        "prototyping": 64,
        "wireframing": 67,
        "information architecture": 52,
        "indesign": 61,
        "after effects": 48,
        "3d modeling": 37,
        "motion graphics": 44,
        "design thinking": 61,
        "accessibility": 56
    }
    
    # Determine which skill prevalence map to use
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        skill_prevalence_map = tech_skills_prevalence
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        skill_prevalence_map = marketing_skills_prevalence
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        skill_prevalence_map = design_skills_prevalence
    else:
        # Combine all maps for general roles
        skill_prevalence_map = {**tech_skills_prevalence, **marketing_skills_prevalence, **design_skills_prevalence}
    
    # Get prevalence for requested skills or assign default values
    skill_prevalence = []
    for skill in skills:
        skill_lower = skill.lower()
        prevalence = None
        
        # Try to find an exact match
        if skill_lower in skill_prevalence_map:
            prevalence = skill_prevalence_map[skill_lower]
        else:
            # Try to find a partial match
            for key, value in skill_prevalence_map.items():
                if skill_lower in key or key in skill_lower:
                    prevalence = value
                    break
        
        # If no match found, assign a random value between 20-60%
        if prevalence is None:
            import random
            prevalence = random.randint(20, 60)
        
        skill_prevalence.append({
            "skill": skill,
            "prevalence": prevalence,
            "gap_opportunity": 100 - prevalence
        })
    
    # Sort by prevalence (highest first)
    return sorted(skill_prevalence, key=lambda x: x["prevalence"], reverse=True)

def calculate_talent_growth_rate(job_role: str, location: str) -> Dict[str, Any]:
    """
    Calculate talent growth rate for a job role in a specific location.
    """
    # Base growth rates by role category
    tech_growth = 8.2
    marketing_growth = 6.5
    design_growth = 7.3
    general_growth = 5.4
    
    # Location adjustments
    high_growth_locations = ["austin", "seattle", "denver", "raleigh", "nashville"]
    medium_growth_locations = ["san francisco", "new york", "boston", "atlanta", "chicago"]
    low_growth_locations = ["detroit", "cleveland", "pittsburgh", "st. louis", "philadelphia"]
    
    # Determine base growth rate by role
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        base_growth = tech_growth
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        base_growth = marketing_growth
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        base_growth = design_growth
    else:
        base_growth = general_growth
    
    # Apply location adjustment
    location_lower = location.lower()
    if any(loc in location_lower for loc in high_growth_locations):
        adjusted_growth = base_growth * 1.3
    elif any(loc in location_lower for loc in medium_growth_locations):
        adjusted_growth = base_growth * 1.1
    elif any(loc in location_lower for loc in low_growth_locations):
        adjusted_growth = base_growth * 0.8
    else:
        adjusted_growth = base_growth
    
    # Calculate year-over-year projections
    current_year = 2025
    projections = []
    
    import random
    base_value = calculate_candidate_estimate(job_role, location)
    
    for year_offset in range(5):
        year = current_year + year_offset
        # Add some variability to growth rate
        year_growth = adjusted_growth * random.uniform(0.9, 1.1)
        base_value = int(base_value * (1 + (year_growth / 100)))
        projections.append({
            "year": year,
            "talent_count": base_value,
            "growth_rate": round(year_growth, 1)
        })
    
    return {
        "current_growth_rate": round(adjusted_growth, 1),
        "year_over_year_projections": projections
    }

def get_competing_companies(job_role: str, location: str) -> List[Dict[str, Any]]:
    """
    Get companies competing for the same talent.
    """
    # Common tech companies
    tech_companies = [
        {"name": "Google", "hiring_velocity": "High", "role_count": 48},
        {"name": "Microsoft", "hiring_velocity": "High", "role_count": 42},
        {"name": "Amazon", "hiring_velocity": "Very High", "role_count": 65},
        {"name": "Facebook", "hiring_velocity": "Medium", "role_count": 31},
        {"name": "Apple", "hiring_velocity": "Medium", "role_count": 27},
        {"name": "Netflix", "hiring_velocity": "Medium", "role_count": 19},
        {"name": "Salesforce", "hiring_velocity": "High", "role_count": 38},
        {"name": "Oracle", "hiring_velocity": "Medium", "role_count": 29},
        {"name": "IBM", "hiring_velocity": "Medium", "role_count": 35},
        {"name": "Adobe", "hiring_velocity": "Medium", "role_count": 22}
    ]
    
    # Common marketing companies
    marketing_companies = [
        {"name": "HubSpot", "hiring_velocity": "High", "role_count": 28},
        {"name": "Salesforce", "hiring_velocity": "High", "role_count": 33},
        {"name": "Adobe", "hiring_velocity": "Medium", "role_count": 26},
        {"name": "Procter & Gamble", "hiring_velocity": "Medium", "role_count": 31},
        {"name": "Unilever", "hiring_velocity": "Medium", "role_count": 29},
        {"name": "Coca-Cola", "hiring_velocity": "Low", "role_count": 18},
        {"name": "PepsiCo", "hiring_velocity": "Medium", "role_count": 22},
        {"name": "Johnson & Johnson", "hiring_velocity": "Medium", "role_count": 24},
        {"name": "Meta", "hiring_velocity": "High", "role_count": 35},
        {"name": "Twitter", "hiring_velocity": "Medium", "role_count": 21}
    ]
    
    # Common design companies
    design_companies = [
        {"name": "Adobe", "hiring_velocity": "High", "role_count": 32},
        {"name": "Figma", "hiring_velocity": "Very High", "role_count": 28},
        {"name": "Airbnb", "hiring_velocity": "Medium", "role_count": 22},
        {"name": "Spotify", "hiring_velocity": "High", "role_count": 26},
        {"name": "Apple", "hiring_velocity": "High", "role_count": 31},
        {"name": "Meta", "hiring_velocity": "Medium", "role_count": 27},
        {"name": "Google", "hiring_velocity": "High", "role_count": 30},
        {"name": "Uber", "hiring_velocity": "Medium", "role_count": 19},
        {"name": "Microsoft", "hiring_velocity": "Medium", "role_count": 25},
        {"name": "Twitter", "hiring_velocity": "Low", "role_count": 17}
    ]
    
    # Determine which company list to use
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        companies = tech_companies
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        companies = marketing_companies
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        companies = design_companies
    else:
        # Take a mix of companies from different lists
        import random
        companies = random.sample(tech_companies, 3) + random.sample(marketing_companies, 3) + random.sample(design_companies, 4)
    
    # Sort by role count (highest first)
    return sorted(companies, key=lambda x: x["role_count"], reverse=True)

def get_education_breakdown(job_role: str) -> List[Dict[str, Any]]:
    """
    Get education level breakdown for a specific job role.
    """
    # Education breakdowns by role type
    tech_education = [
        {"level": "Bachelor's Degree", "percentage": 48},
        {"level": "Master's Degree", "percentage": 32},
        {"level": "Self-taught / Bootcamp", "percentage": 15},
        {"level": "PhD", "percentage": 5}
    ]
    
    marketing_education = [
        {"level": "Bachelor's Degree", "percentage": 62},
        {"level": "Master's Degree", "percentage": 22},
        {"level": "Associate's Degree", "percentage": 12},
        {"level": "High School / GED", "percentage": 4}
    ]
    
    design_education = [
        {"level": "Bachelor's Degree", "percentage": 55},
        {"level": "Self-taught", "percentage": 25},
        {"level": "Master's Degree", "percentage": 15},
        {"level": "Associate's Degree", "percentage": 5}
    ]
    
    general_education = [
        {"level": "Bachelor's Degree", "percentage": 58},
        {"level": "Master's Degree", "percentage": 22},
        {"level": "Associate's Degree", "percentage": 12},
        {"level": "Self-taught / Bootcamp", "percentage": 5},
        {"level": "PhD", "percentage": 3}
    ]
    
    # Determine which education breakdown to use
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        return tech_education
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        return marketing_education
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        return design_education
    else:
        return general_education

def get_experience_distribution(job_role: str, location: str) -> List[Dict[str, Any]]:
    """
    Get experience level distribution for a job role in a location.
    """
    # Experience level distributions by role type
    tech_experience = [
        {"level": "Entry Level (0-2 years)", "percentage": 24},
        {"level": "Mid Level (3-5 years)", "percentage": 38},
        {"level": "Senior Level (6-10 years)", "percentage": 27},
        {"level": "Director+ (10+ years)", "percentage": 11}
    ]
    
    marketing_experience = [
        {"level": "Entry Level (0-2 years)", "percentage": 32},
        {"level": "Mid Level (3-5 years)", "percentage": 36},
        {"level": "Senior Level (6-10 years)", "percentage": 22},
        {"level": "Director+ (10+ years)", "percentage": 10}
    ]
    
    design_experience = [
        {"level": "Entry Level (0-2 years)", "percentage": 28},
        {"level": "Mid Level (3-5 years)", "percentage": 41},
        {"level": "Senior Level (6-10 years)", "percentage": 24},
        {"level": "Director+ (10+ years)", "percentage": 7}
    ]
    
    general_experience = [
        {"level": "Entry Level (0-2 years)", "percentage": 30},
        {"level": "Mid Level (3-5 years)", "percentage": 35},
        {"level": "Senior Level (6-10 years)", "percentage": 25},
        {"level": "Director+ (10+ years)", "percentage": 10}
    ]
    
    # Major tech hubs have fewer entry-level candidates
    tech_hubs = ["san francisco", "new york", "seattle", "boston"]
    
    # Determine which experience distribution to use
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        experience_dist = tech_experience.copy()
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        experience_dist = marketing_experience.copy()
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        experience_dist = design_experience.copy()
    else:
        experience_dist = general_experience.copy()
    
    # Adjust for location if in a major tech hub
    location_lower = location.lower()
    if any(hub in location_lower for hub in tech_hubs):
        # Reduce entry-level percentage
        entry_level_index = next(i for i, item in enumerate(experience_dist) if "Entry Level" in item["level"])
        mid_level_index = next(i for i, item in enumerate(experience_dist) if "Mid Level" in item["level"])
        
        entry_level_reduction = 8
        experience_dist[entry_level_index]["percentage"] -= entry_level_reduction
        experience_dist[mid_level_index]["percentage"] += entry_level_reduction
    
    return experience_dist

def calculate_remote_availability(job_role: str, skills: List[str]) -> Dict[str, Any]:
    """
    Calculate remote work availability and preferences for a job role.
    """
    # Base remote work tendencies by role type
    tech_remote = {
        "remote_percentage": 68,
        "hybrid_percentage": 24,
        "onsite_percentage": 8
    }
    
    marketing_remote = {
        "remote_percentage": 52,
        "hybrid_percentage": 38,
        "onsite_percentage": 10
    }
    
    design_remote = {
        "remote_percentage": 58,
        "hybrid_percentage": 32,
        "onsite_percentage": 10
    }
    
    general_remote = {
        "remote_percentage": 45,
        "hybrid_percentage": 40,
        "onsite_percentage": 15
    }
    
    # Determine base remote work tendency
    if any(tech_term in job_role.lower() for tech_term in ["software", "developer", "engineer", "data", "programmer", "devops"]):
        remote_tendency = dict(tech_remote)
    elif any(marketing_term in job_role.lower() for marketing_term in ["marketing", "sales", "content", "seo", "social media", "business"]):
        remote_tendency = dict(marketing_remote)
    elif any(design_term in job_role.lower() for design_term in ["design", "ux", "ui", "graphic", "creative", "artist"]):
        remote_tendency = dict(design_remote)
    else:
        remote_tendency = dict(general_remote)
    
    # Skills that tend to increase remote work potential
    remote_friendly_skills = ["programming", "development", "coding", "software", "writing", "content", "social media", "design", "research", "data analysis"]
    
    # Calculate skills effect on remote tendency
    remote_skill_count = sum(1 for skill in skills if any(rs in skill.lower() for rs in remote_friendly_skills))
    skill_factor = min(remote_skill_count * 2, 10)  # Cap at 10% adjustment
    
    # Apply skill factor adjustment
    if skill_factor > 0:
        remote_tendency["remote_percentage"] = min(remote_tendency["remote_percentage"] + skill_factor, 100)
        remote_tendency["onsite_percentage"] = max(remote_tendency["onsite_percentage"] - skill_factor, 0)
    
    # Add trend data
    trend_value = "increasing" if remote_tendency["remote_percentage"] > 50 else "stable"
    salary_diff = -5 if remote_tendency["remote_percentage"] > 60 else -2
    
    remote_tendency["trend"] = trend_value
    remote_tendency["remote_salary_difference"] = salary_diff
    
    return remote_tendency