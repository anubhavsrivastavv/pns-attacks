import random
import pickle
from node import Node
import argparse
import fcntl
import socket

# Standard loopback interface address (localhost) and port for connecting with Alice
HOST = '127.0.0.1'  
PORT = 65321

# Standard loopback interface address (localhost) and port for connecting with Bob
HOST_Bob, PORT_Bob = '127.0.0.1', 65330


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print('Listening to Alice...')
    conn, addr = s.accept()


class Eve(Node):
    def __init__(self, p):
        self.p = p

        self.sb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sb.connect((HOST_Bob, PORT_Bob))
        print('Connected to Bob..')
        return super().__init__("Eve")

    def recv_qubits_and_strategy(self, to):
        qubit_list = []

        with conn:
            print('Connected to Alice', addr)
            start_recv = conn.recv(1024).decode()
            
            #Start receiving qubits once Alice starts sending them 
            while start_recv == 'True':
                q = self.conn.recvQubit()
                qubit_list.append(q)
                start_recv = conn.recv(1024).decode()

            #Can now access global structure consisting of no. of photons in each pulse
            global_file_access_flag = conn.recv(1024).decode()
            if global_file_access_flag == 'True':
                print('Starting to access global structure...')
                pickle_in2 = open("globallist.pickle", "rb")
                photon_list = pickle.load(pickle_in2)

        #Identifying single bit photon pulses
        print("Identifying single photon pulses")
        index = 0
        no_of_stolen_photons=0
        stolen_photons = []
        for ele in photon_list:

            if(ele <= 1):
                #stolen_photons.append(9)
                pass
            else:
                # pass
                # split the photon and store in Eve's List
                stolen_photons.append(qubit_list[index+ele-1])
                # print(qubit_list[index+ele-1])
                # qubit_list[index+ele-1] =   #empty out the qubit from qubit list, not deleting element so that indices don't shift while handling empty pulses at Bob ------- this is not working since NoneType cannot be sent via send_qubit method
                #photon_list[ele] = index+ele
                del qubit_list[index+ele-1]
                ele = ele-1
                no_of_stolen_photons=no_of_stolen_photons+1
                # print(index)                    #reduce one photon in photon list

            index = index+ele


        # update the photon list
        pickle_out = open("globallist.pickle", "wb")
        pickle.dump(photon_list, pickle_out)
        print('Written the updated global structure to pickle file')
        pickle_out.close()
        del pickle_out

    
        # Sending this updated qubit list to Bob
        print('Waiting to send qubits to Bob')
        self.sb.sendall(b'True')
        self.send_updated_qubits("Bob", qubit_list, self.sb)
        self.sb.sendall(b'False')

        #Measure the stolen photon bases
        for i in range(no_of_stolen_photons):
            if random.random() < self.p:
                basis = random.randint(0,1)
                self.bases.append(basis)
                if basis == 1:
                    stolen_photons[i].H()
                outcome = stolen_photons[i].measure()
                self.raw_key.append(outcome)
                q2 = self.encode_qubit(outcome, basis)
                self.conn.sendQubit(q2, to)
            else:
                self.conn.sendQubit(stolen_photons[i], to)
                self.raw_key.append("X")


    def compare_bases(self):
        for i in range(self.N):
            if self.bases_1[i] == self.bases_2[i]:
                self.sifted_key.append(self.raw_key[i])

    def send_updated_qubits(self, to, qubitlist, soc):
        for ele in qubitlist:
            self.conn.sendQubit(ele, to)
            soc.sendall(b'True')
        print("Sending updated qubit list to Bob...")

    def main(self):
        self.set_size(self.recv_classical_integer())
        print(self.N)

        self.recv_qubits_and_strategy("Bob")

        self.bases_1 = self.recv_bases()  
        print('Bases received once')
        print('Bob\'s bases : ', self.bases_1)

        self.bases_2 = self.recv_bases()
        print('Alice\'s bases : ', self.bases_2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Eve.')
    parser.add_argument('p', metavar='p', type=float,
                        help='Eve strategy (probability to measure and resend)')
    args = parser.parse_args()
    eve = Eve(args.p)
    eve.main()
    print(eve)
    print(eve.bases_1)
    print(eve.bases_2)
