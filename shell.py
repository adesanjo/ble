#!/bin/env python3

import os
import readline

import language
from values import NoneValue

while True:
    try:
        cmd = input("$> ")
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
        elif not isinstance(res, NoneValue):
            print(repr(res))
    except KeyboardInterrupt:
        print()
    except EOFError:
        print()
        print("Goodbye")
        break
