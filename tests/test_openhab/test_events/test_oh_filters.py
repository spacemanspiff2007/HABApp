from tests.helpers import check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations so we test that every event has those"""

    check_class_annotations('HABApp.openhab.events', exclude=['OpenhabEvent'], skip_imports=False)
