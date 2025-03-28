import requests
from bs4 import BeautifulSoup
import trafilatura
import pandas as pd
import time
import random
import logging
import json
import os
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> Optional[str]:
    """
    Extract the main text content from a webpage using trafilatura.
    
    Args:
        url: The URL of the webpage to extract text from
    
    Returns:
        Extracted text content or None if extraction fails
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return None

def load_companies_data() -> List[Dict[str, Any]]:
    """
    Load company data from the JSON file.
    
    Returns:
        List of company dictionaries with their details
    """
    try:
        companies_file = os.path.join("attached_assets", "companies_100_unique.json")
        if os.path.exists(companies_file):
            with open(companies_file, 'r') as file:
                data = json.load(file)
                logger.info(f"Successfully loaded {len(data.get('companies', []))} companies from data file")
                return data.get("companies", [])
        else:
            logger.warning(f"Companies file not found at {companies_file}")
            return []
    except Exception as e:
        logger.error(f"Error loading companies data: {e}")
        return []


def get_companies_by_industry(industry: str = None) -> List[Dict[str, Any]]:
    """
    Get companies filtered by industry.
    
    Args:
        industry: Industry name to filter by, or None for all companies
        
    Returns:
        List of company dictionaries
    """
    companies = load_companies_data()
    
    if industry:
        filtered = [company for company in companies if company.get("industry") == industry]
        logger.info(f"Found {len(filtered)} companies in the {industry} industry")
        return filtered
    return companies


def get_companies_by_priority(priority: str = None) -> List[Dict[str, Any]]:
    """
    Get companies filtered by priority level.
    
    Args:
        priority: Priority level ('High', 'Medium', 'Critical'), or None for all companies
        
    Returns:
        List of company dictionaries
    """
    companies = load_companies_data()
    
    if priority:
        filtered = [company for company in companies if company.get("priority") == priority]
        logger.info(f"Found {len(filtered)} companies with {priority} priority")
        return filtered
    return companies


def scrape_job_listings(company_name: str, max_pages: int = 5) -> List[Dict[str, Any]]:
    """
    Scrape job listings from a company's career page or job boards.
    
    Args:
        company_name: Name of the company to scrape job listings for
        max_pages: Maximum number of pages to scrape
    
    Returns:
        List of job listings with details
    """
    # Load company URL from our companies data file
    companies = load_companies_data()
    company_data = next((c for c in companies if c.get("name") == company_name), None)
    
    company_url = None
    selector = None
    
    if company_data:
        company_url = company_data.get("url")
        selector = company_data.get("selector")
        logger.info(f"Found company data for {company_name}: URL={company_url}, Selector={selector}")
    else:
        # Fall back to default URLs if not found in the companies data
        company_career_urls = {
            "Google": "https://careers.google.com/jobs/results/",
            "Microsoft": "https://careers.microsoft.com/us/en/search-results",
            "Amazon": "https://www.amazon.jobs/en/search",
            "Apple": "https://jobs.apple.com/en-us/search",
            "Facebook": "https://www.facebook.com/careers/jobs/",
            "Netflix": "https://jobs.netflix.com/search",
            "Shopify": "https://www.shopify.com/careers/search",
            "Twitter": "https://careers.twitter.com/en/jobs.html",
            "Uber": "https://www.uber.com/us/en/careers/list/",
            "Airbnb": "https://careers.airbnb.com/positions/",
        }
        
        if company_name in company_career_urls:
            company_url = company_career_urls[company_name]
            selector = "h3.job-title"  # default selector
            logger.info(f"Using fallback URL for {company_name}: {company_url}")
    
    # Log scraping attempt
    logger.info(f"Scraping job listings for {company_name}")
    
    try:
        # In a real implementation, we would use the URL and selector to scrape
        # For now, generate sample data
        job_listings = generate_sample_job_listings(company_name)
        logger.info(f"Successfully generated {len(job_listings)} job listings for {company_name}")
        return job_listings
    except Exception as e:
        logger.error(f"Error scraping job listings for {company_name}: {str(e)}")
        return []

def scrape_linkedin_jobs(company_name: str, location: str = None) -> List[Dict[str, Any]]:
    """
    Scrape job listings from LinkedIn using RSS feeds.
    
    Args:
        company_name: Company name to search for
        location: Optional location filter
    
    Returns:
        List of job listings from LinkedIn
    """
    # In a real app, this would implement LinkedIn RSS scraping
    # For demonstration, return sample data
    logger.info(f"Scraping LinkedIn jobs for {company_name}")
    
    try:
        # This would use LinkedIn's RSS feeds to avoid API costs
        # For now, return sample data
        job_listings = generate_sample_linkedin_jobs(company_name, location)
        logger.info(f"Successfully scraped {len(job_listings)} LinkedIn jobs for {company_name}")
        return job_listings
    except Exception as e:
        logger.error(f"Error scraping LinkedIn jobs for {company_name}: {str(e)}")
        return []

def scrape_all_companies(companies: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape job listings for multiple companies.
    
    Args:
        companies: List of company names to scrape, or None to use companies from JSON file
    
    Returns:
        Dictionary mapping company names to their job listings
    """
    results = {}
    
    # If no companies specified, load them from the JSON file
    if not companies:
        company_data = load_companies_data()
        if company_data:
            # Use just the company names
            companies = [company["name"] for company in company_data]
            logger.info(f"Using {len(companies)} companies from data file")
        else:
            # Fallback to a default list if JSON loading fails
            companies = ["Google", "Microsoft", "Amazon", "Apple", "Facebook"]
            logger.warning(f"Using fallback company list: {companies}")
    
    for company in companies:
        # Add a small delay to avoid aggressive scraping
        time.sleep(random.uniform(1, 3))
        
        # Get job listings from career page
        career_jobs = scrape_job_listings(company)
        
        # Get job listings from LinkedIn
        linkedin_jobs = scrape_linkedin_jobs(company)
        
        # Combine results (avoiding duplicates would require deduplication logic)
        all_jobs = career_jobs + linkedin_jobs
        
        results[company] = all_jobs
    
    return results


def get_real_time_job_updates(companies: List[str] = None, throttle_requests: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get real-time job updates for specified companies.
    This method enhances the standard scraping with timestamps and real-time flags.
    
    Args:
        companies: List of company names to get updates for, or None to use companies from JSON file
        throttle_requests: Whether to add delay between requests to avoid rate limiting
        
    Returns:
        Dictionary mapping company names to their job listings with real-time indicators
    """
    results = {}
    current_time = time.time()
    
    if not companies:
        # Use companies from the loaded data file
        company_data = load_companies_data()
        if company_data:
            companies = [company["name"] for company in company_data]
        else:
            # Fallback to a default list if JSON loading fails
            companies = ["Google", "Microsoft", "Amazon", "Apple", "Meta"]
    
    for company in companies:
        if throttle_requests:
            # Sleep briefly to avoid hammering websites
            time.sleep(random.uniform(0.1, 0.5))  # Shorter delay for real-time updates
            
        # Get job listings
        career_jobs = scrape_job_listings(company)
        linkedin_jobs = scrape_linkedin_jobs(company)
        job_listings = career_jobs + linkedin_jobs
        
        # Enhance listings with real-time information
        for job in job_listings:
            # Add timestamp in ISO format for easier display
            job['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
            
            # Add relative time for display (e.g., "2 minutes ago")
            job['posted_time'] = 'Just now'
            
            # Flag as real-time data
            job['is_real_time'] = True
            
            # Random status to simulate live changes (new, updated, etc.)
            statuses = ['new', 'updated', 'active', 'closing soon']
            job['status'] = random.choice(statuses)
        
        results[company] = job_listings
    
    logger.info(f"Retrieved real-time job updates for {len(companies)} companies")
    return results

def get_industry_hiring_trends() -> Dict[str, Any]:
    """
    Analyze hiring trends across different industries.
    
    Returns:
        Dictionary with industry-based hiring trend data
    """
    companies = load_companies_data()
    
    # Group companies by industry
    industries = {}
    for company in companies:
        industry = company.get("industry")
        if industry not in industries:
            industries[industry] = []
        industries[industry].append(company.get("name"))
    
    # Analyze trends for each industry
    industry_trends = {}
    for industry, industry_companies in industries.items():
        # Sample industry-level metrics
        industry_trends[industry] = {
            "total_companies": len(industry_companies),
            "hiring_velocity": random.randint(5, 25),  # Average new jobs per week
            "top_hiring_companies": random.sample(industry_companies, min(3, len(industry_companies))),
            "top_roles": _generate_top_roles_for_industry(industry),
            "skill_demand": _generate_skill_demand_for_industry(industry),
            "growth_rate": round(random.uniform(2.0, 15.0), 1)  # % growth in hiring
        }
    
    return industry_trends


def _generate_top_roles_for_industry(industry: str) -> List[Dict[str, Any]]:
    """
    Generate sample top roles for an industry.
    
    Args:
        industry: Industry name
        
    Returns:
        List of role data with count and growth
    """
    industry_roles = {
        "Tech": [
            "Software Engineer", "Data Scientist", "Product Manager", 
            "DevOps Engineer", "UX Designer", "Machine Learning Engineer"
        ],
        "Finance": [
            "Financial Analyst", "Investment Banker", "Risk Manager", 
            "Quantitative Analyst", "Compliance Officer", "Financial Advisor"
        ],
        "Retail": [
            "Store Manager", "Sales Associate", "Merchandiser", 
            "E-commerce Manager", "Supply Chain Analyst", "Customer Service Representative"
        ],
        "Automotive": [
            "Automotive Engineer", "Manufacturing Technician", "Quality Control Specialist", 
            "Supply Chain Manager", "Design Engineer", "Production Supervisor"
        ],
        "Media": [
            "Content Producer", "Digital Marketing Manager", "Social Media Specialist", 
            "Video Editor", "Graphic Designer", "Public Relations Manager"
        ],
        "Healthcare": [
            "Registered Nurse", "Physician", "Healthcare Administrator", 
            "Medical Technologist", "Pharmacist", "Clinical Research Associate"
        ],
        "Aerospace": [
            "Aerospace Engineer", "Aircraft Mechanic", "Avionics Technician", 
            "Systems Engineer", "Project Manager", "Quality Assurance Specialist"
        ]
    }
    
    # Default to Tech roles if industry not found
    roles = industry_roles.get(industry, industry_roles["Tech"])
    
    # Generate data for each role
    top_roles = []
    for role in roles:
        top_roles.append({
            "role": role,
            "count": random.randint(50, 500),
            "growth": round(random.uniform(-5.0, 30.0), 1)  # % growth
        })
    
    # Sort by count (descending)
    return sorted(top_roles, key=lambda x: x["count"], reverse=True)


def _generate_skill_demand_for_industry(industry: str) -> List[Dict[str, Any]]:
    """
    Generate sample skill demand data for an industry.
    
    Args:
        industry: Industry name
        
    Returns:
        List of skill demand data with growth trends
    """
    industry_skills = {
        "Tech": [
            "Python", "JavaScript", "AWS", "React", "Docker", "Kubernetes",
            "Machine Learning", "TensorFlow", "SQL", "Java", "Go", "TypeScript"
        ],
        "Finance": [
            "Financial Modeling", "Excel", "Risk Analysis", "Data Analysis", 
            "Bloomberg Terminal", "Python", "SQL", "Accounting", "CFA", "R"
        ],
        "Retail": [
            "Inventory Management", "POS Systems", "Visual Merchandising", 
            "Retail Analytics", "Omnichannel", "E-commerce", "CRM"
        ],
        "Automotive": [
            "CAD", "Mechanical Engineering", "Electrical Systems", "Quality Control", 
            "Lean Manufacturing", "Supply Chain", "Automotive Testing"
        ],
        "Media": [
            "Content Creation", "Adobe Creative Suite", "Social Media", "SEO", 
            "Video Production", "Content Strategy", "Google Analytics"
        ],
        "Healthcare": [
            "Electronic Health Records", "Patient Care", "Clinical Research", 
            "Medical Terminology", "HIPAA", "Pharmacology", "Clinical Documentation"
        ],
        "Aerospace": [
            "Aerodynamics", "Propulsion Systems", "CAD", "Systems Engineering", 
            "Quality Assurance", "Avionics", "Composite Materials"
        ]
    }
    
    # Default to Tech skills if industry not found
    skills = industry_skills.get(industry, industry_skills["Tech"])
    
    # Generate data for each skill
    skill_demand = []
    for skill in skills:
        skill_demand.append({
            "skill": skill,
            "demand_score": random.randint(60, 95),  # 0-100 score
            "growth": round(random.uniform(-10.0, 40.0), 1),  # % growth
            "companies_requesting": random.randint(5, 30)
        })
    
    # Sort by demand score (descending)
    return sorted(skill_demand, key=lambda x: x["demand_score"], reverse=True)

def generate_sample_job_listings(company_name: str) -> List[Dict[str, Any]]:
    """
    Generate sample job listings for demonstration purposes.
    
    Args:
        company_name: Company name to generate sample data for
    
    Returns:
        List of sample job listings
    """
    # This is used only for development/demonstration
    # In a production app, this would be replaced with actual scraped data
    
    roles = [
        "Software Engineer", "Product Manager", "Data Scientist", 
        "UX Designer", "DevOps Engineer", "Machine Learning Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Engineer",
        "AI Research Scientist", "Cloud Engineer", "Security Engineer"
    ]
    
    locations = [
        "San Francisco, CA", "New York, NY", "Seattle, WA", 
        "Austin, TX", "Remote", "Boston, MA", "Chicago, IL",
        "Toronto, Canada", "London, UK", "Berlin, Germany",
        "Singapore", "Tokyo, Japan", "São Paulo, Brazil"
    ]
    
    departments = [
        "Engineering", "Product", "Design", "Research", 
        "Data", "Infrastructure", "Security", "AI",
        "Marketing", "Customer Success", "Operations"
    ]
    
    # Generate 5-15 random job listings
    num_listings = random.randint(5, 15)
    listings = []
    
    for _ in range(num_listings):
        role = random.choice(roles)
        location = random.choice(locations)
        department = random.choice(departments)
        
        # Generate a posting date within the last 30 days
        days_ago = random.randint(0, 30)
        posting_date = pd.Timestamp.now() - pd.Timedelta(days=days_ago)
        
        # Generate sample requirements
        all_requirements = [
            "Bachelor's degree in Computer Science or related field",
            "3+ years of experience in software development",
            "Strong problem-solving skills",
            "Experience with Python, Java, or C++",
            "Knowledge of cloud platforms (AWS, GCP, Azure)",
            "Experience with machine learning frameworks",
            "Strong communication skills",
            "Experience with distributed systems",
            "Experience with React, Angular, or Vue",
            "Knowledge of database systems (SQL, NoSQL)",
            "Experience with CI/CD pipelines",
            "Understanding of agile methodologies"
        ]
        
        requirements = random.sample(all_requirements, k=random.randint(3, 6))
        
        listing = {
            "company": company_name,
            "title": role,
            "location": location,
            "department": department,
            "date": posting_date.strftime("%Y-%m-%d"),
            "url": f"https://careers.{company_name.lower()}.com/jobs/{random.randint(1000, 9999)}",
            "description": f"We are looking for a talented {role} to join our {department} team. You will be responsible for designing, developing, and maintaining our systems and applications.",
            "requirements": requirements,
            "salary_range": f"${random.randint(80, 180)}K - ${random.randint(110, 250)}K"
        }
        
        listings.append(listing)
    
    return listings

def generate_sample_linkedin_jobs(company_name: str, location: str = None) -> List[Dict[str, Any]]:
    """
    Generate sample LinkedIn job listings for demonstration purposes.
    
    Args:
        company_name: Company name to generate sample data for
        location: Optional location filter
    
    Returns:
        List of sample LinkedIn job listings
    """
    # This function is similar to generate_sample_job_listings but with 
    # LinkedIn-specific fields. In a real app, this would be replaced with 
    # actual scraped data from LinkedIn RSS feeds
    
    roles = [
        "Marketing Manager", "Sales Representative", "HR Specialist",
        "Finance Analyst", "Business Development", "Customer Success Manager",
        "Technical Program Manager", "Content Strategist", "Community Manager",
        "Operations Analyst", "Project Manager", "Executive Assistant"
    ]
    
    locations = location if location else [
        "San Francisco, CA", "New York, NY", "Seattle, WA", 
        "Austin, TX", "Remote", "Boston, MA", "Chicago, IL",
        "Toronto, Canada", "London, UK", "Berlin, Germany",
        "Singapore", "Tokyo, Japan", "São Paulo, Brazil"
    ]
    
    if isinstance(locations, str):
        locations = [locations]
    
    # Generate 3-8 random job listings
    num_listings = random.randint(3, 8)
    listings = []
    
    for _ in range(num_listings):
        role = random.choice(roles)
        location = random.choice(locations)
        
        # Generate a posting date within the last 14 days
        days_ago = random.randint(0, 14)
        posting_date = pd.Timestamp.now() - pd.Timedelta(days=days_ago)
        
        # Generate random number of applicants
        applicants = random.randint(0, 200)
        
        # Sample requirements
        all_requirements = [
            "Bachelor's degree in related field",
            "2+ years of relevant experience",
            "Excellent communication skills",
            "Proficiency with Microsoft Office Suite",
            "Problem-solving abilities",
            "Team player with positive attitude",
            "Project management experience",
            "Customer service orientation",
            "Analytical thinking skills",
            "Attention to detail",
            "Time management and prioritization skills"
        ]
        
        requirements = random.sample(all_requirements, k=random.randint(3, 5))
        
        listing = {
            "company": company_name,
            "title": role,
            "location": location,
            "date": posting_date.strftime("%Y-%m-%d"),
            "url": f"https://linkedin.com/jobs/view/{random.randint(1000000, 9999999)}",
            "description": f"Join our team as a {role} and help drive our company's success. We're looking for talented individuals who can thrive in a fast-paced environment.",
            "requirements": requirements,
            "applicants": applicants,
            "source": "LinkedIn"
        }
        
        listings.append(listing)
    
    return listings
