from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Content(db.Model):
    """Main content table - stores all editable content"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Hero Section
    hero_label = db.Column(db.String(200), default='◆ Innovation Redefined')
    hero_title = db.Column(db.String(200), default='The Future of Medical Aesthetics')
    hero_description = db.Column(db.Text)
    stat1_number = db.Column(db.String(50), default='100%')
    stat1_text = db.Column(db.String(100), default='CE Certified Excellence')
    stat2_number = db.Column(db.String(50), default='DSE')
    stat2_text = db.Column(db.String(100), default='South Korea Technology')
    
    # Features Section Header
    features_label = db.Column(db.String(100), default='◆ Why Choose Us')
    features_title = db.Column(db.String(200), default='Advancing Science. Elevating Life.')
    features_description = db.Column(db.Text)
    
    # Products Section Header
    products_label = db.Column(db.String(100), default='◆ Our Portfolio')
    products_title = db.Column(db.String(200), default='Next-Gen Medical Devices')
    products_description = db.Column(db.Text)
    
    # Contact Section
    contact_tagline = db.Column(db.String(100), default='◆ Connect With Us')
    contact_title = db.Column(db.String(200), default='Transform Your Practice')
    contact_description = db.Column(db.Text)
    contact_phone = db.Column(db.String(50), default='+95 95128556')
    contact_email = db.Column(db.String(100), default='khinlapyaewoon6@gmail.com')
    contact_address = db.Column(db.Text)
    
    # Company Info
    company_name = db.Column(db.String(100), default='ALTIUS BIOTECH')
    company_tagline = db.Column(db.String(200), default='Advancing Science. Elevating Life.')
    footer_text = db.Column(db.Text)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Feature(db.Model):
    """Features list"""
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(10))  # Keep for backward compatibility
    image = db.Column(db.String(255))  # Store feature image filename
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)


class Product(db.Model):
    """Products list"""
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(10))  # Keep for backward compatibility
    image = db.Column(db.String(255))  # Store product image filename
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)


class ContentHistory(db.Model):
    """Content backup history for rollback feature"""
    id = db.Column(db.Integer, primary_key=True)
    content_snapshot = db.Column(db.Text)  # JSON snapshot of content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(50), default='admin')
    description = db.Column(db.String(200))


class Admin(db.Model):
    """Admin login"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))  # Stores hashed password (pbkdf2:sha256)