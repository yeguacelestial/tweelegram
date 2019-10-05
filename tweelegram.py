import json       # json: Se usa para analizar las respuestas de Telegram y las convierte en diccionarios de Python
import requests   # requests: Hace peticiones web usando Python, se usa para interactuar con la API de Telegram
import time       # time: Utilizado para retrasos entre cada petición
import tweepy     # tweepy: Librería de Twitter
import urllib     # urllib: se usa para arreglar el problema de encoding

# Variables

    #Telegram:
TOKEN = "TelegramBotToken"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

    #Twitter:
consumer_key = 'ConsumerKeyToken'
consumer_secret = 'ConsumerSecretToken'
access_token = 'AccessToken'
acces_token_secret = 'AccessTokenSecret'

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

def send_message (text, chat_id):       # Toma el mensaje que se desea enviar (text) y el chat id al que queremos  enviar el mensaje. (chat_id)
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)  # Llama al comando de la API, y le envía el mensaje.
    get_url(url)    # Se manda la nueva URL a la funcion "get_url"

# Twitter OAuth:
def OAuth():
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, acces_token_secret)
        return auth

    except Exception as error:
        return None

oauth = OAuth()
api = tweepy.API(oauth)

# Loop:
def main():                                                         
    last_textchat = (None, None)
    while True:
        text, chat = get_last_chat_id_and_text(get_updates())
        if (text, chat) != last_textchat:
            send_message (text, chat)
            last_textchat = (text, chat)
            api.update_status(text) # Twitter
            send_message ("^Tweet sent.", chat) # Telegram
        time.sleep(0.5)

if __name__ == "__main__":  # Este if permite que se puedan usar las clases de este script sin que se esté ejecutando.
    main()
