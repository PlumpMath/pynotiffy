import unittest
import pynotiffy
import os, sys
import shutil
TEST_DIR = "./test_scratch"
TEST_FILE = "./test_scratch/file"

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
        if os.path.isdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        os.mkdir(TEST_DIR)
        pynotiffy.Watcher.watchers = []
        pynotiffy.Watcher.event_dict = {}
    def tearDown(self):
        if os.path.isdir(TEST_DIR):
            shutil.rmtree(TEST_DIR)

    def test_watching_single_file(self):
        fd = open(TEST_FILE, "w")
        fd.write("test\n");
        fd.close()
        self.watcher = pynotiffy.Watcher(TEST_FILE)
        self.count = 0
        def lnr(evt):
            self.count += 1
        self.watcher.add_listener(lnr)
        fd = open(TEST_FILE, "a")
        fd.write("test\n");
        fd.close()
        os.rename(TEST_FILE, TEST_FILE+"2")
        os.rename(TEST_FILE+"2", TEST_FILE)
        os.unlink(TEST_FILE)
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.count, 4)

    def test_blocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr)
        write_empty_file("test")
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,3)
        
    def test_nonblocking_poll(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        def lnr(x):
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
        self.assertEqual(self.insert_count,6)

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
        self.assertEqual(self.insert_count,6)

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

    def test_multiple_listeners(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        self.insert_count2 = 0
        def lnr(x):
            self.insert_count += 1
        def lnr2(x):
            self.insert_count2 += 1
        self.watcher.add_listener(lnr, pynotiffy.IN_CREATE)
        self.watcher.add_listener(lnr2, pynotiffy.IN_CREATE)
        write_empty_file("test")
        modify_file("test")
        pynotiffy.Watcher.block_poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,self.insert_count2)
    def test_multiple_listeners2(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        self.insert_count2 = 0
        def lnr(x):
            self.insert_count += 1
        def lnr2(x):
            self.insert_count2 += 1
        self.watcher.add_listener(lnr, pynotiffy.IN_MODIFY)
        self.watcher.add_listener(lnr2, pynotiffy.IN_MODIFY)
        write_empty_file("test")
        modify_file("test")
        pynotiffy.Watcher.block_poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,self.insert_count2)
    def test_multiple_listeners3(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        self.insert_count2 = 0
        def lnr(x):
            self.insert_count += 1
        def lnr2(x):
            self.insert_count2 += 1
        self.watcher.add_listener(lnr, pynotiffy.IN_MODIFY)
        self.watcher.add_listener(lnr2, pynotiffy.IN_MODIFY)
        write_empty_file("test")
        modify_file("test")
        pynotiffy.Watcher.poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,self.insert_count2)
    def test_multiple_listeners3(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR)
        self.insert_count = 0
        self.insert_count2 = 0
        def lnr(x):
            self.insert_count += 1
        def lnr2(x):
            self.insert_count2 += 1
        self.watcher.add_listener(lnr, pynotiffy.IN_MODIFY | pynotiffy.IN_CREATE)
        self.watcher.add_listener(lnr2, pynotiffy.IN_MODIFY | pynotiffy.IN_CREATE)
        write_empty_file("test")
        modify_file("test")
        self.watcher.block_poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,self.insert_count2)

    
    def test_creating_masked_listener(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR, mask=pynotiffy.IN_DELETE)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,0)
    def test_creating_masked_listener2(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR, mask=pynotiffy.IN_CREATE)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        self.watcher.poll()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)
    def test_creating_masked_listener_with_poll_all(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR, mask=pynotiffy.IN_CREATE)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        pynotiffy.Watcher.block_poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)
    def test_creating_masked_listener_with_poll_all2(self):
        self.watcher = pynotiffy.Watcher(TEST_DIR, mask=pynotiffy.IN_CREATE)
        self.insert_count = 0
        def lnr(x):
            self.insert_count += 1
        self.watcher.add_listener(lnr, mask=pynotiffy.IN_CREATE)
        write_empty_file("test")
        pynotiffy.Watcher.poll_all()
        self.watcher.close()
        self.assertEqual(self.insert_count,1)
def main():
    unittest.main()
if __name__ == '__main__':
    main()
