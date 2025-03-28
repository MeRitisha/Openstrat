import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
import re
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_job_data(job_listings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Process raw job listing data into structured format for analysis.
    
    Args:
        job_listings: Dictionary mapping company names to lists of job listings
    
    Returns:
        Processed data ready for analysis
    """
    logger.info("Processing job data")
    
    try:
        processed_data = {
            "companies": [],
            "job_counts": [],
            "roles": {},
            "locations": {},
            "skills": {},
            "time_series": {},
            "salary_ranges": {}
        }
        
        all_roles = set()
        all_locations = set()
        all_skills = set()
        
        # Process data for each company
        for company, listings in job_listings.items():
            processed_data["companies"].append(company)
            processed_data["job_counts"].append(len(listings))
            
            # Process roles
            company_roles = {}
            for job in listings:
                role = job["title"]
                if role in company_roles:
                    company_roles[role] += 1
                else:
                    company_roles[role] = 1
                all_roles.add(role)
            
            processed_data["roles"][company] = company_roles
            
            # Process locations
            company_locations = {}
            for job in listings:
                location = job["location"]
                if location in company_locations:
                    company_locations[location] += 1
                else:
                    company_locations[location] = 1
                all_locations.add(location)
            
            processed_data["locations"][company] = company_locations
            
            # Process skills from requirements
            company_skills = {}
            for job in listings:
                for requirement in job.get("requirements", []):
                    # Extract skills from requirements using simple matching
                    # In a real app, we would use more sophisticated NLP techniques
                    potential_skills = extract_skills_from_text(requirement)
                    for skill in potential_skills:
                        if skill in company_skills:
                            company_skills[skill] += 1
                        else:
                            company_skills[skill] = 1
                        all_skills.add(skill)
            
            processed_data["skills"][company] = company_skills
            
            # Process time series data
            dates = [datetime.strptime(job["date"], "%Y-%m-%d") for job in listings if "date" in job]
            
            # Create time series for the last 30 days
            today = datetime.now()
            date_range = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
            
            date_counts = {}
            for date in date_range:
                date_counts[date] = 0
            
            for job_date in dates:
                job_date_str = job_date.strftime("%Y-%m-%d")
                if job_date_str in date_counts:
                    date_counts[job_date_str] += 1
            
            processed_data["time_series"][company] = date_counts
            
            # Process salary ranges
            salary_data = []
            for job in listings:
                if "salary_range" in job:
                    salary_range = job["salary_range"]
                    min_salary, max_salary = extract_salary_range(salary_range)
                    if min_salary and max_salary:
                        salary_data.append({
                            "role": job["title"],
                            "min_salary": min_salary,
                            "max_salary": max_salary,
                            "avg_salary": (min_salary + max_salary) / 2
                        })
            
            processed_data["salary_ranges"][company] = salary_data
        
        # Add aggregate data across all companies
        processed_data["all_roles"] = list(all_roles)
        processed_data["all_locations"] = list(all_locations)
        processed_data["all_skills"] = list(all_skills)
        
        logger.info("Successfully processed job data")
        return processed_data
    
    except Exception as e:
        logger.error(f"Error processing job data: {str(e)}")
        # Return minimal structure to avoid breaking downstream code
        return {
            "companies": list(job_listings.keys()),
            "job_counts": [len(listings) for listings in job_listings.values()],
            "roles": {},
            "locations": {},
            "skills": {},
            "time_series": {},
            "salary_ranges": {}
        }

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from requirement text using simple keyword matching.
    
    Args:
        text: Requirement text to extract skills from
    
    Returns:
        List of extracted skills
    """
    # In a real app, we would use NLP techniques or a skills taxonomy
    # This is a simplified approach using keyword matching
    common_skills = [
        "Python", "Java", "JavaScript", "C++", "C#", "SQL", "React", "Angular",
        "Vue", "Node.js", "AWS", "GCP", "Azure", "Docker", "Kubernetes",
        "Machine Learning", "AI", "Data Science", "Cloud", "DevOps",
        "CI/CD", "Agile", "Scrum", "Product Management", "UX", "UI",
        "Design", "Marketing", "Sales", "Finance", "HR", "Operations",
        "Communication", "Leadership", "Project Management", "Teamwork",
        "Problem Solving", "Critical Thinking", "Analytics", "Statistics",
        "Research", "Development", "Testing", "QA", "Security", "Networking",
        "Database", "Frontend", "Backend", "Full Stack", "Mobile", "iOS",
        "Android", "REST", "API", "Microservices", "Big Data", "Hadoop",
        "Spark", "Tableau", "Power BI", "Excel", "Word", "PowerPoint",
        "Office", "Git", "GitHub", "Jira", "Confluence", "Slack", "Teams"
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

def extract_salary_range(salary_text: str) -> Tuple[float, float]:
    """
    Extract minimum and maximum salary from a salary range string.
    
    Args:
        salary_text: Salary range text (e.g., "$80K - $120K")
    
    Returns:
        Tuple of (min_salary, max_salary) in thousands
    """
    try:
        # Match patterns like "$80K - $120K" or "$80,000 - $120,000"
        pattern = r'[\$£€](\d{1,3}(?:,\d{3})*|\d+)K?\s*-\s*[\$£€](\d{1,3}(?:,\d{3})*|\d+)K?'
        match = re.search(pattern, salary_text)
        
        if match:
            min_salary_str = match.group(1).replace(',', '')
            max_salary_str = match.group(2).replace(',', '')
            
            min_salary = float(min_salary_str)
            max_salary = float(max_salary_str)
            
            # Convert to thousands if not already
            if 'K' not in salary_text and min_salary > 1000:
                min_salary /= 1000
                max_salary /= 1000
            
            return min_salary, max_salary
        
        return None, None
    
    except Exception:
        return None, None

def aggregate_job_data(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create aggregate views of processed job data.
    
    Args:
        processed_data: Processed job data
    
    Returns:
        Aggregated data suitable for visualization and analysis
    """
    logger.info("Aggregating job data")
    
    try:
        aggregated = {
            "total_jobs_by_company": {},
            "skills_by_company": {},
            "locations_by_company": {},
            "roles_by_company": {},
            "skills_heatmap_data": [],
            "location_distribution": [],
            "role_distribution": [],
            "hiring_velocity": []
        }
        
        # Total jobs by company
        for company, count in zip(processed_data["companies"], processed_data["job_counts"]):
            aggregated["total_jobs_by_company"][company] = count
        
        # Skills by company
        for company, skills in processed_data["skills"].items():
            aggregated["skills_by_company"][company] = skills
        
        # Locations by company
        for company, locations in processed_data["locations"].items():
            aggregated["locations_by_company"][company] = locations
        
        # Roles by company
        for company, roles in processed_data["roles"].items():
            aggregated["roles_by_company"][company] = roles
        
        # Skills heatmap data
        if processed_data["all_skills"]:
            for skill in processed_data["all_skills"]:
                for company in processed_data["companies"]:
                    if company in processed_data["skills"] and skill in processed_data["skills"][company]:
                        aggregated["skills_heatmap_data"].append({
                            "skill": skill,
                            "company": company,
                            "count": processed_data["skills"][company][skill]
                        })
        
        # Location distribution
        for location in processed_data["all_locations"]:
            location_data = {"location": location}
            for company in processed_data["companies"]:
                if company in processed_data["locations"] and location in processed_data["locations"][company]:
                    location_data[company] = processed_data["locations"][company][location]
                else:
                    location_data[company] = 0
            aggregated["location_distribution"].append(location_data)
        
        # Role distribution
        for role in processed_data["all_roles"]:
            role_data = {"role": role}
            for company in processed_data["companies"]:
                if company in processed_data["roles"] and role in processed_data["roles"][company]:
                    role_data[company] = processed_data["roles"][company][role]
                else:
                    role_data[company] = 0
            aggregated["role_distribution"].append(role_data)
        
        # Hiring velocity (time series data)
        dates = sorted(list(next(iter(processed_data["time_series"].values())).keys()))
        for date in dates:
            date_data = {"date": date}
            for company in processed_data["companies"]:
                if company in processed_data["time_series"] and date in processed_data["time_series"][company]:
                    date_data[company] = processed_data["time_series"][company][date]
                else:
                    date_data[company] = 0
            aggregated["hiring_velocity"].append(date_data)
        
        logger.info("Successfully aggregated job data")
        return aggregated
    
    except Exception as e:
        logger.error(f"Error aggregating job data: {str(e)}")
        return {
            "total_jobs_by_company": {},
            "skills_by_company": {},
            "locations_by_company": {},
            "roles_by_company": {},
            "skills_heatmap_data": [],
            "location_distribution": [],
            "role_distribution": [],
            "hiring_velocity": []
        }
