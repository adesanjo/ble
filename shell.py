#!/bin/env python3

import os

import language

while True:
    cmd = input(">>> ")
    if cmd in ("quit", "exit"):
        break
    if cmd in ("clear", "cls"):
        os.system("cls" if os.name == "nt" else "clear")
        continue
    if cmd == "global":
        print(language.globalSymbolTable)
        continue
    
    res, err = language.run("<stdin>", cmd)
    if err:
        print(err)
    elif res:
        print(repr(res))
