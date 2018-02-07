import unittest
import threading
import time
import random

from ThreadPool import ThreadPool

cnt_handle=0


class TaskTest(ThreadPool.Task):
    def __init__(self, name: str, handle):
        super().__init__(name)
        self.__handle = handle

    def execute(self):
        time.sleep(random.random() / 2)
        self.__handle(1)

class TestThreadPool(unittest.TestCase):

    def get_worker_thread_cnt(self):
        threads = threading.enumerate()
        thread_cnt = 0
        for thread in threads:
            if "ThreadPool worker thread" in thread.getName():
                thread_cnt += 1
        return thread_cnt

    def test_initialization(self):
        threadpool_list = []
        total_cnt_expected = 0
        for i in range(0,5):
            total_cnt_expected += i
            threadpool_list.append(ThreadPool(i,3,extra_debug_info=True))
            cnt = self.get_worker_thread_cnt()
            self.assertEqual(cnt,total_cnt_expected)



    def task_handle(self, i):
        global cnt_handle
        cnt_handle += i

    def test_task_execution(self):
        global cnt_handle
        thread_pool = ThreadPool()
        task_list = []
        total_cnt_expected = 10
        for i in range(total_cnt_expected):
            task_list.append(TaskTest("task %s" %i, self.task_handle))
        for task in task_list:
            thread_pool.add_task(task)

        time_start = time.time()
        while(True):
            if time.time()-time_start>1.0:
                break
            if cnt_handle == total_cnt_expected:
                break

        self.assertEqual(cnt_handle, total_cnt_expected)



if __name__ == "__main__":
    unittest.main()