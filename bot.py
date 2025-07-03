# -*- coding: utf-8 -*-
import logging
import os
import telebot
import gspread
import tempfile
import requests
from threading import Thread
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import InputMediaPhoto, ReplyKeyboardMarkup

# --- РЅР°СЃС‚СЂРѕР№РєРё ---
ADMIN_ID = 1882770883
BOT_TOKEN = '7678242447:AAGl9N1SOahegCN8VL-9fQUXVuHyLuSY74'
GOOGLE_SHEET_NAME = 'Р§Р°С‚-Р±РѕС‚/РёРіСЂСѓС€РєРё'

GOOGLE_CREDENTIALS_JSON = '''{
  "type": "service_account",
  "project_id": "telegram-bot-project-463116",
  "private_key_id": "4ab0284a6c817e0f1e818a1c8be5b8803dc38433",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "telegram-bot-service@telegram-bot-project-463116.iam.gserviceaccount.com",
  "client_id": "105207713238843476124",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/telegram-bot-service%40telegram-bot-project-463116.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'''

# Р›РѕРіРёСЂРѕРІР°РЅРёРµ РґР»СЏ РѕС‚Р»Р°РґРєРё
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
    f.write(GOOGLE_CREDENTIALS_JSON)
    temp_keyfile = f.name

creds = ServiceAccountCredentials.from_json_keyfile_name(temp_keyfile, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

def convert_drive_link(link):
    if "drive.google.com/file/d/" in link:
        try:
            file_id = link.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except IndexError:
            return None
    return None

welcome_message = (
    "РџСЂРёРІРµС‚! н Ѕн±‹ Р’С‹ РІ РєР°С‚Р°Р»РѕРіРµ РІСЏР·Р°РЅС‹С… СЃСѓРІРµРЅРёСЂРЅС‹С… РёРіСЂСѓС€РµРє СЂСѓС‡РЅРѕР№ СЂР°Р±РѕС‚С‹ н ѕн·ё\n"
    "РЇ РїРѕРјРѕРіСѓ РІР°Рј РІС‹Р±СЂР°С‚СЊ РёРіСЂСѓС€РєСѓ Рё СЃРІСЏР·Р°С‚СЊСЃСЏ СЃ РјР°СЃС‚РµСЂРѕРј.\n\n"
    "Р”РѕСЃС‚СѓРїРЅС‹ РєРЅРѕРїРєРё:\n"
    "н Ѕні¦ РљР°С‚Р°Р»РѕРі вЂ” РїРѕСЃРјРѕС‚СЂРµС‚СЊ РІСЃРµ РёРіСЂСѓС€РєРё СЃ С†РµРЅР°РјРё\n"
    "н ѕн·µ РЎРІСЏР·СЊ СЃ РјР°СЃС‚РµСЂРѕРј вЂ” Р·Р°РґР°С‚СЊ РІРѕРїСЂРѕСЃ РёР»Рё РѕС„РѕСЂРјРёС‚СЊ Р·Р°РєР°Р·\n"
    "н ѕн·ѕ РЈСЃР»РѕРІРёСЏ Р·Р°РєР°Р·Р° вЂ” РІР°Р¶РЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ РґР»СЏ РїРѕРєСѓРїР°С‚РµР»СЏ\n\n"
    "Р’ РєР°СЂС‚РѕС‡РєРµ РєР°Р¶РґРѕР№ РёРіСЂСѓС€РєРё СѓРєР°Р·Р°РЅС‹:\n"
    "н Ѕні· Р¤РѕС‚Рѕ\nн Ѕніђ Р Р°Р·РјРµСЂ\nн ЅнІ° Р¦РµРЅР° (Р±РµР· СѓС‡С‘С‚Р° РґРѕСЃС‚Р°РІРєРё)\nн Ѕні¦ РќР°Р»РёС‡РёРµ (РІ РЅР°Р»РёС‡РёРё, РЅР° Р·Р°РєР°Р·, РѕСЃС‚Р°Р»Р°СЃСЊ 1 С€С‚СѓРєР° Рё С‚.Рї.)\n\n"
    "Р‘РѕС‚ СЂР°Р±РѕС‚Р°РµС‚ РєСЂСѓРіР»РѕСЃСѓС‚РѕС‡РЅРѕ.\nР”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ! н ЅнІ›"
)

order_terms_text = (
    "### н ѕн·ѕ РЈСЃР»РѕРІРёСЏ РѕС„РѕСЂРјР»РµРЅРёСЏ Р·Р°РєР°Р·Р°\n\n"
    "**1. РћРїР»Р°С‚Р°:**\n"
    "- Р•СЃР»Рё РёРіСЂСѓС€РєР° **РІ РЅР°Р»РёС‡РёРё**, С‚СЂРµР±СѓРµС‚СЃСЏ **РїРѕР»РЅР°СЏ РїСЂРµРґРѕРїР»Р°С‚Р°**.\n"
    "- Р•СЃР»Рё РёРіСЂСѓС€РєР° **РІСЏР¶РµС‚СЃСЏ РЅР° Р·Р°РєР°Р·**, РІРѕР·РјРѕР¶РЅР° **С‡Р°СЃС‚РёС‡РЅР°СЏ РїСЂРµРґРѕРїР»Р°С‚Р°** вЂ” СЃСѓРјРјР° РѕР±СЃСѓР¶РґР°РµС‚СЃСЏ РёРЅРґРёРІРёРґСѓР°Р»СЊРЅРѕ.\n"
    "- РћРїР»Р°С‚Р° РѕСЃСѓС‰РµСЃС‚РІР»СЏРµС‚СЃСЏ РїРµСЂРµРІРѕРґРѕРј РЅР° РєР°СЂС‚Сѓ (СЂРµРєРІРёР·РёС‚С‹ РїСЂРµРґРѕСЃС‚Р°РІР»СЋ РїСЂРё РѕС„РѕСЂРјР»РµРЅРёРё).\n\n"
    "**2. РЎСЂРѕРє РёР·РіРѕС‚РѕРІР»РµРЅРёСЏ:**\n"
    "- РЎСЂРѕРє Р·Р°РІРёСЃРёС‚ РѕС‚ СЃР»РѕР¶РЅРѕСЃС‚Рё Рё Р·Р°РіСЂСѓР¶РµРЅРЅРѕСЃС‚Рё вЂ” РѕР±С‹С‡РЅРѕ РѕС‚ 3 РґРѕ 10 РґРЅРµР№.\n"
    "- РџСЂРё РІС‹СЃРѕРєРѕР№ Р·Р°РіСЂСѓР¶РµРЅРЅРѕСЃС‚Рё СЃСЂРѕРєРё РјРѕРіСѓС‚ Р±С‹С‚СЊ СѓРІРµР»РёС‡РµРЅС‹, РѕР± СЌС‚РѕРј РїСЂРµРґСѓРїСЂРµР¶РґР°СЋ Р·Р°СЂР°РЅРµРµ.\n\n"
    "**3. Р”РѕСЃС‚Р°РІРєР°:**\n"
    "- Р”РѕСЃС‚Р°РІРєР° РїРѕ Р РѕСЃСЃРёРё РѕСЃСѓС‰РµСЃС‚РІР»СЏРµС‚СЃСЏ РџРѕС‡С‚РѕР№ Р РѕСЃСЃРёРё РёР»Рё РЎР”Р­Рљ.\n"
    "- **РЎС‚РѕРёРјРѕСЃС‚СЊ РґРѕСЃС‚Р°РІРєРё РЅРµ РІРєР»СЋС‡РµРЅР° РІ С†РµРЅСѓ РёРіСЂСѓС€РєРё.**\n"
    "- Р”РѕСЃС‚Р°РІРєР° **РѕРїР»Р°С‡РёРІР°РµС‚СЃСЏ РїСЂРё РїРѕР»СѓС‡РµРЅРёРё** РІ РїСѓРЅРєС‚Рµ РІС‹РґР°С‡Рё (РЅР°Р»РѕР¶РµРЅРЅС‹Р№ РїР»Р°С‚С‘Р¶ Р·Р° РґРѕСЃС‚Р°РІРєСѓ).\n\n"
    "**4. Р’РѕР·РІСЂР°С‚ Рё РѕР±РјРµРЅ:**\n"
    "- РР·РґРµР»РёСЏ СЂСѓС‡РЅРѕР№ СЂР°Р±РѕС‚С‹ РЅРµ РїРѕРґР»РµР¶Р°С‚ РІРѕР·РІСЂР°С‚Сѓ РёР»Рё РѕР±РјРµРЅСѓ, РєСЂРѕРјРµ СЃР»СѓС‡Р°РµРІ Р±СЂР°РєР° (РЅРµРѕР±С…РѕРґРёРјРѕ С„РѕС‚Рѕ).\n"
    "- **РџРµСЂРµРґ РѕС‚РїСЂР°РІРєРѕР№** СЏ РѕР±СЏР·Р°С‚РµР»СЊРЅРѕ РїСЂРµРґРѕСЃС‚Р°РІР»СЏСЋ РєР»РёРµРЅС‚Сѓ **С„РѕС‚Рѕ РіРѕС‚РѕРІРѕР№ РёРіСЂСѓС€РєРё**, С‡С‚РѕР±С‹ РїРѕРґС‚РІРµСЂРґРёС‚СЊ РµС‘ РєР°С‡РµСЃС‚РІРѕ Рё СЃРѕСЃС‚РѕСЏРЅРёРµ. Р­С‚Рѕ РїРѕРјРѕРіР°РµС‚ РёР·Р±РµР¶Р°С‚СЊ РЅРµРґРѕСЂР°Р·СѓРјРµРЅРёР№ РїСЂРё РїРѕР»СѓС‡РµРЅРёРё.\n\n"
    "**5. РЈРїР°РєРѕРІРєР°:**\n"
    "- РљР°Р¶РґР°СЏ РёРіСЂСѓС€РєР° СѓРїР°РєРѕРІС‹РІР°РµС‚СЃСЏ РІ **РїСЂРѕР·СЂР°С‡РЅС‹Р№ РїР»Р°СЃС‚РёРєРѕРІС‹Р№ РїР°РєРµС‚**.\n"
    "- РџРѕ Р·Р°РїСЂРѕСЃСѓ РІРѕР·РјРѕР¶РЅР° РїРѕРґР°СЂРѕС‡РЅР°СЏ СѓРїР°РєРѕРІРєР° (РѕР±СЃСѓР¶РґР°РµС‚СЃСЏ РѕС‚РґРµР»СЊРЅРѕ).\n\n"
    "**6. РРЅРґРёРІРёРґСѓР°Р»СЊРЅС‹Рµ Р·Р°РєР°Р·С‹:**\n"
    "- РњРѕР¶РЅРѕ РІРЅРµСЃС‚Рё РёР·РјРµРЅРµРЅРёСЏ РІ С†РІРµС‚, СЂР°Р·РјРµСЂ РёР»Рё РґРµС‚Р°Р»Рё РёРіСЂСѓС€РєРё вЂ” РѕР±СЃСѓРґРёРј РёРЅРґРёРІРёРґСѓР°Р»СЊРЅРѕ РїРµСЂРµРґ РЅР°С‡Р°Р»РѕРј СЂР°Р±РѕС‚С‹.\n\n"
    "**7. РЎРІСЏР·СЊ:**\n"
    "- Р—Р°РґР°С‚СЊ РІРѕРїСЂРѕСЃС‹ РјРѕР¶РЅРѕ С‡РµСЂРµР· РєРЅРѕРїРєСѓ **'РЎРІСЏР·СЊ СЃ РјР°СЃС‚РµСЂРѕРј'**."
)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("н Ѕні¦ РљР°С‚Р°Р»РѕРі", "н ѕн·µ РЎРІСЏР·СЊ СЃ РјР°СЃС‚РµСЂРѕРј")
    markup.row("н ѕн·ѕ РЈСЃР»РѕРІРёСЏ Р·Р°РєР°Р·Р°")
    if message.from_user.id == ADMIN_ID:
        markup.row("вљ™пёЏ РђРґРјРёРЅРєР°")
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "н Ѕні¦ РљР°С‚Р°Р»РѕРі")
def send_catalog(message):
    records = sheet.get_all_records()
    def price_key(x):
        try:
            return float(x.get('Р¦РµРЅР°', 0))
        except (ValueError, TypeError):
            return 0
    sorted_records = sorted(records, key=price_key)

    for item in sorted_records:
        raw_urls = [item.get("Р¤РѕС‚Рѕ 1", "").strip(), item.get("Р¤РѕС‚Рѕ 2", "").strip(), item.get("Р¤РѕС‚Рѕ 3", "").strip()]
        photo_files = []
        for url in raw_urls:
            if not url:
                continue
            converted = convert_drive_link(url)
            if not converted:
                continue
            try:
                response = requests.get(converted)
                if response.status_code == 200:
                    photo_files.append(response.content)
            except Exception as e:
                print(f"РћС€РёР±РєР° РїСЂРё СЃРєР°С‡РёРІР°РЅРёРё С„РѕС‚Рѕ: {e}")

        name = item.get("РќР°Р·РІР°РЅРёРµ", "")
        price = item.get("Р¦РµРЅР°", "")
        size = item.get("Р Р°Р·РјРµСЂ", "")
        status = item.get("РќР°Р»РёС‡РёРµ", "")
        caption = f"#{name}\n\nн ЅнІ° Р¦РµРЅР°: {price} СЂСѓР±Р»РµР№ (Р±РµР· СѓС‡С‘С‚Р° РґРѕСЃС‚Р°РІРєРё)\nн Ѕніђ Р Р°Р·РјРµСЂ: {size}\nн Ѕні¦ РќР°Р»РёС‡РёРµ: {status}"

        if not photo_files:
            bot.send_message(message.chat.id, caption)
            continue

        media_group = []
        temp_files = []
        try:
            for i, content in enumerate(photo_files):
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                tmp.write(content)
                tmp.flush()
                temp_files.append(tmp.name)

                if i == 0:
                    media_group.append(InputMediaPhoto(open(tmp.name, 'rb'), caption=caption))
                else:
                    media_group.append(InputMediaPhoto(open(tmp.name, 'rb')))
            bot.send_media_group(message.chat.id, media_group)
        except Exception as e:
            print(f"РћС€РёР±РєР° РїСЂРё РѕС‚РїСЂР°РІРєРµ media_group: {e}")
            bot.send_message(message.chat.id, caption)
        finally:
            for path in temp_files:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"РћС€РёР±РєР° РїСЂРё СѓРґР°Р»РµРЅРёРё РІСЂРµРјРµРЅРЅРѕРіРѕ С„Р°Р№Р»Р°: {e}")

@bot.message_handler(func=lambda m: m.text == "н ѕн·µ РЎРІСЏР·СЊ СЃ РјР°СЃС‚РµСЂРѕРј")
def contact(message):
    bot.send_message(message.chat.id, "Р’С‹ РјРѕР¶РµС‚Рµ СЃРІСЏР·Р°С‚СЊСЃСЏ СЃРѕ РјРЅРѕР№:\n\nн Ѕні§ Email: polypropile.n@ya.ru\nн ЅнІ¬ Telegram: @zabawwka")

@bot.message_handler(func=lambda m: m.text == "н ѕн·ѕ РЈСЃР»РѕРІРёСЏ Р·Р°РєР°Р·Р°")
def order_terms(message):
    bot.send_message(message.chat.id, order_terms_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "вљ™пёЏ РђРґРјРёРЅРєР°" and m.from_user.id == ADMIN_ID)
def admin_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("н Ѕніќ РўРµСЃС‚РѕРІР°СЏ СЂР°СЃСЃС‹Р»РєР°", "н ЅніЉ РЎС‚Р°С‚СѓСЃ Р±РѕС‚Р°")
    markup.row("н ЅніЁ РЎРґРµР»Р°С‚СЊ СЂР°СЃСЃС‹Р»РєСѓ")
    markup.row("вќЊ Р’С‹С…РѕРґ РІ РјРµРЅСЋ")
    bot.send_message(message.chat.id, "Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ Р°РґРјРёРЅРєСѓ!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "вќЊ Р’С‹С…РѕРґ РІ РјРµРЅСЋ")
def back_to_menu(message):
    start(message)

# Р—Р°РїСѓСЃРє Р±РѕС‚Р°
if __name__ == "__main__":
    bot.infinity_polling()
