# flake8: noqa

import io

from HABApp.openhab.connection_logic.plugin_things.cfg_validator import UserItem
from HABApp.openhab.connection_logic.plugin_things.file_writer.writer import ItemsFileWriter


class MyStringIO(io.StringIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = None
        self.exists = False

    def open(self, *args, **kwargs):
        return self

    def close(self, *args, **kwargs):
        self.text = self.getvalue()
        super().close(*args, **kwargs)

    def is_file(self):
        return self.exists

    def read_text(self, encoding):
        return self.getvalue()

    def write_text(self, data, encoding):
        return self.write(data)


def get_test_objs():
    meta_auto = {'auto_update': {'value': 'False', 'config': {}}}
    objs = [
        UserItem('String', 'Test_zwave_o_1', '', '', [], [], 'zwave:link:device', {}),
        UserItem('String', 'Test_zwave_o_2', '', '', [], [], 'zwave:link:device1', metadata=meta_auto),
        UserItem('String', 'Test_zwave_no', '', '', [], ['tag1'], '', {}),
        UserItem('String', 'Test_zwave_all', 'label1', 'icon1', ['grp1'], ['tag1', 'tag2'], '', {}),

        UserItem('String', 'NewName', '', '', [], [], '', metadata=meta_auto),
        UserItem('String', 'NewName1', '', '', [], [], '', metadata=meta_auto),

        UserItem('String', 'SoloName', '', '', [], [], '', {}),
    ]
    return objs


def get_result() -> str:
    ret = """
String  NewName     {auto_update="False"}
String  NewName1    {auto_update="False"}

String  Test_zwave_o_1                                                    {channel = "zwave:link:device"                        }
String  Test_zwave_o_2                                                    {channel = "zwave:link:device1",   auto_update="False"}
String  Test_zwave_no                                 ["tag1"]
String  Test_zwave_all  "label1"    <icon1>   (grp1)  ["tag1", "tag2"]

String  SoloName
"""
    return ret.lstrip('\n')


def test_writer_str():
    writer = ItemsFileWriter().add_items(get_test_objs())
    assert writer.generate() == get_result()


def test_no_write():
    file = MyStringIO(get_result())
    file.exists = True

    writer = ItemsFileWriter().add_items(get_test_objs())
    assert not writer.create_file(file)


def test_write_no_exist():
    file = MyStringIO(get_result())
    file.exists = False

    writer = ItemsFileWriter().add_items(get_test_objs())
    assert writer.create_file(file)


def test_write_content_different():
    file = MyStringIO(get_result() + 'asdf')
    file.exists = True

    writer = ItemsFileWriter().add_items(get_test_objs())
    assert writer.create_file(file)
