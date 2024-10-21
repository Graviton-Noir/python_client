#!/usr/bin/env python3

import sys
import client
import time
import json
import pathlib

import typing

def readUserInput(sendMessage: typing.Callable[..., None]):
    try:
        while True:
            str = input("> ")
            
            sendMessage(str)
            
    except KeyboardInterrupt:
        print("")
        print("Interrupted")
        
def singleFileSender(fileName: str, sendMessage: typing.Callable[..., None]):
    
    try:
        file = open(fileName, "r")
        
        print("Opened file", fileName)
    except:
        print("Fail to open file", fileName)
        return
    
    try:
        fileContent = file.read()
    except Exception as e:
        print("File read error:", e)
        return
    finally:
        file.close()
    
    try:        
        ext = pathlib.Path(fileName).suffix
        
        if ext == '.json':
            payload = json.dumps(json.loads(fileContent)) # by doing so, fileContent is compacted (no '\n' for example)
        else:
            payload = fileContent
            
    except Exception as e:
        print("Json parsing failure:", e)
        return
    finally:
        file.close()
        
    sendMessage(payload)
    
    time.sleep(1) # waits for file to be sent
    
def multipleFileSender(sendMessage: typing.Callable[..., None]):
    
    try:
        while True:
            userInput = input("> ")
            
            singleFileSender(userInput, sendMessage)
            
    except KeyboardInterrupt:
        print("")
        print("Interrupted")

def main():
    print("--- Python client ---")
    print("")
    print("usage: py main.py            (user input mode)")
    print("       py main.py <fileName> (single file sender mode)")
    print("       py main.py -f         (multiple file sender mode)")
    
    cli = client.TCPClient()
    
    if cli.run() == False:
        return
    
    args = sys.argv[1:]
    
    if len(args) == 1:
        if args[0] == "-f":
            multipleFileSender(cli.pushMessage)
        else:
            singleFileSender(args[0], cli.pushMessage)
    else:
        readUserInput(cli.pushMessage)
    
    cli.stop()

if __name__ == "__main__":
    main()
