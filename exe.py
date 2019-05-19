import os
import sys
if sys.platform != "ios":
    import readline

import language
from languageInterpreter import KB

if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1]) as f:
            res, err = language.run(sys.argv[1], f.read())
            if err:
                print(err)
    else:
        print("File not found")
else:
    print("No file specified")