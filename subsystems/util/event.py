import math


class Event:
    t = None  # next event time               */
    x = None  # event status, 0 or 1          */


def next_event(events):
    # ---------------------------------------
    # * return the index of the next event type
    # * ---------------------------------------
    # */

    i = 0
    j = 0
    imminent = math.inf
    while j < len(events):
        # filter active events and check for the most imminent      */
        if events[j].x == 1 and events[j].t < imminent:
            imminent = events[j].t
            i = j
        j += 1

    # in case of a draw return the first most imminent              */
    return i
