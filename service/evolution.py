import matplotlib.pyplot as plt
import numpy as np


def count_activities(data):
    activity_counts = {}
    for i, day in enumerate(data, start=1):
        activities = data[day]['activities']
        times = data[day]['times']
        activity_counts[day] = {'count': len(activities), 'total_time': sum(times), 'index': i}
    return activity_counts

def plot_activity_frequency(activity_counts):
    days = list(activity_counts.keys())
    frequencies = [count['count'] for count in activity_counts.values()]
    total_times = [count['total_time'] for count in activity_counts.values()]
    indices = [count['index'] for count in activity_counts.values()]

    fig, ax = plt.subplots()

    # Utiliser des valeurs numériques pour les abscisses
    x_values = np.arange(len(days))

    ax.plot(x_values, frequencies, color='skyblue', marker='o', label='Nombre d\'activités')
    ax.plot(x_values, total_times, color='orange', marker='o', label='Temps total (minutes)')

    # Étiqueter les axes avec les jours de la semaine
    ax.set_xticks(x_values)
    ax.set_xticklabels(days)

    ax.set_xlabel("Jours de la semaine", fontsize=12)
    ax.set_ylabel("Nombre d'activités / Temps total (minutes)", fontsize=12)
    ax.set_title("Évolution du nombre d'activités et du temps total par jour", fontsize=14)

    ax.legend()

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des étiquettes des jours pour une meilleure lisibilité
    plt.savefig("static/plot.png")
    print("j'ai fais plot")
