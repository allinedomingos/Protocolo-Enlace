import Enq
import ARQ
import serial


print('Informar a porta serial')
print('Ex.: /dev/pts/2')
porta = input()

client_ser = serial.Serial(porta, 9600, timeout=20)

enq = Enq.Enquadramento(client_ser,byte_max=256)

quadro = ARQ.ARQ(enq)
while(True):
	print('Digite a mensagem que deseja enviar:\n')
	msg  = input()

	buffer = msg

	quadro.envia(buffer.encode('ascii'))
