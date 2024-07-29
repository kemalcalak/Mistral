from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import check_password_hash
from flask_caching import Cache
import torch
import logging
from functools import wraps
import asyncio
import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# Rate limiting (istek sınırlandırma) kuralları belirlenir
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Swagger UI entegrasyonu
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Mistral-API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Cache yapılandırması
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Model ve tokenizer yükleme
model_name = os.getenv("MODEL_NAME", "mistral-7B-v0.3")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT ayarları
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

# JWT token üretme fonksiyonu
def generate_token(username):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token süresini 1 saat olarak belirle
    token = jwt.encode({'username': username, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

# JWT doğrulama decorator'ı
def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            logger.warning("Missing token")
            return jsonify({'error': 'Missing token'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return jsonify({'error': 'Expired token'}), 401
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Giriş (login) endpoint'i
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    username = auth.get('username')
    password = auth.get('password')

    # Kullanıcı doğrulama örneği (sabit kullanıcı adı ve şifre)
    if username == 'admin' and check_password_hash('pbkdf2:sha256:150000$z2q3Egql$49e3af1ff8c1dcd1eb8bb6f4188f5d5b9e5c616d6ed0d0c8e03e62a8f2a8e5d1', password):
        token = generate_token(username)
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Predict endpoint'i
@app.route('/predict', methods=['POST'])
@require_jwt  # JWT doğrulama gerektirir
@limiter.limit("10 per minute")  # Rate limit
@cache.cached(timeout=300, query_string=True)  # Önbellekleme (cache)
async def predict():
    try:
        data = request.json
        if 'input' not in data:
            return jsonify({'error': 'No input data provided'}), 400
        
        input_data = data['input']
        inputs = tokenizer(input_data, return_tensors="pt").to(device)
        
        # Model tahmini
        with torch.no_grad():
            outputs = await asyncio.to_thread(model.generate, **inputs)
        
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return jsonify({'prediction': prediction})
    
    except Exception as e:
        logger.error("Error during prediction", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Sağlık kontrolü endpoint'i
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# 404 hata yönetimi
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not Found'}), 404

# 500 hata yönetimi
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500

# Uygulamanın debug modunda mı yoksa üretim modunda mı çalışacağını belirler
if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
