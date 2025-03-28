import sqlite3
import pandas as pd
import json
import logging
import os
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = "hiring_intelligence.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database, creating it if it doesn't exist.
    
    Returns:
        SQLite connection object
    """
    # Make sure we're connecting to a file in the current directory
    db_path = os.path.join(os.getcwd(), DB_FILE)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    
    # Initialize the database schema if it doesn't exist
    initialize_db(conn)
    
    return conn

def initialize_db(conn: sqlite3.Connection):
    """
    Initialize the database schema if tables don't exist.
    
    Args:
        conn: SQLite connection object
    """
    cursor = conn.cursor()
    
    # Create watched_companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watched_companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create job_listings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        title TEXT,
        location TEXT,
        department TEXT,
        description TEXT,
        requirements TEXT,  -- Stored as JSON
        salary_range TEXT,
        url TEXT,
        posted_date DATE,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES watched_companies (id)
    )
    ''')
    
    # Create insights table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        data TEXT,  -- Stored as JSON
        insight_text TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create user_settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT UNIQUE,
        setting_value TEXT
    )
    ''')
    
    conn.commit()

def save_company_to_watch(company_name: str) -> bool:
    """
    Add a company to the watchlist.
    
    Args:
        company_name: Name of the company to watch
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO watched_companies (name) VALUES (?)", (company_name,))
        conn.commit()
        
        # Check if the insert was successful
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    except Exception as e:
        logger.error(f"Error saving company to watch: {str(e)}")
        return False

def get_watched_companies() -> List[str]:
    """
    Get the list of companies being watched.
    
    Returns:
        List of company names
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM watched_companies ORDER BY name")
        companies = [row["name"] for row in cursor.fetchall()]
        
        conn.close()
        return companies
    
    except Exception as e:
        logger.error(f"Error getting watched companies: {str(e)}")
        return []

def delete_company_from_watchlist(company_name: str) -> bool:
    """
    Remove a company from the watchlist.
    
    Args:
        company_name: Name of the company to remove
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the company ID
        cursor.execute("SELECT id FROM watched_companies WHERE name = ?", (company_name,))
        result = cursor.fetchone()
        
        if result:
            company_id = result["id"]
            
            # Delete related job listings
            cursor.execute("DELETE FROM job_listings WHERE company_id = ?", (company_id,))
            
            # Delete the company
            cursor.execute("DELETE FROM watched_companies WHERE id = ?", (company_id,))
            
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    except Exception as e:
        logger.error(f"Error deleting company from watchlist: {str(e)}")
        return False

def save_job_listings(company_name: str, job_listings: List[Dict[str, Any]]) -> bool:
    """
    Save job listings for a company to the database.
    
    Args:
        company_name: Name of the company
        job_listings: List of job listing dictionaries
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get company ID
        cursor.execute("SELECT id FROM watched_companies WHERE name = ?", (company_name,))
        result = cursor.fetchone()
        
        if not result:
            # Company doesn't exist, add it
            cursor.execute("INSERT INTO watched_companies (name) VALUES (?)", (company_name,))
            company_id = cursor.lastrowid
        else:
            company_id = result["id"]
        
        # Insert job listings
        for job in job_listings:
            # Convert requirements list to JSON string
            requirements_json = json.dumps(job.get("requirements", []))
            
            cursor.execute('''
            INSERT INTO job_listings 
            (company_id, title, location, department, description, requirements, salary_range, url, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_id,
                job.get("title", ""),
                job.get("location", ""),
                job.get("department", ""),
                job.get("description", ""),
                requirements_json,
                job.get("salary_range", ""),
                job.get("url", ""),
                job.get("date", "")
            ))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error saving job listings: {str(e)}")
        return False

def get_job_listings(company_name: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get job listings from the database, optionally filtered by company.
    
    Args:
        company_name: Optional company name to filter by
        days: Number of days of data to retrieve
    
    Returns:
        List of job listing dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT 
            wc.name as company,
            jl.title,
            jl.location,
            jl.department,
            jl.description,
            jl.requirements,
            jl.salary_range,
            jl.url,
            jl.posted_date as date
        FROM 
            job_listings jl
        JOIN 
            watched_companies wc ON jl.company_id = wc.id
        WHERE 
            jl.posted_date >= date('now', ?)
        '''
        
        params = [f'-{days} days']
        
        if company_name:
            query += " AND wc.name = ?"
            params.append(company_name)
        
        cursor.execute(query, params)
        
        job_listings = []
        for row in cursor.fetchall():
            job_dict = dict(row)
            
            # Convert JSON string back to list
            try:
                job_dict["requirements"] = json.loads(job_dict["requirements"])
            except:
                job_dict["requirements"] = []
            
            job_listings.append(job_dict)
        
        conn.close()
        return job_listings
    
    except Exception as e:
        logger.error(f"Error getting job listings: {str(e)}")
        return []

def save_insight(insight_type: str, insight_text: str, data: Dict[str, Any]) -> bool:
    """
    Save an insight to the database.
    
    Args:
        insight_type: Type of insight
        insight_text: Text description of the insight
        data: Dictionary of additional data about the insight
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        data_json = json.dumps(data)
        
        cursor.execute('''
        INSERT INTO insights (type, insight_text, data)
        VALUES (?, ?, ?)
        ''', (insight_type, insight_text, data_json))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error saving insight: {str(e)}")
        return False

def get_insights(insight_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get insights from the database, optionally filtered by type.
    
    Args:
        insight_type: Optional type to filter by
        limit: Maximum number of insights to retrieve
    
    Returns:
        List of insight dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM insights"
        params = []
        
        if insight_type:
            query += " WHERE type = ?"
            params.append(insight_type)
        
        query += " ORDER BY generated_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        insights = []
        for row in cursor.fetchall():
            insight_dict = dict(row)
            
            # Convert JSON string back to dictionary
            try:
                insight_dict["data"] = json.loads(insight_dict["data"])
            except:
                insight_dict["data"] = {}
            
            insights.append(insight_dict)
        
        conn.close()
        return insights
    
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        return []

def save_user_setting(setting_name: str, setting_value: Any) -> bool:
    """
    Save a user setting to the database.
    
    Args:
        setting_name: Name of the setting
        setting_value: Value of the setting (will be converted to JSON)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert value to JSON string
        if not isinstance(setting_value, str):
            setting_value = json.dumps(setting_value)
        
        cursor.execute('''
        INSERT OR REPLACE INTO user_settings (setting_name, setting_value)
        VALUES (?, ?)
        ''', (setting_name, setting_value))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error saving user setting: {str(e)}")
        return False

def get_user_setting(setting_name: str, default_value: Any = None) -> Any:
    """
    Get a user setting from the database.
    
    Args:
        setting_name: Name of the setting to retrieve
        default_value: Value to return if setting doesn't exist
    
    Returns:
        Setting value, or default value if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_value FROM user_settings WHERE setting_name = ?", (setting_name,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            setting_value = result["setting_value"]
            
            # Try to parse as JSON
            try:
                return json.loads(setting_value)
            except:
                return setting_value
        else:
            return default_value
    
    except Exception as e:
        logger.error(f"Error getting user setting: {str(e)}")
        return default_value
