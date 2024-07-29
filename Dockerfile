# Python 3.8 tabanlı slim bir görüntü kullanılır
FROM python:3.8-slim

# Çalışma dizini oluşturulur
WORKDIR /app

# Sistemin güncellenmesi ve gerekli bağımlılıkların yüklenmesi
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Gereksinimlerin kopyalanması ve yüklenmesi
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarının kopyalanması
COPY . .

# Ortam değişkenleri ayarlanır
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Uygulamanın çalıştırılması
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
