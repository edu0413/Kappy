# DEPLOY - Change this to random bytes
SECRET_KEY = 'umapassqualquer'

UPLOAD_FOLDER = 'templates/assets/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True

MAIL_SERVER ='herse.dnsherse.com'
MAIL_PORT = 465
MAIL_USERNAME = 'CHANGEME'
MAIL_PASSWORD = 'CHANGEME'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

flask_host = '0.0.0.0'