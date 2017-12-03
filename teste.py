import os


job_list = [f for f in os.listdir('data') if 'job_' in f]
print(job_list)