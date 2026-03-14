import os

class Config:

    # ==============================
    # 🔐 SECRET KEY (For Sessions)
    # ==============================
    SECRET_KEY = 'your_super_secret_key_here_change_this'

    # ==============================
    # 🗄 MySQL DATABASE CONFIG
    # ==============================
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''        # Add your MySQL password if any
    MYSQL_DB = 'agrocycle'
    
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'shantanu_aher_patil_'        # Add your MySQL password if any
    MYSQL_DB = 'agrocycle'


    # ==============================
    # 📂 FILE UPLOAD SETTINGS
    # ==============================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

    # Allowed file extensions for waste images
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # ==============================
    # ⚙ OTHER SETTINGS
    # ==============================
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload size