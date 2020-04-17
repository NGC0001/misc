import socket, ipaddress, threading, time
from contextlib import closing


def check_port(ip:str, port:int, timeout:float, results:dict):
    address = (ip, port)
    res:bool = True
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        if not sock.connect_ex(address) == 0:
            res = False
    results[address] = res


def check_net(IPNet, Port, SockTimeout:float=5.0, MaxThreads=50):
    results = {}
    threads = []
    for ip in ipaddress.IPv4Network(IPNet): 
        t = threading.Thread(
                target=check_port, args=[str(ip), Port, SockTimeout, results]
                )
        threads.append(t)
        t.start()
        while threading.active_count() > MaxThreads: # limit the number of threads.
            time.sleep(0.5)
    for t in threads:
        t.join()
    return results


WorkNet = '222.29.50.0/24' # 209
VpsNet = '163.47.9.0/24' # 169
SshPort = 22
WebPort = 80
SslPort = 443

results = check_net(WorkNet, SshPort)
for address, res in results.items():
    if res:
        print(address)

