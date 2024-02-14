import math

from datetime import datetime, timedelta


class Countdown:
    def __init__(self, master, duration, title, command):
        self.prev_title = master.title()
        self.title = title
        self.master = master
        self.duration = duration
        self.command = command
        self.count = 0
        self._restart = False
        self._stop = False

    def start(self):
        if self.duration > 0:
            self.end_time = datetime.now() + timedelta(seconds=self.duration)
            self.count += 1
            self.update_timer()

    def stop(self):
        self._stop = True

    def is_running(self):
        return self.count > 0

    def restart(self):
        self._restart = True
        self._stop = True

    def update_timer(self):
        if not self._stop:
            remaining_time = max(0, (self.end_time - datetime.now()).total_seconds())
            remaining_time = math.ceil(remaining_time)
            hours, remainder = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Update window title with the countdown
            self.master.title(f"{self.title}{formatted_time}")

            if remaining_time > 0:
                self.master.after(1000, self.update_timer)
            else:
                if self.command: self.command()
                self.master.title(f"{self.title}Time's up!")
                self.master.after(2000, self.restore_title)
        else:
            self.master.title(self.prev_title)
            self._stop = False
            self.count -= 1
            if self._restart:
                self._restart = False
                self.start()

    def restore_title(self):
        if self.count < 2:
            self.master.title(self.prev_title)
        self.count -= 1