import copy
import json

import streamlit as st

from src.core.state import save_current_project_snapshot


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


def _draft_signature(values: dict) -> str:
    return json.dumps(values, sort_keys=True, ensure_ascii=False)


def _init_classes_draft():
    base_snapshot = {
        "classes": st.session_state.get("classes", {}),
        "next_class_id": st.session_state.get("next_class_id", 1),
    }
    signature = _draft_signature(base_snapshot)

    if (
        "classes_draft_signature" not in st.session_state
        or st.session_state.classes_draft_signature != signature
    ):
        st.session_state.classes_draft = copy.deepcopy(base_snapshot["classes"])
        st.session_state.next_class_id_draft = base_snapshot["next_class_id"]
        st.session_state.classes_draft_signature = signature


def _validate_classes(draft: dict) -> list[str]:
    errors = []
    if len(draft) != 3:
        errors.append("É necessário cadastrar exatamente 3 classes.")
    for class_id, data in draft.items():
        if not str(data.get("description", "")).strip():
            errors.append(f"Classe {class_id} está sem descrição.")
    return errors


def render_classes():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    _display_and_clear_messages()
    st.markdown("---")
    st.header("Parametrização das Classes / Perfis de Prioridade")
    
    st.markdown(
        "Cadastre as classes ou perfis de prioridade que serão utilizados "
        "para classificar as alternativas." 
    )

    _init_classes_draft()
    project_id = st.session_state.get("current_project_id", "default")
    key_prefix = f"p{project_id}_"
    class_keys = list(st.session_state.classes_draft.keys())
    #available_terms = list(st.session_state.fuzzy_number_alternatives.keys())
    
    if not class_keys:
        st.session_state.messages.append(("info", "Nenhuma classe cadastrada. Clique no botão abaixo para adicionar."))
    else:
        # Colunas sem o termo avaliado
        col_desc, col_del = st.columns([9, 1])
        with col_desc: st.subheader("Lista de Classes")
        
        for cid in class_keys:
            data = st.session_state.classes_draft[cid]
            
            col_desc, col_del = st.columns([9, 1])
            
            with col_desc:
                new_desc = st.text_input(
                    "Descrição Classe", 
                    value=data["description"], 
                    key=f"{key_prefix}class_desc_{cid}", 
                    label_visibility="collapsed",
                    placeholder="Ex: Alta Prioridade"
                )
                if new_desc != data["description"]:
                    st.session_state.classes_draft[cid]["description"] = new_desc

            with col_del:
                if st.button("❌", key=f"{key_prefix}class_del_{cid}", help=f"Excluir {cid}"):
                    del st.session_state.classes_draft[cid]
                    st.rerun()

    st.markdown("---")
    
    if st.button("➕ Adicionar", key=f"{key_prefix}add_class_btn", disabled=len(class_keys) >= 3):
        class_id = f"CLA{st.session_state.next_class_id_draft}"
        st.session_state.classes_draft[class_id] = {
            "description": "",
            "alternative_term": None,
        }
        st.session_state.next_class_id_draft += 1
        st.rerun()

    if st.button("💾 Salvar Alterações", key=f"{key_prefix}save_classes"):
        errors = _validate_classes(st.session_state.classes_draft)
        if errors:
            st.session_state.messages.append(("error", "Há campos em branco. Corrija antes de salvar."))
            for msg in errors:
                st.session_state.messages.append(("error", msg))
            st.rerun()
            return
        st.session_state.classes = copy.deepcopy(st.session_state.classes_draft)
        st.session_state.next_class_id = st.session_state.next_class_id_draft
        st.session_state.classes_draft_signature = _draft_signature(
            {
                "classes": st.session_state.classes,
                "next_class_id": st.session_state.next_class_id,
            }
        )
        save_current_project_snapshot()
        st.session_state.messages.append(("success", "Alterações salvas com sucesso!"))
        st.rerun()
