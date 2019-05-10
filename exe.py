#!/bin/env python3

import sys
import readline

import language

if len(sys.argv)>1:
    with open(sys.argv[1]) as f:
        res, err = language.run(sys.argv[1], f.read())
        if err:
            print(err)
else:
    print("No file specified")