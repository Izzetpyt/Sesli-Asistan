"""İzzet'in yerel, Türkçe sesli/yazılı asistanı."""

from __future__ import annotations

import argparse
import ast
import json
import operator
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus


APP_DIR = Path(__file__).resolve().parent
NOTES_FILE = APP_DIR / "notlar.json"


class SafeCalculator:
    """Sadece temel aritmetik işlemlerine izin veren küçük hesaplayıcı."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    @classmethod
    def calculate(cls, expression: str) -> float | int:
        if len(expression) > 80:
            raise ValueError("İşlem çok uzun.")
        tree = ast.parse(expression, mode="eval")
        return cls._visit(tree.body)

    @classmethod
    def _visit(cls, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**12:
                raise ValueError("Sayı çok büyük.")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls.OPERATORS:
            left, right = cls._visit(node.left), cls._visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Üs en fazla 10 olabilir.")
            result = cls.OPERATORS[type(node.op)](left, right)
            if isinstance(result, (int, float)) and abs(result) > 10**12:
                raise ValueError("Sonuç çok büyük.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.OPERATORS:
            return cls.OPERATORS[type(node.op)](cls._visit(node.operand))
        raise ValueError("Yalnızca sayılar ve +, -, *, /, //, %, ** işlemleri kullanılabilir.")


class Assistant:
    def __init__(self, voice_output: bool = True) -> None:
        self.speaker = None
        if voice_output:
            try:
                import pyttsx3  # type: ignore[import-not-found]

                self.speaker = pyttsx3.init()
                self.speaker.setProperty("rate", 165)
            except Exception:
                print("Sesli yanıt açılamadı; yazılı yanıtla devam ediyorum.")

    @staticmethod
    def normalize(text: str) -> str:
        return text.casefold().translate(str.maketrans({"ı": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c"}))

    def say(self, message: str) -> None:
        print(f"Asistan: {message}")
        if self.speaker:
            try:
                self.speaker.say(message)
                self.speaker.runAndWait()
            except Exception:
                self.speaker = None

    def handle(self, raw_command: str) -> bool:
        command = raw_command.strip()
        normalized = self.normalize(command)
        if not command:
            return True

        if normalized in {"cikis", "cik", "kapat", "gorusuruz", "exit", "quit"}:
            self.say("Görüşürüz!")
            return False

        if normalized in {"yardim", "help", "komutlar"}:
            self.say("Şunları deneyebilirsin: saat, tarih, hesapla 12 * 3, tarayıcı aç, Google'da kediler ara, not al süt al, notlar.")
        elif "saat" in normalized:
            self.say(f"Saat {datetime.now().strftime('%H:%M')}.")
        elif "tarih" in normalized or "bugun" in normalized:
            self.say(f"Bugün {datetime.now().strftime('%d.%m.%Y')}.")
        elif normalized.startswith("hesapla ") or normalized.startswith("hesap "):
            expression = command.split(maxsplit=1)[1]
            try:
                self.say(f"Sonuç: {SafeCalculator.calculate(expression)}")
            except (ValueError, SyntaxError, ZeroDivisionError) as error:
                self.say(f"Bu işlemi yapamadım: {error}")
        elif normalized == "not al" or normalized.startswith("not al "):
            parts = command.split(maxsplit=2)
            if len(parts) < 3:
                self.say("Notun içeriğini de yaz. Örnek: not al süt al")
            else:
                self.add_note(parts[2])
        elif normalized in {"notlar", "notlarimi oku", "notlari oku", "notlari goster"}:
            self.list_notes()
        elif normalized in {"notlari sil", "notlari temizle"}:
            self.clear_notes()
        elif normalized in {"tarayici ac", "internet ac", "browser"}:
            webbrowser.open("https://www.google.com")
            self.say("Tarayıcıyı açtım.")
        elif normalized.startswith("google'da ") or normalized.startswith("google da "):
            query = re.sub(r"^google(?:'da| da)\s+", "", command, flags=re.IGNORECASE)
            query = re.sub(r"\s+ara$", "", query, flags=re.IGNORECASE).strip()
            self.search("https://www.google.com/search?q=", query)
        elif normalized.startswith("youtube'da ") or normalized.startswith("youtube da "):
            query = re.sub(r"^youtube(?:'da| da)\s+", "", command, flags=re.IGNORECASE)
            query = re.sub(r"\s+ara$", "", query, flags=re.IGNORECASE).strip()
            self.search("https://www.youtube.com/results?search_query=", query)
        else:
            self.say("Bu komutu henüz bilmiyorum. 'Yardım' yazarak komutları görebilirsin.")
        return True

    def search(self, base_url: str, query: str) -> None:
        if not query:
            self.say("Ne aramamı istersin?")
            return
        webbrowser.open(base_url + quote_plus(query))
        self.say(f"Şunu arıyorum: {query}")

    def add_note(self, note: str) -> None:
        if not note.strip():
            self.say("Notun içeriğini de yaz. Örnek: not al süt al")
            return
        notes = self.read_notes()
        notes.append({"text": note.strip(), "created_at": datetime.now().isoformat(timespec="minutes")})
        NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
        self.say("Notunu kaydettim.")

    @staticmethod
    def read_notes() -> list[dict[str, str]]:
        if not NOTES_FILE.exists():
            return []
        try:
            data = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def list_notes(self) -> None:
        notes = self.read_notes()
        if not notes:
            self.say("Henüz kayıtlı not yok.")
            return
        self.say(f"{len(notes)} notun var:")
        for index, note in enumerate(notes, start=1):
            print(f"  {index}. {note.get('text', '')} ({note.get('created_at', '')})")

    def clear_notes(self) -> None:
        if not NOTES_FILE.exists():
            self.say("Silinecek not yok.")
            return
        confirmation = input("Bütün notlar silinsin mi? (e/h): ").strip().casefold()
        if confirmation in {"e", "evet", "y", "yes"}:
            NOTES_FILE.unlink(missing_ok=True)
            self.say("Notları sildim.")
        else:
            self.say("Tamam, notlara dokunmadım.")


def run_text_mode(assistant: Assistant) -> None:
    assistant.say("Merhaba! Yardım için 'yardım', çıkmak için 'kapat' yaz.")
    while True:
        try:
            command = input("Sen: ")
        except (EOFError, KeyboardInterrupt):
            print()
            assistant.say("Görüşürüz!")
            break
        if not assistant.handle(command):
            break


def run_voice_mode(assistant: Assistant) -> None:
    try:
        import speech_recognition as sr  # type: ignore[import-not-found]
    except ImportError:
        assistant.say("Mikrofon modu için SpeechRecognition ve PyAudio kurulmalı. README'deki kurulum adımlarına bak.")
        return

    recognizer = sr.Recognizer()
    assistant.say("Mikrofon modu açık. Dinlemek için konuş; çıkmak için 'kapat' de.")
    try:
        with sr.Microphone() as microphone:
            recognizer.adjust_for_ambient_noise(microphone, duration=0.7)
            while True:
                print("Dinliyorum...")
                try:
                    audio = recognizer.listen(microphone, timeout=5, phrase_time_limit=8)
                    command = recognizer.recognize_google(audio, language="tr-TR")
                    print(f"Sen: {command}")
                    if not assistant.handle(command):
                        break
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    assistant.say("Anlayamadım, tekrar söyler misin?")
                except sr.RequestError as error:
                    assistant.say(f"Ses tanıma servisine ulaşılamadı: {error}")
                    break
    except (OSError, AttributeError) as error:
        assistant.say(f"Mikrofon açılamadı: {error}. PyAudio kurulumunu kontrol et.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Türkçe sesli/yazılı masaüstü asistanı")
    parser.add_argument("--voice", action="store_true", help="Mikrofonla komut dinle")
    parser.add_argument("--silent", action="store_true", help="Yanıtları yalnızca yazıyla ver")
    args = parser.parse_args()
    assistant = Assistant(voice_output=not args.silent)
    if args.voice:
        run_voice_mode(assistant)
    else:
        run_text_mode(assistant)


if __name__ == "__main__":
    main()
