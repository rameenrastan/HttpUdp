import argparse
import socket
import sys
from packet import Packet
import ipaddress

# test client to test server-socket
def run(host, port, router_address, router_port):
    """ init and run client server """
    host = ipaddress.ip_address(socket.gethostbyname(host))
    # create socket instance
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print("Establishing connection...")
        packet = Packet(packet_type=2,
                        seq_num=1,
                        peer_ip_addr=host,
                        peer_port=port,
                        payload="SYN".encode("utf-8"))
        sock.sendto(packet.to_bytes(), (router_address, router_port))
        sock.settimeout(10)
        server_response = sock.recv(1024)
        print("Sent SYN")
        response_packet = Packet.from_bytes(server_response)
        response_message = response_packet.payload.decode("utf-8")
        if response_packet.packet_type == 3:
            packet = Packet(packet_type=1,
                        seq_num=1,
                        peer_ip_addr=host,
                        peer_port=port,
                        payload="ACK".encode("utf-8"))
            sock.sendto(packet.to_bytes(), (router_address, router_port))
            print("Sent ACK")
            print("Connection Established...")
            while True:
                request = input("Please input your request:")
                packet = Packet(packet_type=0,
                    seq_num=1,
                    peer_ip_addr=host,
                    peer_port=port,
                    payload=request.encode("utf-8"))
                sock.sendto(packet.to_bytes(), (router_address, router_port))
                sock.settimeout(10)
                server_response = sock.recv(1024)
                response_packet = Packet.from_bytes(server_response)
                print(response_message)
    except Exception as e:
        print("Error occured: {}".format(str(e)))
        sys.exit(0)
    finally:
        sock.close()


''' use argparse when setting up server '''
parser = argparse.ArgumentParser()
parser.add_argument("-host", help="server host", default="localhost")
parser.add_argument("-port", help="server port", type=int, default=8080)
parser.add_argument("-router-address", help="router address", default="localhost")
parser.add_argument("-router-port", help="router port", type=int, default=3000)
args = parser.parse_args()

run(args.host, args.port, args.router_address, args.router_port)
