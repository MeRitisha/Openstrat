import pandas as pd
import numpy as np
import random
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_demo_data() -> Dict[str, Any]:
    """
    Generate demonstration data for the application.
    This is used only for development and demonstration purposes.
    
    Returns:
        Dictionary containing various demo datasets
    """
    logger.info("Generating demo data")
    
    # Sample companies
    companies = ["Google", "Microsoft", "Amazon", "Shopify", "Apple"]
    
    # Sample dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate hiring velocity data (time series)
    hiring_velocity = []
    for date in dates:
        entry = {"date": date}
        for company in companies:
            # Generate a trend with some randomness
            base_value = 10 if company in ["Google", "Amazon"] else 5
            if company == "Shopify" and date > (end_date - timedelta(days=10)).strftime('%Y-%m-%d'):
                # Create a surge for Shopify in the last 10 days
                base_value = 15
                
            entry[company] = max(0, round(base_value + np.random.normal(0, 2)))
        hiring_velocity.append(entry)
    
    # Generate skill demand data (heatmap)
    skills = [
        "Python", "JavaScript", "React", "AWS", "Machine Learning",
        "Data Science", "Cloud", "DevOps", "Product Management", "UX/UI",
        "Mobile", "Kubernetes", "AI", "Blockchain", "Security"
    ]
    
    skill_demand = []
    for skill in skills:
        for company in companies:
            # Different companies have different skill focuses
            base_value = 0
            if skill == "Machine Learning" and company in ["Google", "Microsoft"]:
                base_value = 12
            elif skill == "Cloud" and company in ["Amazon", "Microsoft"]:
                base_value = 10
            elif skill == "React" and company in ["Shopify", "Facebook"]:
                base_value = 8
            elif skill == "Python" and company in ["Google", "Amazon"]:
                base_value = 9
            elif skill == "Mobile" and company in ["Apple", "Google"]:
                base_value = 7
            else:
                base_value = 3
                
            count = max(0, round(base_value + np.random.normal(0, 1)))
            
            if count > 0:
                skill_demand.append({
                    "skill": skill,
                    "company": company,
                    "count": count
                })
    
    # Generate geographic distribution data
    locations = [
        "San Francisco", "New York", "Seattle", "Austin", "Remote",
        "London", "Toronto", "Berlin", "Singapore", "Tokyo", "São Paulo"
    ]
    
    geo_distribution = []
    for location in locations:
        entry = {"location": location}
        for company in companies:
            # Different companies have different geographic focuses
            base_value = 0
            if location == "San Francisco" and company in ["Google", "Apple"]:
                base_value = 8
            elif location == "Seattle" and company in ["Amazon", "Microsoft"]:
                base_value = 10
            elif location == "Remote" and company in ["Shopify"]:
                base_value = 12
            elif location == "London" and company in ["Google", "Amazon"]:
                base_value = 5
            elif location == "New York" and company in ["Apple", "Microsoft"]:
                base_value = 6
            elif location == "São Paulo" and company in ["Amazon"]:
                base_value = 4
            else:
                base_value = 2
                
            count = max(0, round(base_value + np.random.normal(0, 1)))
            entry[company] = count
        geo_distribution.append(entry)
    
    # Generate company-specific data
    company_specific = {
        "Google": {
            "active_jobs": 125,
            "jobs_delta": "+15",
            "velocity": 22,
            "velocity_delta": +7,
            "new_roles": 8,
            "roles_delta": +3,
            "roles": {
                "Software Engineer": 45,
                "Data Scientist": 20,
                "Product Manager": 15,
                "UX Designer": 10,
                "AI Research Scientist": 25,
                "Cloud Engineer": 10
            },
            "recent_jobs": [
                {
                    "title": "AI Research Scientist",
                    "location": "Mountain View, CA",
                    "date": "2023-05-02",
                    "department": "Research",
                    "description": "Join Google's AI research team to advance the state of the art in artificial intelligence and machine learning.",
                    "requirements": [
                        "PhD in Computer Science, Machine Learning, or related field",
                        "Strong publication record in top-tier ML conferences",
                        "Experience with deep learning frameworks",
                        "Excellent programming skills in Python"
                    ]
                },
                {
                    "title": "Senior Software Engineer, ML",
                    "location": "Seattle, WA",
                    "date": "2023-05-01",
                    "department": "Engineering",
                    "description": "Design and implement machine learning systems that power Google's core products.",
                    "requirements": [
                        "Bachelor's degree in Computer Science or related field",
                        "5+ years of software engineering experience",
                        "Experience with ML frameworks like TensorFlow or PyTorch",
                        "Strong problem-solving skills"
                    ]
                },
                {
                    "title": "Product Manager, Search",
                    "location": "Remote",
                    "date": "2023-04-30",
                    "department": "Product",
                    "description": "Lead the product strategy and execution for key Google Search features.",
                    "requirements": [
                        "Bachelor's degree in Computer Science, Engineering, or related field",
                        "3+ years of product management experience",
                        "Strong analytical skills",
                        "Excellent communication and leadership abilities"
                    ]
                }
            ],
            "insights": [
                {
                    "type": "info",
                    "text": "Google has increased hiring for AI research roles by 35% in the past month, indicating a strategic focus on advanced AI capabilities."
                },
                {
                    "type": "success",
                    "text": "25% of new job postings are remote-friendly, showing an evolving stance on distributed work."
                },
                {
                    "type": "warning",
                    "text": "Multiple senior product leadership roles have been posted, suggesting potential new product initiatives or reorganization."
                }
            ]
        },
        "Microsoft": {
            "active_jobs": 110,
            "jobs_delta": "+8",
            "velocity": 15,
            "velocity_delta": +2,
            "new_roles": 6,
            "roles_delta": +1,
            "roles": {
                "Software Engineer": 40,
                "Cloud Solutions Architect": 25,
                "Product Manager": 15,
                "Data Engineer": 10,
                "Security Engineer": 10,
                "UX Designer": 10
            },
            "recent_jobs": [
                {
                    "title": "Principal Cloud Architect",
                    "location": "Redmond, WA",
                    "date": "2023-05-03",
                    "department": "Azure",
                    "description": "Design and implement cloud architecture solutions for Microsoft Azure enterprise customers.",
                    "requirements": [
                        "Bachelor's degree in Computer Science or related field",
                        "7+ years of experience with cloud platforms",
                        "Strong knowledge of Azure services",
                        "Experience with distributed systems"
                    ]
                },
                {
                    "title": "Senior Security Engineer",
                    "location": "Remote",
                    "date": "2023-05-02",
                    "department": "Security",
                    "description": "Develop and implement security solutions to protect Microsoft's cloud infrastructure and services.",
                    "requirements": [
                        "Bachelor's degree in Computer Science, Cybersecurity, or related field",
                        "5+ years of experience in security engineering",
                        "Knowledge of security frameworks and compliance requirements",
                        "Experience with threat modeling and incident response"
                    ]
                },
                {
                    "title": "Product Manager, Teams",
                    "location": "San Francisco, CA",
                    "date": "2023-04-29",
                    "department": "Product",
                    "description": "Lead the product strategy and roadmap for Microsoft Teams collaboration features.",
                    "requirements": [
                        "Bachelor's degree in Business, Computer Science, or related field",
                        "4+ years of product management experience",
                        "Experience with collaboration or productivity software",
                        "Strong customer empathy and analytical skills"
                    ]
                }
            ],
            "insights": [
                {
                    "type": "info",
                    "text": "Microsoft is significantly increasing hiring for cloud security roles, with a 40% increase in the past quarter."
                },
                {
                    "type": "warning",
                    "text": "Several new AI integration roles have been created across multiple product teams, suggesting a company-wide AI strategy shift."
                },
                {
                    "type": "success",
                    "text": "30% of new positions are in emerging markets, indicating global expansion priorities."
                }
            ]
        },
        "Amazon": {
            "active_jobs": 150,
            "jobs_delta": "+22",
            "velocity": 28,
            "velocity_delta": +10,
            "new_roles": 12,
            "roles_delta": +5,
            "roles": {
                "Software Development Engineer": 50,
                "Solutions Architect": 20,
                "Operations Manager": 25,
                "Data Scientist": 15,
                "Product Manager": 20,
                "Research Scientist": 10,
                "UX Designer": 10
            },
            "recent_jobs": [
                {
                    "title": "Senior SDE, AWS",
                    "location": "Seattle, WA",
                    "date": "2023-05-04",
                    "department": "AWS",
                    "description": "Design and implement scalable cloud services for Amazon Web Services.",
                    "requirements": [
                        "Bachelor's degree in Computer Science or related field",
                        "5+ years of software development experience",
                        "Experience with distributed systems",
                        "Strong coding skills in Java, Python, or C++"
                    ]
                },
                {
                    "title": "Applied Scientist, Personalization",
                    "location": "New York, NY",
                    "date": "2023-05-03",
                    "department": "Science",
                    "description": "Develop machine learning models to improve Amazon's personalization systems.",
                    "requirements": [
                        "PhD or MS in Computer Science, Machine Learning, or related field",
                        "Experience with recommendation systems",
                        "Strong programming skills in Python",
                        "Publications in top-tier ML conferences a plus"
                    ]
                },
                {
                    "title": "Technical Program Manager, Supply Chain",
                    "location": "San Francisco, CA",
                    "date": "2023-05-01",
                    "department": "Operations",
                    "description": "Lead technical programs to optimize Amazon's supply chain operations.",
                    "requirements": [
                        "Bachelor's degree in Engineering, Computer Science, or related field",
                        "4+ years of technical program management experience",
                        "Experience with supply chain or logistics operations",
                        "Strong project management and leadership skills"
                    ]
                }
            ],
            "insights": [
                {
                    "type": "warning",
                    "text": "Amazon has doubled AWS security hiring in the past month, suggesting potential new security features or concerns."
                },
                {
                    "type": "info",
                    "text": "Multiple new logistics and supply chain optimization roles have been created, indicating investments in delivery infrastructure."
                },
                {
                    "type": "success",
                    "text": "Significant increase in hiring for the Amazon Business B2B platform, suggesting strategic growth in this area."
                }
            ]
        },
        "Shopify": {
            "active_jobs": 85,
            "jobs_delta": "+18",
            "velocity": 35,
            "velocity_delta": +15,
            "new_roles": 10,
            "roles_delta": +7,
            "roles": {
                "Software Engineer": 30,
                "Product Manager": 15,
                "Data Scientist": 10,
                "UX Researcher": 8,
                "Frontend Developer": 12,
                "Solutions Engineer": 10
            },
            "recent_jobs": [
                {
                    "title": "Senior Frontend Developer",
                    "location": "Remote",
                    "date": "2023-05-04",
                    "department": "Engineering",
                    "description": "Build beautiful, performant, and accessible user interfaces for Shopify's merchant-facing products.",
                    "requirements": [
                        "Experience with modern JavaScript frameworks (React, Vue)",
                        "Strong understanding of web performance",
                        "Knowledge of accessibility standards",
                        "Experience with GraphQL and REST APIs"
                    ]
                },
                {
                    "title": "Data Scientist, Merchant Success",
                    "location": "Toronto, Canada",
                    "date": "2023-05-02",
                    "department": "Data",
                    "description": "Use data analysis and machine learning to help Shopify merchants succeed and grow their businesses.",
                    "requirements": [
                        "Bachelor's or Master's degree in Statistics, Computer Science, or related field",
                        "Experience with Python data science stack",
                        "Strong SQL skills",
                        "Experience with experimental design and causal inference"
                    ]
                },
                {
                    "title": "Senior Product Manager, International Markets",
                    "location": "São Paulo, Brazil",
                    "date": "2023-04-30",
                    "department": "Product",
                    "description": "Lead product strategy and development for Shopify's expansion in Latin American markets.",
                    "requirements": [
                        "5+ years of product management experience",
                        "Experience with e-commerce or fintech products",
                        "Strong understanding of Latin American markets",
                        "Fluency in English and Portuguese or Spanish"
                    ]
                }
            ],
            "insights": [
                {
                    "type": "info",
                    "text": "Shopify has increased hiring for international roles, particularly in Latin America and Southeast Asia."
                },
                {
                    "type": "success",
                    "text": "Surge in hiring for machine learning roles, with emphasis on personalization and fraud prevention."
                },
                {
                    "type": "warning",
                    "text": "Multiple new financial services roles created, indicating expansion of Shopify's payment and financial products."
                }
            ]
        },
        "Apple": {
            "active_jobs": 95,
            "jobs_delta": "+5",
            "velocity": 12,
            "velocity_delta": -3,
            "new_roles": 4,
            "roles_delta": 0,
            "roles": {
                "Software Engineer": 35,
                "Hardware Engineer": 20,
                "Machine Learning Engineer": 15,
                "Product Designer": 10,
                "Product Manager": 5,
                "Operations Manager": 10
            },
            "recent_jobs": [
                {
                    "title": "Machine Learning Engineer, Siri",
                    "location": "Cupertino, CA",
                    "date": "2023-05-03",
                    "department": "AI/ML",
                    "description": "Improve Siri's natural language understanding and generation capabilities through advanced machine learning techniques.",
                    "requirements": [
                        "MS or PhD in Computer Science, Machine Learning, or related field",
                        "Experience with NLP and speech recognition",
                        "Strong programming skills in Python and C++",
                        "Knowledge of deep learning frameworks"
                    ]
                },
                {
                    "title": "Senior Hardware Engineer",
                    "location": "Austin, TX",
                    "date": "2023-05-02",
                    "department": "Hardware",
                    "description": "Design and develop next-generation Apple hardware products.",
                    "requirements": [
                        "Bachelor's or Master's degree in Electrical Engineering or related field",
                        "5+ years of hardware engineering experience",
                        "Experience with product development cycles",
                        "Knowledge of signal integrity and power management"
                    ]
                },
                {
                    "title": "Product Manager, Apple Services",
                    "location": "London, UK",
                    "date": "2023-04-28",
                    "department": "Product",
                    "description": "Lead product strategy and development for Apple's subscription services in European markets.",
                    "requirements": [
                        "Bachelor's degree in Business, Engineering, or related field",
                        "4+ years of product management experience",
                        "Experience with subscription or media products",
                        "Strong understanding of European market dynamics"
                    ]
                }
            ],
            "insights": [
                {
                    "type": "warning",
                    "text": "Apple is significantly increasing hiring for augmented reality roles across hardware and software teams."
                },
                {
                    "type": "info",
                    "text": "Expansion of health-focused hiring, suggesting continued investment in health monitoring capabilities."
                },
                {
                    "type": "success",
                    "text": "New roles focused on privacy and security appearing across multiple product teams."
                }
            ]
        }
    }
    
    # Combine all demo data
    demo_data = {
        "hiring_velocity": hiring_velocity,
        "skill_demand": skill_demand,
        "geo_distribution": geo_distribution,
        "company_specific": company_specific
    }
    
    return demo_data

def parse_date_range(date_range: str) -> tuple:
    """
    Parse a date range string into start and end dates.
    
    Args:
        date_range: String representing a date range (e.g., "Last 7 days", "Last 30 days")
    
    Returns:
        Tuple of (start_date, end_date) as datetime objects
    """
    today = datetime.now()
    
    if date_range == "Last 7 days":
        start_date = today - timedelta(days=7)
    elif date_range == "Last 30 days":
        start_date = today - timedelta(days=30)
    elif date_range == "Last 90 days":
        start_date = today - timedelta(days=90)
    elif date_range == "This year":
        start_date = datetime(today.year, 1, 1)
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
    
    return start_date, today

def format_number(number: float) -> str:
    """
    Format a number for display, using K for thousands.
    
    Args:
        number: Number to format
    
    Returns:
        Formatted number string
    """
    if number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(int(number))

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100
