from typing import Optional

import HABApp
from HABApp.core.const.topics import TOPIC_ERRORS


class BenchBaseRule(HABApp.Rule):
    BENCH_TYPE: str

    def __init__(self):
        super().__init__()

        self.err_watcher = None
        self.errors = []

        self.prev_rule: Optional[BenchBaseRule] = None
        self.next_rule: Optional[BenchBaseRule] = None

    def link_rule(self, next_rule: 'BenchBaseRule'):
        assert self.next_rule is None
        assert next_rule.prev_rule is None

        self.next_rule = next_rule
        next_rule.prev_rule = self
        return next_rule

    def _err_event(self, event):
        self.errors.append(event)

    def do_bench_start(self):
        self.errors.clear()
        self.err_watcher = self.listen_event(TOPIC_ERRORS, self._err_event)

        self.run.at(1, self.do_bench_run)

    def do_bench_run(self):
        try:
            try:
                print('+' + '-' * 78 + '+')
                print(f'| {self.BENCH_TYPE:^76s} |')
                print('+' + '-' * 78 + '+')
                print('')

                self.set_up()
                self.run_bench()
            finally:
                self.tear_down()
        finally:
            self.run.at(1, self.do_bench_finished)

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def run_bench(self):
        raise NotImplementedError()

    def do_bench_finished(self):
        self.err_watcher.cancel()

        if self.errors:
            count = len(self.errors)
            print(f'{count} error{"" if count == 1 else "s"} during Benchmark in {self.rule_name}!')
            for e in self.errors:
                print(f' - {type(e.exception)}: {e.exception}')

        if self.next_rule is None:
            HABApp.runtime.shutdown.request_shutdown()
        else:
            self.run.soon(self.next_rule.do_bench_start)
