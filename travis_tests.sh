#!/bin/bash

cat script.gdb | gdb --args python testpynotiffy.py --verbose
