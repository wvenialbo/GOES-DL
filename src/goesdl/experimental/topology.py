import math

import gudhi as gd
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage


def remove_small_blobs(binary_image, size):
    labeled, nobject = ndimage.label(1 - binary_image)
    for label in range(0, nobject):
        masked = labeled == label
        area = np.count_nonzero(masked)
        if area <= size:
            binary_image[masked] = 1

    return binary_image


def create_complex(field_map, verbose=False):
    # Crear el complejo cúbico
    cubical_complex = gd.CubicalComplex(top_dimensional_cells=field_map)

    if verbose:
        print(
            f"Cubical complex is of dimension {cubical_complex.dimension()} - {cubical_complex.num_simplices()} cubes."
        )

    return cubical_complex


def maximum_persistence(n, persistence_pairs):
    max_birth = 0
    max_death = 0
    max_lifetime = 0
    for h, (birth, death) in persistence_pairs:
        if h == n:
            lifetime = death - birth
            if lifetime > max_lifetime and lifetime != math.inf:
                max_lifetime = lifetime
                max_birth = birth
                max_death = death

    return max_lifetime, (max_birth, max_death)


def plot_persistence_diagram(persistence_pairs):
    # Extract birth and death times
    labels = [pair[0] for pair in persistence_pairs]
    births = [pair[1][0] for pair in persistence_pairs]
    deaths = [pair[1][1] for pair in persistence_pairs]
    deaths = [255 if value > 255 else value for value in deaths]

    # # Plot the persistence diagram
    plt.figure(figsize=(8, 6))
    plt.scatter(births, deaths, c=labels)
    plt.xlabel("Birth")
    plt.ylabel("Death")
    plt.title("Persistence Diagram")
    plt.show()


def plot_persistence_diagram(persistence_pairs):
    # Graficar el diagrama de persistencia
    gd.plot_persistence_diagram(persistence_pairs)
    plt.xlabel("Birth")
    plt.ylabel("Death")
    plt.title("Persistence Diagram")

    plt.tight_layout()
    plt.show()
