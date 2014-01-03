#!/usr/bin/python
from pynotiffy import *
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('dirs', metavar="N", type=str, nargs='+', help="The directories to watch")
    opts = parser.parse_args()
    watchers = []
    print opts
    for target in opts.dirs:
        watcher = Watcher(target)
        def lnr(x):
            print "Generic listener {0}".format(x)
        watcher.add_listener(lnr)
        watchers.append(watcher)
    import time
    while True:
        Watcher.poll_all()
        time.sleep(0.2)
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
    return
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

