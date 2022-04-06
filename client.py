import pickle
import socket
import threading
from pickle_data import get_event
from pickle_data import HEADERSIZE


try:
    sock_fd  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Initialization a UDP socket
    print("[+] socket created")
except socket.error as err:     # Catch any errors or exception thrown during initialization 
    print("[-] Error failed to create socket")
    raise

m_port = int(input("[*] Enter the port for socket :"))  # Input port number for socket  


def xor(x, y):
    res = []
    for i in range(1, len(y)): 
        if x[i] == y[i]: #flip bits when nesscary
            res.append('0')
        else:
            res.append('1')
    return ''.join(res)




def crc(data, G):

    msb = len(G) # get lenght of the divisor so we can segement the data  
    seg = data[0 : msb] # segment data
 
    while msb  < len(G): #start divission algorithim 
 
        if seg[0] == '1': #if divided in  xor to get next segment of focus
            seg= xor(G, seg) + data[msb] #carry down next bit
 
        else:  #if does not divide in the xor with 0 
            seg = xor('0'*msb, seg) + data[msb] #carry down next bit
 
        seg  += 1 #increment to mover across data
 
    if seg[0] == '1': #last loop of the algorithm 
        seg = xor(data, seg)
    else:
        seg = xor('0'*msb, seg)
 
    R = msb
    return R

def encoder(data, G):

    lenght_G = len(G)   
    data_crc = data + '0'*(lenght_G-1)  # add extra zeros for crc
    remainder =crc(data_crc, G) #find the reminder of the crc
    encodeddata = data + str(remainder) #add this remainder onto the end
    return encodeddata    


def decoder(data, G):
    lenght_G = len(G)   
    data_crc = data + '0'*(lenght_G-1)  # add extra zeros for crc
    remainder =crc(data_crc, G) #find the reminder of the crc

    return str(remainder)
 


#Subroutine for the thread which listen for any incoming socket connection 
def l_subroutine():
    try:
        sock_fd  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #Initialization a UDP socket
        print("[+] socket created")
    except socket.error as err:     # Catch any errors or exception thrown during initialization 
        print("[-] Error failed to create socket")
        raise

    try:
        sock_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #Setting socket option to reuse the addresss
        try:
            sock_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)   #Setting socket option to reuse the port
        except AttributeError:
            print("[-] Error setting option")
            raise
    except socket.error as err:
        print("[-] Error setting option") 
        raise

    sock_fd.bind(('0.0.0.0', m_port)) #Binding the socket to port m_port
    while True:
        msg = sock_fd.recv(1024).decode()
                
        G = "1001" #same G on both peers

        R = decoder(msg, G)
    
        temp = "0" * (len(G) - 1) #if the remainder is all zeros 
        if R == temp:
            print("Remainder= "+ R + "no errors found")
        else:
            print("Remainder= "+ R + "errors detected")

            print("[+]peer_msg: {}".format(pickle.loads(msg)))


    


s_thread = threading.Thread(target=l_subroutine)    #Creating a thread for listening on the port
s_thread.daemon = True  # Making the thread low priority daemon in order to use it as backgorund process
sock_fd.close() #closing any open sockets
s_thread.start()

try:
    sock_fd  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #Initialization a UDP socket
    print("[+] socket created")
except socket.error as err:     # Catch any errors or exception thrown during initialization 
    print("[-] Error failed to create socket")
    raise

try:
    sock_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #Setting socket option to reuse the addresss
    try:
        sock_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)   #Setting socket option to reuse the port
    except AttributeError:
        print("[-] Error setting option")
        raise
except socket.error as err:
    print("[-] Error setting option")    
    raise

while True:
    msg = raw_input('> ')
    addr = raw_input('[*] Enter the address of peer :') #Taking peer_address as input from userv
    port = int(input('[*] Enter the port of peer : '))  #Takign peer_port as input from user

    bin_data  = pickle.dumps(input) #covert string to binary
    G= "1001"                                           #four bit checker
    msg = encoder(bin_data,G)


    if msg == "EVENT":
        pkl_data = get_event()
        sock_fd.sendto(pkl_data, (addr, port))
    elif msg == "UPDATE":
        id_x = raw_input('[*] x coordinate :')
        id_y = raw_input('[*] x coordinate :')
        val = raw_input('[*] new value :')


    else:
        sock_fd.sendto(msg, (addr, port))


