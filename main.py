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
