import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import datetime
import os
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration dictionary for email settings
email_config = {
    "enabled": False,
    "server": "smtp.gmail.com",
    "port": 587,
    "use_tls": True,
    "sender_email": None,  # Will be populated from environment variables
    "sender_password": None,  # Will be populated from environment variables
    "recipient_email": None,  # Will be set via the application
    "frequency": "daily",  # "daily", "weekly", or "significant_changes"
    "alert_threshold": 20,  # percentage change that triggers alert
    "last_sent": None  # Track when the last email was sent
}

def setup_email_preferences(email: str, enabled: bool, frequency: str, alert_threshold: int) -> bool:
    """
    Set up email notification preferences.
    
    Args:
        email: Recipient email address
        enabled: Whether email notifications are enabled
        frequency: Notification frequency ("daily", "weekly", "significant_changes")
        alert_threshold: Percentage change that triggers alert
    
    Returns:
        True if setup was successful, False otherwise
    """
    try:
        # Update global email configuration
        email_config["enabled"] = enabled
        email_config["recipient_email"] = email
        email_config["frequency"] = frequency
        email_config["alert_threshold"] = alert_threshold
        
        # Try to get credentials from environment variables
        email_config["sender_email"] = os.getenv("SENDER_EMAIL", "")
        email_config["sender_password"] = os.getenv("SENDER_PASSWORD", "")
        
        # Validate configuration
        if enabled:
            if not email_config["recipient_email"]:
                logger.error("Email notifications enabled but no recipient email provided")
                return False
            
            if not email_config["sender_email"] or not email_config["sender_password"]:
                logger.warning("Email credentials not configured. Using placeholder for demonstration.")
                # For demonstration purposes only - in a real app, this would fail
                email_config["sender_email"] = "demo@example.com"
                email_config["sender_password"] = "placeholder"
        
        logger.info(f"Email preferences set up successfully for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Error setting up email preferences: {str(e)}")
        return False

def send_email(subject: str, body_html: str, recipient: Optional[str] = None) -> bool:
    """
    Send an email notification.
    
    Args:
        subject: Email subject
        body_html: HTML content of the email
        recipient: Optional recipient email (defaults to configured recipient)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    if not email_config["enabled"]:
        logger.info("Email notifications are disabled")
        return False
    
    if not recipient and not email_config["recipient_email"]:
        logger.error("No recipient email provided")
        return False
    
    recipient_email = recipient or email_config["recipient_email"]
    
    try:
        # Create a multipart message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email_config["sender_email"]
        message["To"] = recipient_email
        
        # Attach HTML part
        html_part = MIMEText(body_html, "html")
        message.attach(html_part)
        
        # For demonstration purposes, log the email instead of sending
        # In a real application, we would connect to SMTP server and send
        logger.info(f"Would send email to {recipient_email} with subject: {subject}")
        logger.info(f"Email body (first 100 chars): {body_html[:100]}...")
        
        # Record the time the email was "sent"
        email_config["last_sent"] = datetime.datetime.now()
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def generate_email_digest(insights: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> str:
    """
    Generate HTML content for an email digest.
    
    Args:
        insights: List of insights from analysis
        recommendations: List of strategic recommendations
    
    Returns:
        HTML content for the email
    """
    try:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #0066cc; }}
                h2 {{ color: #0066cc; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
                .insight {{ margin-bottom: 15px; padding: 10px; border-radius: 5px; }}
                .insight.hiring_surge {{ background-color: #e6f7ff; border-left: 4px solid #0066cc; }}
                .insight.leadership_changes {{ background-color: #fff2e6; border-left: 4px solid #f90; }}
                .insight.technology_focus {{ background-color: #e6ffe6; border-left: 4px solid #090; }}
                .insight.geographic_shift {{ background-color: #f2e6ff; border-left: 4px solid #609; }}
                .recommendation {{ margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }}
                .priority.high {{ color: #c00; font-weight: bold; }}
                .priority.medium {{ color: #f90; font-weight: bold; }}
                .priority.low {{ color: #090; font-weight: bold; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>🔍 Competitive Hiring Intelligence Digest</h1>
            <p>Your daily hiring intelligence report for <strong>{today}</strong></p>
            
            <h2>Key Insights</h2>
        """
        
        if insights:
            # Filter and limit insights to most important ones
            key_insight_types = ["hiring_surge", "leadership_changes", "technology_focus", "geographic_shift"]
            filtered_insights = [i for i in insights if i.get("type") in key_insight_types]
            
            for insight in filtered_insights[:5]:  # Limit to top 5 insights
                insight_type = insight.get("type", "other")
                html += f"""
                <div class="insight {insight_type}">
                    <p>{insight.get("insight", "")}</p>
                </div>
                """
        else:
            html += "<p>No key insights available for this period.</p>"
        
        html += "<h2>Strategic Recommendations</h2>"
        
        if recommendations:
            for recommendation in recommendations[:3]:  # Limit to top 3 recommendations
                priority = recommendation.get("priority", "medium")
                html += f"""
                <div class="recommendation">
                    <p><span class="priority {priority}">{priority.upper()}</span>: {recommendation.get("recommendation", "")}</p>
                </div>
                """
        else:
            html += "<p>No strategic recommendations available for this period.</p>"
        
        html += """
            <div class="footer">
                <p>This report was generated by Competitive Hiring Intelligence. 
                To change your email preferences or unsubscribe, visit the settings page in the application.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    except Exception as e:
        logger.error(f"Error generating email digest: {str(e)}")
        return f"""
        <html>
        <body>
            <h1>Competitive Hiring Intelligence Digest</h1>
            <p>An error occurred while generating your digest. Please check the application.</p>
        </body>
        </html>
        """

def should_send_digest() -> bool:
    """
    Determine if an email digest should be sent based on frequency settings.
    
    Returns:
        True if a digest should be sent, False otherwise
    """
    if not email_config["enabled"]:
        return False
    
    now = datetime.datetime.now()
    last_sent = email_config["last_sent"]
    
    # If never sent before, send now
    if last_sent is None:
        return True
    
    frequency = email_config["frequency"]
    
    if frequency == "daily":
        # Send if it's been more than 20 hours since last email
        return (now - last_sent).total_seconds() > 20 * 3600
    
    elif frequency == "weekly":
        # Send if it's been more than 6 days since last email
        return (now - last_sent).total_seconds() > 6 * 24 * 3600
    
    elif frequency == "significant_changes_only":
        # This would check if there are significant changes
        # For demonstration, we'll assume no significant changes
        return False
    
    return False

def send_hiring_alert(company: str, insight: Dict[str, Any]) -> bool:
    """
    Send an immediate alert for significant hiring changes.
    
    Args:
        company: Company name
        insight: Insight dictionary with details about the hiring change
    
    Returns:
        True if alert was sent successfully, False otherwise
    """
    if not email_config["enabled"]:
        return False
    
    insight_type = insight.get("type", "")
    percent_change = insight.get("percent_change", 0)
    
    # Only send alert if it exceeds the threshold
    if abs(percent_change) < email_config["alert_threshold"]:
        return False
    
    subject = f"🚨 Hiring Alert: {company} {insight_type.replace('_', ' ').title()}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #c00; }}
            .alert {{ padding: 15px; background-color: #fff2e6; border-left: 4px solid #f90; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Hiring Alert: {company}</h1>
        
        <div class="alert">
            <p>{insight.get("insight", "")}</p>
            <p>This alert was triggered because the change ({percent_change:.1f}%) exceeded your alert threshold ({email_config["alert_threshold"]}%).</p>
        </div>
        
        <p>Log in to the Competitive Hiring Intelligence dashboard for more details.</p>
    </body>
    </html>
    """
    
    return send_email(subject, html)
