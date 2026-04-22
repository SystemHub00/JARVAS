import pyautogui
import pytesseract
import cv2
import numpy as np
import os
import time

# --- CONFIGURAÇÃO DO OCR ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def localizar_atencao():
    """Função que tira print e verifica a palavra 'Atenção'"""
    try:
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        texto_lido = pytesseract.image_to_string(thresh, lang='por')
        return "atenção" in texto_lido.lower()
    except:
        return False
    
def localizar_editar():
    """Função que tira print e verifica a palavra 'Editar'"""
    try:
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        texto_lido = pytesseract.image_to_string(thresh, lang='por')
        return "editar" in texto_lido.lower()
    except:
        return False

# --- INÍCIO DO SCRIPT ---
time.sleep(7)

for i in range(692):
    print(f"Executando ciclo {i+1}...")
    time.sleep(1)
    pyautogui.press("apps")
    for _ in range(3):
        pyautogui.press("down")
    for _ in range(4):
        pyautogui.press("enter")

    # --- MOMENTO DE LER A TELA ---
    time.sleep(5) # Tempo para o sistema carregar a mensagem
    
    if localizar_atencao():
        print("⚠️ 'Atenção' detectado! Aplicando correção e reiniciando ciclo...")
        pyautogui.press("enter") # Dá o Enter no aviso
        time.sleep(1)
        pyautogui.press("down")  # Dá o Down solicitado
        time.sleep(1)
        continue # VOLTA PARA O COMEÇO DO FOR (pula o restante das ações abaixo)

    if localizar_editar():
        print("⚠️ 'Editar' detectado! Aplicando correção e reiniciando ciclo...")
        pyautogui.press("esc") # Dá o Esc na tela
        time.sleep(1)
        pyautogui.press("down")  # Dá o Down solicitado
        time.sleep(1)
        continue # VOLTA PARA O COMEÇO DO FOR (pula o restante das ações abaixo)

    # --- CONTINUAÇÃO CASO NÃO LEIA "ATENÇÃO" ---
    for _ in range(1):
        pyautogui.press("enter")
    time.sleep(1.5)
    for _ in range(1):
        pyautogui.press("right")
    time.sleep(0.5)
    
    for _ in range(1):
        pyautogui.press("enter")
    time.sleep(1)
    for _ in range(1):
        pyautogui.press("enter")
    time.sleep(0.5)

    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press("down")
    time.sleep(0.5)
    
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.5)
    pyautogui.press("down")
    time.sleep(0.5)