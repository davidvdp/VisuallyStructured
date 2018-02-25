from queue import Queue
from queue import Empty
from threading import Thread
import logging
import sys, traceback


class ThreadPool(object):
    class Task(object):
        """
        Task objects are used by the the threadpool; their execute function is called by the worker thread.
        Derive tasks from this class.
        """

        def __init__(self, name):
            self.name = name

        def execute(self):
            """
            This function is called by the worker thread and should contain task execution code.
            :return:
            """
            raise NotImplementedError("execute function has not been implemented")

    def __init__(self, nr_worker_threads=5, max_queue_size=100, extra_debug_info=False):
        self.__task_queue = Queue(max_queue_size)
        # self.__working_queue = Queue(nr_worker_threads)
        self.__extra_debug_info = extra_debug_info
        for i in range(nr_worker_threads):
            thread_name = "ThreadPool worker thread %s" % i
            t = Thread(target=self.__worker, args=[thread_name])
            t.daemon = True
            t.setName(thread_name)
            t.start()

    def __worker(self, thread_id: str):
        logging.info("started worker thread %s" % thread_id)
        while True:
            if self.__extra_debug_info: logging.debug("'%s' is waiting for a task." % (thread_id))
            task = self.__task_queue.get()
            if self.__extra_debug_info: logging.debug("'%s' got task '%s' from task queue" % (thread_id, task.name))
            try:
                task.execute()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                # formatted_lines =
                logging.error(traceback.format_exc())

            if self.__extra_debug_info: logging.debug("'%s' executed task '%s' from task queue" % (thread_id, task.name))
            # task.done()
            # if self.__extra_debug_info: logging.info("'%s' has been set to DONE." % (task.name))

    def add_task(self, task: Task):
        self.__task_queue.put_nowait(task)
        if self.__extra_debug_info: logging.debug("Added task %s to task queue." % task.name)
