# server module handling server-socket creation, life-cycle and user requests

import argparse
import os
import socket
import sys
from threading import Thread
import util
from packet import Packet
import ipaddress 
import time
directory = "server-files"
global connection_established
connection_established = False
# initialize server with params from user
def init_server():
    args = parse()
    run(port=args['p'], verbose=args['v'])


# perform user help request
def perform_help():
    print('\nhttpfs is a simple file server.')
    print('Usage:\n\thttpfs [-v] [-p PORT] [-d PATH-TO-DIR]\n')
    print('The commands are:\n\n\t-v\tPrints debugging messages.')
    print('\t-p\tSpecifies the port number that the server will listen and serve at. Default is 8080.')
    print('\t-d\tSpecifies the directory that the server will use to read/write requested files. \n\t\tDefault is the current directory when launching the application\n')


# initialize server with params
def parse():
    parser = argparse.ArgumentParser(add_help=False)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # add arguments to CLI
    parser.add_argument('-h', action="store_true")
    parser.add_argument('-v', action="store_true")
    parser.add_argument('-p', type=int, default="8080")
    parser.add_argument('-d', type=str, default="server-files")
    args = parser.parse_args()
    if args.h:
        perform_help()
    else:
        global directory
        directory = args.d
        return vars(args)


# run server
def run(host='localhost', port=8080, verbose=False):

    # create socket and bind it
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if verbose: print('Httpfs socket created...')
    try:
        sock.bind((host, port))
        if verbose: print('Httpfs socket binding has completed...')
    except Exception as e:
        print('Httpfs has encountered an error: %s' % e)
        sys.exit()

    # listen on socket
    if verbose: print("Httpfs socket now listening at: {host: '%s', port: %s}" % (host, port))

    # listen for any incoming connections
    while True:
        conn, addr = sock.recvfrom(1024)
        ip, port = str(addr[0]), str(addr[1])
        if verbose: print('Received connection from: {ip: %s, port: %s}' % (ip, port))
        try:
            Thread(target=client_thread, args=(sock, conn, ip, port)).start()
        except Exception as e:
            print('Httpfs error encountered: %s' % e)
    # close socket
  


# handle user requests
def client_thread(sock, conn, ip, port):
    global connection_established
    ip = ipaddress.ip_address(socket.gethostbyname(ip))
    request_packet = Packet.from_bytes(conn)
    request = request_packet.payload.decode('utf-8')
    print(request_packet.packet_type)
    print(connection_established)
    print('Connection {ip: %s, port: %s} requested: %s' % (ip, port, request))
    if connection_established == False and request_packet.packet_type == 2:
        print(sock)
        response_packet = Packet(packet_type=3, seq_num=1, peer_ip_addr=request_packet.peer_ip_addr, peer_port=request_packet.peer_port, payload="SYN-ACK".encode("utf-8"))
        print(response_packet.payload.decode('utf-8'))
        sock.sendto(response_packet.to_bytes(), ('127.0.0.1', 3000))
        connection_established = True
    elif connection_established == True and request_packet.packet_type == 0:
        # prepare response to send back to client
        response = process_request(directory, request)

        response_packet = Packet(packet_type=0, seq_num=1, peer_ip_addr=request_packet.peer_ip_addr, peer_port=request_packet.peer_port, payload=response.encode("utf-8"))
        print(response_packet.payload.decode('utf-8'))
        sock.sendto(response_packet.to_bytes(), ('127.0.0.1', 3000))
        
        print('Connection from: {ip: %s, port: %s} has closed...' % (ip, port))
    


# handle user request (assumption is that filenames have no spaces)
def process_request(directory, request):
    if request == "get /":
        return util.list_files(directory)
    elif request.startswith("get /"):
        filename = request.replace("get /", "")
        return util.read_file(directory, filename)
    elif request.startswith("post /"):
        # obtain all request terms
        terms = request.split()
        # obtain filename
        filename = terms[1].replace("/", "")
        # obtain content
        content = ""
        content_terms = terms
        content_terms.pop(0)
        content_terms.pop(0)
        for t in content_terms:
            content = content + " " + t
        return util.overwrite_file(directory, filename, content)
    else:
        return "sorry, '%s' command does not exist" % request


def main():
    init_server()


if __name__ == "__main__":
    main()
