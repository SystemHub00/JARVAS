import time
import pyautogui

def press_key(key):
    pyautogui.press(key)

def hotkey(key1, key2):
    pyautogui.hotkey(key1, key2)

def executar_cadastrar_app():
    tempo = 2  # segundos

    for _ in range(105):
        # Tecla de contexto (menu do botão direito)
        press_key('apps')
        time.sleep(2)

        for _ in range(3):
            press_key('down')
        time.sleep(2)

        for _ in range(3):
            press_key('right')
        time.sleep(1)

        press_key('enter')
        time.sleep(1)

        press_key('enter')
        time.sleep(1)

        press_key('right')
        time.sleep(1)

        press_key('enter')
        time.sleep(1)

        press_key('space')
        time.sleep(1)

        hotkey('alt', 'tab')
        time.sleep(tempo)

        hotkey('ctrl', 'v')
        time.sleep(tempo)

        press_key('down')
        time.sleep(tempo)

        hotkey('alt', 'tab')
        time.sleep(tempo)

        press_key('down')
        time.sleep(tempo)

if __name__ == "__main__":
    print("Iniciando em 5 segundos...")
    time.sleep(5)
    executar_cadastrar_app()
