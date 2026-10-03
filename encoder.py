import socket
import ssl
import threading

# --- YOUR STATION DIRECTORY ---
# Format: "Channel Number": ("Host", Port, "Path")
STATIONS = {
    "/1": ("livestreaming-node-4.srg-ssr.ch", 443, "/srgssr/rsc_de/mp3/128"), # Swiss Jazz (HTTPS)
    "/2": ("radio.lotustechnologieslk.net", 2020, "/stream/shaafmgarden"),    # Lotus FM (HTTP)
    "/3": ("ice1.somafm.com", 80, "/groovesalad-128-mp3"),
    "/4": ("cp11.serverse.com",443,"/proxy/nethfm/stream"), 
    "/5": ("dc02.onlineradio.voaplus.com",443,"/rhythmfm")                  # SomaFM (HTTP)
}


def handle_client(client_socket):
    try:
        # 1. Read what channel the ESP32 wants
        request_data = client_socket.recv(1024).decode('utf-8', errors='ignore')
        if not request_data: return
        
        # Extract the requested path (e.g., "/2")
        first_line = request_data.split('\r\n')[0]
        path = first_line.split(' ')[1]

        # Look up the station, default to /1 if it doesn't exist
        target_host, target_port, target_path = STATIONS.get(path, STATIONS["/1"])
        print(f"ESP32 requested Channel {path}. Switching to {target_host}...")
        
        # 2. Connect to the correct radio server
        with socket.create_connection((target_host, target_port)) as sock:
            # Wrap in SSL only if it's a secure 443 port
            if target_port == 443:
                context = ssl.create_default_context()
                secure_sock = context.wrap_socket(sock, server_hostname=target_host)
            else:
                secure_sock = sock 
            
            # 3. Ask for the stream and metadata
            request = (f"GET {target_path} HTTP/1.0\r\n"
                       f"Host: {target_host}\r\n"
                       f"Icy-MetaData: 1\r\n"
                       f"Connection: close\r\n\r\n")
            secure_sock.sendall(request.encode())
            
            # 4. Pipe the data to the ESP32
            while True:
                data = secure_sock.recv(4096)
                if not data: break
                client_socket.sendall(data)
    except Exception as e:
        pass
    finally:
        client_socket.close()

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8000))
    server.listen(5)
    print("Multi-Channel Proxy running on port 8000...")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()