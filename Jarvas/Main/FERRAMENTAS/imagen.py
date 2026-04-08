import os
# Configura o caminho do executável do Tesseract
# Programa para tirar print da tela e ler informações (OCR)
from PIL import ImageGrab
import easyocr

def capturar_e_ler_tela():
	# Captura a tela inteira
	screenshot = ImageGrab.grab()
	# Converte para formato compatível com easyocr (numpy array)
	img_np = np.array(screenshot)
	reader = easyocr.Reader(['pt', 'en'])
	resultado = reader.readtext(img_np, detail=0)
	texto = '\n'.join(resultado)
	print('Texto extraído:')
	print(texto)
	return texto

import numpy as np

if __name__ == "__main__":
	capturar_e_ler_tela()
