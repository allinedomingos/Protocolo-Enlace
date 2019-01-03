#!/usr/bin/python3
'''
Created on 13 de ago de 2018

@author: alline
'''


from enum import Enum
import crc
import serial

class Estado(Enum):
	Ocioso = 0  # Repouso
	Verifica = 1  # Estabelecimento
	Recepcao = 2 # Recepcao
	ESC = 3
	
class Enquadramento:
	
	def __init__(self, porta, byte_max=256):
		self.serial = porta
		self.bytes_min = 0
		self.bytes_max = byte_max
		self.buffer =  b''          # a informacao sera um array de bytes
		self.estado = Estado.Ocioso # Inicia no estado ocioso
		
	   
# envia o quadro apontado por buffer
# o tamanho do quadro e dado por bytes
	def envia(self, buffer):  # o buffer sao inteiros
		self.buffer = b''
		self.buffer += bytes(b'\x7e')  # insere 7e no inicio do pacote  
		buffer = crc.CRC16(buffer).gen_crc() # gera crc e coloca no final do buffer
		for i in range(0, len(buffer)):
			#print(hex(buffer[i]))
			if ((buffer[i].to_bytes(1, 'big') == b'\x7e') or (buffer[i].to_bytes(1, 'big') == b'\x7d')):
				self.buffer += b'\x7d' 
				#print(self.buffer)
				self.buffer +=  (buffer[i] ^ 32).to_bytes(1, 'big')
				#print(self.buffer)
			else:
				self.buffer += buffer[i].to_bytes(1, 'big')
		self.buffer += b'\x7e'
		#print(self.buffer)
		self.serial.write(self.buffer)
		print('\n---------------------------\n')
		print('Enviando Quadro...')
		print('\n---------------------------\n')
		print('Quadro: ' + str(self.buffer))  
	
			
	def recebe(self):
		print('\n---------------------------\n')
		print('Aguardando Quadro...')
		print('\n---------------------------\n')
		while(True):
			buffer = self.serial.read()
				
			if (self.handle(buffer) == True): # Apos finalizar recebimento retorna True
					if(crc.CRC16(self.buffer).check_crc()): # verifica crc
						print('Dado Recebido: ' , self.buffer[0:len(self.buffer)-2]) 
						print('CRC Recebido: ' , self.buffer[-2:]) 
						return self.buffer[0:len(self.buffer)-2]
			
			if(len(buffer) == 0):
				return b''

						
	def handle(self, byte):
		if (self.estado == Estado.Ocioso): # Estado Ocioso
			if (byte == b'\x7e'):
				self.buffer = b''# inicio o buffer
				self.estado = Estado.Verifica
			else: 
				self.estado = Estado.Ocioso
			return False
		elif (self.estado == Estado.Verifica): # Estado de verificacao
			if (byte == b'\x7e'):
				self.estado = Estado.Verifica 
			elif (byte == b'\x7d'):
				self.estado = Estado.ESC
			else:
				self.buffer += byte # adiciono o byte no buffer de informacao
				self.estado = Estado.Recepcao
			return False
		elif (self.estado == Estado.Recepcao): # Estado de recepcao
			if (byte == b'\x7d'):
				self.estado = Estado.ESC
			elif (byte == b'\x7e'):
				self.estado = Estado.Ocioso
				return True # e o fim do quadro
			else:
				self.buffer += byte
				if (len(self.buffer) > self.bytes_max): # se tamanho do buffer maior que o tamanho max jogo pacote fora e volto para estado ocioso 
					self.buffer = b''                 # descarta buffer 
					self.estado = Estados.Ocioso 
			return False
		else: # Estado de Escape
			if (byte == b'\x7d' or byte == b'\x7e'): 
				self.buffer = b''
				self.estado = Estados.Ocioso
			else: 
				byteXor20 = int.from_bytes(byte, 'big') ^ 32 #transforma em 5e ou 5d, no envio eu tenho que colocar 7d antes para sinalizar que houve altercao do byte
				self.buffer += byteXor20.to_bytes(1, 'big') 
				self.estado = Estado.Recepcao 
			return False
       
    
