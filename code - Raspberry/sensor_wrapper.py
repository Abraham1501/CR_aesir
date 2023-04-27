import logging


class SensorWrapper:
    def __init__(self, enable, period, type):
        # Setup logger
        self.logger = logging.getLogger(__name__)
        # Last time get_data() was called
        self.last_run = 0
        # If any of these required values do not exist in the config, display a warning
        
        # Load essential configuration options
        self.enabled = enable
        self.period = period
        self.name = type

    def get_data(self):
        return None

    def get_initial(self):
        return None

    def is_ready(self, now):
        # Time since last checked
        elapsed_time = now - self.last_run
        # Only get data if it has been long enough since last run
        # Or if this is the first time checking since we need some data on the graph
        if elapsed_time > self.period or self.last_run == 0:
            # Store current time as last_time 
            self.last_run = now
            # Only return True if sensor is actually enabled
            return self.enabled
        else:
            return False

    def close(self):
        pass