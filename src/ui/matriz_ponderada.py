import streamlit as st
import pandas as pd
from src.core.data_repository import system_data
from src.services.ftopsis_service import FTopsisService

def render_matriz_ponderada():
    st.header("Resultado da Classificação")
    st.markdown(
        "A tabela abaixo determina a qual classe/perfil cada alternativa melhor se adequa, "
        "com base no maior nível de proximidade (CCi). O **maior CCi indica a classe ideal**."
    )

    alternativas = system_data.get_alternativas()
    criterios = system_data.get_criterios()
    avaliacoes = system_data.get_avaliacoes()
    fuzzy_alternativas = system_data.get_numero_fuzzy_alternativas()
    pesos_criterios = system_data.get_pesos_criterios()
    fuzzy_pesos = system_data.get_numero_fuzzy_pesos()
    classes = system_data.get_classes()

    if not alternativas or not criterios:
        st.warning("É necessário cadastrar alternativas e critérios primeiro.")
        return

    if not avaliacoes:
        st.info("Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações.")
        return
        
    if not pesos_criterios:
        st.info("Nenhum peso definido ainda. Vá para a aba de Pesos.")
        return

    # Injeta a dependência no serviço
    servico_ftopsis = FTopsisService(
        criterios=criterios,
        alternativas=alternativas,
        avaliacoes=avaliacoes,
        fuzzy_alternativas=fuzzy_alternativas,
        pesos_criterios=pesos_criterios,
        fuzzy_pesos=fuzzy_pesos,
        classes=classes
    )

    # Passo 1: Matrizes Brutas Fuzzy
    matriz_bruta = servico_ftopsis.build_decision_matrix()
    matriz_bruta_classes = servico_ftopsis.build_classes_matrix()
    
    # Valores ideais globais
    ideal_values = servico_ftopsis.get_global_ideal_values(matriz_bruta, matriz_bruta_classes)
    
    # Passo 2: Normalizar Matrizes (Alternativas e Classes)
    matriz_normalizada, _ = servico_ftopsis.normalize_matrix(matriz_bruta, ideal_values)
    matriz_normalizada_classes, _ = servico_ftopsis.normalize_matrix(matriz_bruta_classes, ideal_values)
    
    # Passo 3: Ponderar a Matriz Normalizada
    matriz_ponderada = servico_ftopsis.weight_matrix(matriz_normalizada)
    matriz_ponderada_classes = servico_ftopsis.weight_matrix(matriz_normalizada_classes)

    agrupamentos = servico_ftopsis.calculate_ideal_solution_from_classes(matriz_ponderada_classes)
    distancias_ideais = servico_ftopsis.calculate_distances_ideais(matriz_ponderada, agrupamentos)
    
    if distancias_ideais:
        cci_ideais = servico_ftopsis.calculate_cci_ideais(distancias_ideais)
        cci_rows = []
        for alt_id, info_cci in cci_ideais.items():
            alt_nome = alternativas.get(alt_id, alt_id)
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
        st.markdown("Lista das alternativas avaliadas, ordenadas por sua pontuação (Maior CCi) e classe recomendada.")

        # Dicionário de peso para ordenação das classes
        # Ex: "Alta Prioridade" -> 0, "Média Prioridade" -> 1, "Baixa Prioridade" -> 2
        classes_order = {c["descricao"]: i for i, c in enumerate(classes.values())}

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
