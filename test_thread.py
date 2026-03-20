import sys, threading
sys.stdout.reconfigure(encoding='utf-8')
from googletrans import Translator
translator = Translator()

def f():
    try:
        print(translator.translate('hello', dest='hi').text)
    except Exception as e:
        print('Error:', repr(e))

t = threading.Thread(target=f)
t.start()
t.join()
