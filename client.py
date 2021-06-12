#!/usr/bin/env python3.9
import socket
import ssl
import sys

def http_get(URL):
	redirect_status=[b'200',b'301',b'302',b'306',b'307',b'308']
	uses_ssl=True
	path=''
	if 'http' in URL:
		split_url=URL.split("//")
		uses_ssl = 's' in split_url[0]
		split_url=split_url[1].split("/",1)
		URL=split_url[0]
		if len(split_url) == 1:	
			path=''
		else:
			path=split_url[1]
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if uses_ssl:
		client_socket.connect((URL, 443))
		client_socket=ssl.wrap_socket(client_socket)
	else:
		client_socket.connect((URL, 80))
	request_header = b'GET /'+path.encode(encoding='UTF-8')+b'\r\n HTTP/1.0\r\nHost: '+URL.encode(encoding='UTF-8')+b'\r\nAccept-charset: UTF-8\r\n\r\n'
	client_socket.send(request_header)
	response = b''
	f=client_socket.makefile("rwb")
	status_line=f.readline(1024)
	if any(stat in status_line for stat in redirect_status) or b'200' in status_line:
		headers={}
		while True:
			incoming_str = f.readline(1024).decode("ASCII")
			print(incoming_str)
			if not incoming_str:
				break
			if not ':' in incoming_str:
				break
			incoming_pair = incoming_str.split(":",1)
			headers[incoming_pair[0].lower()]=incoming_pair[1].lower()
		if not b'200' in status_line:
			http_get(headers["location"].replace('//\r\n',''))
		else:
			for key, value in headers.items():
				if 'content-length' in key:
					data=f.read(int(value))
					sys.stdout.buffer.write(data)
				else:
					if 'transfer-encoding' in key and ' chunked' in value:
						block_size=1
						while block_size > 0:
							block_size=int(f.readline,16)
							message=f.read(block_size)
							sys.stdout.buffer.write(message)
							f.readline()
	else:
		print('error')		
	client_socket.close()

http_get(sys.argv[1])
