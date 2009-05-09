##############################################################################
#  The Combustion Flame Engine - pyflam3
#  http://combustion.sourceforge.net
#
#  Copyright (C) 2007 by Bobby R. Ward <bobbyrward@gmail.com>
#
#  The Combustion Flame Engine is free software; you can redistribute
#  it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; see the file COPYING.LIB.  If not, write to
#  the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.
##############################################################################
from __future__ import with_statement
import threading
import Queue
import traceback

__all__ = [ 'RenderJob'
          , 'RenderQueue'
          ]

def synchronized(lock):
    def wrap(func):
        def _impl(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return _impl
    return wrap


class RenderJob(object):
    _cancel = False
    _queued = False
    _running = False
    _completed = False
    _lock = threading.Lock()
    buffer = None
    stats = None
    progress = 0
    stage = 0
    args = {}

    def __init__(self, genome, buffer, cancel_cb=None, completed_cb=None,
            error_cb=None, **kwargs):
        self.genome = genome
        self.buffer = buffer
        self.cancel_cb = cancel_cb
        self.completed_cb = completed_cb
        self.error_cb = error_cb
        self.args = kwargs

    def _execute(self, **kwargs):
        self.args.update(kwargs)

        with self._lock:
            self._queued = False
            self._running = True

        try:
            self.stats = self.genome.render(self.buffer, **self.args)
        except Exception, e:
            self.process_error(e)
            return False
        finally:
            self._running = False

        return True

    def reset(self):
        with self._lock:
            if self._queued or self._running:
                raise RuntimeError('cannot reset while the '\
                                   'job is running or queued')
            self._cancel = False
            self._completed = False
            self.progress = 0
            self.stage = 0

    def process_error(self, error):
        if callable(self.error_cb):
            self.error_cb(self, error)

    def process_cancelled(self):
        if callable(self.cancel_cb):
            self.cancel_cb(self)

    def process_progress(self, progress, stage):
        self.progress = progress
        self.stage = stage

    def process_completed(self):
        if callable(self.completed_cb):
            self.completed_cb(self)

    @synchronized(_lock)
    def _get_cancel(self):
        return self._cancel

    @synchronized(_lock)
    def _set_cancel(self, value):
        self._cancel = value

    @synchronized(_lock)
    def _get_running(self):
        return self._running

    @synchronized(_lock)
    def _set_running(self, value):
        self._running = value

    @synchronized(_lock)
    def _get_completed(self):
        return self._completed

    @synchronized(_lock)
    def _set_completed(self, value):
        self._completed = value

    @synchronized(_lock)
    def _get_queued(self):
        return self._queued

    @synchronized(_lock)
    def _set_queued(self, value):
        self._queued = value

    cancel = property(fget=_get_cancel,
            fset=_set_cancel)

    running = property(fget=_get_running,
            fset=_set_running)

    completed = property(fget=_get_completed,
            fset=_set_completed)

    queued = property(fget=_get_queued,
            fset=_set_queued)


class RenderQueue(threading.Thread):
    _queue = Queue.Queue()
    _lock = threading.Lock()
    _quit = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    @synchronized(_lock)
    def _get_quit(self):
        return self._quit

    @synchronized(_lock)
    def _set_quit(self, val):
        self._quit = val

    quit = property(fget=_get_quit, fset=_set_quit)

    def queue(self, job):
        job.queued = True
        self._queue.put(job)

    def run(self):
        while 1:
            if self.quit:
                return

            try:
                job = self._queue.get(block=True, timeout=0.1)
            except Queue.Empty:
                continue

            def progress_proc(progress, stage, eta):
                if self.quit:
                    job.cancel = True
                    return 1

                with job._lock:
                    if job._cancel:
                        return 1

                    job.process_progress(progress, stage)
                    return 0

            if not job._execute(progress=progress_proc):
                print 'ERROR: execute failed'
                #traceback.print_exc()

                self._queue.task_done()
                continue


            if self.quit:
                return

            with job._lock:
                if job._cancel:
                    job._completed = False
                    job.process_cancelled()
                else:
                    job._completed = True
                    job.process_completed()

                job._running = False
                self._queue.task_done()









