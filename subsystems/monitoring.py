from typing import Any

from .libs import rvms, rngs, rvgs
from .util import event

ON = 1                          # flag to signal active event          */
OFF = 0                         # flag to signal inactive event        */
START = 0.0                     # initial time                         */

# routing probabilities
FATAL = 0.12
ERROR = 0.16
WARNING = 1 - FATAL - ERROR

# arrival rate
LAMBDA = 1.446
MU = 0.55
ARRIVAL_TEMP = 0.0

# service times distribution:                                          */
#                X =  Lognormal(a, b)   x > 0                          */
# The mean and variance are                                            */
#               μ = mean = exp(a + 0.5*b*b)  = 0.55                    */
#               σ^2 = variance = (exp(b*b) - 1)*exp(2*a + b*b) = 0.45  */
# Follows that                                                         */
#               a = log(μ) - b^2/2                                     */
#               b = sqrt ( log( [σ^2 / log(μ)^2] + 1 ) )               */
a = -0.854075
b = 0.715875

# TRUNCATION                                                           */
# right tail cut at x = 5 seconds                                      */
#                  β = 1-Pr(X ≤ x) = 1-F(x)                            */
# determine left-tail and right-tail truncation probabilities α and β  */
# in our case only the right truncation is needed                      */
#   alpha = rvms.cdfLognormal(a, b, x=0.0)                             # α */
beta = 1.0 - rvms.cdfLognormal(a, b, x=5.0)                        # β */
# constrained inversion                                                */
u = rvgs.Uniform(0.0, 1.0 - beta)
# now we can use: rvms.idfLognormal(a, b, u)                           */


class MonitoringCentre:
    number = []                 # time integrated numbers in the node  */
    queue = []                  # in the queues  */
    service = []                # in service     */
    departed = []               # number served                        */
    servers = 0                 # number of servers                    */

    def __init__(self, servers) -> None:
        self.servers = servers
        self.number = [0 for i in range(servers)]
        self.queue = [[] for i in range(servers)]
        self.departed = [0 for i in range(servers)]
        self.service = [[] for i in range(servers)]
        pass

    def get_events(self) -> list:
        # azzera la variabile ARRIVAL_TEMP                             */
        # quando sono richiesti gli eventi                             */
        global ARRIVAL_TEMP
        ARRIVAL_TEMP = 0.0
        monitoring_events = []
        # one arrival event for each ssq                                */
        for i in range(self.servers):
            arrival = event.Event()   # arrival                               */
            arrival.t = START
            arrival.x = OFF
            monitoring_events.append(arrival)

        # one departure event for each ssq                              */
        for i in range(self.servers):
            departure = event.Event()   # departure                             */
            departure.t = START
            departure.x = OFF
            monitoring_events.append(departure)

        return monitoring_events

    @staticmethod
    def route_arrival() -> int:
        r = rngs.random()
        if r <= FATAL:
            return 0
        elif FATAL < r <= FATAL+ERROR:
            return 1
        else:
            return 2

    def get_arrival(self, stream) -> tuple[Any, int]:
        # ----------------------------------------------
        # * generate the next arrival time
        # * same stream, different routing
        # * --------------------------------------------
        # */
        global ARRIVAL_TEMP

        rngs.selectStream(stream)
        ARRIVAL_TEMP += rvgs.Exponential(1/LAMBDA)

        centre = self.route_arrival()
        return ARRIVAL_TEMP, centre

    def get_service(self, stream) -> int:
        # ---------------------------------------------
        # * generate the next service time for each
        # * server independently (each their own stream)
        # * --------------------------------------------
        # */
        rngs.selectStream(stream)
        return rvms.idfLognormal(a, b, u)
        # TO VERIFY:
        #return rvgs.Exponential(MU)