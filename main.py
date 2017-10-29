from datetime import datetime, date, timedelta, time

from kivy.app import App
from kivy.properties import (
    ObjectProperty, StringProperty, Clock)
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivymd.list import TwoLineListItem
from kivymd.theming import ThemeManager

from lib import JobManager


# ATOMIC COMPONENTS
class Widget1(RelativeLayout):
    primary_text = StringProperty()
    secondary_text = StringProperty()
    time_o_clock = StringProperty()

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.app = App.get_running_app()
        update_event = Clock.schedule_interval(self.update, 1)


class CurrentTime(Widget1):
    def __init__(self, *args, **kwargs):
        super(CurrentTime, self).__init__(**kwargs)

    def update(self, dt):
        # data = self.app.data
        now = datetime.now().time()

        self.primary_text = self.app.status
        self.secondary_text = date.today().strftime("%a, %d %b")
        self.time_o_clock = datetime.now().strftime("%H:%M")


class NextStop(Widget1):
    def __init__(self, **kwargs):
        super(NextStop, self).__init__(**kwargs)

    def update(self, dt):
        _label = 'see you tomorrow!'
        _time = 'Resting'
        _duraction = ''

        if self.app.status in ('Working', 'In Pause'):
            now = datetime.now().time()
            stops = self.app.job.stops
            for stop in stops:
                if now < stop.start:
                    _label = 'Next Stop'
                    _time = stop.start.strftime("%H:%M")
                    _duraction = 'duraction {}'.format(
                        self._duraction(stop.start, now))

                elif now > stop.end:
                    _label = 'job ends at'
                    _time = self.app.data.end.strftime("%H:%M")
                    _duraction = 'time to end {}'.format(
                        self._duraction(self.app.job.end, now))

                elif stop.start < now < stop.end:
                    if True:
                        pass
                    _label = 'end stop'
                    _time = stop.end.strftime("%H:%M")
                    _duraction = 'stop ends in {}'.format(
                        self._duraction(stop.end, now))
                    break

        self.primary_text = _label
        self.time_o_clock = _time
        self.secondary_text = _duraction

    def _duraction(self, end: time, start: time) -> timedelta:
        """Calculate the timedelta of two times
        :param end: time end
        :param start: time start
        :return: timedelta between end 'start' and 'end'
        """
        start = self._convertTimeToDateTime(start)
        end = self._convertTimeToDateTime(end)

        result = end - start
        return result

    def _convertTimeToDateTime(self, currtime: time) -> datetime:
        """Convert time to DateTime
        :param currtime: time to convert
        :return: currtime converted to datetime
        """
        return datetime.now().replace(
            hour=currtime.hour, minute=currtime.minute, second=currtime.second
        )


class JobListItem(TwoLineListItem):
    def on_release(self):
        app = App.get_running_app()
        JobManager().select_job(self.text)

        app.switch_to('jobdetail')


# SCREENS
class JobListScreen(Screen):
    def __init__(self, **kwargs):
        super(JobListScreen, self).__init__(**kwargs)

        ml = self.ids.mylist

        for c in JobManager().job_list:
            item = JobListItem(text=c['name'], secondary_text=c['description'])
            ml.add_widget(item)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        tb = app.root.ids.toolbar
        tb.left_action_items = [
            ['menu', lambda x: app.root.toggle_nav_drawer()]
        ]

    def new_job(self):
        app = App.get_running_app()
        app.switch_to('newjob')


class JobDetailScreen(Screen):
    home_bg = ObjectProperty()
    job_name = ObjectProperty()
    job_description = ObjectProperty()
    job_status = ObjectProperty()
    job_time = ObjectProperty()
    real_job_time = ObjectProperty()
    job_paused_time = ObjectProperty()

    events = []

    def __init__(self, **kwargs):
        job = JobManager().job
        self.job_name = job['name']
        self.job_description = job['description']

        super(JobDetailScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        tb = app.root.ids.toolbar
        tb.left_action_items = [
            ['arrow-left', lambda x: app.switch_to('joblist')]
        ]

        self.events.append(Clock.schedule_interval(self._update, 1))

    def on_leave(self, *args):
        for e in self.events:
            e.cancel()

    def _update(self, dt):
        self.job_time = ''
        self.real_job_time = ''
        self.job_paused_time = ''

        jm = JobManager()
        self.job_status = jm.job_status
        if jm.job_status != 'stopped':
            self.job_time = 'worked time: ' + str(jm.job_time)
            self.job_paused_time = 'paused time: ' + str(jm.job_total_pause_time)
            self.real_job_time = 'real worked time' + str(jm.real_job_time)

    def play_pause(self):
        jm = JobManager()
        if jm.job_status == 'stopped':
            jm.start_job()
        elif jm.job_status == 'paused':
            JobManager().unpause_job()
        else:
            JobManager().pause_job()

    def stop(self):
        JobManager().stop_job()
        JobManager().save()


class NewJobScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        tb = app.root.ids.toolbar
        tb.left_action_items = [
            ['arrow-left', lambda x: app.switch_to('joblist')]
        ]

    def save_job(self):
        jm = JobManager()

        job_name = self.ids.job_name.text
        job_description = self.ids.job_description.text
        jm.new_job(job_name, job_description)
        jm.select_job(job_name)
        app = App.get_running_app()
        app.switch_to('jobdetail')


class SettingsScreen(Screen):
    pass


# APP
class WorkingAtHome(App):
    theme_cls = ThemeManager(theme_style='Dark')
    previous_date = ObjectProperty()
    title = "Working At Home"

    screens = {
        'newjob': NewJobScreen,
        'joblist': JobListScreen,
        'jobdetail': JobDetailScreen,
        'settings': SettingsScreen,
    }

    def build(self):
        JobManager().load()
        self.scrmngr = self.root.ids['scr_mngr']
        self.scrmngr.add_widget(JobListScreen())
        return self.root

    def on_stop(self):
        JobManager().save()

    def switch_to(self, scr_name: str):
        self.scrmngr.switch_to(self.screens[scr_name]())


if __name__ == '__main__':
    WorkingAtHome().run()
