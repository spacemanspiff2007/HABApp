
class Threshold:
    def __init__(self, lower_threshold, upper_threshold):
        assert upper_threshold > lower_threshold, f'{upper_threshold} > {lower_threshold}'
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        
        self.__over_upper = False
    
    @property
    def current_threshold(self):
        return self.lower_threshold if self.__over_upper else self.upper_threshold
    
    def is_higher(self, value) -> bool:
        
        if value >= self.upper_threshold:
            self.__over_upper = True
            return True
        
        if self.__over_upper:
            if value >= self.lower_threshold:
                return True
            else:
                self.__over_upper = False
            
        return False
        
    
    def is_lower(self, value) -> bool:
        return not self.is_higher(value)
        