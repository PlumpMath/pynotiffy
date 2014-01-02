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

class TestWatcher(unittest.TestCase):
    def setUp(self):
        #Create testdir
        if os.path.isdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        os.mkdir(TEST_DIR)

    def test_blocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        self.watcher.block_poll()
        self.assertEqual(self.insert_count,1)
        
    def test_nonblocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        self.watcher.poll()
        self.assertEqual(self.insert_count,1)

    def test_create_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        self.watcher.poll()
        self.assertEqual(self.insert_count,1)

    def test_exclude_create_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_DELETE)
        write_empty_file("test")
        self.watcher.poll()
        self.assertEqual(self.insert_count,0)

    def test_exclude_create_listener2(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_MODIFY)
        write_empty_file("test")
        self.watcher.poll()
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
        self.assertEqual(self.insert_count,1)

    def test_blocking_poll_all(self):
        pynotiffy.Watcher.block_poll_all()


def main():
    unittest.main()
if __name__ == '__main__':
    main()
