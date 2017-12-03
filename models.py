from datetime import datetime, timedelta

from peewee import (SqliteDatabase, Model, CharField, TextField, DateTimeField,
                    IntegerField, ForeignKeyField, BooleanField)
from playhouse.hybrid import hybrid_property

from config import DATABASE

db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Job(BaseModel):
    name = CharField(unique=True)
    description = TextField()

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)

    status = IntegerField(choices=(
        (0, 'started'), (1, 'paused'), (2, 'stopped')), default=0)

    @hybrid_property
    def active_workday(self):
        return Workday.select().where(Workday.job == self, Workday.active == True).first()

    @hybrid_property
    def total_time_worked(self):
        workdays = Workday.select().where(Workday.job == self)
        _durr = timedelta(seconds=0)
        if workdays:
            for w in workdays:
                _durr += w.real_work_time
        return _durr

    def __repr__(self):
        return '<Job(name="%s")>' % (self.name)


class Workday(BaseModel):
    start = DateTimeField(default=datetime.now)
    end = DateTimeField(null=True)
    job = ForeignKeyField(Job, related_name='workdays')
    active = BooleanField(default=False)

    @hybrid_property
    def work_time(self):
        now = datetime.now()
        return (self.end or now) - self.start

    @hybrid_property
    def stopped_time(self):
        stops = Stop.select().where(Stop.workday == self)
        _durr = timedelta(seconds=0)
        if stops:
            for s in stops:
                _durr += s.duraction
        return _durr

    @hybrid_property
    def real_work_time(self):
        return self.work_time - self.stopped_time

    @hybrid_property
    def active_stop(self):
        return Stop.select().where(Stop.workday == self, Stop.active == True).first()

    def __repr__(self):
        return '<Workday(start=%s, end=%s)>' % (self.start, self.end)


class Stop(BaseModel):
    start = DateTimeField(default=datetime.now)
    end = DateTimeField(null=True)
    workday = ForeignKeyField(Workday, related_name='stops')
    active = BooleanField(default=False)

    @hybrid_property
    def duraction(self):
        if self.end:
            return self.end - self.start
        else:
            return datetime.now() - self.start

    def __repr__(self):
        return '<Stop(start=%s, end=%s)>' % (self.start, self.end)


db.connect()
db.create_tables([Job, Workday, Stop], safe=True)
# db.close()
