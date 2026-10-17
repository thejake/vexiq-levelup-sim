"""Simulation clock.

The engine (main thread) advances sim time in small steps. User code runs in
a separate thread; every blocking VEX call (wait, drive_for, spin_for, ...)
blocks on this clock's condition variable until sim time or a predicate says
it is done. That way `wait(1, SECONDS)` tracks *simulated* seconds, pausing
pauses user code, and running at 4x speed speeds user code up too.
"""

from __future__ import annotations

import threading


class SimShutdown(SystemExit):
    """Raised inside blocked user threads when the simulator window closes."""


class SimClock:
    def __init__(self):
        self._t = 0.0  # simulated seconds since program start
        self._cond = threading.Condition()
        self._running = True

    # ---- engine side (main thread) ----

    def advance(self, dt: float) -> None:
        with self._cond:
            self._t += dt
            self._cond.notify_all()

    def shutdown(self) -> None:
        with self._cond:
            self._running = False
            self._cond.notify_all()

    # ---- shared reads ----

    @property
    def running(self) -> bool:
        return self._running

    def now(self) -> float:
        """Simulated seconds."""
        return self._t

    def now_ms(self) -> float:
        return self._t * 1000.0

    # ---- user-code side (worker threads) ----

    def sleep(self, seconds: float) -> None:
        """Block until `seconds` of sim time pass."""
        self.wait_for(lambda: False, timeout=seconds)

    def wait_for(self, pred, timeout: float | None = None) -> bool:
        """Block until pred() is true or `timeout` sim-seconds elapse.

        Returns the final value of pred(). Raises SimShutdown if the
        simulator exits while we are waiting.
        """
        with self._cond:
            deadline = None if timeout is None else self._t + timeout
            while True:
                if not self._running:
                    raise SimShutdown(0)
                if pred():
                    return True
                if deadline is not None and self._t >= deadline:
                    return bool(pred())
                # Wall-clock wait; woken by advance(). The timeout here is
                # just a safety net so we re-check _running periodically.
                self._cond.wait(0.25)
