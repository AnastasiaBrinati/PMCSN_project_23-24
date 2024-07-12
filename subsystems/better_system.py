from .monitoring import MonitoringCentre
from .better_planning import PlanningCentre
from .util import event, clock
import numpy as np

ON = 1                                                                          # flag to signal active event         */
OFF = 0                                                                         # flag to signal inactive event       */
START = 0.0                                                                     # initial time                        */

MONITORING_SERVERS = 3
ARRIVALS_STREAM = 0


def simulation(stop, batch_size=1.0) -> list:
    INFINITY = (100.0 * stop)                                                   # must be much larger than stop       */

    # statistics                                                                                                      */
    waiting_times_monitor = []
    response_times_monitor = []
    response_times_monitor_1 = []

    waiting_times_plan = [[], []]
    response_times_plan = []
    response_times_plan_1 = []

    k_mon = 0
    k_mon_1 = 0
    k_mon_2 = 0
    k_mon_3 = 0
    departed_mon_1 = 0
    departed_mon_2 = 0
    departed_mon_3 = 0
    batch_response_times_monitor = []
    batch_waiting_times_monitor = []
    batch_response_times_monitor_1 = []
    batch_rho1_monitor = []
    batch_rho2_monitor = []
    batch_rho3_monitor = []

    k_pla = 0
    k_pla_queue1 = 0
    k_pla_queue2 = 0
    departed_queue1 = 0
    departed_queue2 = 0
    batch_response_times_plan = []
    batch_response_times_plan1 = []
    batch_waiting_times_plan = [[],[]]
    batch_rho_plan = []

    # ***************************************************** Monitoring area ********************************************
    # */
    # ------------------------------------------------------------------------------------------------------------------
    # *                                     Initialize 3 SSQs for the Monitoring Area
    # * ----------------------------------------------------------------------------------------------------------------
    # */
    # sub-systems initialization: empty SSQs                                                                          */
    monitoring_centre = MonitoringCentre(MONITORING_SERVERS)

    # events initialization: from START with flag OFF                                                                 */
    monitoring_events = monitoring_centre.get_events()

    # ***************************************************** Analyze&Plan area ******************************************
    # */
    # ------------------------------------------------------------------------------------------------------------------
    # *                                                  Initialize 1 SSQ
    # * ----------------------------------------------------------------------------------------------------------------
    # */

    # sub-systems initialization: empty SSQ                                                                           */
    planning_centre = PlanningCentre()

    # events initialization: from START with flag OFF                                                                 */
    planning_events = planning_centre.get_events()

    # ****************************************************** System ****************************************************
    # SYSTEM VALUES
    number = 0                                                                  # number in the system                */
    departed_jobs = 0                                                           # departed jobs from the system       */

    # **************************************************** Simulation **************************************************
    # monitoring area services will have the streams in range (MONITORING_SERVERS, MONITORING_SERVERS*2-1)
    # planning area service will have the stream MONITORING_SERVERS*2+1

    # SYSTEM CLOCK
    t = clock.Time()
    t.current = START                                                            # set the clock                      */
    t.completion = INFINITY                                                      # first event can't be a completion  */

    events = monitoring_events+planning_events
    first_arrival, e = monitoring_centre.get_arrival(ARRIVALS_STREAM)
    events[e].t = first_arrival                                                  # first event is of course an arrival*/
    events[e].x = ON                                                             # schedule first arrival             */

    # structures to keep track of first and last event at each centre                                                 */
    first = {
        "monitoring": [OFF, OFF, OFF, START, START, START],
        "planning": [OFF, START]
    }
    last = {
        "monitoring": [START, START, START],
        "planning": START
    }

    while (events[0].x == ON) or (events[1].x == ON) or (events[2].x == ON) or (number != 0):

        # get the next event in the timeline                                                                          */
        e = event.next_event(events)                                             # next event                         */
        t.next = events[e].t                                                     # next event time                    */
        t.current = t.next                                                       # advance the clock                  */

        # --------------------------------------------------------------------------------------------------------------
        # *                                         Monitoring Area Events
        # * ------------------------------------------------------------------------------------------------------------
        # */
        if e in range(0, MONITORING_SERVERS):                                    # process an arrival at MonitoringC  */

            number += 1                                                          # plus one job in the system         */
            monitoring_centre.number[e] += 1                                     # plus one job in one of the ssqs    */
            events[e].x = OFF                                                    # turn off arrivals at this centre   */

            if first['monitoring'][e] == OFF:
                first['monitoring'][e+MONITORING_SERVERS] = t.current
                first['monitoring'][e] = ON

            arrived = events[e].t
            arrival, w = monitoring_centre.get_arrival(ARRIVALS_STREAM)          # generate next arrival              */
            events[w].t = arrival                                                # prepare event arrival              */
            events[w].x = ON                                                     # schedule the arrival               */

            if events[w].t > stop:                                               # if the arrival is out of time:     */
                events[w].x = OFF                                                # turn off the arrivals              */

            if monitoring_centre.number[e] == 1:                                 # prepares next departure            */
                service = monitoring_centre.get_service(e+MONITORING_SERVERS)
                served = t.current + service
                monitoring_centre.service[e].append(service)                     # update integrals for utilization   */
                events[e+MONITORING_SERVERS].t = served                          # prepare departure event            */
                events[e+MONITORING_SERVERS].x = ON                              # schedule departure                 */
                waiting_times_monitor.append(0.0)                                # update integrals for E[Tq]         */
                response_times_monitor.append(served - arrived)                  # update integrals for E[Ts]         */
                if e == 0:
                    departed_mon_1 += 1
                    response_times_monitor_1.append(served - arrived)
                if e == 1:
                    departed_mon_2 += 1
                else:
                    departed_mon_3 += 1
            else:
                # save the timestamp of the arrival as token for the job                                              */
                monitoring_centre.queue[e].append(t.current)                     # plus one job in one of the queues  */

        if e in range(MONITORING_SERVERS, MONITORING_SERVERS*2):                 # process a departure from MonitorC  */
            monitoring_centre.number[e-MONITORING_SERVERS] -= 1                  # minus one job in one of the ssq    */
            monitoring_centre.departed[e-MONITORING_SERVERS] += 1                # plus one j departed from the ssq   */

            if first['monitoring'][e-MONITORING_SERVERS] == OFF:
                first['monitoring'][e] = t.current
                first['monitoring'][e-MONITORING_SERVERS] = ON

            if len(monitoring_centre.queue[e-MONITORING_SERVERS]) > 0:           # prepares next departure            */
                arrived = monitoring_centre.queue[e-MONITORING_SERVERS].pop(0)
                service = monitoring_centre.get_service(e)
                monitoring_centre.service[e-MONITORING_SERVERS].append(service)  # update integrals for utilization   */
                served = t.current + service
                events[e].t = served                                             # prepares next departure            */
                waiting_times_monitor.append(t.current - arrived)                # update integrals for E[Tq]         */
                response_times_monitor.append(served - arrived)                  # update integrals for E[Tq]         */
                if e == MONITORING_SERVERS:
                    departed_mon_1 += 1
                    response_times_monitor_1.append(served - arrived)
                if e == MONITORING_SERVERS+1:
                    departed_mon_2 += 1
                else:
                    departed_mon_3 += 1
            else:
                events[e].x = OFF

            if e == MONITORING_SERVERS:
                events[MONITORING_SERVERS*2].x = ON                              # signal an arrival to A&P first q   */
                events[MONITORING_SERVERS*2].t = t.current
            else:
                events[MONITORING_SERVERS*2+1].x = ON                            # signal an arrival to A&P second q  */
                events[MONITORING_SERVERS*2+1].t = t.current

            last['monitoring'][e-MONITORING_SERVERS] = t.current

            # FOR INFINITE-HORIZON SIMULATION
            if batch_size > 1:
                if (monitoring_centre.departed[0]+monitoring_centre.departed[1]+monitoring_centre.departed[2])%batch_size == 0:
                    # Time to save up some metrics

                    # E[Ts]
                    batch_response_times_monitor.append(np.mean(response_times_monitor[k_mon:k_mon+batch_size]))

                    # E[Tq]
                    batch_waiting_times_monitor.append(np.mean(waiting_times_monitor[k_mon:k_mon+batch_size]))

                    k_mon += batch_size

                if departed_mon_1 > 0 and departed_mon_1 % batch_size == 0:
                    # E[Ts1]
                    batch_response_times_monitor_1.append(np.mean(response_times_monitor_1[k_mon_1:k_mon_1+batch_size]))
                    departed_mon_1 = 0

                    # ρ
                    if last['monitoring'][0] > START:
                        batch_rho1_monitor.append(np.sum(monitoring_centre.service[0][k_mon_1:k_mon_1+batch_size]) / (last['monitoring'][0] - first['monitoring'][3]))
                        first['monitoring'][0] = OFF

                    k_mon_1 += batch_size

                if departed_mon_2 > 0 and departed_mon_2 % batch_size == 0:
                    departed_mon_2 = 0
                    # ρ
                    if last['monitoring'][1] > START:
                        batch_rho2_monitor.append(np.sum(monitoring_centre.service[1][k_mon_2:k_mon_2+batch_size]) / (last['monitoring'][1] - first['monitoring'][4]))
                        first['monitoring'][1] = OFF

                    k_mon_2 += batch_size

                if departed_mon_3 > 0 and departed_mon_3 % batch_size == 0:
                    departed_mon_3 = 0
                    # ρ
                    if last['monitoring'][2] > START:
                        batch_rho3_monitor.append(np.sum(monitoring_centre.service[2][k_mon_3:k_mon_3+batch_size]) / (last['monitoring'][2] - first['monitoring'][5]))
                        first['monitoring'][2] = OFF

                    k_mon_3 += batch_size


        # --------------------------------------------------------------------------------------------------------------
        # *                                          Analyze&Plan Area Events
        # * ------------------------------------------------------------------------------------------------------------
        # */

        if e == MONITORING_SERVERS*2:                                            # process an arrival to An&PlaC      */
            planning_centre.number += 1                                          # plus one job in the area           */

            if first['planning'][0] == OFF:
                first['planning'][1] = t.current
                first['planning'][0] = ON

            events[e].x = OFF                                                    # turn off the arrival               */
            if planning_centre.number == 1:                                      # prepares next departure            */
                service = planning_centre.get_service(e+2)
                served = t.current + service
                events[e+2].t = served
                events[e+2].x = ON
                waiting_times_plan[0].append(0.0)                                # update integrals                   */
                departed_queue1 += 1
                response_times_plan.append(served - t.current)
                response_times_plan_1.append(served - t.current)
                planning_centre.service.append(service)                          # update integrals                   */
            else:
                # save the timestamp of the arrival as token for the job                                              */
                planning_centre.queue[0].append(t.current)                       # plus one job in the queue          */

        if e == MONITORING_SERVERS*2+1:                                          # process an arrival to An&PlaC      */
            planning_centre.number += 1                                          # plus one job in the area           */

            if first['planning'][0] == OFF:
                first['planning'][1] = t.current
                first['planning'][0] = ON

            events[e].x = OFF                                                    # turn off the arrival               */
            if planning_centre.number == 1:                                      # prepares next departure            */
                service = planning_centre.get_service(e+1)
                served = t.current + service
                events[e+1].t = served
                events[e+1].x = ON
                waiting_times_plan[1].append(0.0)                                # update integrals                   */
                departed_queue2 += 1
                response_times_plan.append(served - t.current)
                planning_centre.service.append(service)                          # update integrals                   */
            else:
                # save the timestamp of the arrival as token for the job                                              */
                planning_centre.queue[1].append(t.current)                       # plus one job in the queue          */

        if e == MONITORING_SERVERS*2+2:
            planning_centre.number -= 1                                          # minus one job in the area          */
            planning_centre.departed += 1                                        # plus one departure from the PArea  */
            number -= 1                                                          # minus one job in the system        */
            departed_jobs += 1                                                   # plus one departed job from system  */

            if len(planning_centre.queue[0]) > 0:                                # prepares next departure            */
                arrived = planning_centre.queue[0].pop(0)
                waiting_times_plan[0].append(t.current - arrived)                # update integrals                   */
                departed_queue1 += 1
                service = planning_centre.get_service(e)
                served = t.current + service
                events[e].t = served                                             # schedule next departure            */
                response_times_plan.append(served - arrived)
                response_times_plan_1.append(served - arrived)
                planning_centre.service.append(service)                          # update integrals                   */
            else:
                if len(planning_centre.queue[1]) > 0:
                    arrived = planning_centre.queue[1].pop(0)
                    waiting_times_plan[1].append(t.current - arrived)            # update integrals                   */
                    departed_queue2 += 1
                    service = planning_centre.get_service(e)
                    served = t.current + service
                    events[e].t = served                                         # schedule next departure            */
                    response_times_plan.append(served - arrived)
                    planning_centre.service.append(service)                      # update integrals                   */
                else:
                    events[e].x = OFF

            last['planning'] = t.current

            # FOR INFINITE-HORIZON SIMULATION
            if batch_size > 1:
                if planning_centre.departed % batch_size == 0:
                    # Time to save up some metrics

                    # E[Ts]
                    batch_response_times_plan.append(np.mean(response_times_plan[k_pla:k_pla+batch_size]))

                    # ρ
                    if last['planning'] > START:
                        batch_rho_plan.append(np.sum(planning_centre.service[k_pla:k_pla+batch_size]) / (last['planning'] - first['planning'][1]))
                        first['planning'][0] = OFF

                    k_pla += batch_size

                if departed_queue1 > 0 and  departed_queue1 % batch_size == 0:
                    # E[Tq1]
                    batch_waiting_times_plan[0].append(np.mean(waiting_times_plan[0][k_pla_queue1:k_pla_queue1+batch_size]))
                    batch_response_times_plan1.append(np.mean(response_times_plan_1[k_pla_queue1:k_pla_queue1+batch_size]))
                    k_pla_queue1 += batch_size
                    departed_queue1 = 0
                if departed_queue2 > 0 and  departed_queue2 % batch_size == 0:
                    # E[Tq2]
                    batch_waiting_times_plan[1].append(np.mean(waiting_times_plan[1][k_pla_queue2:k_pla_queue2+batch_size]))
                    k_pla_queue2 += batch_size
                    departed_queue2 = 0

    rho_mon_1 = np.sum(monitoring_centre.service[0]) / (last['monitoring'][0] - first['monitoring'][3])
    rho_mon_2 = np.sum(monitoring_centre.service[1]) / (last['monitoring'][1] - first['monitoring'][4])
    rho_mon_3 = np.sum(monitoring_centre.service[2]) / (last['monitoring'][2] - first['monitoring'][5])
    rho_pla = np.sum(planning_centre.service) / (last['planning'] - first['planning'][1])

    batch_stats = {
        "monitor_response_times": batch_response_times_monitor,
        "response_times_monitor_1": batch_response_times_monitor_1,
        "monitor_waiting_times": batch_waiting_times_monitor,
        "plan_response_times": batch_response_times_plan,
        "plan_response_times_1": batch_response_times_plan1,
        "plan_waiting_times_queue1": batch_waiting_times_plan[0],
        "plan_waiting_times_queue2": batch_waiting_times_plan[1],

        "rho1_mon": batch_rho1_monitor,
        "rho2_mon": batch_rho2_monitor,
        "rho3_mon": batch_rho3_monitor,
        "rho_plan": batch_rho_plan,
    }

    return [response_times_monitor, waiting_times_monitor, response_times_plan, waiting_times_plan[0]+waiting_times_plan[1], rho_mon_1, rho_mon_2, rho_mon_3, rho_pla, batch_stats, waiting_times_plan[0], waiting_times_plan[1], response_times_monitor_1, response_times_plan_1]
