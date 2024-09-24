
import HABApp
from HABApp.core import shutdown
from HABApp.core.const.topics import TOPIC_ERRORS


class BenchBaseRule(HABApp.Rule):
    BENCH_TYPE: str

    def __init__(self) -> None:
        super().__init__()

        self.err_watcher = None
        self.errors = []

        self.prev_rule: BenchBaseRule | None = None
        self.next_rule: BenchBaseRule | None = None

    def link_rule(self, next_rule: 'BenchBaseRule'):
        assert self.next_rule is None
        assert next_rule.prev_rule is None

        self.next_rule = next_rule
        next_rule.prev_rule = self
        return next_rule

    def _err_event(self, event) -> None:
        self.errors.append(event)

    def do_bench_start(self) -> None:
        self.errors.clear()
        self.err_watcher = self.listen_event(TOPIC_ERRORS, self._err_event)

        self.run.at(1, self.do_bench_run)

    def do_bench_run(self) -> None:
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

    def set_up(self) -> None:
        pass

    def tear_down(self) -> None:
        pass

    def run_bench(self):
        raise NotImplementedError()

    def do_bench_finished(self) -> None:
        self.err_watcher.cancel()

        if self.errors:
            count = len(self.errors)
            print(f'{count} error{"" if count == 1 else "s"} during Benchmark in {self.rule_name}!')
            for e in self.errors:
                print(f' - {type(e.exception)}: {e.exception}')

        if self.next_rule is None:
            shutdown.request()
        else:
            self.run.soon(self.next_rule.do_bench_start)
