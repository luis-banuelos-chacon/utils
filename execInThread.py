    def execInThread(self, ins, method, *args):
        """Executes method in object instance on a separate thread.
        If a task is already executing on the instance, place on
        queue.
        """
        # function to execute after method execution
        def finished():
            # finish current execution
            ins._thread.quit()
            ins._thread.wait()

            # if a method is on queue, execute
            if len(ins._queue) > 0:
                ins._thread.started.connect(ins._queue.pop(0))
                ins._thread.start()
            else:
                ins.finished.disconnect()
                del ins._thread
                del ins._queue

        # create thread if not existing
        try:
            ins._thread
        except:
            ins._thread = QtCore.QThread()

        # add method to queue
        try:
            ins._queue.append(method)
        except:
            ins._queue = [method]

        # setup and execute thread
        if not ins._thread.isRunning():
            ins.moveToThread(ins._thread)
            ins._thread.started.connect(ins._queue.pop(0))
            ins.finished.connect(finished)
            ins._thread.start()
