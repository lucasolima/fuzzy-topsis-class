import streamlit as st
from src.core.state import add_alternative, update_alternative, delete_alternative

def render_home():
    st.header("Parametrização das Alternativas")
    
    st.markdown(
        "Informe ao sistema quais são as alternatives que iremos "
        "classificar com o algoritmo Fuzzy TOPSIS."
    )

    st.subheader("Lista de Alternativas")

    # Pegamos o layout da lista atual guardada no state
    current_alternatives = list(st.session_state.alternatives.items())
    
    if not current_alternatives:
        st.info("Nenhuma alternativa cadastrada. Clique no botão abaixo para adicionar.")
    else:
        for alt_id, alt_value in current_alternatives:
            col_input, col_del = st.columns([10, 1])
            
            with col_input:
                # O próprio st.text_input permite editar ao clicar nele, 
                # atualizando o valor interno automaticamente quando pressionar enter (ou perder o foco).
                # O label foi ocultado para ficar apenas a "caixa do input" em foco visual, conforme solicitado.
                new_val = st.text_input(
                    label=f"Alternativa {alt_id}",
                    value=alt_value,
                    label_visibility="collapsed",
                    key=f"input_{alt_id}",
                    placeholder="Digite o nome da alternativa (Ex: Sistema X - Módulo Y)..."
                )
                
                # Se algo foi modificado, atualiza no core
                if new_val != alt_value:
                    update_alternative(alt_id, new_val)
            
            with col_del:
                # Botão com símbolo X de excluir
                if st.button("❌", key=f"del_{alt_id}", help=f"Excluir {alt_id}"):
                    delete_alternative(alt_id)
                    st.rerun()

    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Botão com símbolo ➕ para adicionar novo input de alternativa
        if st.button("➕ Adicionar", type="primary", use_container_width=True):
            add_alternative()
            st.rerun()

    from src.ui.classes_config import render_classes
    render_classes()


