import copy
import json

import streamlit as st

from src.ui.classes_config import render_classes


def _draft_signature(values: dict) -> str:
    return json.dumps(values, sort_keys=True, ensure_ascii=False)


def _init_alternatives_draft():
    base_snapshot = {
        "alternatives": st.session_state.get("alternatives", {}),
        "next_alt_id": st.session_state.get("next_alt_id", 1),
    }
    signature = _draft_signature(base_snapshot)

    if (
        "alternatives_classes_draft_signature" not in st.session_state
        or st.session_state.alternatives_classes_draft_signature != signature
    ):
        st.session_state.alternatives_draft = copy.deepcopy(base_snapshot["alternatives"])
        st.session_state.next_alt_id_draft = base_snapshot["next_alt_id"]
        st.session_state.alternatives_classes_draft_signature = signature

def render_alternatives():
    st.header("Parametrização das Alternativas")

    
    st.markdown(
        "Informe ao sistema quais são as alternatives que iremos "
        "classificar com o algoritmo Fuzzy TOPSIS."
    )

    st.subheader("Lista de Alternativas")

    _init_alternatives_draft()
    current_alternatives = list(st.session_state.alternatives_draft.items())
    
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
                    st.session_state.alternatives_draft[alt_id] = new_val
            
            with col_del:
                # Botão com símbolo X de excluir
                if st.button("❌", key=f"del_{alt_id}", help=f"Excluir {alt_id}"):
                    del st.session_state.alternatives_draft[alt_id]
                    st.rerun()

    st.markdown("---")
    
    # Botão com símbolo ➕ para adicionar novo input de alternativa
    if st.button("➕ Adicionar", key="add_alternative_btn"):
        alt_id = f"ALT{st.session_state.next_alt_id_draft}"
        st.session_state.alternatives_draft[alt_id] = ""
        st.session_state.next_alt_id_draft += 1
        st.rerun()

    if st.button("💾 Salvar Alterações", key="save_alternatives"):
        st.session_state.alternatives = copy.deepcopy(st.session_state.alternatives_draft)
        st.session_state.next_alt_id = st.session_state.next_alt_id_draft
        st.session_state.alternatives_classes_draft_signature = _draft_signature(
            {
                "alternatives": st.session_state.alternatives,
                "next_alt_id": st.session_state.next_alt_id,
            }
        )
        st.success("Alterações salvas com sucesso!")
        st.rerun()

    render_classes()


