import random
import numpy as np
import time
import pickle
import fcntl
from cqc.pythonLib import CQCConnection, qubit
import socket

TEMPLATE = """
NAME : {}
BASES : {}
KEY : {}
SIFTED KEY : {}
"""


class Node:

    def __init__(self, name):
        self.conn = CQCConnection(name)
        self.name = name
        self.N = 0
        self.bases = []
        self.raw_key = []
        self.sifted_key = []
        self.remote_bases = []
        self.num = 1

    def __del__(self):
        self.conn.__exit__(None, None, None)

    def set_size(self, N):
        self.N = N
        # print(num)

    def send_classical_integer(self, to, integer):
        self.conn.sendClassical(to, integer.to_bytes(
            (integer.bit_length() + 7) // 8, byteorder="big"))

    def recv_classical_integer(self):
        return int.from_bytes(self.conn.recvClassical(), byteorder="big")

    def send_bases(self, to):
        msg = b''
        for i, base in enumerate(self.bases):
            msg += base.to_bytes(1, byteorder="big")
        self.conn.sendClassical(to, msg)
        print('sent bases to: ', to)

    def recv_bases(self):
        res = []
        print('Receiving bases information.....')
        msg = self.conn.recvClassical()
        
        for i in range(self.N):
            res.append(msg[i])
        print('Receive done')
        return res

    def compare_bases(self,photon_list):
        for i in range(self.N):
            if self.bases[i] == self.remote_bases[i] and photon_list[i]>0: 
                self.sifted_key.append(self.raw_key[i])

    def encode_qubit(self, bit, basis):
        q = qubit(self.conn)
        if bit == 1:
            q.X()
        if basis == 1:
            q.H()
        return q

    def send_qubits(self, to, soc): #sent by Alice to Eve
        no_of_photons_list = []
        for i in range(self.N):
            num_photons = self.photons_in_pulse(self.num)
            no_of_photons_list.append(num_photons)
            basis = random.randint(0, 1)
            bit = random.randint(0, 1)
            self.bases.append(basis)
            #if num_photons != 0 :
            self.raw_key.append(bit)
            
            for j in range(num_photons):
                q = self.encode_qubit(bit, basis)
                # actual qubit transfer
                self.conn.sendQubit(q, to)  
                soc.sendall(b'True')
                
        total=0 
        for ele in no_of_photons_list:
            total=total+ele  
            
        print('No of photons ', total)

        return no_of_photons_list

    def recv_qubits(self, photon_list, s): #used by Bob to receive qubits 
        """
            1. We'll recieve qubits in the form of stream that is being sent by Alice and store them in a list
            2. This base calculation for each pulse will be done after collecting the stream ----  This  might not even 
            be necessary since Alice ultimately shares bases but continuing for now
        """
        
        qubit_list = []
        
        start_recv = 'True'
        while start_recv=='True':
            q = self.conn.recvQubit()
            qubit_list.append(q)
            start_recv = s.recv(1024).decode()
        
              
        """Calculating bases for N pulses"""
        
        pickle_in2 = open("globallist.pickle", "rb")
        photon_list=pickle.load(pickle_in2)
        
        first_photon_in_pulse_index=0
        
        for i in range(self.N):
            
            #Decide the basis for this pulse
            basis = random.randint(0, 1)
            self.bases.append(basis)
            
            #Fetching the number of photons for this pulse
            photons_in_this_pulse = photon_list[i]
            
            #If the pulse is not empty, we append the basis and raw key for that pulse, otherwise we ignore it            
            if photons_in_this_pulse > 0:
                try:
                    q = qubit_list[first_photon_in_pulse_index]
                except:
                    print('Exception occurred')
                    print('Index to be found: ', first_photon_in_pulse_index)
                    print('Size of list: ', len(qubit_list))
                    self.raw_key.append(9)
                    print('Photons in this pulse: Index of first photon', photons_in_this_pulse, first_photon_in_pulse_index)
                    continue
                print('Qubit Received')
      
                if basis == 1:
                    q.H()
                self.raw_key.append(q.measure())
            else:
                #Now the raw_key size should be equal to N to avoid the index_error so we append 
                #a place holder value '9' in its place
                self.raw_key.append(9)
            
            print('photons in this pulse, index of first photon', photons_in_this_pulse, first_photon_in_pulse_index)
            
            #For next pulse we increment the pointer accordingly
            first_photon_in_pulse_index = first_photon_in_pulse_index + photons_in_this_pulse
            
        print('Basis calculation completed')
        print('raw key at Bob: ', self.raw_key)
        print('bases at Bob: ', self.bases)
            

    def __str__(self):
        return TEMPLATE.format(self.name, self.bases, self.raw_key, self.sifted_key)

    def photons_in_pulse(self, mean):
        return np.random.poisson(mean)

    def main(self):
        pass
