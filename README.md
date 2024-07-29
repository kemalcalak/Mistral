# Mistral-API

## Proje Açıklaması

Mistral-API, JWT kimlik doğrulaması, istek sınırlandırma (rate limiting), önbellekleme (caching) ve Docker yapılandırması ile geliştirilmiş bir Flask tabanlı bir API'dir. Bu API, kullanıcıların metin girdileri için tahminlerde bulunmasına olanak tanır.

### Özellikler

- **JWT Kimlik Doğrulama**: Güvenli API erişimi için JSON Web Token kullanımı.
- **İstek Sınırlandırma**: Kullanıcı başına belirli zaman dilimlerinde sınırlı sayıda istek yapılabilmesi.
- **Önbellekleme**: Sık yapılan tahminlerin hızlı yanıtlanması için caching.
- **Swagger UI**: API dokümantasyonu ve test için entegre Swagger arayüzü.
- **Docker Desteği**: Projenin kolay dağıtımı için Docker yapılandırması.

## Kurulum ve Çalıştırma

### Gerekli Yazılımlar

- [Python 3.8](https://www.python.org/downloads/release/python-380/)
- [Docker](https://www.docker.com/products/docker-desktop)
