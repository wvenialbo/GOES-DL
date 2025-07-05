from math import ceil
from typing import Any

import numpy as np
from numpy import all as npall
from numpy import floating
from numpy.typing import NDArray

from ..utils.array import ArrayFloat, ArrayIndex, ToIndex
from .config import ConfigDict

_Array = NDArray[floating[Any]]
_Series = list[_Array]


_MAX_ITEMS = 10

_DESCRIPTIONS = {
    0.001: "EXTREMADAMENTE SIGNIFICATIVAS",
    0.01: "MUY SIGNIFICATIVAS",
    0.05: "SIGNIFICATIVAS",
}

_ICONS = {
    0.001: "🌟",  # Una estrella dorada para lo más significativo, indicando la "excelencia" o lo "más brillante", como CH.
    0.01: "🚀",  # Un cohete para "muy significativo", sugiriendo un despegue o un impacto fuerte. "Va a salir como un cohete esto, creo..."
    0.05: "🔔",  # Una campana para "significativo", como una "alerta" de algo notable
}

_LEVELS = [0.001, 0.01, 0.05]
_LEVEL = _LEVELS[-1]


def interpretar_p_valores(
    frecuencias: ArrayFloat,
    p_valores: ArrayFloat,
    indices_picos_reales: ArrayIndex | None = None,
) -> None:
    """
    Genera interpretación automática de la curva de p-valores.

    Se enfoca en los picos dominantes señalados por 'indices' para las
    estadísticas de conteo y listado de picos significativos, mientras
    que las estadísticas generales (min, median) y las proporciones se
    basan en todo el espectro de p-valores.

    Parameters
    ----------
    frecuencias (np.array)
        Array de frecuencias de todo el espectro.
    p_valores (np.array)
        Array de p-valores correspondientes a todas las frecuencias.
    indices_picos_reales (np.array, list, optional)
        Índices de las "cimas de los picos" que se desean analizar para
        los conteos y listados específicos.  Si es None (por defecto),
        se considerarán todos los índices del array de frecuencias como
        'picos' para este propósito.
    """
    print("\n" + "=" * 60)
    print("INTERPRETACIÓN AUTOMÁTICA DE P-VALORES ESPECTRALES")
    print("=" * 60)

    # --- 1. Manejo del parámetro opcional 'indices_picos_reales' y creación de subconjuntos ---
    # Si 'indices' no se proporciona, usa todos los índices del array de frecuencias.
    if indices_picos_reales is None:
        indices_a_analizar: ArrayIndex = np.arange(len(frecuencias))
        print(
            "\nℹ️ 'indices_picos_reales' no fue proporcionado. "
            "Analizando el espectro completo."
        )
    else:
        # Asegurarse de que 'indices_picos_reales' sea un array de numpy para indexación
        # avanzada eficiente. Esto es útil si el usuario pasa una lista normal.
        indices_a_analizar = np.asarray(indices_picos_reales)
        if len(indices_a_analizar) == 0:
            print(
                "⚠️ Advertencia: 'indices_picos_reales' fue proporcionado "
                "pero está vacío. No se contarán picos específicos."
            )
            indices_a_analizar = np.arange(len(frecuencias))
        else:
            print(
                f"\nℹ️ Preselección: Analizando {len(indices_a_analizar)} "
                "frecuencias específicas."
            )

    # Extraer los subconjuntos de p-valores y frecuencias una sola vez.
    # Esto evita indexar p_valores[indices_a_analizar] y frecuencias[indices_a_analizar]
    # repetidamente, lo que es más eficiente para arrays grandes.
    p_valores_analisis = p_valores[indices_a_analizar]
    frecuencias_analisis = frecuencias[indices_a_analizar]

    # --- 2. Estadísticas generales ---
    n_total = len(p_valores)
    n_analizadas = len(p_valores_analisis)
    n_sig_05 = np.sum(p_valores_analisis < 0.05)
    n_sig_01 = np.sum(p_valores_analisis < 0.01)
    n_sig_001 = np.sum(p_valores_analisis < 0.001)

    prop_05 = n_sig_05 / n_total if n_total > 0 else 0
    prop_01 = n_sig_01 / n_total if n_total > 0 else 0
    prop_001 = n_sig_001 / n_total if n_total > 0 else 0
    esperado_05 = 0.05

    p_min = np.min(p_valores) if n_total > 0 else 0
    p_median = np.median(p_valores) if n_total > 0 else 0

    print("\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total de frecuencias analizadas: {n_total}")
    if 0 < n_analizadas < n_total:
        print(
            f"   • Total de frecuencias puras: {n_analizadas} ({n_analizadas/n_total:.1%})"
        )
    if n_total > 0:
        print(f"   • P-valor mínimo encontrado: {p_min:.2e}")
        print(f"   • P-valor mediano: {p_median:.3f}")
    else:
        print("   • No hay p-valores para analizar.")

    print("\n🎯 NIVELES DE SIGNIFICANCIA:")
    if n_total > 0:
        print(f"   • p < 0.05:  {n_sig_05:3d} frecuencias ({prop_05:.1%})")
        print(f"   • p < 0.01:  {n_sig_01:3d} frecuencias ({prop_01:.1%})")
        print(f"   • p < 0.001: {n_sig_001:3d} frecuencias ({prop_001:.1%})")
    else:
        print("   • No hay p-valores para analizar.")

    # --- 3. Evaluación estadística ---
    print("\n📈 EVALUACIÓN ESTADÍSTICA:")
    mensaje_base = f"{prop_05:.1%} vs {esperado_05:.1%} esperado"
    if n_total == 0:
        print("   • No hay datos para realizar una evaluación estadística.")
    elif prop_05 > esperado_05 * 2:
        print(f"   ⚠️ SEÑALES DETECTADAS: {mensaje_base}")
        print("       → Evidencia fuerte de componentes no-aleatorias.")
    elif prop_05 > esperado_05 * 1.5:
        print(f"   ⚡ POSIBLES SEÑALES: {mensaje_base}")
        print("       → Evidencia moderada de componentes no-aleatorias.")
    elif prop_05 < esperado_05 * 0.5:
        print(f"   💤 ESPECTRO MUY SILENCIOSO: {mensaje_base}")
        print(
            "       → Posible preselección, sobre-filtrado o señal muy débil."
        )
    else:
        print(f"   ✅ COMPORTAMIENTO NORMAL: {mensaje_base}")
        print("       → Consistente con ruido de fondo.")

    print(f"\n🔍 RESUMEN EJECUTIVO (> percentil {_LEVEL:.1%}):")
    if n_total == 0:
        print("No se puede generar un resumen ejecutivo sin datos.")
    elif prop_05 > 0.1:
        print(
            f"   🔴 ALTA ACTIVIDAD: {prop_05:.1%} "
            "del espectro es significativo"
        )
    elif prop_05 > 0.075:
        print(
            f"   🟡 ACTIVIDAD MODERADA: {prop_05:.1%} "
            "del espectro es significativo"
        )
    elif prop_05 > 0.025:
        print(
            f"   🟢 ACTIVIDAD NORMAL: {prop_05:.1%} "
            "del espectro es significativo"
        )
    else:
        print(
            f"   🔵 BAJA ACTIVIDAD: {prop_05:.1%} "
            "del espectro es significativo)"
        )

    # --- 4. Identificar picos más significativos---

    indices_ya_reportados: set[ToIndex] = set()

    if n_total > 0:
        n_count = 5

        n_reportados = 0

        for umbral_actual in _LEVELS:
            # Filtra p_valores_analisis para excluir los que ya fueron reportados
            mascara_no_reportados: ArrayIndex = np.array(
                [
                    i not in indices_ya_reportados
                    for i in range(len(p_valores_analisis))
                ]
            )

            # Aplica la máscara para obtener los p_valores y frecuencias que aún no han sido reportados
            p_valores_para_analisis_actual = p_valores_analisis[
                mascara_no_reportados
            ]

            # Obtiene los índices (locales al subconjunto 'p_valores_analisis')
            indices_extremos_locales = np.nonzero(
                p_valores_para_analisis_actual < umbral_actual
            )[0]

            n_extremos = len(indices_extremos_locales)
            n_reportados += n_extremos

            if n_extremos > 0 and n_count > 0:
                descripcion = _DESCRIPTIONS[umbral_actual]
                icon = _ICONS[umbral_actual]

                # Obtenemos los índices originales de los elementos no reportados
                indices_originales_no_reportados = np.nonzero(
                    mascara_no_reportados
                )[0]

                print(
                    f"\n{icon} FRECUENCIAS {descripcion} (p < {umbral_actual}):"
                )

                # Obtener los p_valores correspondientes a los indices_extremos_locales
                p_valores_a_ordenar = p_valores_para_analisis_actual[
                    indices_extremos_locales
                ]

                # Obtener los índices de ordenamiento (argsort) en base a estos p_valores
                orden_para_aplicar = np.argsort(p_valores_a_ordenar)

                # 3. Reordenar los propios indices_extremos_locales.
                indices_extremos_locales = indices_extremos_locales[
                    orden_para_aplicar
                ]

                # Mostrar solo los primeros 5 picos para no saturar la salida
                for i_local in indices_extremos_locales[:n_count]:
                    # El índice original de esta frecuencia significativa
                    indice_original = indices_originales_no_reportados[i_local]

                    # Usamos i_local para acceder a los valores en los subconjuntos
                    frecuencia_valor = frecuencias_analisis[indice_original]
                    periodo_valor = 24 / frecuencia_valor
                    p_valor_sig = p_valores_analisis[indice_original]
                    print(
                        "       "
                        f"f = {frecuencia_valor:>7.4f} c/d, "
                        f"T = {periodo_valor:>5.2f} h/c, "
                        f"p = {p_valor_sig:.2e}"
                    )
                    # Agrega el índice original al conjunto de índices ya reportados
                    indices_ya_reportados.add(indice_original)
                    n_count -= 1
                    n_extremos = n_extremos - 1
                if n_extremos > n_count:
                    print(f"       ... y {n_extremos-n_count} más")

        if n_reportados:
            print(
                "\n⚠️ Advertencia: Las frecuencias estadísticamente "
                "significativas\n\u2800\u2800 pueden diferir ligeramente de "
                "las físicamente significativas."
            )
        else:
            print(
                "\nℹ️ Observación: No se encontraron frecuencias significativas"
                "\n\u2800\u2800 con un nivel significancia estadística "
                f"de {_LEVEL:0.1%}."
            )
    else:
        print(
            "\nNo hay picos que mostrar debido a la falta de datos analizados."
        )

    # --- 5. Recomendaciones ---
    print("\n💡 RECOMENDACIONES:")
    if n_total == 0:
        print(
            "   • No se pueden hacer recomendaciones sin datos para analizar."
        )
    else:
        if n_sig_001 > 0:
            print("   • Investigar físicamente las frecuencias con p < 0.001")
            print("   • Considerar análisis de armónicos y sub-armónicos")
        if prop_05 > 0.1:
            print("   • Aplicar corrección por comparaciones múltiples")
            print("   • Evaluar significancia física, no solo estadística")
        if prop_05 < 0.02:
            print("   • Verificar que el modelo de ruido sea apropiado")
            print("   • Considerar aumentar resolución espectral")

    print("\n" + "=" * 60)


def visualizar_espectrogramas(
    analysers_: Any, average_analysers_: Any, settings: ConfigDict
) -> None:
    from goesdl.experimental.fourier import FourierAnalysis
    from goesdl.experimental.plotting import get_template, render_template
    from goesdl.experimental.report import interpretar_p_valores

    analysers: list[FourierAnalysis] = analysers_
    average_analysers: dict[str, FourierAnalysis] = average_analysers_

    mean_analyser = average_analysers["coherent_mean_timeseries"]

    frequencies = 24 * analysers[0].frequencies
    noise_type = settings.as_str("evaluation.noise_model")
    noise_map = {"red": "rojo", "white": "blanco"}

    global_dominant_frequency = mean_analyser.dominant_frequencies[0] * 24
    global_dominant_density = mean_analyser.dominant_densities[0]

    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        radii_km = settings.get_astype("parameters.radii_km", list[float])
        data_label = [f"r = {radius_km:.0f}-km" for radius_km in radii_km]
        ylabel = "Densidad espectral de potencia  [K²d/c]"
    elif algorithm_id in {"algorithm_1", "algorithm_2"}:
        bt_scale = settings.as_int("algorithm.bt_scale", 1)
        bt_thresholds = settings.get_astype(
            "parameters.bt_thresholds", list[int]
        )
        if bt_scale > 1:
            data_label = [
                f"µ = {bt_threshold/bt_scale:.1f} K"
                for bt_threshold in bt_thresholds
            ]
        else:
            data_label = [
                f"µ = {bt_threshold:.0f} K" for bt_threshold in bt_thresholds
            ]
        ylabel = "Densidad espectral de potencia  [km²d/c]"
    else:
        data_label = []
        ylabel = ""

    selected_analysers = analysers + [mean_analyser]

    for i, analyser in enumerate(selected_analysers):
        significant_frequencies = 24 * analyser.significant_frequencies(
            0.95, 0.99
        )
        significant_densities = analyser.significant_densities(0.95, 0.99)
        very_significant_frequencies = 24 * analyser.significant_frequencies(
            0.99
        )
        very_significant_densities = analyser.significant_densities(0.99)

        template = get_template(settings.to_dict(), "spectrogram")
        periodogram = template["subplots"]["periodogram"]
        periodogram["ylabel"] = ylabel
        plot = periodogram["plot"]

        plot[0] |= {"x": frequencies, "y": analyser.density_spectrum}
        if analyser is not mean_analyser:
            plot[0]["label"] = plot[0]["label"] % data_label[i]

        plot[1] |= {"x": frequencies, "y": mean_analyser.density_spectrum}

        plot[2] |= {"x": frequencies, "y": analyser.null}
        plot[3] |= {"x": frequencies, "y": analyser.confidence_threshold(0.90)}
        plot[4] |= {"x": frequencies, "y": analyser.confidence_threshold(0.95)}
        plot[5] |= {"x": frequencies, "y": analyser.confidence_threshold(0.99)}

        plot[6] |= {"x": frequencies, "y": analyser.significant_peaks(0.95)}

        plot[7] |= {"x": significant_frequencies, "y": significant_densities}
        plot[8] |= {
            "x": very_significant_frequencies,
            "y": very_significant_densities,
        }
        plot[9] |= {
            "x": global_dominant_frequency,
            "y": global_dominant_density,
        }

        if analyser is mean_analyser:
            plot.pop(0)
            plot[0]["linestyle"] = "-"

        x_min = periodogram["xlim"]["left"]
        x_max = periodogram["xlim"]["right"]
        x_range = x_max - x_min
        x_offset = 0.01 * x_range

        y_min = periodogram["ylim"]["bottom"]
        y_max = float(
            max(analyser.dominant_densities[0], global_dominant_density)
        )
        y_range = y_max - y_min
        y_offset = 0.01 * y_range

        periodogram["ylim"]["top"] = 1.10 * y_max

        significant_frequencies = 24 * analyser.significant_frequencies(0.95)
        significant_densities = analyser.significant_densities(0.95)
        significant_p_values = analyser.significant_p_values(0.95)

        periodogram["text"] = []
        for frequency, density in zip(
            significant_frequencies, significant_densities
        ):
            x_loc = frequency + x_offset
            y_loc = density + y_offset
            llabel = periodogram["local_text"] | {"x": x_loc, "y": y_loc}
            llabel["s"] = llabel["s"] % frequency
            periodogram["text"].append(llabel)

        x_loc = global_dominant_frequency + x_offset
        y_loc = global_dominant_density + y_offset
        glabel = periodogram["global_text"] | {"x": x_loc, "y": y_loc}
        glabel["s"] = glabel["s"] % global_dominant_frequency
        periodogram["text"].append(glabel)

        if len(significant_frequencies) == 0:
            significant_frequencies = 24 * analyser.dominant_frequencies
            significant_p_values = analyser.dominant_p_values

        dominant_frequency = significant_frequencies[0]
        dominant_period = 24 / dominant_frequency
        dominant_p_value = significant_p_values[0]

        title = periodogram["title"]
        if analyser is not mean_analyser:
            title[0]["label"] = title[0]["label"] % data_label[i]
        else:
            title[0]["label"] = periodogram["global_title"]
        title[1]["label"] = title[1]["label"] % (
            dominant_frequency,
            dominant_period,
            noise_map[noise_type],
            analyser.dof,
        )

        p_valuegram = template["subplots"]["p_valuegram"]
        plot = p_valuegram["plot"]

        plot[0] |= {"x": frequencies, "y": analyser.p_value}
        if analyser is not mean_analyser:
            plot[0]["label"] = plot[0]["label"] % data_label[i]
        else:
            plot[0]["label"] = p_valuegram["global_title"]

        for k in range(len(p_valuegram["fill_between"])):
            fill = p_valuegram["fill_between"][k]
            p_valuegram["fill_between"][k] = fill | {"x": frequencies}

        title = p_valuegram["title"]
        if analyser is not mean_analyser:
            title[0]["label"] = title[0]["label"] % data_label[i]
        else:
            title[0]["label"] = p_valuegram["global_title"]
        title[1]["label"] = title[1]["label"] % (
            dominant_p_value,
            100 * (1.0 - dominant_p_value),
        )

        frequencies_report = frequencies.copy()
        frequencies_report[analyser.peak_indices] = (
            24 * analyser.dominant_frequencies
        )
        interpretar_p_valores(
            frequencies_report, analyser.p_value, analyser.peak_indices
        )

        render_template(template)


def visualizar_capturas(
    bt_timeseries: Any,
    bt_filled_timeseries: Any,
    bt_mean_timeseries: Any,
    bt_gap_indices: Any,
    settings: ConfigDict,
) -> None:
    nseries = len(bt_timeseries)
    ngroups = ceil(nseries / 10)

    for nblock in range(ngroups + 1):
        _visualizar_capturas(
            bt_timeseries,
            bt_filled_timeseries,
            bt_mean_timeseries,
            bt_gap_indices,
            settings,
            nblock,
            nblock == ngroups,
        )


def _visualizar_capturas(
    bt_timeseries: Any,
    bt_filled_timeseries: Any,
    bt_mean_timeseries: Any,
    bt_gap_indices: Any,
    settings: ConfigDict,
    nblock: int,
    last: bool,
) -> None:
    from goesdl.experimental.plotting import plot_timeseries
    from goesdl.experimental.sequence import Sequencer

    samples_per_day = settings.as_int("subsampling.sampling_rate")
    sampling_rate = samples_per_day // 24
    series_length = settings.as_int("parameters.series_length")
    timedelta_h = settings.as_int("algorithm.delta_t")

    sequencer = Sequencer(sampling_rate)

    times_days = sequencer.build_times(series_length) / 24

    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        radii_km = settings.get_astype("parameters.radii_km", list[float])
        data_label = [f"r = {radius_km:.0f}-km" for radius_km in radii_km]
        ylabel = f"Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)  [K]"
    elif algorithm_id in {"algorithm_1", "algorithm_2"}:
        bt_scale = settings.as_int("algorithm.bt_scale", 1)
        bt_thresholds = settings.get_astype(
            "parameters.bt_thresholds", list[int]
        )
        if bt_scale > 1:
            data_label = [
                f"µ = {bt_threshold/bt_scale:.1f} K"
                for bt_threshold in bt_thresholds
            ]
        else:
            data_label = [
                f"µ = {bt_threshold:.0f} K" for bt_threshold in bt_thresholds
            ]
        ylabel = f"Max PH₀[Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)]  [km]"
    else:
        data_label = []
        ylabel = ""

    title_right = (
        f"(fs ≈ {samples_per_day} muestras/d, dt ≈ {timedelta_h:0.1f}h)",
        "right",
    )

    xlim = (0, times_days[-1])

    if last:
        timeseries = [
            [
                bt_mean_timeseries["incoherent_mean_timeseries"],
                bt_mean_timeseries["incoherent_mean_timeseries"][
                    bt_gap_indices
                ],
            ],
        ]
        params = [
            {
                "title": [
                    ["Promedio incoherente y puntos imputados", "center"],
                    title_right,
                ],
                "label": ["Serie promedio", "Puntos imputados"],
                "xarray": [times_days, times_days[bt_gap_indices]],
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": ["o-", "x"],
                "markersize": [3, 8],
                "color": [None, "red"],
            },
        ]
    else:
        m = nblock * _MAX_ITEMS
        n = m + _MAX_ITEMS

        timeseries = [
            bt_timeseries[m:n],
            bt_filled_timeseries[m:n],
        ]
        params = [
            {
                "title": [["Valores capturados", "center"], title_right],
                "label": data_label[m:n],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": "o-",
            },
            {
                "title": [["Series imputadas", "center"], title_right],
                "label": data_label[m:n],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": "--",
            },
        ]

    plot_timeseries(timeseries, settings.to_dict(), params, "series")


def visualizar_normalizados(
    bt_detrended_timeseries: Any,
    bt_mean_timeseries: Any,
    settings: ConfigDict,
) -> None:
    nseries = len(bt_detrended_timeseries)
    ngroups = ceil(nseries / 10)

    for nblock in range(ngroups + 1):
        _visualizar_normalizados(
            bt_detrended_timeseries,
            bt_mean_timeseries,
            settings,
            nblock,
            nblock == ngroups,
        )


def _visualizar_normalizados(
    bt_detrended_timeseries: Any,
    bt_mean_timeseries: Any,
    settings: ConfigDict,
    nblock: int,
    last: bool,
) -> None:
    from goesdl.experimental.plotting import plot_timeseries
    from goesdl.experimental.sequence import Sequencer

    samples_per_day = settings.as_int("subsampling.sampling_rate")
    sampling_rate = samples_per_day // 24
    series_length = settings.as_int("parameters.series_length")
    timedelta_h = settings.as_int("algorithm.delta_t")

    sequencer = Sequencer(sampling_rate)

    times_days = sequencer.build_times(series_length) / 24

    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        radii_km = settings.get_astype("parameters.radii_km", list[float])
        data_label = [f"r = {radius_km:.0f}-km" for radius_km in radii_km]
        ylabel = f"Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)  [K]"
    elif algorithm_id in {"algorithm_1", "algorithm_2"}:
        bt_scale = settings.as_int("algorithm.bt_scale", 1)
        bt_thresholds = settings.get_astype(
            "parameters.bt_thresholds", list[int]
        )
        if bt_scale > 1:
            data_label = [
                f"µ = {bt_threshold/bt_scale:.1f} K"
                for bt_threshold in bt_thresholds
            ]
        else:
            data_label = [
                f"µ = {bt_threshold:.0f} K" for bt_threshold in bt_thresholds
            ]
        ylabel = f"Max PH₀[Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)]  [km]"
    else:
        data_label = []
        ylabel = ""

    title_right = (
        f"(fs ≈ {samples_per_day} muestras/d, dt ≈ {timedelta_h:0.1f}h)",
        "right",
    )

    xlim = (0, times_days[-1])

    if last:
        timeseries = [
            [
                bt_mean_timeseries["detrended_mean_timeseries"],
                bt_mean_timeseries["incoherent_mean_timeseries"],
            ],
            [
                bt_mean_timeseries["coherent_mean_timeseries"],
                bt_mean_timeseries["detrended_mean_timeseries"],
            ],
        ]
        params = [
            {
                "title": [["Promedios incoherentes", "center"], title_right],
                "label": ["Serie sin tendencia", "Serie original"],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": ["-", "--"],
            },
            {
                "title": [["Promedios sin tendencia", "center"], title_right],
                "label": ["Promedio coherente", "Promedio incoherente"],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": ["-", "-."],
                "color": [None, "red"],
            },
        ]
    else:
        m = nblock * _MAX_ITEMS
        n = m + _MAX_ITEMS

        timeseries = [
            bt_detrended_timeseries[m:n],
        ]
        params = [
            {
                "title": [["Series sin tendencia", "center"], title_right],
                "label": data_label[m:n],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
            },
        ]

    plot_timeseries(timeseries, settings.to_dict(), params, "series")


def visualizar_filtrados(
    bt_filtered_timeseries: Any,
    bt_filtered_mean_timeseries: Any,
    settings: ConfigDict,
) -> None:
    filter_frequency = settings.as_float("filter.frequency", 0.0)

    if filter_frequency == 0:
        return

    nseries = len(bt_filtered_timeseries)
    ngroups = ceil(nseries / _MAX_ITEMS)

    for nblock in range(ngroups + 1):
        _visualizar_filtrados(
            bt_filtered_timeseries,
            bt_filtered_mean_timeseries,
            settings,
            nblock,
            nblock == ngroups,
        )


def _visualizar_filtrados(
    bt_filtered_timeseries: Any,
    bt_filtered_mean_timeseries: Any,
    settings: ConfigDict,
    nblock: int,
    last: bool,
) -> None:
    from goesdl.experimental.plotting import plot_timeseries
    from goesdl.experimental.sequence import Sequencer

    samples_per_day = settings.as_int("subsampling.sampling_rate")
    sampling_rate = samples_per_day // 24
    series_length = settings.as_int("parameters.series_length")
    timedelta_h = settings.as_int("algorithm.delta_t")

    sequencer = Sequencer(sampling_rate)

    times_days = sequencer.build_times(series_length) / 24

    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        radii_km = settings.get_astype("parameters.radii_km", list[float])
        data_label = [f"r = {radius_km:.0f}-km" for radius_km in radii_km]
        ylabel = f"Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)  [K]"
    elif algorithm_id in {"algorithm_1", "algorithm_2"}:
        bt_scale = settings.as_int("algorithm.bt_scale", 1)
        bt_thresholds = settings.get_astype(
            "parameters.bt_thresholds", list[int]
        )
        if bt_scale > 1:
            data_label = [
                f"µ = {bt_threshold/bt_scale:.1f} K"
                for bt_threshold in bt_thresholds
            ]
        else:
            data_label = [
                f"µ = {bt_threshold:.0f} K" for bt_threshold in bt_thresholds
            ]
        ylabel = f"Max PH₀[Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)]  [km]"
    else:
        data_label = []
        ylabel = ""

    xlim = (0, times_days[-1])

    filter_frequency = settings.as_float("filter.frequency")
    title_right = (
        f"(fs ≈ {samples_per_day} muestras/d, dt ≈ {timedelta_h:0.1f}h, fc ≈ {filter_frequency} c/d)",
        "right",
    )

    if last:
        timeseries = [
            [
                bt_filtered_mean_timeseries["coherent_mean_timeseries"],
                bt_filtered_mean_timeseries["detrended_mean_timeseries"],
            ],
        ]
        params = [
            {
                "title": [["Promedios sin tendencia", "center"], title_right],
                "label": ["Promedio coherente", "Promedio incoherente"],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
                "linestyle": ["-", "-."],
                "color": [None, "red"],
            },
        ]
    else:
        m = nblock * _MAX_ITEMS
        n = m + _MAX_ITEMS

        timeseries = [bt_filtered_timeseries[m:n]]
        params = [
            {
                "title": [["Series filtradas", "center"], title_right],
                "label": data_label[m:n],
                "xarray": times_days,
                "xlim": xlim,
                "ylabel": ylabel,
            },
        ]

    plot_timeseries(timeseries, settings.to_dict(), params, "series")


def visualizar_ciclos_dominantes(
    diurnal_cycle: Any,
    mean_diurnal_cycle: Any,
    dominant_cycle: Any,
    mean_dominant_cycle: Any,
    analysers_: Any,
    average_analysers_: Any,
    bt_detrended_timeseries: Any,
    bt_filtered_timeseries: Any,
    bt_mean_timeseries: Any,
    bt_filtered_mean_timeseries: Any,
    settings: ConfigDict,
) -> None:
    from goesdl.experimental.fourier import FourierAnalysis
    from goesdl.experimental.plotting import plot_timeseries
    from goesdl.experimental.sequence import Sequencer
    from goesdl.experimental.utilities import (
        combine_tick_labels,
        get_date_markers,
        get_time_ticks,
    )

    analysers: list[FourierAnalysis] = analysers_
    average_analysers: dict[str, FourierAnalysis] = average_analysers_

    sampling_rate = settings.as_int("subsampling.sampling_rate") // 24
    series_length = settings.as_int("parameters.series_length")
    timedelta_h = settings.as_int("algorithm.delta_t")

    sequencer = Sequencer(sampling_rate)

    times_days = sequencer.build_times(series_length) / 24

    algorithm_id = settings.as_str("algorithm_id")

    if algorithm_id == "algorithm_0":
        radii_km = settings.get_astype("parameters.radii_km", list[float])
        title_inset = [f"r = {radius_km:.0f}-km" for radius_km in radii_km]
        ylabel = f"Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)  [K]"
    elif algorithm_id in {"algorithm_1", "algorithm_2"}:
        bt_scale = settings.as_int("algorithm.bt_scale", 1)
        bt_thresholds = settings.get_astype(
            "parameters.bt_thresholds", list[int]
        )
        if bt_scale > 1:
            title_inset = [
                f"µ = {bt_threshold/bt_scale:.1f} K"
                for bt_threshold in bt_thresholds
            ]
        else:
            title_inset = [
                f"µ = {bt_threshold:.0f} K" for bt_threshold in bt_thresholds
            ]
        ylabel = f"Max PH₀[Tbb(t) − Tbb(t+{timedelta_h:0.0f}h)]  [km]"
    else:
        title_inset = []
        ylabel = ""

    ext_analysers = analysers + [average_analysers["coherent_mean_timeseries"]]
    ext_detrended_timeseries = bt_detrended_timeseries + [
        bt_mean_timeseries["coherent_mean_timeseries"]
    ]
    ext_filtered_timeseries = bt_filtered_timeseries + [
        bt_filtered_mean_timeseries["coherent_mean_timeseries"]
    ]
    ext_dominant_cycle = dominant_cycle + [
        mean_dominant_cycle["coherent_mean_timeseries"]
    ]
    ext_diurnal_cycle = diurnal_cycle + [
        mean_diurnal_cycle["coherent_mean_timeseries"]
    ]

    amp_factor = 3

    dalpha = [
        (0 if npall(dcycle == 0) else 0.8) for dcycle in ext_diurnal_cycle
    ]
    talpha = [
        (0 if npall(dcycle == tcycle) else 1)
        for dcycle, tcycle in zip(ext_diurnal_cycle, ext_dominant_cycle)
    ]

    dlable = [
        (None if npall(dcycle == 0) else f"Ciclo diurno {amp_factor}×")
        for dcycle in ext_diurnal_cycle
    ]
    tlabel = [
        (None if npall(dcycle == tcycle) else f"Ciclo dominante {amp_factor}×")
        for dcycle, tcycle in zip(ext_diurnal_cycle, ext_dominant_cycle)
    ]

    config = settings.section("plotting.series")
    sav_suptitle = config["suptitle"]
    config["suptitle"] = None

    sav_height = config["height"]
    config["height"] = [4.5]

    title_inset.append("(promedio coherente)")

    tick_label: list[str]
    tick_position, tick_ilabel, time_hours = get_time_ticks(settings)
    mark_position, mark_label = get_date_markers(settings)
    tick_label = combine_tick_labels(
        tick_position, tick_ilabel, mark_position, mark_label
    )

    xmarkers = [
        {"x": pos, "color": "black", "linestyle": "--", "alpha": 0.7}
        for pos in mark_position
    ]

    for i, inset in enumerate(title_inset):
        dominant_frequency = 24 * ext_analysers[i].dominant_frequencies[0]
        dominant_period = 24 / dominant_frequency
        title_center = [f"Serie de tiempo {inset}", "center"]
        title_right = (
            f"(f ≈ {dominant_frequency:.2f} c/d, T ≈ {dominant_period:.2f} h/c)",
            "right",
        )
        timeseries: list[_Series] = [
            [
                ext_detrended_timeseries[i],
                ext_filtered_timeseries[i],
                amp_factor * ext_dominant_cycle[i],
                amp_factor * ext_diurnal_cycle[i],
            ],
        ]
        params = [
            {
                "title": [title_center, title_right],
                "label": [
                    "Serie original",
                    "Serie filtrada",
                    tlabel[i],
                    dlable[i],
                ],
                "xarray": 24 * times_days,
                "xlabel": "Fecha  [h]",
                "ylabel": ylabel,
                "suptitle": None,
                "alpha": [0.6, 0.6, talpha[i], dalpha[i]],
                "linestyle": ["-", "-.", ":", "--"],
                "xmarkers": xmarkers,
                "xticks": tick_position,
                "xticklabels": {
                    "labels": tick_label,
                    "rotation": 45,
                    "ha": "right",
                },
                "xlim": (0, time_hours),
            },
        ]

        plot_timeseries(timeseries, settings.to_dict(), params, "series")

    config["height"] = sav_height
    config["suptitle"] = sav_suptitle
