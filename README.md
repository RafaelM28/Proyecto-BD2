# Proyecto-BD2

Es importante saber que si no quieres hacer instalación global de las librerias y quieres hacerlo en un proyecto dado
podemos crear un entorno virtual usando:

python -m venv nombre_del_entorno  # Ej: python -m venv .venv

para activarlo usamos:
.\venv\Scripts\activate
posteriormente podemos intstalar las librerias que deseemos y su version en el proyecto
(para desactivarla usamos: desactive)

## Instalación
 ------------------------ Para la conexion a la API ------------------------------------------
 
para la conexion a twitter (x) instalamos ejecutamos el siguiente comando:
pip install tweepy  python-dotenv

Esto instalará la libreria tweepy para la conexion a la API de twitter y python-dotenv sirve para manejar 
variables de entorno

------------------------------------------------------------------------------------------------
## Ejecución
-------------------- Para la conexion de la API ----------------------------------------------

NOTA: Esta fue la forma en que lo realice, habra otras formas, sin embargo el uso del .env me parece el mas correcto
      el como llamemos los metodos y lo usemos puede depender de cada quien

1- creamos nuestro archivo .env donde establecemos las credenciales que nos da la pagina de developer.x.com
TWITTER_API_KEY= #"tu_api_key"
TWITTER_API_SECRET= #"tu_api_secret"
TWITTER_ACCESS_TOKEN= #"tu_access_token"
TWITTER_ACCESS_TOKEN_SECRET= #"tu_token_secret"
TWITTER_BEARER_TOKEN= #"tu_bearer_token"

2- luego en un archivo .py importamos
import os
import tweepy
from dotenv import load_dotenv

cargamos las credenciales
# Cargar credenciales desde .env
load_dotenv()

client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

creamos un metodo que nos permita hacer lo que deseemos


# Autenticación

## Contribuciones

Se aceptan contribuciones al proyecto. Para ello, debes de seguir estos pasos:

1. Clona el repositorio en tu maquina local; luego, crea una rama de desarrollo.
2. Realiza los cambios que consideres utiles y necesarios.
3. Realiza un commit de los cambios.
4. Crea una solicitud de extracción.

**Es necesario seguir los pasos para considerar la aceptación de la contribución.**
