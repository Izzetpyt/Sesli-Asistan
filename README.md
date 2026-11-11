# Sesli Asistan — geliştirilmiş sürüm

Bu proje, GitHub'daki `Izzetpyt/Sesli-Asistan` deposunda README içine konmuş küçük komut örneğini başlangıç noktası alır. Kod ayrı bir Python dosyasına taşındı ve yazılı kullanım, isteğe bağlı mikrofon modu, güvenli hesaplama, tarayıcı araması ve kalıcı notlar eklendi.

## Gereksinimler

- Python 3.10 veya üzeri
- İsteğe bağlı sesli yanıt için `pyttsx3`
- İsteğe bağlı mikrofon modu için `SpeechRecognition` ve `PyAudio`

## Kurulum

Proje klasöründe terminal aç:

```powershell
py -m pip install -r requirements.txt
```

Mikrofon modu için PyAudio da gerekir:

```powershell
py -m pip install PyAudio
```

## Çalıştırma

Yazılı komut modu:

```powershell
py main.py
```

Mikrofonla komut modu:

```powershell
py main.py --voice
```

Sesli yanıtı kapat:

```powershell
py main.py --silent
```

## Örnek komutlar

- `saat` veya `tarih`
- `hesapla (12 + 8) * 3`
- `tarayıcı aç`
- `Google'da uzay haberleri ara`
- `YouTube'da lo-fi ara`
- `not al yarın kitabı çantaya koy`
- `notlar`
- `notları temizle`
- `yardım` veya `kapat`

Notlar proje klasöründeki `notlar.json` dosyasına kaydedilir. Hesap makinesi Python kodu çalıştırmaz; yalnızca temel matematik işlemlerini kabul eder.

## Mikrofon hakkında

Türkçe konuşmayı yazıya çevirmek için `SpeechRecognition` içindeki Google tanıma servisi kullanılır; bu mod internet bağlantısı ister. Mikrofon modu kurulu değilse yazılı komut modu yine kullanılabilir.
