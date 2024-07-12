import sys
import subsystems.system as system
import subsystems.libs as libs
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from plots import plots

RESPONSE_TIME_MONITOR1 = []
RESPONSE_TIME_MONITOR = []
WAITING_TIME_MONITOR = []
RESPONSE_TIME_PLAN = []
WAITING_TIME_PLAN = []

RHO_MONITOR_1 = []
RHO_MONITOR_2 = []
RHO_MONITOR_3 = []
RHO_PLAN = []

ALPHA = 0.05
SEED = 123456789


def confidence_interval(alpha, n, l) -> float:
    sigma = np.std(l, ddof=1)
    if n > 1:
        t = libs.rvms.idfStudent(n - 1, 1 - alpha / 2)
        return (t * sigma) / np.sqrt(n - 1)
    else:
        return 0.0


def batch_means(data, batch_size):
    n = len(data)
    num_batches = n // batch_size
    batch_means = []

    for i in range(num_batches):
        batch = data[i * batch_size: (i + 1) * batch_size]
        batch_means.append(np.mean(batch))

    return batch_means


def write_on_csv(input_list):
    with open("acs.dat", mode='w', newline='') as file:
        writer = csv.writer(file)
        for element in input_list:
            writer.writerow([element])


def cumulative_mean(data):
    # Computes the cumulative mean for an array of data
    return np.cumsum(data) / np.arange(1, len(data) + 1)


def plot_cumulative_means(cumulative_means, stationary_value, ylabel, title, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_means, label=ylabel)
    plt.xlabel('Batch Number')

    # Plot a horizontal line for the stationary value
    plt.axhline(stationary_value, color='orange', label='Mean of means')

    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)

    # Create folder 'plots' if it doesn't exist
    if not os.path.exists('plots'):
        os.makedirs('plots')

    # Save plots
    plt.savefig(f'plots/{filename}.png')
    plt.close()


def finite(seed, n, stop):
    libs.rngs.plantSeeds(seed)
    for i in range(n):
        try:
            res = system.simulation(stop)
            response_times_monitor, waiting_times_monitor = res[0], res[1]
            response_times_monitor_1 = res[9]
            response_times_plan, waiting_times_plan = res[2], res[3]
            rho_1_man, rho_2_man, rho_3_man = res[4], res[5], res[6]
            rho_plan = res[7]

            response_times_monitor_avg = np.mean(response_times_monitor)
            response_times_monitor_avg_1 = np.mean(response_times_monitor_1)
            waiting_times_monitor_avg = np.mean(waiting_times_monitor)
            response_times_plan_avg = np.mean(response_times_plan)
            waiting_times_plan_avg = np.mean(waiting_times_plan)

            RESPONSE_TIME_MONITOR.append(response_times_monitor_avg)
            RESPONSE_TIME_MONITOR1.append(response_times_monitor_avg_1)
            WAITING_TIME_MONITOR.append(waiting_times_monitor_avg)
            RESPONSE_TIME_PLAN.append(response_times_plan_avg)
            WAITING_TIME_PLAN.append(waiting_times_plan_avg)

            RHO_MONITOR_1.append(rho_1_man)
            RHO_MONITOR_2.append(rho_2_man)
            RHO_MONITOR_3.append(rho_3_man)
            RHO_PLAN.append(rho_plan)
        except Exception as e:
            print(f"An error occurred during execution {i + 1}: {e}")


def infinite(seed, stop, batch_size=1.0):
    libs.rngs.plantSeeds(seed)
    try:
        res = system.simulation(stop, batch_size)
        batch_stats = res[8]

        RESPONSE_TIME_MONITOR.extend(batch_stats["monitor_response_times"])
        RESPONSE_TIME_MONITOR1.extend(batch_stats["response_times_monitor_1"])
        WAITING_TIME_MONITOR.extend(batch_stats["monitor_waiting_times"])
        RESPONSE_TIME_PLAN.extend(batch_stats["plan_response_times"])
        WAITING_TIME_PLAN.extend(batch_stats["plan_waiting_times"])

        RHO_MONITOR_1.extend(batch_stats["rho1_mon"])
        RHO_MONITOR_2.extend(batch_stats["rho2_mon"])
        RHO_MONITOR_3.extend(batch_stats["rho3_mon"])
        RHO_PLAN.extend(batch_stats["rho_plan"])

        write_on_csv(RESPONSE_TIME_MONITOR1)

    except Exception as e:
        print(f"An error occurred during execution: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python originalmain.py <number_of_times> [finite | infinite]")
        sys.exit(1)

    if sys.argv[2] == "finite":
        try:
            n = int(sys.argv[1])
            stop = 20000.0
            finite(SEED, n, stop)

            response_time_monitor_interval = confidence_interval(ALPHA, n, RESPONSE_TIME_MONITOR)
            response_time_monitor1_interval = confidence_interval(ALPHA, n, RESPONSE_TIME_MONITOR1)
            waiting_time_monitor_interval = confidence_interval(ALPHA, n, WAITING_TIME_MONITOR)
            response_time_plan_interval = confidence_interval(ALPHA, n, RESPONSE_TIME_PLAN)
            waiting_time_plan_interval = confidence_interval(ALPHA, n, WAITING_TIME_PLAN)

            rho_man1_interval = confidence_interval(ALPHA, n, RHO_MONITOR_1)
            rho_man2_interval = confidence_interval(ALPHA, n, RHO_MONITOR_2)
            rho_man3_interval = confidence_interval(ALPHA, n, RHO_MONITOR_3)
            rho_pla_interval = confidence_interval(ALPHA, n, RHO_PLAN)

            print("Monitor Centre")
            print(f"E[Tq] = {np.mean(WAITING_TIME_MONITOR)} +/- {waiting_time_monitor_interval}")
            print(f"E[Ts] = {np.mean(RESPONSE_TIME_MONITOR)} +/- {response_time_monitor_interval}")
            print(f"E[Ts1] = {np.mean(RESPONSE_TIME_MONITOR1)} +/- {response_time_monitor1_interval}")
            print(f"rho1 = {np.mean(RHO_MONITOR_1)} +/- {rho_man1_interval}")
            print(f"rho2 = {np.mean(RHO_MONITOR_2)} +/- {rho_man2_interval}")
            print(f"rho3 = {np.mean(RHO_MONITOR_3)} +/- {rho_man3_interval}")

            print("Plan Centre")
            print(f"E[Tq] = {np.mean(WAITING_TIME_PLAN)} +/- {waiting_time_plan_interval}")
            print(f"E[Ts] = {np.mean(RESPONSE_TIME_PLAN)} +/- {response_time_plan_interval}")
            print(f"rho = {np.mean(RHO_PLAN)} +/- {rho_pla_interval}")

        except ValueError:
            print("The argument must be an integer.")
            sys.exit(1)

    elif sys.argv[2] == "infinite":
        stop = 2000000.0
        batch_size=128

        infinite(SEED, stop, batch_size=batch_size)

        # response_time_monitor_mean: Provided no points are discarded,                                           */
        # the “mean of the means” is the same as the “grand sample mean”                                          */
        response_time_monitor_mean = np.mean(RESPONSE_TIME_MONITOR)
        response_time_monitor_interval = confidence_interval(ALPHA, len(RESPONSE_TIME_MONITOR), RESPONSE_TIME_MONITOR)

        response_time_monitor1_mean = np.mean(RESPONSE_TIME_MONITOR1)
        response_time_monitor1_interval = confidence_interval(ALPHA, len(RESPONSE_TIME_MONITOR1), RESPONSE_TIME_MONITOR1)

        waiting_time_monitor_mean = np.mean(WAITING_TIME_MONITOR)
        waiting_time_monitor_interval = confidence_interval(ALPHA, len(WAITING_TIME_MONITOR), WAITING_TIME_MONITOR)

        response_time_plan_mean = np.mean(RESPONSE_TIME_PLAN)
        response_time_plan_interval = confidence_interval(ALPHA, len(RESPONSE_TIME_PLAN), RESPONSE_TIME_PLAN)

        waiting_time_plan_mean = np.mean(WAITING_TIME_PLAN)
        waiting_time_plan_interval = confidence_interval(ALPHA, len(WAITING_TIME_PLAN), WAITING_TIME_PLAN)


        rho_man1_mean = np.mean(RHO_MONITOR_1)
        rho_man1_interval = confidence_interval(ALPHA, len(RHO_MONITOR_1), RHO_MONITOR_1)
        rho_man2_mean = np.mean(RHO_MONITOR_2)
        rho_man2_interval = confidence_interval(ALPHA, len(RHO_MONITOR_2), RHO_MONITOR_2)
        rho_man3_mean = np.mean(RHO_MONITOR_3)
        rho_man3_interval = confidence_interval(ALPHA, len(RHO_MONITOR_3), RHO_MONITOR_3)
        rho_plan_mean = np.mean(RHO_PLAN)
        rho_plan_interval = confidence_interval(ALPHA, len(RHO_PLAN), RHO_PLAN)


        print("Monitor Centre")
        print(f"E[Tq] = {waiting_time_monitor_mean} +/- {waiting_time_monitor_interval}")
        print(f"E[Ts] = {response_time_monitor_mean} +/- {response_time_monitor_interval}")
        print(f"E[Ts1] = {response_time_monitor1_mean} +/- {response_time_monitor1_interval}")
        print(f"rho_1 = {rho_man1_mean} +/- {rho_man1_interval}")
        print(f"rho_2 = {rho_man2_mean} +/- {rho_man2_interval}")
        print(f"rho_3 = {rho_man3_mean} +/- {rho_man3_interval}")

        print("Plan Centre")
        print(f"E[Tq] = {waiting_time_plan_mean} +/- {waiting_time_plan_interval}")
        print(f"E[Ts] = {response_time_plan_mean} +/- {response_time_plan_interval}")
        print(f"rho = {rho_plan_mean} +/- {rho_plan_interval}")

        # Compute cumulative means
        cumulative_response_time_monitor = cumulative_mean(RESPONSE_TIME_MONITOR)
        cumulative_response_time1_monitor = cumulative_mean(RESPONSE_TIME_MONITOR1)
        cumulative_waiting_time_monitor = cumulative_mean(WAITING_TIME_MONITOR)
        cumulative_response_time_plan = cumulative_mean(RESPONSE_TIME_PLAN)
        cumulative_waiting_time_plan = cumulative_mean(WAITING_TIME_PLAN)

        # Plot for QoS1
        values = (np.array(cumulative_response_time_monitor) + np.array(cumulative_response_time_plan)).tolist()
        plots.plot_qos1_base(values)

        # Plot for QoS2
        min_length = min(len(cumulative_response_time1_monitor), len(cumulative_response_time_plan))
        array1 = np.array(cumulative_response_time1_monitor[:min_length])
        array2 = np.array(cumulative_response_time_plan[:min_length])
        values = (np.array(array1) + np.array(array2)).tolist()
        plots.plot_qos2_base(values)


        # Plot cumulative means for Monitor area
        plot_cumulative_means(cumulative_response_time_monitor, response_time_monitor_mean,
                              'Cumulative Mean Response Time (Monitor)',
                              'Cumulative Mean Response Time over Batches (Monitor Centre)',
                              'cumulative_response_time_monitor')
        plot_cumulative_means(cumulative_response_time1_monitor, response_time_monitor1_mean,
                              'Cumulative Mean Response Time 1 (Monitor)',
                              'Cumulative Mean Response Time 1 over Batches (Monitor Centre)',
                              'cumulative_response_time1_monitor')
        plot_cumulative_means(cumulative_waiting_time_monitor, waiting_time_monitor_mean,
                              'Cumulative Mean Waiting Time (Monitor)',
                              'Cumulative Mean Waiting Time over Batches (Monitor Centre)',
                              'cumulative_waiting_time_monitor')

        # Plot cumulative means for Plan area
        plot_cumulative_means(cumulative_response_time_plan, response_time_plan_mean,
                              'Cumulative Mean Response Time (Plan)',
                              'Cumulative Mean Response Time over Batches (Plan Centre)',
                              'cumulative_response_time_plan')
        plot_cumulative_means(cumulative_waiting_time_plan, waiting_time_plan_mean,
                              'Cumulative Mean Waiting Time (Plan)',
                              'Cumulative Mean Waiting Time over Batches (Plan Centre)', 'cumulative_waiting_time_plan')

    else:
        print("Usage: python originalmain.py <number_of_times> [finite | infinite]")
        sys.exit(1)
