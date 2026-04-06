import streamlit as st
import pandas as pd
from src.core.data_repository import system_data
from src.services.ftopsis_service import FTopsisService

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
    servico_ftopsis = FTopsisService(
        criteria=criteria,
        alternatives=alternatives,
        evaluations=evaluations,
        fuzzy_alternatives=fuzzy_alternatives,
        criteria_weights=criteria_weights,
        fuzzy_weights=fuzzy_weights,
        classes=classes
    )

    # Passo 1: Matrizes Brutas Fuzzy
    raw_matrix = servico_ftopsis.build_decision_matrix()
    raw_matrix_classes = servico_ftopsis.build_classes_matrix()
    
    # Valores ideais globais
    ideal_values = servico_ftopsis.get_global_ideal_values(raw_matrix, raw_matrix_classes)
    
    # Passo 2: Normalizar Matrizes (Alternativas e Classes)
    normalized_matrix, _ = servico_ftopsis.normalize_matrix(raw_matrix, ideal_values)
    normalized_matrix_classes, _ = servico_ftopsis.normalize_matrix(raw_matrix_classes, ideal_values)
    
    # Passo 3: Ponderar a Matriz Normalizada
    weighted_matrix = servico_ftopsis.weight_matrix(normalized_matrix)
    weighted_matrix_classes = servico_ftopsis.weight_matrix(normalized_matrix_classes)

    agrupamentos = servico_ftopsis.calculate_ideal_solution_from_classes(weighted_matrix_classes)
    distancias_ideais = servico_ftopsis.calculate_distances_ideais(weighted_matrix, agrupamentos)
    
    if distancias_ideais:
        cci_ideais = servico_ftopsis.calculate_cci_ideais(distancias_ideais)
        cci_rows = []
        for alt_id, info_cci in cci_ideais.items():
            alt_nome = alternatives.get(alt_id, alt_id)
            row = {"Alternativa": alt_nome}
            
            # Identificar a classe com maior CCi
            melhor_classe = None
            maior_cci = -1.0
            
            for label_combinacao, cci_val in info_cci.items():
                row[label_combinacao] = cci_val
                if cci_val > maior_cci:
                    maior_cci = cci_val
                    melhor_classe = label_combinacao
                    
            row["⭐ Classe Recomendada"] = melhor_classe
            cci_rows.append(row)
            
        df_cci = pd.DataFrame(cci_rows)
        
        # Estilizar o DataFrame: destacar o maior valor nas colunas numéricas de CCi
        numeric_cols = [col for col in df_cci.columns if col not in ["Alternativa", "⭐ Classe Recomendada"]]
        
        def highlight_max(row):
            is_max = row == row.max()
            return ['background-color: #2e7b32; color: white; font-weight: bold;' if v else '' for v in is_max]
            
        styled_df = df_cci.style.apply(highlight_max, subset=numeric_cols, axis=1)
        styled_df = styled_df.format({col: "{:.3f}" for col in numeric_cols})
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.header("Ranking")
        st.markdown("Lista das alternatives avaliadas, ordenadas por sua pontuação (Maior CCi) e classe recomendada.")

        # Dicionário de peso para ordenação das classes
        # Ex: "Alta Prioridade" -> 0, "Média Prioridade" -> 1, "Baixa Prioridade" -> 2
        classes_order = {c["description"]: i for i, c in enumerate(classes.values())}

        ranking_data = []
        for index, row in df_cci.iterrows():
            maior_cci = max([row[col] for col in numeric_cols])
            classe_rec = row["⭐ Classe Recomendada"]
            ranking_data.append({
                "Alternativa": row["Alternativa"],
                "Pontuação": maior_cci,
                "Classe": classe_rec,
                "ordem_classe": classes_order.get(classe_rec, 99)
            })

        df_ranking = pd.DataFrame(ranking_data)
        # Ordena primariamente pela classe recomendada e secundariamente pela pontuação
        df_ranking.sort_values(by=["ordem_classe", "Pontuação"], ascending=[True, False], inplace=True)
        df_ranking.drop(columns=["ordem_classe"], inplace=True)

        st.dataframe(
            df_ranking.style.format({"Pontuação": "{:.3f}"}), 
            use_container_width=True, 
            hide_index=True
        )
