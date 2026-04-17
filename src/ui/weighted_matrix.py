import streamlit as st
import html
from src.core.data_repository import system_data
from src.services.ftopsis_service import FTopsisService


def _render_html_table(headers, rows):
    header_html = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    body_html = ""
    for row in rows:
        cells = []
        for cell in row:
            value = cell.get("value", "")
            style = cell.get("style", "")
            cells.append(f'<td style="{style}">{html.escape(str(value))}</td>')
        body_html += f"<tr>{''.join(cells)}</tr>"

    table_html = f"""
    <style>
        .ftopsis-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .ftopsis-table th, .ftopsis-table td {{
            border: 1px solid #ddd;
            padding: 0.5rem;
            text-align: left;
        }}
        .ftopsis-table th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
    </style>
    <table class="ftopsis-table">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{body_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

def render_weighted_matrix():
    st.header("Resultado da Classificação")
    st.markdown(
        "A tabela abaixo determina a qual classe/perfil cada alternativa melhor se adequa, "
        "com base no maior nível de proximidade (CCi). O **maior CCi indica a classe ideal**."
    )

    alternatives = system_data.get_alternatives()
    criteria = system_data.get_criteria()
    evaluations = system_data.get_evaluations()
    fuzzy_alternatives = system_data.get_fuzzy_number_alternatives()
    criteria_weights = system_data.get_criteria_weights()
    fuzzy_weights = system_data.get_fuzzy_number_weights()
    classes = system_data.get_classes()

    if not alternatives or not criteria:
        st.warning("É necessário cadastrar alternatives e critérios primeiro.")
        return

    if not evaluations:
        st.info("Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações.")
        return
        
    if not criteria_weights:
        st.info("Nenhum peso definido ainda. Vá para a aba de Pesos.")
        return

    # Injeta a dependência no serviço
    ftopsis_service = FTopsisService(
        criteria=criteria,
        alternatives=alternatives,
        evaluations=evaluations,
        fuzzy_alternatives=fuzzy_alternatives,
        criteria_weights=criteria_weights,
        fuzzy_weights=fuzzy_weights,
        classes=classes
    )

    # Passo 1: Matrizes Brutas Fuzzy
    raw_matrix = ftopsis_service.build_decision_matrix()
    raw_matrix_classes = ftopsis_service.build_classes_matrix()
    
    # Valores ideais globais
    ideal_values = ftopsis_service.get_global_ideal_values(raw_matrix, raw_matrix_classes)
    
    # Passo 2: Normalizar Matrizes (Alternativas e Classes)
    normalized_matrix, _ = ftopsis_service.normalize_matrix(raw_matrix, ideal_values)
    normalized_matrix_classes, _ = ftopsis_service.normalize_matrix(raw_matrix_classes, ideal_values)
    
    # Passo 3: Ponderar a Matriz Normalizada
    weighted_matrix = ftopsis_service.weight_matrix(normalized_matrix)
    weighted_matrix_classes = ftopsis_service.weight_matrix(normalized_matrix_classes)

    agrupamentos = ftopsis_service.calculate_ideal_solution_from_classes(weighted_matrix_classes)
    ideals_distances = ftopsis_service.calculate_distances_ideais(weighted_matrix, agrupamentos)
    
    if ideals_distances:
        ideals_cci = ftopsis_service.calculate_cci_ideais(ideals_distances)
        cci_rows = []
        label_order = list(next(iter(ideals_cci.values())).keys()) if ideals_cci else []
        for alt_id, info_cci in ideals_cci.items():
            alt_nome = alternatives.get(alt_id, alt_id)
            row = {"Alternativa": alt_nome}

            best_class = None
            greater_cci = -1.0

            for label_combinacao in label_order:
                cci_val = info_cci.get(label_combinacao, 0.0)
                row[label_combinacao] = cci_val
                if cci_val > greater_cci:
                    greater_cci = cci_val
                    best_class = label_combinacao

            row["⭐ Classe Recomendada"] = best_class
            cci_rows.append(row)

        headers = ["Alternativa"] + label_order + ["⭐ Classe Recomendada"]
        table_rows = []
        for row in cci_rows:
            max_cci = max((row[label] for label in label_order), default=0.0)
            formatted_row = []
            formatted_row.append({"value": row["Alternativa"]})
            for label in label_order:
                value = row[label]
                is_max = value == max_cci
                style = "background-color: #2e7b32; color: white; font-weight: bold;" if is_max else ""
                formatted_row.append({"value": f"{value:.3f}", "style": style})
            formatted_row.append({"value": row["⭐ Classe Recomendada"]})
            table_rows.append(formatted_row)

        _render_html_table(headers, table_rows)

        st.markdown("---")
        st.header("Ranking")
        st.markdown("Lista das alternatives avaliadas, ordenadas por sua pontuação (Maior CCi) e classe recomendada.")

        # Dicionário de peso para ordenação das classes
        # Ex: "Alta Prioridade" -> 0, "Média Prioridade" -> 1, "Baixa Prioridade" -> 2
        classes_order = {c["description"]: i for i, c in enumerate(classes.values())}

        ranking_data = []
        for index, row in df_cci.iterrows():
            greater_cci = max([row[col] for col in numeric_cols])
            classe_rec = row["⭐ Classe Recomendada"]
            ranking_data.append({
                "Alternativa": row["Alternativa"],
                "Pontuação": greater_cci,
                "Classe": classe_rec,
                "ordem_classe": classes_order.get(classe_rec, 99)
            })

        ranking_data.sort(key=lambda item: (item["ordem_classe"], -item["Pontuação"]))

        st.table([
            {
                "Alternativa": item["Alternativa"],
                "Pontuação": f'{item["Pontuação"]:.3f}',
                "Classe": item["Classe"]
            }
            for item in ranking_data
        ])
