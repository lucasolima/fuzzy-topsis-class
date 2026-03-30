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
    tab1, tab2, tab3 = st.tabs(["Alternativas e Classes", "Números Fuzzy (Critérios)", "Critérios"])

    with tab1:
        render_home()
        
    with tab2:
        render_fuzzy_alternatives()

    with tab3:
        from src.ui.criterios_config import render_criterios
        render_criterios()

    # Botão de debug no final da navegação global (barra lateral ou rodapé)
    st.markdown("---")
    if st.button("🖨️ Printar Dados no Console (Debug)", use_container_width=True):
        print("\n" + "="*50)
        print("ESTRUTURAS DE DADOS ATUAIS CAPTURADAS NO BACKEND")
        print("="*50)
        
        print("\n[ ALTERNATIVAS ]")
        print(system_data.get_alternativas())
        
        print("\n[ NÚMEROS FUZZY (ALTERNATIVAS) ]")
        print(system_data.get_numero_fuzzy_alternativas())
        
        print("\n[ NÚMEROS FUZZY (PESOS) ]")
        print(system_data.get_numero_fuzzy_pesos())
        
        print("\n[ CLASSES ]")
        print(system_data.get_classes())
        
        print("\n[ CRITÉRIOS ]")
        import json
        print(json.dumps(system_data.get_criterios(), indent=2, ensure_ascii=False))
        
        print("="*50 + "\n")
        st.success("Dados printados no console do terminal!")

if __name__ == "__main__":
    main()
