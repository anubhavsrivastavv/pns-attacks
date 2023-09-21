import argparse
import numpy
import pickle
import socket
from node import Node


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65321        # Port for connection


class Alice(Node):
    def __init__(self):
        #Socket initialisation for connection with Eve
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.s.connect((HOST, PORT))
        print('Connected to Eve..') 
        return super().__init__("Alice")

    def main(self):
        self.send_classical_integer("Bob", self.N)
        self.send_classical_integer("Eve", self.N)
        
        #Notify Eve to start receiving qubits
        self.s.sendall(b'True')
        print('Notified Eve to start receiving qubits...')

        #Send qubits to Eve
        photon_list = self.send_qubits("Eve",self.s)

        #Notify Eve to stop receiving qubits
        self.s.sendall(b'False')

        #Writing global structure of no of photons in a pulse
        pickle_in2 = open("globallist.pickle", "wb")
        pickle.dump(photon_list, pickle_in2)
        print('No. of photons in each pulse calculated in each pulse...')
        pickle_in2.close()
        self.s.sendall(b'True')
     

        print('Waiting for basis exchange at Alice...')

        #Receving bases from Bob
        self.remote_bases = self.recv_bases() 
        print('Received remote bases from Bob')
        
        #Sent bases to Bob
        self.send_bases("Bob")
        print('Sent bases to Bob')
        
        #Sent bases to Eve(classical channel)
        self.send_bases("Eve")
        print('Sent bases to Eve')
                
        print('Announced bases on classical channel.....(can be seen by Eve as well)')
        print('Bob \'s bases on Alice \'s side ',self.remote_bases)        
        print('Alice \'s bases on Alice \'s side  ', self.bases)
        self.compare_bases(photon_list)
        print('Bases have been compared')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Alice.')
    parser.add_argument('N', metavar='N', type=int,
                        help='Number of qubits to send to Bob (please be aware of simulaqron\'s max-qubits paramater')
    args = parser.parse_args()
    N = args.N
    alice = Alice()
    alice.set_size(N)
    alice.main()
    print(alice)
    
