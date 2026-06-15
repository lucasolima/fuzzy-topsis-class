import copy
import json

import streamlit as st

from src.core.state import save_current_project_snapshot
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


def _validate_alternatives(draft: dict) -> list[str]:
    errors = []
    for alt_id, name in draft.items():
        if not str(name).strip():
            errors.append(f"Alternativa {alt_id} está sem descrição.")
    return errors

def render_alternatives():
    st.header("Cadastro das Demandas")

    
    st.markdown(
        "Informe ao sistema quais são as demandas que iremos "
        "classificar com o algoritmo Fuzzy TOPSIS."
    )

    st.subheader("Lista das Demandas")

    _init_alternatives_draft()
    project_id = st.session_state.get("current_project_id", "default")
    key_prefix = f"p{project_id}_"
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
                    key=f"{key_prefix}input_{alt_id}",
                    placeholder="Digite o nome da alternativa (Ex: Sistema X - Módulo Y)..."
                )
                
                # Se algo foi modificado, atualiza no core
                if new_val != alt_value:
                    st.session_state.alternatives_draft[alt_id] = new_val
            
            with col_del:
                # Botão com símbolo X de excluir
                if st.button("❌", key=f"{key_prefix}del_{alt_id}", help=f"Excluir {alt_id}"):
                    del st.session_state.alternatives_draft[alt_id]
                    st.rerun()

    st.markdown("---")
    
    # Botão com símbolo ➕ para adicionar novo input de alternativa
    if st.button("➕ Adicionar", key=f"{key_prefix}add_alternative_btn"):
        alt_id = f"ALT{st.session_state.next_alt_id_draft}"
        st.session_state.alternatives_draft[alt_id] = ""
        st.session_state.next_alt_id_draft += 1
        st.rerun()

    if st.button("💾 Salvar Alterações", key=f"{key_prefix}save_alternatives"):
        errors = _validate_alternatives(st.session_state.alternatives_draft)
        if errors:
            st.error("Há campos em branco. Corrija antes de salvar.")
            for msg in errors:
                st.caption(msg)
            return
        st.session_state.alternatives = copy.deepcopy(st.session_state.alternatives_draft)
        st.session_state.next_alt_id = st.session_state.next_alt_id_draft
        st.session_state.alternatives_classes_draft_signature = _draft_signature(
            {
                "alternatives": st.session_state.alternatives,
                "next_alt_id": st.session_state.next_alt_id,
            }
        )
        save_current_project_snapshot()
        st.success("Alterações salvas com sucesso!")
        st.rerun()

    render_classes()
