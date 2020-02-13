
import os as _os
import multiprocessing as _mp
import copy as _copy
import logging as _logging

# thin wrappers to use multiprocessing module with parallelpython api
# no support for external servers, yet


class Job:
    def __init__(self,job):
        self.job = job
    def __call__(self):
        self.job.wait()
        try:
            res = self.job.get()
        except Exception as e:
            print('Error in parallel job:',e)
            res = None
        return res
    
class Res:
    def __init__(self,res):
        self.res = [res]
    def __call__(self):
        return self.res.pop()

class Server:
    def __init__(self,ncpus=None,ppservers=None,secret=None):
        if ncpus == 'autodetect':
            ncpus = _os.cpu_count()//2
        elif ncpus:
            ncpus = min(ncpus,_os.cpu_count())
        else:
            ncpus = None

        # if ppservers or secret:
        #     print('WARNING: external nodes not supported (requested',ppservers,\
        #                     f'with secret key {secret})' if secret else ')')

        self.ncpus = ncpus
        self.ppservers = ppservers
        self.secret = secret

        if ncpus:
            assert ncpus > 0
            self.pool = _mp.Pool(processes=ncpus)
            self.logger = _mp.get_logger()
        else:
            self.pool = None
            self.logger = _logging.getLogger()
        
    def get_ncpus(self):
        return self.ncpus

    def submit(self,fn,args=(),kwargs={},depfuncs=(),modules=()):
        if self.pool is None:
            res = fn(*args,**kwargs)
            return Res(res)
        else:
            job = self.pool.apply_async(fn,args=args,kwds=kwargs)
            return Job(job)

    def destroy(self):
        if self.pool is not None:
            self.pool.terminate()

    def get_active_nodes(self):
        return None

    def print_stats(self):
        pass
        # print("this isn't the real parallelpython, there are no stats to print")

