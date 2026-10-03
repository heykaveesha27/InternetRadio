import socket
import ssl
import threading

# --- YOUR STATION DETAILS ---

#Format: "Channe"

STATIONS = {
    "/1": ("livestreaming-node-4.srg-ssr.ch", 443, "/srgssr/rsc_de/mp3/128"), # Swiss Jazz (HTTPS)
    "/2": ("radio.lotustechnologieslk.net", 2020, "/stream/shaafmgarden"),    # Lotus FM (HTTP)
    "/3": ("ice1.somafm.com", 80, "/groovesalad-128-mp3")                     # SomaFM (HTTP)
}

TARGET_HOST = "radio.lotustechnologieslk.net" 
TARGET_PORT = 2020 # Use 443 for HTTPS, 80 for HTTP
TARGET_PATH = "/stream/shaafmgarden" # e.g., "/stream"

def handle_client(client_socket):
    try:
        # 1. Catch and discard the ESP32's initial connection request
        client_socket.recv(1024)
        
        # 2. Connect to the heavy/secure radio server
        context = ssl.create_default_context()
        with socket.create_connection((TARGET_HOST, TARGET_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=TARGET_HOST) as secure_sock:
                
                # 3. Ask for the raw stream AND the hidden metadata (Icy-MetaData: 1)
                request = (f"GET {TARGET_PATH} HTTP/1.0\r\n"
                           f"Host: {TARGET_HOST}\r\n"
                           f"Icy-MetaData: 1\r\n"
                           f"Connection: close\r\n\r\n")
                secure_sock.sendall(request.encode())
                
                print(f"Connected to {TARGET_HOST}. Forwarding raw bytes to ESP32...")
                
                # 4. Pipe the raw, unaltered data directly to the ESP32
                while True:
                    data = secure_sock.recv(4096)
                    if not data:
                        break
                    client_socket.sendall(data)
    except Exception as e:
        print(f"Connection dropped: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8000))
    server.listen(5)
    print("Raw TCP Proxy running on port 8000... Waiting for ESP32.")
    
    while True:
        client_socket, addr = server.accept()
        print(f"ESP32 Connected from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()