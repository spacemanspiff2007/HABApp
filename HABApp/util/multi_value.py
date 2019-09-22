import datetime
import typing, logging
import operator
from threading import Lock
from HABApp.core.items import Item


class ValueWithPriority:
    DISABLE_OPERATORS = {
        '>': operator.gt, '<': operator.lt, '>=': operator.ge, '<=': operator.le, '==': operator.eq, None: None
    }
    
    def __init__(self, parent, name:str, initial_value=None, auto_disable_on=None, auto_disable_after=None):

        assert isinstance(parent, MultiValueItem), type(parent)
        assert isinstance(name, str), type(name)
        self.__parent: MultiValueItem = parent
        self.__name = name
        
        self.__value = None
        self.__enabled = False
        
        assert isinstance(auto_disable_after, datetime.timedelta) or auto_disable_after is None, type(auto_disable_after)
        assert auto_disable_on in ValueWithPriority.DISABLE_OPERATORS, auto_disable_on
        self.auto_disable_after: datetime.timedelta = auto_disable_after
        self.auto_disable_on: str = auto_disable_on

        #: Timestamp of the last update/enable of this value
        self.last_update: datetime.datetime = datetime.datetime.now()

        # do not call callback for initial value
        if initial_value is not None:
            self.__enabled = True
            self.__value = initial_value

    @property
    def value(self):
        """Returns the current value"""
        return self.__value

    @property
    def enabled(self) -> bool:
        """Returns if the value is enabled"""
        return self.__enabled

    def set_value(self, value):
        """Set new value and recalculate overall value

        :param value: new value
        """
        self.__enabled = True if value is not None else False
        self.__value = value

        self.last_update = datetime.datetime.now()

        if self.__parent.log is not None:
            self.__parent.log.info(f'{self.__parent.name}: {self.__name} set value to {self.__value}')

        self.__parent.recalculate_value()

    def set_enabled(self, value: bool):
        """Enable or disable this value and recalculate overall value

        :param value: True/False
        """
        assert value is True or value is False, value
        self.__enabled = value

        self.last_update = datetime.datetime.now()

        self.__parent.recalculate_value()

    def calculate_value(self, lower_value):

        # so we don't spam the log if we are already disabled
        if not self.__enabled:
            return lower_value

        # Automatically disable after certain time
        if self.auto_disable_after is not None:
            if datetime.datetime.now() > self.last_update + self.auto_disable_after:
                self.__enabled = True
                self.last_update = datetime.datetime.now()
                if self.__parent.log is not None:
                    self.__parent.log.info(f'{self.__parent.name}: {self.__name} disabled '
                                           f'(after {self.auto_disable_after})!')
        
        # Automatically disable if <> etc.
        if self.auto_disable_on is not None:
            if ValueWithPriority.DISABLE_OPERATORS[self.auto_disable_on](lower_value, self.__value):
                self.__enabled = False
                self.last_update = datetime.datetime.now()
                if self.__parent.log is not None:
                    self.__parent.log.info(f'{self.__parent.name}: {self.__name} disabled '
                                           f'({lower_value}{self.auto_disable_on}{self.__value})!')

        if not self.__enabled:
            return lower_value

        return self.__value

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f'<{self.__class__.__name__} enabled: {self.__enabled}, value: {self.__value}>'


class MultiValueItem(Item):
    """Thread safe value prioritizer"""

    def __init__(self, name: str, state=None):
        super().__init__(name=name, state=state)

        self.__values_by_prio: typing.Dict[int, ValueWithPriority] = {}
        self.__values_by_name: typing.Dict[str, ValueWithPriority] = {}
        
        self.__lock = Lock()
        
        self.log: logging._loggerClass = None

    def add_multivalue(self, name: str, priority: int,
                       initial_value=None, auto_disable_on=None, auto_disable_after=None):
        # Silently overwrite the values
        # assert not name.lower() in self.__values_by_name, name.lower()
        # assert not priority in self.__values_by_prio, priority
        
        with self.__lock:
            ret = ValueWithPriority(
                self, name,
                initial_value=initial_value, auto_disable_on=auto_disable_on, auto_disable_after=auto_disable_after
            )
            self.__values_by_prio[priority] = ret
            self.__values_by_name[name.lower()] = ret
        return ret

    def get_multivalue(self, name: str):
        return self.__values_by_name[name.lower()]

    def get_value_until(self, child_to_stop):
        assert isinstance(child_to_stop, ValueWithPriority), type(child_to_stop)
        new_value = None
        with self.__lock:
            for priority, child in sorted(self.__values_by_prio.items()):
                if child is child_to_stop:
                    return new_value
                
                assert isinstance(child, ValueWithPriority)
                new_value = child.calculate_value(new_value)
        raise ValueError()

    def recalculate_value(self):
        """Recalculate the output value and call the registered callback (if output has changed)

        :param child: child that changed
        :return: output value
        """

        # recalculate value
        new_value = None
        with self.__lock:
            for priority, child in sorted(self.__values_by_prio.items()):
                assert isinstance(child, ValueWithPriority)
                new_value = child.calculate_value(new_value)

        # Notify that the value has changed
        if new_value is not None:
            self.post_state(new_value)
        return new_value
