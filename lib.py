# TODO: implementar classes para representar os Jobs, stops, e workdays

import hashlib
import json
import os
from datetime import datetime, timedelta
from time import sleep

from kivy.app import App


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
    def data_dir(self):
        return App.get_running_app().user_data_dir

    def job_fn(self, job: dict = None):
        if job is None:
            return

        if 'id' not in job.keys():
            job['id'] = hashlib.md5(os.urandom(32)).hexdigest()[:8]

        return os.path.join(self.data_dir, 'job_{}.json'.format(job['id']))

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
        self.save(job)

    def select_job(self, name):
        job = [j for j in self.job_list if j['name'] == name][0]

        # job['status'] = self.__job_status[2]
        self.__curr_job = job

    def start_job(self, ):
        try:
            self.__curr_job['workdays'].append({'start': datetime.now()})
        except Exception as ex:
            self.__curr_job['workdays'] = [{'start': datetime.now()}]
        self.__curr_job['status'] = self.__job_status[0]
        # self.save(self.__curr_job)

    def stop_job(self, ):
        if self.__curr_job['status'] == 'paused':
            self.unpause_job()

        self.__curr_job['workdays'][-1]['end'] = datetime.now()
        self.__curr_job['status'] = self.__job_status[2]
        # self.save(self.__curr_job)

    def pause_job(self, ):
        try:
            self.__curr_job['workdays'][-1]['pauses'].append({'start': datetime.now()})
        except Exception as ex:
            self.__curr_job['workdays'][-1]['pauses'] = [{'start': datetime.now()}]
        self.__curr_job['status'] = self.__job_status[1]
        # self.save(self.__curr_job)

    def unpause_job(self, ):
        self.__curr_job['workdays'][-1]['pauses'][-1]['end'] = datetime.now()
        self.__curr_job['status'] = self.__job_status[0]
        # self.save(self.__curr_job)

    def save(self, job=None):
        if job is None:
            return

        with open(self.job_fn(job), 'w') as _file:
            json.dump(self.job_to_dict(job), _file)

    def save_all(self):
        for job in self.job_list:
            self.save(job)

    def load(self):
        job_list = [f for f in os.listdir(self.data_dir) if 'job_' in f]
        for job in job_list:
            try:
                with open(os.path.join(self.data_dir, job)) as _file:
                    self.__all_jobs.append(self.job_from_dict(json.load(_file)))
            except Exception as err:
                print(err)
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
