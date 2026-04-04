import streamlit as st
from src.core.state import initialize_state
from src.core.data_repository import system_data
from src.ui.home import render_home
from src.ui.fuzzy_alternatives import render_fuzzy_alternatives

# 1. Configuração da página (deve ser o primeiro comando do app)
st.set_page_config(
    page_title="Fuzzy TOPSIS Class",
    page_icon="📊",
    layout="wide"  # Alterado para 'wide' para acomodar melhor a tabela de fuzzy
)

def main():
    st.title("Sistema Baseado em Fuzzy TOPSIS Class")

    # 2. Inicializa gerência de estado (regras e dados visuais)
    initialize_state()

    # Preenchimento Automático (Botão)
    with st.sidebar:
        st.header("Ferramentas")
        if st.button("Preencher Dados de Avaliação"):
            avaliacoes_iniciais = {
                "ALT1": ["A", "MB", "A", "MB", "M", "B"],
                "ALT2": ["M", "B", "B", "B", "M", "A"],
                "ALT3": ["M", "MB", "A", "MB", "B", "B"],
                "ALT4": ["M", "A", "M", "MB", "A", "M"],
                "ALT5": ["M", "MB", "A", "MB", "B", "B"],
                "ALT6": ["M", "B", "M", "MB", "B", "A"],
                "ALT7": ["M", "A", "A", "B", "B", "B"],
                "ALT8": ["A", "MB", "MA", "A", "A", "M"],
                "ALT9": ["M", "MA", "M", "A", "A", "A"]
            }
            pesos_iniciais = ["AI", "MAI", "IM", "BI", "BI", "MAI"]
            
            criterios = st.session_state.get("criterios", {})
            cri_keys = list(criterios.keys())
            
            # Preencher avaliacoes
            if "avaliacoes" not in st.session_state:
                st.session_state.avaliacoes = {}
                
            for alt_id, valores in avaliacoes_iniciais.items():
                if alt_id not in st.session_state.avaliacoes:
                    st.session_state.avaliacoes[alt_id] = {}
                for i, val in enumerate(valores):
                    if i < len(cri_keys):
                        cri_id = cri_keys[i]
                        for d in criterios[cri_id].get("descricoes", []):
                            if d.get("termo_alternativa") == val:
                                st.session_state.avaliacoes[alt_id][cri_id] = d["descricao"]
                                break
                                
            # Preencher pesos
            if "pesos_criterios" not in st.session_state:
                st.session_state.pesos_criterios = {}
                
            pesos_fuzzy = st.session_state.get("numero_fuzzy_pesos", {})
            for i, p in enumerate(pesos_iniciais):
                if i < len(cri_keys):
                    cri_id = cri_keys[i]
                    if p in pesos_fuzzy:
                        st.session_state.pesos_criterios[cri_id] = pesos_fuzzy[p]["descricao"]
                        
            st.success("Dados preenchidos com sucesso!")
            st.rerun()

    # 2.1 Sincroniza estado da interface com a camada de regras de negócio estática
    system_data.update_from_state(st.session_state)

    # 3. Navegação por Abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Alternativas e Classes", 
        "Números Fuzzy", 
        "Critérios", 
        "Avaliações", 
        "Pesos",
        "Matriz de Decisão",
        "Matriz Ponderada"
    ])

    with tab1:
        render_home()
        
    with tab2:
        render_fuzzy_alternatives()

    with tab3:
        from src.ui.criterios_config import render_criterios
        render_criterios()

    with tab4:
        from src.ui.avaliacoes import render_avaliacoes
        render_avaliacoes()

    with tab5:
        from src.ui.pesos_criterios import render_pesos_criterios
        render_pesos_criterios()

    with tab6:
        from src.ui.matriz_decisao import render_matriz_decisao
        render_matriz_decisao()

    with tab7:
        from src.ui.matriz_ponderada import render_matriz_ponderada
        render_matriz_ponderada()

if __name__ == "__main__":
    main()
