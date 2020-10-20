# flake8: noqa
import io

from HABApp.openhab.connection_logic.plugin_things.items_file import create_items_file, UserItem

class MyStringIO(io.StringIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = None

    def open(self, *args, **kwargs):
        return self

    def close(self, *args, **kwargs):
        self.text = self.getvalue()
        super().close(*args, **kwargs)


def test_creation(tmp_path_factory):

    meta_auto = {'auto_update': {'value': 'False', 'config': {}}}

    objs = [
        UserItem('String', 'Test_zwave_o_1', '', '', [], [], 'zwave:link:device', {}),
        UserItem('String', 'Test_zwave_o_2', '', '', [], [], 'zwave:link:device1', metadata=meta_auto),
        UserItem('String', 'Test_zwave_no', '', '', [], ['tag1'], '', {}),
        UserItem('String', 'Test_zwave_all', 'label1', 'icon1', ['grp1'], ['tag1', 'tag2'], '', {}),

        UserItem('String', 'NewName', '', '', [], [], '', metadata=meta_auto),
        UserItem('String', 'NewName1', '', '', [], [], '', metadata=meta_auto),
    ]

    t = MyStringIO()
    create_items_file(t, {k.name: k for k in objs})

    print('\n-' + t.text + '-')

    expected = """String  Test_zwave_o_1                                                {channel = "zwave:link:device"                        }
String  Test_zwave_o_2                                                {channel = "zwave:link:device1",   auto_update="False"}
String  Test_zwave_no                                 [tag1]
String  Test_zwave_all  "label1"    <icon1>   (grp1)  [tag1, tag2]

String  NewName     {auto_update="False"}
String  NewName1    {auto_update="False"}

"""
    assert expected == t.text
