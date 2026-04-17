import streamlit as st
from src.core.state import initialize_state
from src.core.data_repository import system_data
from src.ui.alternatives import render_alternatives
from src.ui.fuzzy_alternatives import render_fuzzy_alternatives

# 1. Configuração da página (deve ser o primeiro comando do app)
st.set_page_config(
    page_title="FTOPSIS Class",
    page_icon="📊",
    layout="wide"  # Alterado para 'wide' para acomodar melhor a tabela de fuzzy
)

def main():
    st.title("FTOPSIS Class - Customizações de SIGS")

    # 2. Inicializa gerência de estado (regras e dados visuais)
    initialize_state()

    # Menu Lateral
    with st.sidebar:    
        st.header("Menu Principal")
        
        secao = st.selectbox("Selecione a Seção:", ["Parametrização do Modelo", "Avaliação das Alternativas", "Classificação Final"])
        
        if secao == "Parametrização do Modelo":
            selected_menu = st.radio(
                "Opções de Parametrização:",
                ["Alternativas e Classes", "Números Fuzzy", "Critérios"]
            )
        elif secao == "Avaliação das Alternativas":
            selected_menu = st.radio(
                "Opções de Avaliação:",
                ["Alternativas", "Pesos"]
            )
        else:
            selected_menu = st.radio(
                "Opções de Classificação:",
                ["Matriz de Decisão", "Classificação Final"]
            )
        
        st.markdown("---")
        
        st.header("Ferramentas")
        if st.button("Preencher Dados Amostrais"):
            initial_evaluations = {
                "ALT1":  ["M", "MB", "A", "M", "M", "MB"],
                "ALT2":  ["A", "M", "MB", "B", "B", "MB"],
                "ALT3":  ["A", "MB", "M", "M", "B", "M"],
                "ALT4":  ["MA", "MA", "MA", "M", "M", "B"],
                "ALT5":  ["MA", "B", "A", "M", "M", "MB"],
                "ALT6":  ["A", "M", "M", "B", "M", "B"],
                "ALT7":  ["M", "B", "M", "M", "A", "A"],
                "ALT8":  ["A", "B", "B", "M", "M", "M"],
                "ALT9":  ["MA", "MB", "MA", "M", "M", "M"],
                "ALT10": ["M", "MB", "A", "M", "B", "MB"],
                "ALT11": ["M", "M", "M", "B", "M", "M"],
                "ALT12": ["M", "MB", "A", "A", "MA", "MA"]
            }
            initial_weights = ["AI", "IM", "MAI", "BI", "IM", "MAI"]
            
            criteria = st.session_state.get("criteria", {})
            cri_keys = list(criteria.keys())
            
            # Preencher evaluations
            if "evaluations" not in st.session_state:
                st.session_state.evaluations = {}
                
            for alt_id, values in initial_evaluations.items():
                if alt_id not in st.session_state.evaluations:
                    st.session_state.evaluations[alt_id] = {}
                for i, val in enumerate(values):
                    if i < len(cri_keys):
                        crit_id = cri_keys[i]
                        for d in criteria[crit_id].get("descriptions", []):
                            if d.get("alternative_term") == val:
                                st.session_state.evaluations[alt_id][crit_id] = d["description"]
                                break
                                
            # Preencher pesos
            if "criteria_weights" not in st.session_state:
                st.session_state.criteria_weights = {}
                
            fuzzy_weights = st.session_state.get("fuzzy_number_weights", {})
            for i, p in enumerate(initial_weights):
                if i < len(cri_keys):
                    crit_id = cri_keys[i]
                    if p in fuzzy_weights:
                        st.session_state.criteria_weights[crit_id] = fuzzy_weights[p]["description"]
                        
            st.success("Dados preenchidos com sucesso!")
            st.rerun()

    # 2.1 Sincroniza estado da interface com a camada de regras de negócio estática
    system_data.update_from_state(st.session_state)

    # 3. Renderização Condicional da Navegação
    if selected_menu == "Alternativas e Classes":
        render_alternatives()
        
    elif selected_menu == "Números Fuzzy":
        render_fuzzy_alternatives()
        
    elif selected_menu == "Critérios":
        from src.ui.criteria_config import render_criteria
        render_criteria()
        
    elif selected_menu == "Alternativas":
        from src.ui.evaluations import render_evaluations
        render_evaluations()
        
    elif selected_menu == "Pesos":
        from src.ui.criteria_weights import render_criteria_weights
        render_criteria_weights()
        
    elif selected_menu == "Matriz de Decisão":
        from src.ui.decision_matrix import render_decision_matrix
        render_decision_matrix()
        
    elif selected_menu == "Classificação Final":
        from src.ui.weighted_matrix import render_weighted_matrix
        render_weighted_matrix()

if __name__ == "__main__":
    main()
