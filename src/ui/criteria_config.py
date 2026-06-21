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


def _init_criteria_draft():
    base_snapshot = {
        "criteria": st.session_state.get("criteria", {}),
        "next_cri_id": st.session_state.get("next_cri_id", 1),
        "classes": st.session_state.get("classes", {}),
    }
    signature = _draft_signature(base_snapshot)

    if (
        "criteria_draft_signature" not in st.session_state
        or st.session_state.criteria_draft_signature != signature
    ):
        st.session_state.criteria_draft = copy.deepcopy(base_snapshot["criteria"])
        st.session_state.next_cri_id_draft = base_snapshot["next_cri_id"]
        st.session_state.criteria_draft_signature = signature


def add_criterion(criteria_draft: dict, next_id_key: str, classes: dict):
    crit_id = f"CRI{st.session_state[next_id_key]}"

    imported_classes = {
        cid: {"description": cdata["description"], "alternative_term": None}
        for cid, cdata in classes.items()
    }

    criteria_draft[crit_id] = {
        "criterion": "",
        "type": "benefício",
        "descriptions": [],
        "classes": imported_classes,
    }
    st.session_state[next_id_key] += 1


def update_criterion_field(criteria_draft: dict, crit_id: str, field: str, value):
    if crit_id in criteria_draft:
        criteria_draft[crit_id][field] = value


def delete_criterion(criteria_draft: dict, crit_id: str):
    if crit_id in criteria_draft:
        del criteria_draft[crit_id]


def add_criterion_description(criteria_draft: dict, crit_id: str):
    if crit_id in criteria_draft:
        criteria_draft[crit_id]["descriptions"].append(
            {
                "description": "",
                "alternative_term": None,
                "weight_term": None,
            }
        )


def update_criterion_description(criteria_draft: dict, crit_id: str, idx: int, field: str, value):
    if crit_id in criteria_draft:
        descriptions = criteria_draft[crit_id]["descriptions"]
        if 0 <= idx < len(descriptions):
            descriptions[idx][field] = value


def delete_criterion_description(criteria_draft: dict, crit_id: str, idx: int):
    if crit_id in criteria_draft:
        descriptions = criteria_draft[crit_id]["descriptions"]
        if 0 <= idx < len(descriptions):
            descriptions.pop(idx)


def update_criterion_class(criteria_draft: dict, crit_id: str, class_id: str, field: str, value):
    if crit_id in criteria_draft:
        classes = criteria_draft[crit_id].get("classes", {})
        if class_id in classes:
            classes[class_id][field] = value


def sync_classes_in_criteria(criteria_draft: dict, classes: dict):
    for crit_data in criteria_draft.values():
        if "classes" not in crit_data:
            crit_data["classes"] = {}

        for cid in list(crit_data["classes"].keys()):
            if cid not in classes:
                del crit_data["classes"][cid]

        for cid, cdata in classes.items():
            if cid not in crit_data["classes"]:
                crit_data["classes"][cid] = {
                    "description": cdata["description"],
                    "alternative_term": None,
                }
            else:
                crit_data["classes"][cid]["description"] = cdata["description"]


def _validate_criteria(criteria: dict) -> list[str]:
    errors = []
    for crit_id, crit_data in criteria.items():
        name_clean = str(crit_data.get("criterion", "")).strip()
        if not name_clean:
            errors.append(f"Critério {crit_id} está sem nome.")
        else:
            if len(name_clean) > 50:
                errors.append(f"O nome do critério {crit_id} deve ter no máximo 50 caracteres.")
            if not name_clean[0].isalnum():
                errors.append(f"O primeiro caractere do critério {crit_id} não pode ser um caractere especial.")

        for idx, desc_item in enumerate(crit_data.get("descriptions", []), start=1):
            desc_clean = str(desc_item.get("description", "")).strip()
            if not desc_clean:
                errors.append(f"Critério {crit_id}: descrição {idx} está vazia.")
            else:
                if len(desc_clean) > 250:
                    errors.append(f"Critério {crit_id}: a descrição {idx} deve ter no máximo 250 caracteres.")
                if not desc_clean[0].isalnum():
                    errors.append(f"Critério {crit_id}: o primeiro caractere da descrição {idx} não pode ser um caractere especial.")
            if not desc_item.get("alternative_term"):
                errors.append(f"Critério {crit_id}: descrição {idx} sem termo de alternativa.")
            if not desc_item.get("weight_term"):
                errors.append(f"Critério {crit_id}: descrição {idx} sem termo de peso.")

        for class_id, class_data in crit_data.get("classes", {}).items():
            if not class_data.get("alternative_term"):
                errors.append(
                    f"Critério {crit_id}: classe {class_id} sem termo mínimo de alternativa."
                )

    return errors

def render_criteria():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    _display_and_clear_messages()
    st.header("Parametrização dos Critérios")
    st.markdown("Cadastre os critérios (Benefício ou Custo), as descrições de valoração e os termos linguísticos mínimos aceitos por classe em relação a este critério.")
    
    _init_criteria_draft()
    project_id = st.session_state.get("current_project_id", "default")
    key_prefix = f"p{project_id}_"
    criteria = st.session_state.criteria_draft
    classes = st.session_state.get("classes", {})


    # Sincroniza caso classes tenham sido adicionadas/removidas ou renomeadas na primeira aba
    sync_classes_in_criteria(criteria, classes)

    terms_alt = list(st.session_state.get("fuzzy_number_alternatives", {}).keys())
    terms_peso = list(st.session_state.get("fuzzy_number_weights", {}).keys())
    
    options_alt = terms_alt if terms_alt else ["(Vazio)"]
    weight_options = terms_peso if terms_peso else ["(Vazio)"]

    
    
    if not criteria:
        st.session_state.messages.append(("info", "Nenhum critério cadastrado. Clique no botão abaixo para adicionar."))
    else:
        for crit_id, crit_data in criteria.items():
            name_to_show = crit_data["criterion"] if crit_data["criterion"].strip() else "Novo Critério"
            
            with st.expander(name_to_show, expanded=False):
                # Campos principais do critério
                col_nome, col_type, col_del = st.columns([6, 3, 1])
                
                with col_nome:
                    new_name = st.text_input(
                        "Nome do Critério", 
                        value=crit_data["criterion"], 
                        key=f"{key_prefix}nome_{crit_id}",
                        max_chars=50
                    )
                    if new_name != crit_data["criterion"]:
                        update_criterion_field(criteria, crit_id, "criterion", new_name)
                        
                with col_type:
                    types = ["benefício", "custo"]
                    idx_tipo = types.index(crit_data["type"]) if crit_data["type"] in types else 0
                    new_type = st.selectbox(
                        "Tipo", 
                        options=types, 
                        index=idx_tipo, 
                        key=f"{key_prefix}tipo_{crit_id}"
                    )
                    if new_type != crit_data["type"]:
                        update_criterion_field(criteria, crit_id, "type", new_type)
                        
                with col_del:
                    st.write("") 
                    st.write("") 
                    if st.button("❌", key=f"{key_prefix}del_cri_{crit_id}", help=f"Excluir {crit_id}", use_container_width=True):
                        delete_criterion(criteria, crit_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Descrições
                st.markdown("#### Descrições de Valoração")
                
                # Headers das descrições
                if len(crit_data["descriptions"]) > 0:
                    hd1, hd2, hd3, hd_del = st.columns([5, 2, 2, 1])
                    with hd1: st.write("**Descrição**")
                    with hd2: st.write("**Termo Alternativa**")
                    with hd3: st.write("**Termo Peso**")

                for i, desc in enumerate(crit_data["descriptions"]):
                    cd1, cd2, cd3, cd_del = st.columns([5, 2, 2, 1])
                    with cd1:
                        n_desc = st.text_input(
                            "Descrição",
                            value=desc["description"],
                            key=f"{key_prefix}d_desc_{crit_id}_{i}",
                            label_visibility="collapsed",
                            max_chars=250
                        )
                        if n_desc != desc["description"]:
                            update_criterion_description(criteria, crit_id, i, "description", n_desc)
                            
                    with cd2:
                        t_alt_val = desc["alternative_term"]
                        if t_alt_val not in options_alt and terms_alt:
                            t_alt_val = options_alt[0]
                        idx_alt = options_alt.index(t_alt_val) if t_alt_val in options_alt else 0
                        
                        n_t_alt = st.selectbox(
                            "Termo Alt",
                            options=options_alt,
                            index=idx_alt,
                            key=f"{key_prefix}d_talt_{crit_id}_{i}",
                            label_visibility="collapsed",
                        )
                        if n_t_alt != desc["alternative_term"] and terms_alt:
                            update_criterion_description(criteria, crit_id, i, "alternative_term", n_t_alt)
                            
                    with cd3:
                        t_peso_val = desc["weight_term"]
                        if t_peso_val not in weight_options and terms_peso:
                            t_peso_val = weight_options[0]
                        idx_peso = weight_options.index(t_peso_val) if t_peso_val in weight_options else 0
                        
                        n_t_peso = st.selectbox(
                            "Termo Peso",
                            options=weight_options,
                            index=idx_peso,
                            key=f"{key_prefix}d_tpeso_{crit_id}_{i}",
                            label_visibility="collapsed",
                        )
                        if n_t_peso != desc["weight_term"] and terms_peso:
                            update_criterion_description(criteria, crit_id, i, "weight_term", n_t_peso)
                            
                    with cd_del:
                        if st.button("🗑️", key=f"{key_prefix}del_d_{crit_id}_{i}"):
                            delete_criterion_description(criteria, crit_id, i)
                            st.rerun()
                
                col_btn_add_d, _ = st.columns([3, 7])
                with col_btn_add_d:
                    if st.button("➕ Adicionar Descrição", key=f"{key_prefix}add_d_{crit_id}"):
                        add_criterion_description(criteria, crit_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Classes
                st.markdown("#### Classes (Limiares do Critério)")
                if not crit_data["classes"]:
                    st.session_state.messages.append(("info", "Não há classes cadastradas na primeira aba."))
                else:
                    ch1, ch2, _ = st.columns([5, 3, 2])
                    with ch1: st.write("**Classe**")
                    with ch2: st.write("**Termo Mínimo (Alternativa)**")
                    
                    for cid, cdata in crit_data["classes"].items():
                        cc1, cc2, _ = st.columns([5, 3, 2])
                        with cc1:
                            st.text_input(
                                "Classe",
                                value=cdata["description"],
                                disabled=True,
                                key=f"{key_prefix}c_desc_{crit_id}_{cid}",
                                label_visibility="collapsed",
                            )
                        with cc2:
                            current_c_alt = cdata["alternative_term"]
                            if current_c_alt not in options_alt and terms_alt:
                                current_c_alt = options_alt[0]
                            idx_calt = options_alt.index(current_c_alt) if current_c_alt in options_alt else 0
                            
                            n_c_alt = st.selectbox(
                                "Termo Mínimo",
                                options=options_alt,
                                index=idx_calt,
                                key=f"{key_prefix}c_talt_{crit_id}_{cid}",
                                label_visibility="collapsed",
                            )
                            if n_c_alt != cdata["alternative_term"] and terms_alt:
                                update_criterion_class(criteria, crit_id, cid, "alternative_term", n_c_alt)

    st.markdown("---")
    if st.button("➕ Adicionar", key=f"{key_prefix}add_criteria_btn"):
        add_criterion(criteria, "next_cri_id_draft", classes)
        st.rerun()

    if st.button("💾 Salvar Alterações", key=f"{key_prefix}save_criteria"):
        errors = _validate_criteria(criteria)
        if errors:
            st.session_state.messages.append(("error", "Há campos em branco. Corrija antes de salvar."))
            for msg in errors:
                st.session_state.messages.append(("error", msg))
            st.rerun()
            return
        st.session_state.criteria = copy.deepcopy(criteria)
        st.session_state.next_cri_id = st.session_state.next_cri_id_draft
        st.session_state.criteria_draft_signature = _draft_signature(
            {
                "criteria": st.session_state.criteria,
                "next_cri_id": st.session_state.next_cri_id,
                "classes": st.session_state.get("classes", {}),
            }
        )
        save_current_project_snapshot()
        st.session_state.messages.append(("success", "Alterações salvas com sucesso!"))
        st.rerun()
