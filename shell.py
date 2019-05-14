import os
import sys
if sys.platform != "ios":
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
        if cmd == "reset":
            language.globalSymbolTable.clear()
            continue
        if cmd == "help":
            print("help:       print this message")
            print("cls/clear:  clear screen")
            print("exit/quit:  exit inerpreter")
            print("gobal:      show global symbol table")
            print("reset:      reset global symbol table")
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
