import Enq
import ARQ
import serial

print('Informar a porta serial')
print('Ex.: /dev/pts/3')
porta = input()

client_ser = serial.Serial(porta, 9600, timeout=4)

enq = Enq.Enquadramento(client_ser,byte_max=256)

quadro = ARQ.ARQ(enq)
while(True):
	msg = quadro.recebe()

