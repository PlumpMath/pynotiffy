#!/bin/bash

cat script.gdb | sudo gdb --args python testpynotiffy.py --verbose
