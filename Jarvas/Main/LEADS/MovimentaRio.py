import numpy as np
from PIL import ImageGrab
import easyocr
import pyautogui
import pyperclip
import time
import re

# Inicialize o reader apenas uma vez
reader = easyocr.Reader(['pt'])  # Use só o idioma necessário

# Aguarda 5 segundos antes de começar
time.sleep(5)

def capturar_e_ler_tela():
    # Captura a tela inteira
    screenshot = ImageGrab.grab()
    # Converte para formato compatível com easyocr (numpy array)
    img_np = np.array(screenshot)
    resultado = reader.readtext(img_np, detail=0)
    texto = '\n'.join(resultado)
    print('Texto extraído:')
    print(texto)
    return texto

for programa in range(100):
    # COPIA CPF   
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    pyperclip.paste() 
    time.sleep(1)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)
    pyautogui.hotkey('alt', 'o', 'i')
    time.sleep(1)
    pyautogui.press('tab')
    pyautogui.press('Enter')
    time.sleep(1)
    pyautogui.hotkey('Ctrl', 'v')
    time.sleep(1)
    # EXTRA
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.hotkey('Ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    
    # BOTÃO PROXIMO - 1
    pyautogui.click(x=892, y=843)
    time.sleep(1)
    if "Digito Verificador do CPF ou do CNPJ não confere" in capturar_e_ler_tela():
        time.sleep(1)
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        pyautogui.press('down')
        time.sleep(1)
        pyautogui.hotkey('Ctrl', 'c')
        pyperclip.paste() 
        time.sleep(1)
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        pyautogui.press('Enter')
        time.sleep(1)
        pyautogui.hotkey('', 'tab')
        time.sleep(1) 
        
        pyautogui.press('tab')
        time.sleep(3)
        pyautogui.hotkey('Ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
    if "Sexo" in capturar_e_ler_tela():
        time.sleep(1)
        pyautogui.write("M")
        time.sleep(1)
        pyautogui.click(x=892, y=843)
        
    time.sleep(2)
    pyautogui.press('tab')
    time.sleep(1)

    # TIPO DE CONTRATO
    pyautogui.write("Bolsa")
    pyautogui.press('tab')
    
    # DATA DA MATRÍCULAM
    # CHROME
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)
    for i in range(4):
        pyautogui.press('left')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    data_de_inscricao = pyperclip.paste()
    time.sleep(1)
    for i in range(4):
        pyautogui.press('right')
    time.sleep(1)

    # F10
    
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)
    for i in range(8):
        pyautogui.press('backspace')
    pyautogui.write(data_de_inscricao)
    time.sleep(1)
    pyautogui.press('tab')
    pyautogui.press('tab')

    # EVENTO
    pyautogui.write("11 - Movimenta.Rio: Ação Externa")
    time.sleep(1)
    pyautogui.press('tab')  

    # CURSO
    '''for i in range(67):
        pyautogui.press('down')
    pyautogui.press('tab')
    '''
    curso = "Movimenta.Rio: Hibrido - Marketing Digital v2"
    pyautogui.write(curso)
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    # ADMINISTRADO
    pyautogui.write("Lucas Luan Pereira Vieira")
    time.sleep(1)
    pyautogui.press('tab')

    
    # COORDENADOR
    pyautogui.write("Marcus Vinicius Coppola Souto")
    time.sleep(1)

    # BOTÃO PROXIMO - 2
    for _ in range(5):
        pyautogui.press('tab')      
    time.sleep(1)

    # PARTE - 3
    pyautogui.press('space')
    for _ in range(2):
        pyautogui.press('tab')
    pyautogui.write("RJ - Movimenta.Rio")
    time.sleep(1)

    # BOTÃO GRAVAR
    for _ in range(6):
        pyautogui.press('tab')
    pyautogui.press('enter')
    time.sleep(1)

    # EXCEL
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)
    pyautogui.press('left')
    pyautogui.press('space')
    time.sleep(1)       
    pyautogui.press('down')
    pyautogui.press('right')
    time.sleep(1)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)
    pyautogui.hotkey('alt', 'tab')
