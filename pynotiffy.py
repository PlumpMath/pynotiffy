import os, fcntl
import errno
from cffi import FFI
ffi = FFI()
ffi.cdef("""

int inotify_init();

int inotify_add_watch(int fd, const char* name, uint32_t mask);

void block_read_events(int fd);

int define_in_modify();
int define_in_create();
int define_in_delete();
int event_size();

void (*callback_data)(int wd, int mask, int cookie, int length, const char* name);
        """)

C = ffi.verify(r"""
#include <errno.h>
#include <sys/inotify.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <fcntl.h>

void (*callback_data)(int wd, int mask, int cookie, int length, const char* name);

int define_in_create()
{
    return IN_CREATE;
}
int define_in_modify()
{
    return IN_MODIFY;
}
int define_in_delete()
{
    return IN_DELETE;
}

int event_size()
{
    return sizeof(struct inotify_event);
}


void block_read_events(int fd)
{
    unsigned int len = ((sizeof(struct inotify_event)+256) * 10); 
    char buffer[len];
    int rc = read(fd, buffer, len);
    struct inotify_event* bstruct = ((struct inotify_event*)buffer);
    int wd = bstruct->wd;
    uint32_t mask = bstruct->mask;
    uint32_t cookie = bstruct->cookie;
    uint32_t length = bstruct->len;
    callback_data(wd, mask, cookie, length, (const char*)bstruct->name); 
}

        """)

def get_in_attrs():
    return {"IN_MODIFY":C.define_in_modify(), 
            "IN_CREATE":C.define_in_create(),
            "IN_DELETE":C.define_in_delete(),
            "EVENT_SIZE":C.event_size(),
            }

def block_read_events(fd):
    C.block_read_events(fd)

def inotify_init():
    return C.inotify_init()

def inotify_add_watch(fd, name, mask):
    return C.inotify_add_watch(fd, name, mask)



@ffi.callback("void(int, int, int, int, const char*)")
def callback_data(wd, mask, cookie, length, name):
    obj = (mask, cookie, length, ffi.string(name))
    Watcher.handle_event(wd, obj)
C.callback_data = callback_data

attrs = get_in_attrs()
IN_MODIFY = attrs["IN_MODIFY"]
IN_CREATE = attrs["IN_CREATE"]
IN_DELETE = attrs["IN_DELETE"]
EVENT_SIZE = attrs["EVENT_SIZE"]


class Watcher:
    watchers = []
    event_dict = {}
    @staticmethod
    def handle_event(wd, evt):
        if not wd in Watcher.event_dict.keys():
            Watcher.event_dict[wd] = [evt]
        else:
            Watcher.event_dict[wd].append(evt)

    @staticmethod
    def block_poll_all():
        for watcher in Watcher.watchers:
            watcher.block_poll()

    def __init__(self, path):
        #Create the watcher
        self.watcher = inotify_init()
        Watcher.watchers.append(self)
        self.listeners = []
        self.watch_obj = inotify_add_watch(self.watcher, path, IN_MODIFY | IN_CREATE | IN_DELETE)
    def block_poll(self):
        block_read_events(self.watcher)
        if Watcher.event_dict.get(self.watch_obj) == None:
            return
        else:
            for x in Watcher.event_dict[self.watch_obj]:
                for listener in self.listeners:
                    listener(x)
            del Watcher.event_dict[self.watch_obj]

    def add_listener(self, listener):
        self.listeners.append(listener)


def main():
    w = Watcher("./test")
    def lnr(x):
        print "LNR!" + str(x)
    w.add_listener(lnr)
    import time
    while True:
        w.block_poll()
        time.sleep(0.2)

if __name__ == '__main__':
    main()
