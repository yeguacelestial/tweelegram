import json       # json: Se usa para analizar las respuestas de Telegram y las convierte en diccionarios de Python
import requests   # requests: Hace peticiones web usando Python, se usa para interactuar con la API de Telegram
import time       # time: Utilizado para retrasos entre cada petición
import tweepy     # tweepy: Librería de Twitter
import urllib     # urllib: se usa para arreglar el problema de encoding
from dbhelper import DBHelper

# Variables

    #Telegram:
TOKEN = "TelegramToken"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

    #db:
db = DBHelper()

def get_url(url):                                   # Descarga el contenido de una URL y se obtiene una string.
    response = requests.get(url)
    content = response.content.decode("utf8")   # "decode" se usa con fines de compatibildad.
    return content

def get_json_from_url(url):             # Toma el string de arriba y lo pasa a un diccionario de Python...
    content = get_url(url)
    js = json.loads(content)            # ...usando json.loads() (LoadString)
    return js

def get_updates(offset=None):                      # Llama al comando de actualización de la API, y regresa una lista de
    url = URL + "getUpdates?timeout=100"            #  "updates", los cuales son los mensajes enviados al bot.
    if offset:
        url += "&offset={}".format(offset)      # Indica a la API que ya no se desea recibir update_id menor al del update recibido.
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):     # Da información del id del chat y del mensaje más reciente recibido.
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message (text, chat_id, reply_markup=None):       # Toma el mensaje que se desea enviar (text) y el chat id al que queremos  enviar el mensaje. (chat_id)
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)  # Llama al comando de la API, y le envía el mensaje.
    
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)

    get_url(url)    # Se manda la nueva URL a la funcion "get_url"

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#keyboard:
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

#db:
def handle_updates(updates):
    for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)

            if text == "/kappa":
                keyboard = build_keyboard(items)
                send_message("Mandame una pendejada", chat, keyboard)

            elif text in items:
                db.delete_item(text, chat)
                items = db.get_items(chat)
                keyboard = build_keyboard(items)
                send_message("Mandame una pendejada", chat, keyboard)

            else:
                db.add_item(text, chat)
                items = db.get_items(chat)
                message = "\n".join(items)
                send_message(message,chat)


# Loop:
def main():
    db.setup()           
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == "__main__":  # Este if permite que se puedan usar las clases de este script sin que se esté ejecutando.
    main()
