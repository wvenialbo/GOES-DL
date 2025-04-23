from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from ..utils.array import ArrayBool, ArrayInt32, MaskedFloat32

ADD_OFFSET = "add_offset"
BOUNDS = "bounds"
MISSING_VALUE = "missing_value"
SCALE_FACTOR = "scale_factor"


class Explorer:

    visited: list[str] = []
    dim_visited: list[str] = []
    grp_visited: list[str] = []

    def __init__(self) -> None:
        self.visited = []
        self.dim_visited = []
        self.grp_visited = []

    def __call__(self, file_path: str | Path) -> None:
        self.visited = []
        self.dim_visited = []
        self.grp_visited = []

        self._explore_netcdf(file_path)

    def _explore_netcdf(self, file_path: str | Path) -> None:
        try:
            file_path = Path(file_path)

            with Dataset(file_path, "r") as nc_file:
                print(f"----- Dataset: {file_path} -----\n")
                print(nc_file)
                print()

                variable_names = nc_file.variables.keys()

                for variable_name in list(variable_names):
                    self._explore_variable(variable_name, nc_file)

                dimension_names = nc_file.dimensions.keys()

                for dimension_name in list(dimension_names):
                    self._explore_dimension(dimension_name, nc_file)

                group_names = nc_file.groups.keys()

                for group_name in list(group_names):
                    self._explore_group(group_name, nc_file)

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")

        except KeyError:
            print(
                f"Error: The field '{variable_name}' does not exist in the file."
            )

        except Exception as e:
            print(f"An error occurred: {e}")

    def _explore_dimension(
        self, dimension_name: str, nc_file: Dataset
    ) -> None:
        if dimension_name in self.dim_visited:
            return

        self.dim_visited.append(dimension_name)

        # Accede a la variable
        dimension = nc_file.dimensions[dimension_name]

        print(f"----- Dimension: {dimension_name} -----\n")
        print(dimension)

        print()

    def _explore_group(self, group_name: str, nc_file: Dataset) -> None:
        if group_name in self.grp_visited:
            return

        self.grp_visited.append(group_name)

        # Accede a la variable
        group = nc_file.dimensions[group_name]

        print(f"----- Dimension: {group_name} -----\n")
        print(group)

        print()

    def _explore_variable(self, variable_name: str, nc_file: Dataset) -> None:
        if variable_name in self.visited:
            return

        self.visited.append(variable_name)

        # Accede a la variable
        variable = nc_file.variables[variable_name]

        print(f"----- Variable: {variable_name} -----\n")
        print(variable)

        if hasattr(variable, SCALE_FACTOR) or hasattr(variable, ADD_OFFSET):
            self._check_variable(variable_name, nc_file)

        print()

        if hasattr(variable, BOUNDS):
            bounds_variable_name: str = getattr(variable, BOUNDS)
            self._explore_variable(bounds_variable_name, nc_file)

    @staticmethod
    def _check_variable(variable_name: str, nc_file: Dataset) -> None:
        # Desactiva la conversión automática de máscara y escala
        nc_file.set_auto_maskandscale(False)

        # Accede a la variable
        variable = nc_file.variables[variable_name]

        # Lee los datos sin aplicar la conversión automática
        datos_originales: ArrayInt32 = variable[:]

        scale_factor: float = (
            getattr(variable, SCALE_FACTOR)
            if hasattr(variable, SCALE_FACTOR)
            else 1.0
        )
        add_offset: float = (
            getattr(variable, ADD_OFFSET)
            if hasattr(variable, ADD_OFFSET)
            else 0.0
        )
        missing_value: float = (
            getattr(variable, MISSING_VALUE)
            if hasattr(variable, MISSING_VALUE)
            else np.nan
        )

        print(f"scale_factor = {scale_factor}")
        print(f"add_offset = {add_offset}")
        print(f"missing_value = {missing_value}")

        mask: ArrayBool = datos_originales == missing_value
        data = datos_originales * scale_factor + add_offset

        datos_calculados: MaskedFloat32 = MaskedFloat32(data, mask=mask)

        data[mask] = np.nan

        datos_filtrados = datos_originales[datos_originales != missing_value]

        no_data = datos_filtrados.size == 0

        if no_data:
            datos_filtrados = datos_calculados

        print(f"raw min = {np.min(datos_filtrados)}")
        print(f"raw max = {np.max(datos_filtrados)}")
        print(f"actual min = {np.min(datos_calculados)}")
        print(f"actual max = {np.max(datos_calculados)}")

        # Activa la conversión automática de máscara y escala
        nc_file.set_auto_maskandscale(True)

        # Lee los datos aplicando la conversión automática
        datos_automaticos = variable[:]

        if no_data:
            print("consistent conversion: no data")
        else:
            igual = np.all(datos_calculados == datos_automaticos)
            print(f"consistent conversion: {'yes' if igual else 'no'}")


explore_netcdf = Explorer()
