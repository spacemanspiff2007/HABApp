import logging
import typing
from datetime import datetime, timedelta

import HABApp
from HABApp.core.lib import PendingFuture
from .base_item_watch import BaseWatch

if typing.TYPE_CHECKING:
    from .base_item import BaseItem


TMP_DATA: typing.Dict[str, 'TmpItemData'] = {}


class TmpItemData:
    def __init__(self):
        self.ts = datetime.now()
        self.update: typing.Set[BaseWatch] = set()
        self.change: typing.Set[BaseWatch] = set()

    def add_tasks(self, update, change):
        self.ts = datetime.now()
        self.update.update(update)
        self.change.update(change)

        self.clean()

    def clean(self):
        # remove canceled
        for obj in (self.update, self.change):
            canceled = [k for k in obj if k.fut.is_canceled]
            for p in canceled:
                obj.remove(p)


def add_tmp_data(item: 'BaseItem'):
    if not item._last_update.tasks and not item._last_change.tasks:
        return None

    data = TMP_DATA.setdefault(item.name, TmpItemData())
    data.add_tasks(item._last_update.tasks, item._last_change.tasks)

    CLEANUP.reset(thread_safe=True)


def restore_tmp_data(item: 'BaseItem'):
    data = TMP_DATA.pop(item.name, None)
    if data is None:
        return None

    # delete old watcher
    data.clean()

    for t in data.update:
        item._last_update.tasks.append(t)
    for t in data.change:
        item._last_change.tasks.append(t)


async def clean_tmp_data():
    now = datetime.now()
    diff_max = timedelta(seconds=CLEANUP.secs)

    to_del = []
    for name, obj in TMP_DATA.items():
        diff = now - obj.ts
        if diff < diff_max:
            continue

        to_del.append(name)

        # show a warning because otherwise it's not clear what is happening
        w = HABApp.core.logger.HABAppWarning(logging.getLogger('HABApp.Item'))
        w.add(f'Item {name} has been deleted {diff.total_seconds():.1f}s ago even though it has item watchers. '
              f'If it will be added again the watchers have to be created again, too!')
        w.dump()

    for name in to_del:
        TMP_DATA.pop(name)


CLEANUP = PendingFuture(clean_tmp_data, 3600)
