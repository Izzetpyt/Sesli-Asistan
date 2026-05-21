# Sesli-Asistan
import pyttsx3
import os 

motor = pyttsx3.init()
motor.setProperty("rate",140)

def asistan_konus(metin):
    print(f"Asistan: {metin}")
    motor.say(metin)
    motor.runAndWait()

komut = input("Bir komut yaz (örneğin: 'oyun, tarayıcı, kapat): ").lower()

if"oyun" in komut:
    asistan_konus("oyun modu aktif ediliyor İzzet. Bol şans!")
    os.system("calc")

elif "tarayıcı" in komut:
    asistan_konus("İnternet dünyaysına bağlanıyoruz.")
    exit()

else:
    asistan_konus("Bu komutu henüz öğrenmedim ama istersen senin için araştırabilirim.")
