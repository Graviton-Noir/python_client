#!/usr/bin/env python3

import socket
import threading
import time

from typing import List

class TCPClient:

    def __init__(self):
        self.interruptEvent = threading.Event()
        
        self.client : socket.socket = None
        self.senderThread : threading.Thread = None
        
        self.receiverThread : threading.Thread = None
        
        self.messageRecv : List[str] = []
        self.sendMutex = threading.Lock()
        
        self.messageToSend : List[str] = []
        self.recvMutex = threading.Lock()
        
        
    def run(self):
        
        addr = ("127.0.0.1", 1234)
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            self.client.connect(addr)
            print("Connected to", addr)
        except:
            print("Failed to connect to", addr[0], addr[1])
            self.interruptEvent.set()
            return False
        
        self.senderThread = threading.Thread(target=self.sendMessage, args=[self.interruptEvent])
        self.senderThread.start()
        
        self.receiverThread = threading.Thread(target=self.recvMessage, args=[self.interruptEvent])
        self.receiverThread.start()
        
        return True
        
    def stop(self):
        
        self.interruptEvent.set()
        
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print("Client shutdown failure")
        finally:
            self.client.close()
            
        if self.senderThread != None:
            self.senderThread.join()
            
        if self.receiverThread != None:
            self.receiverThread.join()
            
    def sendMessage(self, interruptEvent: threading.Event):
        
        while interruptEvent.is_set() == False and self.client.fileno() != -1:
            if len(self.messageToSend) != 0:
                
                message: str = ""
                
                with self.sendMutex:
                    message = self.messageToSend.pop(0).encode("utf-8")
            
                try:
                    self.client.sendall(message)
                    print("Send", message)
                except:
                    print("Client disconnected")
                    self.interruptEvent.set()
            
            time.sleep(0.1) # sleep for 100ms
            
    def recvMessage(self, interruptEvent: threading.Event):
        
        while interruptEvent.is_set() == False and self.client.fileno() != -1:
            
            buf : bytes = b''
            
            try:
                while interruptEvent.is_set() == False:
                    chunk : bytes = self.client.recv(1024).strip()
                    buf += chunk
                    if len(chunk) != 1024:
                        break
                
                if len(buf) == 0:
                    continue
                    
                message: str = buf.decode("utf-8")
                
                print("Received:", message)
                
                #if len(self.messageRecv) != 0:
                #    print("Warning: recv message buffer not empty")
                #
                #with self.recvMutex:
                #    self.messageRecv.append(message)
                
            except Exception as e:
                print("Recv thread Stopped")
                interruptEvent.set()
                
    def pushMessage(self, message: str):
        
        with self.sendMutex:
            self.messageToSend.append(message)
        
    def pullMessage(self):
        
        if len(self.messageRecv) != 0:
            with self.recvMutex:
                return self.messageRecv.pop(0)
        
        return ""
