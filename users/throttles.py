from rest_framework.exceptions import Throttled
from rest_framework.throttling import ScopedRateThrottle


class CustomScopedRateThrottle(ScopedRateThrottle):
    def wait(self):
        wait_time = super().wait()

        if wait_time is None:
            return None

        try:
            wait_time = round(wait_time, 1)
        except (ValueError, TypeError):
            # Handle cases where wait_time is not a valid number
            return None

        raise Throttled(detail={
            "detail": f"Try again in {wait_time} seconds",
        }, code=429)
