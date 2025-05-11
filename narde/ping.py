
from re import findall
from subprocess import Popen, PIPE

def ping (host,ping_count):

    for ip in host:
        data = ""
        output= Popen(f"ping {ip} -c {ping_count}", stdout=PIPE, encoding="utf-8", shell=True)

        for line in output.stdout:
            data = data + line
            ping_test = findall("TTL", data)

        if ping_test:
            print(f"{ip} : Successful Ping")
        else:
            print(f"{ip} : Failed Ping")

nodes = ["0.0.0.0", "127.0.0.1"]

ping(nodes,3)