import json
import os
from datetime import datetime, timedelta
from time import sleep



class JobManager():
    __instance = None
    __curr_job = None
    __all_jobs = []
    __job_status = {0: 'started', 1: 'paused', 2: 'stopped'}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(JobManager, cls).__new__(cls)
        return cls.__instance

    @property
    def jobs_fn(self):
        return os.path.join('data', 'jobs.json')

    @property
    def job_list(self):
        return self.__all_jobs

    @property
    def job(self):
        return self.__curr_job

    @property
    def job_time(self):
        wordkays = self.job['workdays']
        if len(wordkays) >= 1:
            return datetime.now() - wordkays[-1]['start']
        else:
            return timedelta(seconds=0)

    @property
    def job_total_pause_time(self):
        workdays = self.job['workdays']
        if len(workdays) >= 1:
            pauses = workdays[-1].get('pauses')
            if pauses is not None and len(pauses) >= 1:
                now = datetime.now()
                _durr = timedelta(seconds=0)
                for p in self.job['workdays'][-1]['pauses']:
                    _durr += p.get('end', now) - p['start']
                return _durr
        return timedelta(seconds=0)

    @property
    def real_job_time(self):
        return self.job_time - self.job_total_pause_time

    @property
    def job_status(self):
        return self.__curr_job['status']

    def new_job(self, name, description):
        job = dict(name=name, description=description, workdays=[], status=self.__job_status[2])
        self.__all_jobs.append(job)
        self.save()

    def select_job(self, name):
        job = [j for j in self.__all_jobs if j['name'] == name][0]
        # job['status'] = self.__job_status[2]
        self.__curr_job = job

    def start_job(self, ):
        try:
            self.__curr_job['workdays'].append({'start': datetime.now()})
        except Exception as ex:
            self.__curr_job['workdays'] = [{'start': datetime.now()}]
        self.__curr_job['status'] = self.__job_status[0]

    def stop_job(self, ):
        self.__curr_job['workdays'][-1]['end'] = datetime.now()
        self.__curr_job['status'] = self.__job_status[2]

    def pause_job(self, ):
        try:
            self.__curr_job['workdays'][-1]['pauses'].append({'start': datetime.now()})
        except Exception as ex:
            self.__curr_job['workdays'][-1]['pauses'] = [{'start': datetime.now()}]
        self.__curr_job['status'] = self.__job_status[1]

    def unpause_job(self, ):
        self.__curr_job['workdays'][-1]['pauses'][-1]['end'] = datetime.now()
        self.__curr_job['status'] = self.__job_status[0]

    def save(self, ):
        with open(self.jobs_fn, 'w') as _file:
            json.dump([self.job_to_dict(j) for j in self.__all_jobs], _file)

    def load(self):
        try:
            with open(self.jobs_fn) as _file:
                self.__all_jobs = [self.job_from_dict(j) for j in json.load(_file)]
        except:
            print("can't load jobs file")

    def job_from_dict(self, job):
        _dict = {}
        for k, v in job.items():
            if k in ['start', 'end']:
                v = datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

            if isinstance(v, list):
                v = [self.job_from_dict(i) for i in v]
            _dict[k] = v
        return _dict

    def job_to_dict(self, job):
        _dict = {}
        for k, v in job.items():
            if isinstance(v, datetime):
                v = str(v)

            if isinstance(v, list):
                v = [self.job_to_dict(i) for i in v]

            _dict[k] = v
        return _dict


if __name__ == '__main__':
    jm = JobManager()
    jm.load()

    print('creating a new job')
    jm.new_job('job', 'description')

    print('selecting job')
    jm.select_job('job')

    print('starting job')
    jm.start_job()
    sleep(2)

    print('pausing job')
    jm.pause_job()
    sleep(2)

    print('unpausing job')
    jm.unpause_job()
    sleep(2)

    print('stoping job')
    jm.stop_job()

    print('trying save the jobs')
    jm.save()
