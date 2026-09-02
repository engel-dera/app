import os
from mixpanel import Mixpanel


MIXPANEL_TOKEN = os.environ.get("MIXPANEL_TOKEN")

mp = Mixpanel(MIXPANEL_TOKEN) if MIXPANEL_TOKEN else None


def track_event(user_id, event_name, properties=None):
    """
    Send an event to Mixpanel.
    Analytics failures should never break RiskWatch.
    """

    if mp is None:
        return

    try:

        props = properties or {}

        props["distinct_id"] = str(user_id)

        mp.track(
            str(user_id),
            event_name,
            props
        )

    except Exception:
        # Analytics should never crash the application
        pass