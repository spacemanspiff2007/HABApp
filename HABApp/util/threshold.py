import threading


class Threshold:
    def __init__(self, upper_threshold, lower_threshold):
        """This is a simple Schmitt Trigger implementation.
        If the value is >= upper_threshold is_higher will return true.
        The return value will stay true until the value goes below lower_threshold.
        
        :param upper_threshold:
        :param lower_threshold:
        """
        assert upper_threshold > lower_threshold, f'{upper_threshold} > {lower_threshold}'
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        
        self.__over_upper = False
        self.__lock = threading.Lock()
    
    @property
    def current_threshold(self):
        return self.lower_threshold if self.__over_upper else self.upper_threshold
    
    def is_higher(self, value) -> bool:
        
        with self.__lock:
            if value >= self.upper_threshold:
                self.__over_upper = True

            if value < self.lower_threshold:
                self.__over_upper = False
        
        return self.__over_upper
    
    def is_lower(self, value) -> bool:
        return not self.is_higher(value)
