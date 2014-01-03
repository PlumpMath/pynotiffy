import unittest
import pynotiffy
import os, sys
import shutil
TEST_DIR = "./test_scratch"

def write_empty_file(fname):
    fd = open("{test_dir}/{fname}".format(test_dir=TEST_DIR, fname=fname), "w")
    fd.close()

def modify_file(fname):
    fd = open("{test_dir}/{fname}".format(test_dir=TEST_DIR, fname=fname), "a+")
    fd.write("This is a modification\n")
    fd.flush()
    fd.close()

def delete_file(fname):
    os.unlink("{test_dir}/{fname}".format(test_dir=TEST_DIR, fname=fname))

class TestWatcher(unittest.TestCase):
    def setUp(self):
        #Create testdir
        if os.path.isdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        os.mkdir(TEST_DIR)
        pynotiffy.Watcher.watchers = []
        pynotiffy.Watcher.event_dict = {}

    def test_blocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,2)
        
    def test_nonblocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            print x
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)

    def test_create_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            print x
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)

    def test_exclude_create_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_DELETE)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,0)

    def test_exclude_create_listener2(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_MODIFY)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,0)

    def test_modify_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_MODIFY)
        write_empty_file("test")
        modify_file("test")
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)

    def test_exclude_modify_listener(self):
        write_empty_file("test")
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        modify_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,0)
   
    def test_delete_listener(self):
        write_empty_file("test")
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_DELETE)
        delete_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)
       
    def test_exclude_delete_listener(self):
        write_empty_file("test")
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_DELETE)
        write_empty_file("test2")
        modify_file("test")
        delete_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,0)

    def test_handle_more_than_one_event_per_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        modify_file("test")
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,3)

    def test_blocking_poll_all(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        modify_file("test")
        pynotiffy.Watcher.block_poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,3)

    def test_remove_from_poll_all_list_on_delete(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.watcher.close()
        self.assertEqual(len(pynotiffy.Watcher.watchers), 0)

    def test_poll_with_no_events(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.watcher.poll()
        self.watcher.close()
    def test_evt_with_None(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.watcher.handle_listeners((None, None, None, None))
        self.watcher.close()

def main():
    unittest.main()
if __name__ == '__main__':
    main()
