import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import db, Content, Feature, Product, Admin, ContentHistory

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security Configuration
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5MB

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///cms.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Security Headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; frame-src https://www.google.com;"
    return response

# Context processor to inject variables into all templates
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'content': Content.query.first()
    }

# Initialize database
with app.app_context():
    db.create_all()

    # Create default admin if doesn't exist with hashed password
    if not Admin.query.first():
        default_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = Admin(
            username=os.environ.get('ADMIN_USERNAME', 'admin'),
            password=generate_password_hash(default_password, method='pbkdf2:sha256')
        )
        db.session.add(admin)
        db.session.commit()
    
    # Create default content if doesn't exist
    if not Content.query.first():
        content = Content(
            # Hero Section
            hero_label="◆ Innovation Redefined",
            hero_title="The Future of Medical Aesthetics",
            hero_description="ALTIUS BIOTECH brings cutting-edge medical aesthetic technology from South Korea's DSE Inc. to Myanmar. We're not just distributing equipment—we're revolutionizing healthcare delivery with premium CE-certified solutions.",
            stat1_number="100%",
            stat1_text="CE Certified Excellence",
            stat2_number="DSE",
            stat2_text="South Korea Technology",

            # Features Section
            features_label="◆ Why Choose Us",
            features_title="Advancing Science. Elevating Life.",
            features_description="ALTIUS BIOTECH Co., Ltd is Myanmar's premier distributor of advanced medical aesthetic devices, bringing world-class technology to your practice.",

            # Products Section
            products_label="◆ Our Portfolio",
            products_title="Next-Gen Medical Devices",
            products_description="Exclusive distributor of DSE Inc. (South Korea) premium aesthetic medical equipment",

            # Contact Section
            contact_tagline="◆ Connect With Us",
            contact_title="Transform Your Practice",
            contact_description="Ready to elevate your capabilities with premium medical aesthetic technology? Get in touch with our specialists to discover how ALTIUS BIOTECH can provide the solutions your practice needs to deliver exceptional results.",
            contact_phone="+95 95128556",
            contact_email="khinlapyaewoon6@gmail.com",
            contact_address="No: 31, Inya Myaing Road\nKhayay Myaing Street, Golden Valley 1 Ward\nBahan, Yangon, Myanmar",

            # Company Info
            company_name="ALTIUS BIOTECH",
            company_tagline="Advancing Science. Elevating Life.",
            footer_text="Leading Myanmar's aesthetic medicine revolution with premium technology and unwavering commitment to excellence. Advancing science and elevating life through innovative healthcare solutions."
        )
        db.session.add(content)
        db.session.commit()
    
    # Create default features if don't exist
    if Feature.query.count() == 0:
        features = [
            Feature(icon='🎯', title='Premium Quality', description='Every device meets rigorous CE certification standards, ensuring the highest level of safety and performance for your patients.', order=1),
            Feature(icon='🚀', title='Innovation First', description="Access to the latest aesthetic medical technology from DSE Inc., South Korea's leading manufacturer of advanced devices.", order=2),
            Feature(icon='💎', title='Expert Support', description='Comprehensive training, technical support, and ongoing assistance to ensure optimal results with every treatment.', order=3),
            Feature(icon='🏥', title='Trusted Partner', description="Serving Myanmar's leading medical clinics and hospitals with reliable, professional distribution services.", order=4),
            Feature(icon='🌏', title='Global Vision', description='Expanding from local excellence to international impact, bringing global standards to Myanmar healthcare.', order=5),
            Feature(icon='✓', title='Proven Results', description='Delivering measurable outcomes and exceptional patient satisfaction through superior medical technology.', order=6),
        ]
        db.session.add_all(features)
        db.session.commit()
    
    # Create default products if don't exist
    if Product.query.count() == 0:
        products = [
            Product(icon='⚡', title='Advanced Laser Systems', description='Precision-engineered laser technology delivering superior aesthetic results with unmatched safety profiles and patient comfort.', order=1),
            Product(icon='💉', title='Injectable Solutions', description='State-of-the-art delivery systems optimized for precision, control, and exceptional patient experience.', order=2),
            Product(icon='🔬', title='RF Energy Devices', description='Cutting-edge radiofrequency technology for skin rejuvenation and body contouring with proven clinical efficacy.', order=3),
        ]
        db.session.add_all(products)
        db.session.commit()


# ============ FRONTEND ============
@app.route('/')
def index():
    content = Content.query.first()
    features = Feature.query.order_by(Feature.order).all()
    products = Product.query.order_by(Product.order).all()
    return render_template('index.html', content=content, features=features, products=products)


@app.route('/contact', methods=['POST'])
def submit_contact():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # For now, just redirect back to home with a success anchor
    # In production, you would save to database or send email
    return redirect(url_for('index') + '#contact')


# ============ ADMIN ============
@app.route('/admin')
def admin_login():
    if 'admin' in session:
        # If already logged in, show dashboard directly
        content = Content.query.first()
        features = Feature.query.order_by(Feature.order).all()
        products = Product.query.order_by(Product.order).all()

        # Dashboard stats
        features_count = Feature.query.count()
        products_count = Product.query.count()
        unread_messages = 0
        recent_messages = []

        return render_template('admin/dashboard.html',
                             content=content,
                             features=features,
                             products=products,
                             features_count=features_count,
                             products_count=products_count,
                             unread_messages=unread_messages,
                             recent_messages=recent_messages)

    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password, password):
        session.permanent = True
        session['admin'] = True
        session['username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('admin_dashboard'))

    flash('Invalid username or password. Please try again.', 'danger')
    return redirect(url_for('admin_login'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    features = Feature.query.order_by(Feature.order).all()
    products = Product.query.order_by(Product.order).all()

    # Dashboard stats
    features_count = Feature.query.count()
    products_count = Product.query.count()
    unread_messages = 0  # Placeholder for now
    recent_messages = []  # Placeholder for now

    return render_template('admin/dashboard.html',
                         content=content,
                         features=features,
                         products=products,
                         features_count=features_count,
                         products_count=products_count,
                         unread_messages=unread_messages,
                         recent_messages=recent_messages)


def create_content_snapshot(content, description="Manual backup"):
    """Create a backup snapshot of current content"""
    snapshot = {
        'hero_label': content.hero_label,
        'hero_title': content.hero_title,
        'hero_description': content.hero_description,
        'stat1_number': content.stat1_number,
        'stat1_text': content.stat1_text,
        'stat2_number': content.stat2_number,
        'stat2_text': content.stat2_text,
        'features_label': content.features_label,
        'features_title': content.features_title,
        'features_description': content.features_description,
        'products_label': content.products_label,
        'products_title': content.products_title,
        'products_description': content.products_description,
        'contact_tagline': content.contact_tagline,
        'contact_title': content.contact_title,
        'contact_description': content.contact_description,
        'contact_phone': content.contact_phone,
        'contact_email': content.contact_email,
        'contact_address': content.contact_address,
        'company_name': content.company_name,
        'company_tagline': content.company_tagline,
        'footer_text': content.footer_text,
    }

    history = ContentHistory(
        content_snapshot=json.dumps(snapshot),
        description=description
    )
    db.session.add(history)
    db.session.commit()
    return history.id


@app.route('/admin/update/hero', methods=['POST'])
def update_hero():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    create_content_snapshot(content, "Before hero section update")

    # Update only hero fields
    if request.form.get('hero_label') is not None:
        content.hero_label = request.form.get('hero_label')
    if request.form.get('hero_title') is not None:
        content.hero_title = request.form.get('hero_title')
    if request.form.get('hero_description') is not None:
        content.hero_description = request.form.get('hero_description')
    if request.form.get('stat1_number') is not None:
        content.stat1_number = request.form.get('stat1_number')
    if request.form.get('stat1_text') is not None:
        content.stat1_text = request.form.get('stat1_text')
    if request.form.get('stat2_number') is not None:
        content.stat2_number = request.form.get('stat2_number')
    if request.form.get('stat2_text') is not None:
        content.stat2_text = request.form.get('stat2_text')

    db.session.commit()
    flash('Hero section updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/update/features', methods=['POST'])
def update_features():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    create_content_snapshot(content, "Before features section update")

    # Update only features section header fields
    if request.form.get('features_label') is not None:
        content.features_label = request.form.get('features_label')
    if request.form.get('features_title') is not None:
        content.features_title = request.form.get('features_title')
    if request.form.get('features_description') is not None:
        content.features_description = request.form.get('features_description')

    db.session.commit()
    flash('Features section updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/update/products', methods=['POST'])
def update_products():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    create_content_snapshot(content, "Before products section update")

    # Update only products section header fields
    if request.form.get('products_label') is not None:
        content.products_label = request.form.get('products_label')
    if request.form.get('products_title') is not None:
        content.products_title = request.form.get('products_title')
    if request.form.get('products_description') is not None:
        content.products_description = request.form.get('products_description')

    db.session.commit()
    flash('Products section updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/update/contact', methods=['POST'])
def update_contact():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    create_content_snapshot(content, "Before contact section update")

    # Update only contact fields
    if request.form.get('contact_tagline') is not None:
        content.contact_tagline = request.form.get('contact_tagline')
    if request.form.get('contact_title') is not None:
        content.contact_title = request.form.get('contact_title')
    if request.form.get('contact_description') is not None:
        content.contact_description = request.form.get('contact_description')
    if request.form.get('contact_phone') is not None:
        content.contact_phone = request.form.get('contact_phone')
    if request.form.get('contact_email') is not None:
        content.contact_email = request.form.get('contact_email')
    if request.form.get('contact_address') is not None:
        content.contact_address = request.form.get('contact_address')

    db.session.commit()
    flash('Contact section updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/update/general', methods=['POST'])
def update_general():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    content = Content.query.first()
    create_content_snapshot(content, "Before general settings update")

    # Update only general/company fields
    if request.form.get('company_name') is not None:
        content.company_name = request.form.get('company_name')
    if request.form.get('company_tagline') is not None:
        content.company_tagline = request.form.get('company_tagline')
    if request.form.get('footer_text') is not None:
        content.footer_text = request.form.get('footer_text')

    # Handle logo upload with security validation
    if 'logo' in request.files:
        logo_file = request.files['logo']
        if logo_file and logo_file.filename:
            # Validate file extension
            if not allowed_file(logo_file.filename):
                flash('Invalid file type. Only JPG, PNG, GIF, and WEBP files are allowed.', 'danger')
                return redirect(url_for('admin_dashboard'))

            # Secure the filename to prevent directory traversal
            secure_filename(logo_file.filename)
            # Always save as logo.jpg for consistency
            logo_path = os.path.join('static', 'images', 'logo.jpg')
            logo_file.save(logo_path)
            flash('Logo updated successfully!', 'success')

    db.session.commit()
    flash('General settings updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/feature/add', methods=['POST'])
def add_feature():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Handle feature image upload
    image_filename = None
    if 'feature_image' in request.files:
        image_file = request.files['feature_image']
        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                # Generate unique filename
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"feature_{timestamp}_{filename}"
                image_path = os.path.join('static', 'images', 'features', image_filename)

                # Create features directory if it doesn't exist
                os.makedirs(os.path.join('static', 'images', 'features'), exist_ok=True)
                image_file.save(image_path)
            else:
                flash('Invalid image file type. Only JPG, PNG, GIF, and WEBP allowed.', 'danger')
                return redirect(url_for('admin_dashboard'))

    feature = Feature(
        icon=None,  # No longer using emoji icons
        image=image_filename,
        title=request.form.get('title'),
        description=request.form.get('description'),
        order=request.form.get('order', 0)
    )
    db.session.add(feature)
    db.session.commit()
    flash('Feature added successfully!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/feature/edit/<int:id>', methods=['GET', 'POST'])
def edit_feature(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    feature = Feature.query.get_or_404(id)

    if request.method == 'POST':
        feature.title = request.form.get('title')
        feature.description = request.form.get('description')
        feature.order = request.form.get('order', 0)

        # Handle feature image upload
        if 'feature_image' in request.files:
            image_file = request.files['feature_image']
            if image_file and image_file.filename:
                if allowed_file(image_file.filename):
                    # Delete old image if exists
                    if feature.image:
                        old_image_path = os.path.join('static', 'images', 'features', feature.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                    # Save new image
                    filename = secure_filename(image_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"feature_{timestamp}_{filename}"
                    image_path = os.path.join('static', 'images', 'features', image_filename)
                    os.makedirs(os.path.join('static', 'images', 'features'), exist_ok=True)
                    image_file.save(image_path)
                    feature.image = image_filename
                else:
                    flash('Invalid image file type. Only JPG, PNG, GIF, and WEBP allowed.', 'danger')
                    return redirect(url_for('edit_feature', id=id))

        db.session.commit()
        flash('Feature updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_feature.html', feature=feature)


@app.route('/admin/feature/delete/<int:id>')
def delete_feature(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    feature = Feature.query.get(id)
    if feature:
        # Delete image file if exists
        if feature.image:
            image_path = os.path.join('static', 'images', 'features', feature.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(feature)
        db.session.commit()
        flash('Feature deleted successfully!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Handle product image upload
    image_filename = None
    if 'product_image' in request.files:
        image_file = request.files['product_image']
        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                # Generate unique filename
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"product_{timestamp}_{filename}"
                image_path = os.path.join('static', 'images', 'products', image_filename)

                # Create products directory if it doesn't exist
                os.makedirs(os.path.join('static', 'images', 'products'), exist_ok=True)
                image_file.save(image_path)
            else:
                flash('Invalid image file type. Only JPG, PNG, GIF, and WEBP allowed.', 'danger')
                return redirect(url_for('admin_dashboard'))

    product = Product(
        icon=None,  # No longer using emoji icons
        image=image_filename,
        title=request.form.get('title'),
        description=request.form.get('description'),
        order=request.form.get('order', 0)
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.title = request.form.get('title')
        product.description = request.form.get('description')
        product.order = request.form.get('order', 0)

        # Handle product image upload
        if 'product_image' in request.files:
            image_file = request.files['product_image']
            if image_file and image_file.filename:
                if allowed_file(image_file.filename):
                    # Delete old image if exists
                    if product.image:
                        old_image_path = os.path.join('static', 'images', 'products', product.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                    # Save new image
                    filename = secure_filename(image_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"product_{timestamp}_{filename}"
                    image_path = os.path.join('static', 'images', 'products', image_filename)
                    os.makedirs(os.path.join('static', 'images', 'products'), exist_ok=True)
                    image_file.save(image_path)
                    product.image = image_filename
                else:
                    flash('Invalid image file type. Only JPG, PNG, GIF, and WEBP allowed.', 'danger')
                    return redirect(url_for('edit_product', id=id))

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_product.html', product=product)


@app.route('/admin/product/delete/<int:id>')
def delete_product(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    product = Product.query.get(id)
    if product:
        # Delete image file if exists
        if product.image:
            image_path = os.path.join('static', 'images', 'products', product.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/history')
def admin_history():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Get all history entries, newest first, limit to last 20
    history_entries = ContentHistory.query.order_by(ContentHistory.created_at.desc()).limit(20).all()

    return render_template('admin/history.html', history_entries=history_entries)


@app.route('/admin/rollback/<int:history_id>')
def admin_rollback(history_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Get the history entry
    history = ContentHistory.query.get(history_id)
    if not history:
        flash('History entry not found.', 'danger')
        return redirect(url_for('admin_history'))

    # Get current content
    content = Content.query.first()

    # Create a backup of current state before rollback
    create_content_snapshot(content, "Before rollback to version from " + history.created_at.strftime('%Y-%m-%d %H:%M:%S'))

    # Restore from snapshot
    snapshot = json.loads(history.content_snapshot)
    for key, value in snapshot.items():
        setattr(content, key, value)

    db.session.commit()

    flash('Content successfully restored to previous version!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/history/delete/<int:history_id>')
def delete_history(history_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    history = ContentHistory.query.get(history_id)
    if history:
        db.session.delete(history)
        db.session.commit()
        flash('History entry deleted.', 'success')

    return redirect(url_for('admin_history'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)