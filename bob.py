from node import Node
import pickle
import fcntl
import socket

#Standard Host and port for connection with Eve
HOST, PORT = '127.0.0.1', 65330  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    s.bind((HOST, PORT))
    s.listen()
    print('Listening to Alice...')
    conn, addr = s.accept()

class Bob(Node):
    def __init__(self):
        return super().__init__("Bob")

    def main(self):
        self.set_size(self.recv_classical_integer())
      
        
        with conn:
            print('Connected to Alice', addr)
            
            start_recv = conn.recv(1024).decode()
            
            if start_recv=='True':
                #If notified to receive the qubits from Eve, load the structure containing no. of photons in each pulse
                pickle_in2 = open("globallist.pickle", "rb")
                photon_list=pickle.load(pickle_in2)

                #Start receiving the qubits
                self.recv_qubits(photon_list, conn)
                
                #Send bases to Alice and Eve over the classical channel
                self.send_bases("Alice") 
                self.send_bases("Eve")        
                
                #Receiving bases from Alice 
                self.remote_bases = self.recv_bases()    

                print('Bob \'s bases on Bob\'s side  ', self.bases) 
                print('Alice\'s bases on Bob\'s side ',self.remote_bases)        
                  
                #Compare the bases
                self.compare_bases(photon_list)
       

if __name__ == "__main__":
    bob = Bob()
    bob.main()
    print(bob)
