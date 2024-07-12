import matplotlib.pyplot as plt
import numpy as np


def plot_cumulative_and_qos(qos, cumulative_values, x_label, y_label, title, filename, label_values, label_qos):
    # Dati da plottare
    x = np.arange(len(cumulative_values))
    y = cumulative_values

    # Creazione del plot
    plt.figure(figsize=(9, 5))  # Dimensioni del plot (larghezza, altezza)
    plt.plot(x, y, label=label_values)  # Plot dei dati con linea e marker
    plt.axhline(y=qos, color='r', label=label_qos)
    plt.title(title)  # Titolo del grafico
    plt.xlabel(x_label)  # Etichetta dell'asse X
    plt.ylabel(y_label)  # Etichetta dell'asse Y
    plt.grid(True)  # Mostra griglia
    plt.legend()  # Mostra legenda
    # Salvataggio del plot come immagine PNG
    plt.savefig('plots/' + filename + '.png')


#_______________QoS1 base________________________________________________________________
def plot_qos1_base(value_list):
    print("Plotting QoS 1 base")
    qos = 0.5
    # Values: Global mean response times (Base)
    cumulative_values = value_list
    x_label = 'Batch Number'
    y_label = 'Cumulative response time value (s)'
    title = 'QoS1: Cumulative global mean response time (Base System)'
    filename = 'qos1_response_time_base'
    label_values = 'Cumulative global mean response time'
    label_qos = 'QoS1: Response time'
    plot_cumulative_and_qos(qos, cumulative_values, x_label, y_label, title, filename, label_values, label_qos)


#________________QoS2 base______________________________________________________________
def plot_qos2_base(value_list):
    qos = 0.0019320729
    # Values: Fatal mean response times (Base)
    cumulative_values = value_list
    x_label = 'Batch Number'
    y_label = 'Cumulative response time value (s)'
    title = 'QoS2: Cumulative mean response time for Web server logs (Base System)'
    filename = 'qos2_response_time_1_base'
    label_values = 'Cumulative Mean response time for Web server logs'
    label_qos = 'QoS2: Response time'
    plot_cumulative_and_qos(qos, cumulative_values, x_label, y_label, title, filename, label_values, label_qos)


#______________________________QoS1 better______________________________________________
def plot_qos1_better(value_list):
    qos = 0.5
    # Values: Global mean response times (Better)
    cumulative_values = value_list
    x_label = 'Batch Number'
    y_label = 'Cumulative response time value (s)'
    title = 'QoS1: Cumulative global mean response time (Better System)'
    filename = 'qos1_response_time_better'
    label_values = 'Cumulative global mean response time'
    label_qos = 'QoS1: Response time'
    plot_cumulative_and_qos(qos, cumulative_values, x_label, y_label, title, filename, label_values, label_qos)


#_____________________________QoS2 better__________________________________________________
def plot_qos2_better(value_list):
    qos = 0.0019320729
    # Values:Fatal mean response times (Better)
    cumulative_values = value_list
    x_label = 'Batch Number'
    y_label = 'Cumulative response time value (s)'
    title = 'QoS2: Cumulative mean response time for Web server logs (Better System)'
    filename = 'qos2_response_time_1_better'
    label_values = 'Cumulative Mean response time for Web server logs'
    label_qos = 'QoS2: Response time'
    plot_cumulative_and_qos(np.mean(value_list), cumulative_values, x_label, y_label, title, filename, label_values, label_qos)
