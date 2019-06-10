import sys
if sys.platform == in ("linux", "darwin"):
    import readline

import language
from values import NoneValue
from languageInterpreter import KB

dev = len(sys.argv) > 1 and sys.argv[1] == "dev"

while True:
    try:
        KB.set_normal_term()
        cmd = input("$> ")
        KB.set_getch_term()
        if cmd in ("quit", "exit"):
            break
        if cmd == "global":
            print(language.globalSymbolTable)
            continue
        if cmd == "reset":
            language.globalSymbolTable.clear()
            continue
        if cmd == "help":
            print("help:       print this message")
            print("exit/quit:  exit inerpreter")
            print("global:     show global symbol table")
            print("reset:      reset global symbol table")
            continue
        
        res, err = language.run("<stdin>", cmd, dev=dev)
        if err:
            print(err)
        elif not isinstance(res, NoneValue):
            print(repr(res))
    except KeyboardInterrupt:
        print()
        if sys.platform == "ios":
            break
    except EOFError:
        break
print()
print("Goodbye")
