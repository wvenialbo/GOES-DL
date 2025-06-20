import numpy as np

from ..utils.array import ArrayFloat, ArrayIndex, ToIndex


def interpretar_p_valores(
    frecuencias: ArrayFloat,
    p_valores: ArrayFloat,
    indices_picos_reales: ArrayIndex | None = None,
) -> None:
    """
    Genera interpretación automática de la curva de p-valores.

    Se enfoca en los picos dominantes señalados por 'indices' para las estadísticas de conteo
    y listado de picos significativos, mientras que las estadísticas generales (min, median)
    y las proporciones se basan en todo el espectro de p-valores.

    Args:
        frecuencias (np.array): Array de frecuencias de todo el espectro.
        p_valores (np.array): Array de p-valores correspondientes a todas las frecuencias.
        indices (np.array, list, optional): Índices de las "cimas de los picos"
                                            que se desean analizar para los conteos
                                            y listados específicos.
                                            Si es None (por defecto), se considerarán
                                            todos los índices del array de frecuencias
                                            como 'picos' para este propósito.
        umbral (float, optional): Umbral de significancia para los p-valores.
                                  Por defecto es 0.05.
    """
    print("\n" + "=" * 60)
    print("INTERPRETACIÓN AUTOMÁTICA DE P-VALORES ESPECTRALES")
    print("=" * 60)

    # --- 1. Manejo del parámetro opcional 'indices_picos_reales' y creación de subconjuntos ---
    # Si 'indices' no se proporciona, usa todos los índices del array de frecuencias.
    if indices_picos_reales is None:
        indices_a_analizar: ArrayIndex = np.arange(len(frecuencias))
        print(
            "\nℹ️  'indices_picos_reales' no fue proporcionado. Analizando el espectro completo."
        )
    else:
        # Asegurarse de que 'indices_picos_reales' sea un array de numpy para indexación
        # avanzada eficiente. Esto es útil si el usuario pasa una lista normal.
        indices_a_analizar = np.asarray(indices_picos_reales)
        if len(indices_a_analizar) == 0:
            print(
                "⚠️  Advertencia: 'indices_picos_reales' fue proporcionado pero está vacío. No se contarán picos específicos."
            )
            indices_a_analizar = np.arange(len(frecuencias))
        else:
            print(
                f"\nℹ️  Preselección: Analizando {len(indices_a_analizar)} frecuencias específicas"
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
    if n_total == 0:
        print("   • No hay datos para realizar una evaluación estadística.")
    elif prop_05 > esperado_05 * 2:
        print(
            f"   ⚠️  SEÑALES DETECTADAS: {prop_05:.1%} vs {esperado_05:.1%} esperado"
        )
        print("       → Evidencia fuerte de componentes no-aleatorias")
    elif prop_05 > esperado_05 * 1.5:
        print(
            f"   ⚡ POSIBLES SEÑALES: {prop_05:.1%} vs {esperado_05:.1%} esperado"
        )
        print("       → Evidencia moderada de componentes no-aleatorias")
    elif prop_05 < esperado_05 * 0.5:
        print(
            f"   💤 ESPECTRO MUY SILENCIOSO: {prop_05:.1%} vs {esperado_05:.1%} esperado"
        )
        print(
            "       → Posible preselección, sobre-filtrado o señal muy débil"
        )
    else:
        print(
            f"   ✅ COMPORTAMIENTO NORMAL: {prop_05:.1%} vs {esperado_05:.1%} esperado"
        )
        print("       → Consistente con ruido de fondo")

    umbral = 0.05

    print(f"\n🔍 RESUMEN EJECUTIVO (> percentil {umbral:.1%}):")
    if n_total == 0:
        print("No se puede generar un resumen ejecutivo sin datos.")
    elif prop_05 > 0.1:
        print(
            f"   🔴 ALTA ACTIVIDAD: {prop_05:.1%} del espectro es significativo"
        )
    elif prop_05 > 0.075:
        print(
            f"   🟡 ACTIVIDAD MODERADA: {prop_05:.1%} del espectro es significativo"
        )
    elif prop_05 > 0.025:
        print(
            f"   🟢 ACTIVIDAD NORMAL: {prop_05:.1%} del espectro es significativo"
        )
    else:
        print(
            f"   🔵 BAJA ACTIVIDAD: {prop_05:.1%} del espectro es significativo)"
        )

    # --- 4. Identificar picos más significativos---
    descripciones = {
        0.001: "EXTREMADAMENTE SIGNIFICATIVAS",
        0.01: "MUY SIGNIFICATIVAS",
        0.05: "SIGNIFICATIVAS",
    }
    icons = {
        0.001: "🌟",  # Una estrella dorada para lo más significativo, indicando la "excelencia" o lo "más brillante", como CH.
        0.01: "🚀",  # Un cohete para "muy significativo", sugiriendo un despegue o un impacto fuerte. "Va a salir como un cohete esto, creo..."
        0.05: "🔔",  # Una campana para "significativo", como una "alerta" de algo notable
    }

    indices_ya_reportados: set[ToIndex] = set()
    n_count = 5

    if n_total > 0:
        umbral_niveles = [0.001, 0.01, 0.05]
        for umbral_actual in umbral_niveles:
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
            descripcion = descripciones[umbral_actual]
            icon = icons[umbral_actual]

            # Obtenemos los índices originales de los elementos no reportados
            indices_originales_no_reportados = np.nonzero(
                mascara_no_reportados
            )[0]

            if n_extremos > 0 and n_count > 0:
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
                    n_count = n_count - 1
                    n_extremos = n_extremos - 1
                if n_extremos > n_count:
                    print(f"       ... y {n_extremos-n_count} más")
        print(
            "\n⚠️  Advertencia: Las frecuencias estadísticamente "
            "significativas pueden diferir ligeramente de las "
            "físicamente significativas."
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
