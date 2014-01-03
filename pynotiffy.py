import os, fcntl
import errno
from cffi import FFI
ffi = FFI()
ffi.cdef("""

int inotify_init();

int inotify_add_watch(int fd, const char* name, uint32_t mask);
int inotify_rm_watch(int fd, int wd);
void pynotiffy_close(int fd);

void read_events(int fd);
void block_read_events(int fd);

int define_in_modify();
int define_in_create();
int define_in_delete();
int define_in_access();
int define_in_open();
int define_in_close_write();
int define_in_close_nowrite();
int define_in_attrib();
int event_size();

void (*callback_data)(int wd, int mask, int cookie, int length, const char* name);
        """)

C = ffi.verify(r"""
#include <errno.h>
#include <sys/inotify.h>
#include <sys/ioctl.h>
#include <sys/select.h>
#include <sys/time.h>
#include <unistd.h>

#include <fcntl.h>

void pynotiffy_close(int fd)
{
    close(fd);
}
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
int define_in_access()
{
    return IN_ACCESS;
}
int define_in_open()
{
    return IN_OPEN;
}
int define_in_close_nowrite()
{
    return IN_CLOSE_NOWRITE;
}
int define_in_close_write()
{
    return IN_CLOSE_WRITE;
}
int define_in_attrib()
{
    return IN_ATTRIB;
}
int event_size()
{
    return sizeof(struct inotify_event);
}


void read_events(int fd)
{
    unsigned int len = 0; 
    ioctl(fd, FIONREAD, &len);
    
    fd_set r;
    FD_ZERO(&r);
    FD_SET(fd, &r);
    struct timeval tv;
    tv.tv_sec = 0; 
    tv.tv_usec = 0;

    int rv = select(fd+1, &r, NULL, NULL, &tv);
    if (rv == -1)
        printf("There was an error.\n");
    if (FD_ISSET(fd, &r))
    {
        char buffer[len];
        int rc = read(fd, buffer, len);
        int ptr = 0;
        while (ptr < rc)
        {
            struct inotify_event* bstruct = ((struct inotify_event*)buffer+ptr);
            int wd = bstruct->wd;
            uint32_t mask = bstruct->mask;
            uint32_t cookie = bstruct->cookie;
            uint32_t length = bstruct->len;
            callback_data(wd, mask, cookie, length, (const char*)bstruct->name); 
            ptr += sizeof(struct inotify_event)+length;
        }
    }
}

void block_read_events(int fd)
{
    unsigned int len = 0; 
    ioctl(fd, FIONREAD, &len);
    char buffer[len];
    int rc = read(fd, buffer, len);
    int ptr = 0;
    while (ptr < rc)
    {
        struct inotify_event* bstruct = ((struct inotify_event*)(buffer+ptr));
        int wd = bstruct->wd;
        uint32_t mask = bstruct->mask;
        uint32_t cookie = bstruct->cookie;
        uint32_t length = bstruct->len;
        callback_data(wd, mask, cookie, length, (const char*)bstruct->name); 
        ptr += sizeof(struct inotify_event)+length;
    }
}
        """)

def get_in_attrs():
    return {"IN_MODIFY":C.define_in_modify(), 
            "IN_CREATE":C.define_in_create(),
            "IN_DELETE":C.define_in_delete(),
            "IN_ACCESS":C.define_in_access(),
            "IN_CLOSE_WRITE":C.define_in_close_write(),
            "IN_CLOSE_NOWRITE":C.define_in_close_nowrite(),
            "IN_OPEN":C.define_in_open(),
            "IN_ATTRIB":C.define_in_attrib(),
            "EVENT_SIZE":C.event_size(),
            }

#def block_read_events(fd):
#    C.block_read_events(fd)
#def read_events(fd):
#    C.read_events(fd)
#def inotify_init():
#    return C.inotify_init()
#def pynotiffy_close(fd):
#    return C.pynotiffy_close(fd)

#def inotify_add_watch(fd, name, mask):
#    return C.inotify_add_watch(fd, name, mask)
#def inotify_rm_watch(fd, wd):
#    return C.inotify_rm_watch(fd, wd)



@ffi.callback("void(int, int, int, int, const char*)")
def callback_data(wd, mask, cookie, length, name):
    if length == 0:
        name_str = None
    else:
        name_str = ffi.string(name)
    obj = (mask, cookie, length, name_str)
    Watcher.handle_event(wd, obj)
C.callback_data = callback_data

attrs = get_in_attrs()
IN_MODIFY = attrs["IN_MODIFY"]
IN_CREATE = attrs["IN_CREATE"]
IN_DELETE = attrs["IN_DELETE"]
IN_ACCESS = attrs["IN_ACCESS"]
IN_CLOSE_WRITE = attrs["IN_CLOSE_WRITE"]
IN_CLOSE_NOWRITE = attrs["IN_CLOSE_NOWRITE"]
IN_CLOSE = IN_CLOSE_NOWRITE | IN_CLOSE_WRITE
IN_ATTRIB = attrs["IN_ATTRIB"]

IN_OPEN = attrs["IN_OPEN"]
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

    @staticmethod
    def poll_all():
        for watcher in Watcher.watchers:
            watcher.poll()

    def __init__(self, path, mask=None):
        if mask == None: 
            mask = IN_MODIFY | IN_CREATE | IN_DELETE | IN_ACCESS | IN_OPEN | IN_CLOSE_NOWRITE | IN_CLOSE_WRITE | IN_ATTRIB
        self.watcher = C.inotify_init()
        Watcher.watchers.append(self)
        self.closed = False
        self.listeners = []
        self.listener_masks = {}
        self.watch_obj = C.inotify_add_watch(self.watcher, path, mask)
    def close(self):
        self.closed = True
        C.inotify_rm_watch(self.watcher, self.watch_obj)
        C.pynotiffy_close(self.watcher)
        Watcher.watchers.remove(self)
    def __del__(self):
        if not self.closed:
            self.close()
    def block_poll(self):
        C.block_read_events(self.watcher)
        self.handle_events()
    def poll(self):
        C.read_events(self.watcher)
        self.handle_events()
    def handle_events(self):
        if Watcher.event_dict.get(self.watch_obj) == None:
            return
        else:
            for x in Watcher.event_dict[self.watch_obj]:
                self.handle_listeners(x)
            del Watcher.event_dict[self.watch_obj]
    def handle_listeners(self, evt):
        for listener in self.listeners:
            listener(evt)
        for mask in self.listener_masks.keys():
            if mask & evt[0]: 
                for listener in self.listener_masks[mask]:
                    listener(evt)


    def add_listener(self, listener, mask=None):
        if mask == None:
            self.listeners.append(listener)
            return
        if self.listener_masks.get(mask) == None:
            self.listener_masks[mask] = [listener]
        else:
            self.listener_masks[mask].append(listener)

