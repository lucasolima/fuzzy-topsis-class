import streamlit as st
from src.core.data_repository import system_data


# Helper function to display and clear messages from session state
def _display_and_clear_messages():
    if "messages" in st.session_state and st.session_state.messages:
        for msg_type, msg_text in st.session_state.messages:
            if msg_type == "success":
                st.success(msg_text)
            elif msg_type == "error":
                st.error(msg_text)
            elif msg_type == "warning":
                st.warning(msg_text)
            elif msg_type == "info":
                st.info(msg_text)
        st.session_state.messages = [] # Clear messages after displaying


def render_decision_matrix():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    _display_and_clear_messages()
    st.header("Matriz de Decisão")
    st.markdown(
        "Representação tabular da avaliação das demandas. Utilize para verificar se a avaliação foi realizada corretamente."
    )
    
    alternatives = system_data.get_alternatives()
    criteria = system_data.get_criteria()
    evaluations = system_data.get_evaluations()
    
    
    if not alternatives or not criteria:
        st.session_state.messages.append(("warning", "É necessário cadastrar alternatives e critérios primeiro."))
        return
        
    if not evaluations:
        st.session_state.messages.append(("info", "Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações."))
    else:
        description_term_by_criterion = {
            crit_id: {
                description_data.get("description"): description_data.get("alternative_term")
                for description_data in crit_data.get("descriptions", [])
                if description_data.get("description")
            }
            for crit_id, crit_data in criteria.items()
        }

        # Onde iremos armazenar os dados para plotar no Pandas e Streamlit
        matrix_data = []

        # Iterar sobre todas as alternatives preenchidas
        for alt_id, alt_name in alternatives.items():
            # Captura as respostas daquela alternativa, se houver
            answers_alt = evaluations.get(alt_id, {})
            
            # Vamos inicializar a linha do DataFrame com o ID e/ou nome da alternativa
            row = {"Alternativa": f"{alt_name}"}
            
            for crit_id, crit_data in criteria.items():
                crit_name = crit_data.get("criterion", crit_id)
                selected_desc = answers_alt.get(crit_id)
                
                find_term = description_term_by_criterion.get(crit_id, {}).get(selected_desc)
                
                # Se não encontrou o termo (ou o usuário não avaliou aquele critério ainda)
                if not find_term:
                    find_term = "-"
                    
                row[crit_name] = find_term
                
            matrix_data.append(row)
            
        st.table(matrix_data)

    st.markdown("---")
    st.header("Matriz dos Critérios")
    st.markdown(
        "Representação tabular da ponderação dos critérios. Utilize para verificar se a ponderação foi realizada corretamente."
    )
    
    saved_weights = system_data.get_criteria_weights()
    fuzzy_weights = system_data.get_fuzzy_number_weights()
    
    if not saved_weights:
        st.session_state.messages.append(("info", "Nenhum peso foi definido ainda. Vá para a aba de Pesos."))
        return
        
    weight_term_by_description = {
        w_data["description"]: term_key
        for term_key, w_data in fuzzy_weights.items()
        if w_data.get("description")
    }

    row_pesos = {}
    
    for crit_id, crit_data in criteria.items():
        crit_name = crit_data.get("criterion", crit_id)
        selected_desc = saved_weights.get(crit_id)
        
        weight_term = weight_term_by_description.get(selected_desc)
                    
        if not weight_term:
            weight_term = "-"
            
        row_pesos[crit_name] = weight_term

    st.table([row_pesos])
