#!/usr/bin/python
from pynotiffy import *

def main():
    w = Watcher("./test")
    def lnr(x):
        print "Generic listener {0}".format(x)
    def create_lnr(x):
        print "Create Listener Called: {0}".format(x)
    def modify_lnr(x):
        print "Modify Listener Called: {0}".format(x)
    def delete_lnr(x):
        print "Delete Listener Called: {0}".format(x)
    def open_lnr(x):
        print "Open Listener Called: {0}".format(x)
    def access_lnr(x):
        print "Access Listener Called: {0}".format(x)
    w.add_listener(lnr)
    w.add_listener(create_lnr, mask=IN_CREATE)
    w.add_listener(modify_lnr, mask=IN_MODIFY)
    w.add_listener(delete_lnr, mask=IN_DELETE)
    w.add_listener(access_lnr, mask=IN_ACCESS)
    w.add_listener(open_lnr, mask=IN_OPEN)
    import time
    while True:
        w.poll()
        time.sleep(0.2)

if __name__ == '__main__':
    main()

