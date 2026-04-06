import streamlit as st
import pandas as pd
from src.core.data_repository import system_data

def render_decision_matrix():
    st.header("Matriz de Decisão")
    st.markdown(
        "Esta tabela apresenta os **Termos Linguísticos (Alternativas)** atrelados às "
        "avaliações (descrições) que foram selecionadas na aba anterior."
    )
    
    alternatives = system_data.get_alternatives()
    criteria = system_data.get_criteria()
    evaluations = system_data.get_evaluations()
    
    if not alternatives or not criteria:
        st.warning("É necessário cadastrar alternatives e critérios primeiro.")
        return
        
    if not evaluations:
        st.info("Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações.")
    else:
        # Onde iremos armazenar os dados para plotar no Pandas e Streamlit
        matrix_data = []

        # Iterar sobre todas as alternatives preenchidas
        for alt_id, alt_nome in alternatives.items():
            # Captura as respostas daquela alternativa, se houver
            answers_alt = evaluations.get(alt_id, {})
            
            # Vamos inicializar a linha do DataFrame com o ID e/ou nome da alternativa
            row = {"Alternativa": f"{alt_nome}"}
            
            for crit_id, crit_data in criteria.items():
                crit_name = crit_data.get("criterion", crit_id)
                selected_desc = answers_alt.get(crit_id)
                
                # Buscar no critério qual é o alternative_term vinculado a esta descrição
                find_term = None
                if selected_desc:
                    # Procura a descrição dentro das descrições do critério
                    for d in crit_data.get("descriptions", []):
                        if d["description"] == selected_desc:
                            find_term = d.get("alternative_term")
                            break
                
                # Se não encontrou o termo (ou o usuário não avaliou aquele critério ainda)
                if not find_term:
                    find_term = "-"
                    
                row[crit_name] = find_term
                
            matrix_data.append(row)
            
        df_matrix = pd.DataFrame(matrix_data)
        
        # Exibir a tabela
        st.dataframe(
            df_matrix,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.header("Matriz dos Critérios")
    st.markdown(
        "Esta tabela apresenta os **Termos Linguísticos (Pesos)** atrelados aos "
        "níveis de importância que foram selecionados na aba de Pesos."
    )
    
    saved_weights = system_data.get_criteria_weights()
    fuzzy_weights = system_data.get_fuzzy_number_weights()
    
    if not saved_weights:
        st.info("Nenhum peso foi definido ainda. Vá para a aba de Pesos.")
        return
        
    row_pesos = {}
    
    for crit_id, crit_data in criteria.items():
        crit_name = crit_data.get("criterion", crit_id)
        selected_desc = saved_weights.get(crit_id)
        
        weight_term = None
        if selected_desc:
            # Encontrar no dicionario de pesos fuzzy qual é a chave (termo) dessa descrição
            for termo_key, w_data in fuzzy_weights.items():
                if w_data["description"] == selected_desc:
                    weight_term = termo_key
                    break
                    
        if not weight_term:
            weight_term = "-"
            
        row_pesos[crit_name] = weight_term

    df_pesos = pd.DataFrame([row_pesos])
    
    st.dataframe(
        df_pesos,
        use_container_width=True,
        hide_index=True
    )
