import re
import pandas as pd
from typing import Dict, List, Any, Tuple

def extract_resume_content(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured content from a resume text.
    
    Args:
        resume_text: Plain text of the resume
    
    Returns:
        Dictionary with structured resume information
    """
    # Basic structure to hold resume data
    resume_data = {
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "contact_info": {},
        "summary": ""
    }
    
    # Extract skills (enhanced approach with more comprehensive patterns)
    # In a production app, you would use NLP or a predefined skill taxonomy
    skills_patterns = [
        # Programming languages
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|R|Scala|Perl|Shell|Bash|PowerShell|Haskell|Clojure|Groovy|Fortran|COBOL|Assembly|Visual Basic|Objective-C|Dart|Julia)\b',
        
        # Frameworks and libraries
        r'\b(React|Angular|Vue\.js|Django|Flask|Express|Spring|TensorFlow|PyTorch|Pandas|NumPy|SciPy|Scikit-learn|Keras|Matplotlib|Seaborn|jQuery|Bootstrap|Tailwind|Semantic UI|Material UI|Next\.js|Gatsby|Svelte|D3\.js|Ember\.js|Meteor|Backbone\.js|FastAPI|Pyramid|Falcon|NestJS|GraphQL|Apollo|Redux|MobX|RxJS|Socket\.io|Enzyme|Jest|Mocha|Chai|Cypress|Selenium|Puppeteer|Beautiful Soup|Playwright)\b',
        
        # Databases and data storage
        r'\b(SQL|MySQL|PostgreSQL|MongoDB|Firebase|Redis|Elasticsearch|Oracle|DynamoDB|Cassandra|Neo4j|MariaDB|SQLite|CouchDB|InfluxDB|Supabase|Snowflake|BigQuery|Redshift|Teradata|Couchbase|RavenDB|ArangoDB|SQLAlchemy|Sequelize|Prisma|TypeORM|Mongoose|Hibernate|JDBC|Realm|Firestore)\b',
        
        # Cloud and DevOps
        r'\b(AWS|Azure|GCP|Google Cloud|Oracle Cloud|IBM Cloud|Linode|DigitalOcean|Heroku|Netlify|Vercel|Docker|Kubernetes|CI/CD|Jenkins|GitHub Actions|CircleCI|Travis CI|GitLab CI|TeamCity|Ansible|Puppet|Chef|Terraform|Pulumi|CloudFormation|Serverless|Lambda|ECS|EKS|S3|EC2|RDS|CloudFront|Route53|IAM|Prometheus|Grafana|ELK Stack|Datadog|New Relic|PagerDuty|Sentry)\b',
        
        # Data and ML
        r'\b(Machine Learning|Deep Learning|NLP|Natural Language Processing|Computer Vision|Data Science|Data Analysis|Data Engineering|Big Data|Data Mining|Statistical Analysis|Predictive Modeling|Regression|Classification|Clustering|Data Visualization|ETL|Data Warehousing|OLAP|Business Intelligence|Power BI|Tableau|Looker|Qlik|Apache Spark|Hadoop|Databricks|Airflow|Luigi|Prefect|Kubeflow|MLOps|A/B Testing|Reinforcement Learning|Time Series Analysis|Anomaly Detection|Feature Engineering|Dimensionality Reduction|Neural Networks|CNN|RNN|LSTM|GAN|Transformer|BERT|GPT|Word2Vec|Sentiment Analysis|Text Mining)\b',
        
        # Software development
        r'\b(Object-Oriented Programming|OOP|Functional Programming|Test-Driven Development|TDD|Behavior-Driven Development|BDD|Agile|Scrum|Kanban|Lean|SAFe|Pair Programming|Code Review|Version Control|Git|Mercurial|SVN|Continuous Integration|Continuous Deployment|Microservices|Monolithic|Serverless|API|REST|SOAP|GraphQL|gRPC|WebSockets|Authentication|OAuth|JWT|SAML|Design Patterns|MVC|MVVM|SOLID|DRY|Code Refactoring|Legacy Code Maintenance|Technical Debt Management)\b',
        
        # Front-end technologies
        r'\b(HTML|CSS|DOM|AJAX|JSON|XML|SASS|SCSS|Less|Stylus|Webpack|Rollup|Vite|Parcel|Babel|Gulp|Grunt|BEM|Web Components|Progressive Web Apps|PWA|Service Workers|SEO|Responsive Design|Cross-Browser Compatibility|Mobile-First Design|Accessibility|WCAG|ARIA|Internationalization|i18n|Localization|l10n|WebGL|Canvas|SVG|Animation|Transitions)\b',
        
        # Mobile development
        r'\b(Android|iOS|React Native|Flutter|Xamarin|Ionic|Swift|SwiftUI|Kotlin|Jetpack Compose|Objective-C|Mobile UI/UX|App Store Optimization|ASO|Mobile Analytics|Push Notifications|Mobile Security|Offline Functionality|In-App Purchases|Deep Linking|App Performance Optimization|Universal Links|App Clips|Widgets)\b',
        
        # DevSecOps and security
        r'\b(Security|Encryption|Authentication|Authorization|OWASP|Penetration Testing|Vulnerability Assessment|Security Auditing|Compliance|GDPR|HIPAA|SOC 2|ISO 27001|PCI DSS|Network Security|Web Application Firewall|WAF|DDoS Protection|Intrusion Detection|Intrusion Prevention|Security Information and Event Management|SIEM|Identity and Access Management|IAM|Single Sign-On|SSO|Multi-Factor Authentication|MFA|Key Management|Secret Management|HashiCorp Vault|Certificate Management|PKI|Security Automation)\b',
        
        # Project management and tools
        r'\b(Project Management|Program Management|Product Management|Agile Methodologies|Scrum Master|Product Owner|JIRA|Confluence|Trello|Asana|Monday\.com|ClickUp|Notion|Basecamp|Microsoft Project|Smartsheet|Gantt Charts|Critical Path Method|CPM|Resource Allocation|Risk Management|Stakeholder Management|Project Planning|Project Scheduling|Project Budgeting|Scope Management|Change Management|Vendor Management|Contract Negotiation|Project Documentation|Requirements Gathering|User Stories|Acceptance Criteria|Sprint Planning|Retrospectives|Daily Stand-ups|Release Management|Feature Prioritization|Roadmapping|OKRs|KPIs)\b',
        
        # Soft skills
        r'\b(Leadership|Communication|Teamwork|Problem Solving|Critical Thinking|Analytical Skills|Decision Making|Time Management|Prioritization|Adaptability|Flexibility|Creativity|Innovation|Collaboration|Interpersonal Skills|Conflict Resolution|Negotiation|Presentation Skills|Public Speaking|Customer Service|Client Management|Relationship Building|Mentoring|Coaching|Emotional Intelligence|EQ|Self-motivation|Perseverance|Attention to Detail|Organization|Strategic Thinking|Business Acumen|Cultural Awareness|Cross-functional Collaboration|Remote Work|Virtual Collaboration|Active Listening|Feedback|Constructive Criticism)\b',
    ]
    
    # Extract contact information
    # Look for email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    if email_match:
        resume_data["contact_info"]["email"] = email_match.group(0)
    
    # Look for phone number
    phone_match = re.search(r'(\+\d{1,3}[-\.\s]?)?(\d{3}[-\.\s]?)?\d{3}[-\.\s]?\d{4}', resume_text)
    if phone_match:
        resume_data["contact_info"]["phone"] = phone_match.group(0)
    
    # Look for LinkedIn profile
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', resume_text)
    if linkedin_match:
        resume_data["contact_info"]["linkedin"] = f"https://www.{linkedin_match.group(0)}"
    
    # Extract summary - first paragraph that's not a contact info
    lines = resume_text.split('\n')
    for i, line in enumerate(lines):
        if i > 2 and len(line.strip()) > 50 and "SKILLS" not in line.upper() and "EXPERIENCE" not in line.upper():
            resume_data["summary"] = line.strip()
            break
    
    # Find skills in resume
    for pattern in skills_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            if match.lower() not in [s.lower() for s in resume_data["skills"]]:
                resume_data["skills"].append(match)
    
    # Additional skill extraction from lists and bullets
    bullet_skills = re.findall(r'[•\-\*]\s*([A-Za-z0-9][\w\s\-\/\&\+\#\.]+)', resume_text)
    for skill in bullet_skills:
        skill = skill.strip()
        if len(skill) > 3 and len(skill) < 30 and skill.lower() not in [s.lower() for s in resume_data["skills"]]:
            # Check if it's likely a skill and not part of a sentence
            if not any(word in skill.lower() for word in ["and", "the", "with", "for", "to", "in", "on"]):
                resume_data["skills"].append(skill)
    
    # Extract education (simplified approach)
    education_patterns = [
        r'(Bachelor|BS|B\.S\.|B\.A\.|BA|Master|MS|M\.S\.|M\.A\.|MA|PhD|Ph\.D\.|Doctorate|Associates|Certificate)'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            if match not in resume_data["education"]:
                resume_data["education"].append(match)
    
    return resume_data

def match_resume_to_job_skills(resume_data: Dict[str, Any], job_skills: List[str]) -> Dict[str, Any]:
    """
    Match resume skills to job requirements and calculate match percentage.
    Enhanced with advanced partial matching and weighted scoring.
    
    Args:
        resume_data: Structured resume data
        job_skills: List of skills required for the job
    
    Returns:
        Dictionary with match information
    """
    resume_skills = [skill.lower() for skill in resume_data["skills"]]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    # Find matching skills with exact and partial matching
    matching_skills = []
    partial_matching_skills = []
    missing_skills = []
    
    # Dictionary to track skill importance (based on position in the requirements list)
    skill_weights = {}
    for i, skill in enumerate(job_skills_lower):
        # Skills mentioned first are typically more important
        weight = 1.0 - (i / (2 * len(job_skills_lower))) if len(job_skills_lower) > 0 else 1.0
        skill_weights[skill] = max(0.5, weight)  # Minimum weight of 0.5
    
    for job_skill in job_skills_lower:
        if any(job_skill == rs for rs in resume_skills):
            # Exact match
            matching_skills.append(job_skill)
        elif any(job_skill in rs or rs in job_skill for rs in resume_skills):
            # Partial match (e.g., "Python" matches "Python Programming")
            partial_matching_skills.append(job_skill)
        else:
            missing_skills.append(job_skill)
    
    # Calculate match percentage with weighted scoring
    match_score = 0
    total_weight = sum(skill_weights.values())
    
    # Full matches get full weight
    for skill in matching_skills:
        match_score += skill_weights.get(skill, 0.75)
    
    # Partial matches get half weight
    for skill in partial_matching_skills:
        match_score += skill_weights.get(skill, 0.5) * 0.5
    
    # Calculate percentage
    match_percentage = 0
    if total_weight > 0:
        match_percentage = (match_score / total_weight) * 100
    
    # Additional metadata about the match
    skill_coverage = {
        "exact_match_count": len(matching_skills),
        "partial_match_count": len(partial_matching_skills),
        "missing_count": len(missing_skills),
        "total_required": len(job_skills),
        "total_resume": len(resume_data["skills"]),
        "skill_match_ratio": f"{(len(matching_skills) + len(partial_matching_skills) * 0.5):.1f}/{len(job_skills)}"
    }
    
    return {
        "matching_skills": matching_skills,
        "partial_matching_skills": partial_matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
        "skill_coverage": skill_coverage
    }

def analyze_resume_vs_company_jobs(resume_data: Dict[str, Any], company_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze resume against all jobs for a company and return matches.
    Enhanced with partial matching and skill coverage metrics.
    
    Args:
        resume_data: Structured resume data
        company_jobs: List of job listings for a company
    
    Returns:
        List of job matches with match percentage and details
    """
    job_matches = []
    
    for job in company_jobs:
        # Extract skills from job requirements
        job_skills = job.get("requirements", [])
        
        # Match resume to job
        match_info = match_resume_to_job_skills(resume_data, job_skills)
        
        # Calculate match quality metrics
        match_quality = "Excellent" if match_info["match_percentage"] >= 85 else (
            "Good" if match_info["match_percentage"] >= 70 else (
            "Fair" if match_info["match_percentage"] >= 50 else "Poor"
        ))
        
        # Add salary range when available
        salary_range = job.get("salary_range", "")
        
        job_matches.append({
            "job_title": job.get("title", ""),
            "job_location": job.get("location", ""),
            "job_department": job.get("department", ""),
            "match_percentage": match_info["match_percentage"],
            "match_quality": match_quality,
            "matching_skills": match_info["matching_skills"],
            "partial_matching_skills": match_info.get("partial_matching_skills", []),
            "missing_skills": match_info["missing_skills"],
            "skill_coverage": match_info.get("skill_coverage", {}),
            "posted_date": job.get("posted_date", ""),
            "salary_range": salary_range
        })
    
    # Sort by match percentage (highest first)
    job_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return job_matches

def generate_resume_insights(resume_data: Dict[str, Any], job_matches: List[Dict[str, Any]]) -> List[str]:
    """
    Generate comprehensive career insights based on resume analysis and job matches.
    Enhanced with detailed analysis and personalized recommendations.
    
    Args:
        resume_data: Structured resume data
        job_matches: List of job matches with details
    
    Returns:
        List of insight strings
    """
    insights = []
    
    # Analyze skill gaps and opportunities
    if not job_matches:
        insights.append("Add companies to your watchlist to see how your resume matches with their job requirements.")
        return insights
        
    # Get the top match
    top_match = job_matches[0]
    
    # Match quality insights
    if top_match["match_percentage"] >= 85:
        insights.append(f"🌟 Your profile is an excellent match for {top_match['job_title']} roles with a {top_match['match_percentage']:.1f}% match rate.")
    elif top_match["match_percentage"] >= 70:
        insights.append(f"👍 Your profile is a good match for {top_match['job_title']} roles with a {top_match['match_percentage']:.1f}% match rate.")
    elif top_match["match_percentage"] >= 50:
        insights.append(f"📊 Your profile shows potential for {top_match['job_title']} roles with a {top_match['match_percentage']:.1f}% match rate.")
    else:
        insights.append(f"⚠️ Your profile may need significant development for {top_match['job_title']} roles with only a {top_match['match_percentage']:.1f}% match rate.")
    
    # Skill gap insights
    if "missing_skills" in top_match and top_match["missing_skills"]:
        critical_skills = top_match["missing_skills"][:3]
        missing_skills_str = ", ".join(critical_skills)
        insights.append(f"🎯 Skill Development: Focus on learning {missing_skills_str} to improve match for top roles.")
        
        # Suggest learning resources based on missing skills (simulated)
        if any(skill.lower() in ["python", "javascript", "react", "aws", "machine learning"] for skill in critical_skills):
            insights.append(f"📚 Learning Path: Consider online courses or certifications in {missing_skills_str} to enhance your qualifications.")
    
    # Partial skills insight
    if "partial_matching_skills" in top_match and top_match["partial_matching_skills"]:
        partial_skills = top_match["partial_matching_skills"][:3]
        partial_skills_str = ", ".join(partial_skills)
        insights.append(f"💡 You show potential in {partial_skills_str} - consider strengthening these areas for better job matches.")
    
    # Department & industry insights
    departments = [job["job_department"] for job in job_matches if job["match_percentage"] > 60]
    if departments:
        from collections import Counter
        department_count = Counter(departments)
        top_department = department_count.most_common(1)[0][0]
        insights.append(f"🏢 Department Alignment: Your skills align well with roles in the {top_department} department.")
    
    # Geographic insights
    locations = [job["job_location"] for job in job_matches if job["match_percentage"] > 60]
    if locations:
        from collections import Counter
        location_count = Counter(locations)
        top_locations = [loc for loc, _ in location_count.most_common(2)]
        if len(top_locations) > 1:
            insights.append(f"🌎 Location Opportunities: Your skills are in demand in {top_locations[0]} and {top_locations[1]}.")
        elif len(top_locations) == 1:
            insights.append(f"🌎 Location Opportunity: Your skills are particularly in demand in {top_locations[0]}.")
            
    # Experience level insight (simulated)
    experience_level = "Mid-Senior" if len(resume_data["skills"]) > 10 else "Entry-Mid"
    insights.append(f"📈 Career Stage: Your resume reflects a {experience_level} level professional profile.")
    
    # Salary potential (when available)
    has_salary = False
    for job in job_matches[:3]:
        if job.get("salary_range"):
            has_salary = True
            insights.append(f"💰 Salary Potential: Top matching positions like {job['job_title']} typically offer {job['salary_range']}.")
            break
            
    if not has_salary and top_match["match_percentage"] > 70:
        insights.append("💰 Salary Research: Consider researching salary ranges for your top matching positions to set appropriate expectations.")
    
    return insights

def get_career_opportunity_score(job_matches: List[Dict[str, Any]]) -> float:
    """
    Calculate an overall opportunity score based on job matches.
    
    Args:
        job_matches: List of job matches with details
    
    Returns:
        Opportunity score from 0-100
    """
    if not job_matches:
        return 0
    
    # Average of top 3 matches, weighted by match percentage
    top_matches = job_matches[:3] if len(job_matches) >= 3 else job_matches
    total_score = sum(match["match_percentage"] for match in top_matches)
    
    return total_score / len(top_matches)