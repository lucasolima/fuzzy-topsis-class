import copy
import json

import streamlit as st

from src.core.state import save_current_project_snapshot


def _draft_signature(values: dict) -> str:
    return json.dumps(values, sort_keys=True, ensure_ascii=False)


def _init_fuzzy_alt_draft():
    base_snapshot = {
        "fuzzy_number_alternatives": st.session_state.get("fuzzy_number_alternatives", {}),
        "next_fuzzy_alt_id": st.session_state.get("next_fuzzy_alt_id", 1),
    }
    signature = _draft_signature(base_snapshot)

    if (
        "fuzzy_alt_draft_signature" not in st.session_state
        or st.session_state.fuzzy_alt_draft_signature != signature
    ):
        st.session_state.fuzzy_number_alternatives_draft = copy.deepcopy(
            base_snapshot["fuzzy_number_alternatives"]
        )
        st.session_state.next_fuzzy_alt_id_draft = base_snapshot["next_fuzzy_alt_id"]
        st.session_state.fuzzy_alt_draft_signature = signature


def _init_fuzzy_weight_draft():
    base_snapshot = {
        "fuzzy_number_weights": st.session_state.get("fuzzy_number_weights", {}),
        "next_fuzzy_weight_id": st.session_state.get("next_fuzzy_weight_id", 1),
    }
    signature = _draft_signature(base_snapshot)

    if (
        "fuzzy_weight_draft_signature" not in st.session_state
        or st.session_state.fuzzy_weight_draft_signature != signature
    ):
        st.session_state.fuzzy_number_weights_draft = copy.deepcopy(
            base_snapshot["fuzzy_number_weights"]
        )
        st.session_state.next_fuzzy_weight_id_draft = base_snapshot["next_fuzzy_weight_id"]
        st.session_state.fuzzy_weight_draft_signature = signature


def _validate_fuzzy_terms(draft: dict, label: str) -> list[str]:
    errors = []
    for term_key, data in draft.items():
        if not str(data.get("description", "")).strip():
            errors.append(f"{label}: termo {term_key} está sem descrição.")
    return errors


def add_fuzzy_term(fuzzy_terms: dict, next_id_key: str, prefix: str = "NOVO"):
    term_id = f"{prefix}_{st.session_state[next_id_key]}"
    fuzzy_terms[term_id] = {
        "description": "",
        "lmu": [0.0, 0.0, 0.0],
    }
    st.session_state[next_id_key] += 1


def update_fuzzy_term_key(fuzzy_terms: dict, old_key: str, new_key: str):
    if new_key and new_key != old_key and new_key not in fuzzy_terms:
        fuzzy_terms[new_key] = fuzzy_terms.pop(old_key)


def update_fuzzy_term_value(fuzzy_terms: dict, key: str, field: str, value):
    if key in fuzzy_terms:
        if field in ["l", "m", "u"]:
            idx = ["l", "m", "u"].index(field)
            fuzzy_terms[key]["lmu"][idx] = value
        else:
            fuzzy_terms[key][field] = value


def delete_fuzzy_term(fuzzy_terms: dict, key: str):
    if key in fuzzy_terms:
        del fuzzy_terms[key]

def render_fuzzy_config_table(
    dict_name: str,
    next_id_key: str,
    prefix: str,
    title: str,
    fuzzy_terms: dict,
    key_prefix: str = "",
):
    """Função genérica para renderizar a tabela de configurações fuzzy."""
    st.subheader(title)

    fuzzy_keys = list(fuzzy_terms.keys())
    
    if not fuzzy_keys:
        st.info(f"Nenhum termo cadastrado em {title}. Clique no botão abaixo para adicionar.")
    else:
        # Cabeçalhos da tabela
        col_term, col_desc, col_l, col_m, col_u, col_del = st.columns([2, 3, 2, 2, 2, 1])
        with col_term: st.write("**Termo**")
        with col_desc: st.write("**Descrição**")
        with col_l: st.write("**l**")
        with col_m: st.write("**m**")
        with col_u: st.write("**u**")
        
        for key in fuzzy_keys:
            data = fuzzy_terms[key]
            
            col_term, col_desc, col_l, col_m, col_u, col_del = st.columns([2, 3, 2, 2, 2, 1])
            
            # Usando uma string única por base (dict_name) para não conflitar chaves
            k_base = f"{key_prefix}{dict_name}_{key}"

            with col_term:
                new_key = st.text_input(
                    "Termo", 
                    value=key, 
                    key=f"term_{k_base}", 
                    label_visibility="collapsed"
                )
                if new_key != key:
                    update_fuzzy_term_key(fuzzy_terms, key, new_key)
            
            with col_desc:
                new_desc = st.text_input(
                    "Descrição", 
                    value=data["description"], 
                    key=f"desc_{k_base}", 
                    label_visibility="collapsed"
                )
                if new_desc != data["description"]:
                    update_fuzzy_term_value(
                        fuzzy_terms,
                        new_key if new_key != key else key,
                        "description",
                        new_desc,
                    )
            
            with col_l:
                new_l = st.number_input(
                    "l", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][0]), 
                    key=f"l_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_l != data["lmu"][0]:
                     update_fuzzy_term_value(
                         fuzzy_terms,
                         new_key if new_key != key else key,
                         "l",
                         new_l,
                     )

            with col_m:
                new_m = st.number_input(
                    "m", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][1]), 
                    key=f"m_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_m != data["lmu"][1]:
                     update_fuzzy_term_value(
                         fuzzy_terms,
                         new_key if new_key != key else key,
                         "m",
                         new_m,
                     )

            with col_u:
                new_u = st.number_input(
                    "u", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][2]), 
                    key=f"u_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_u != data["lmu"][2]:
                     update_fuzzy_term_value(
                         fuzzy_terms,
                         new_key if new_key != key else key,
                         "u",
                         new_u,
                     )

            with col_del:
                if st.button("❌", key=f"del_{k_base}", help=f"Excluir {key}"):
                    delete_fuzzy_term(fuzzy_terms, key)
                    st.rerun()

def render_fuzzy_alternatives():
    st.header("Parametrização dos Números Fuzzy e Termos Linguísticos")

    
    st.markdown(
        "Cadastre e parametrize os termos linguísticos e seus respectivos "
        "números fuzzy triangulares (l, m, u) tanto para **Alternativas** quanto para **Pesos**."
    )

    _init_fuzzy_alt_draft()
    _init_fuzzy_weight_draft()
    project_id = st.session_state.get("current_project_id", "default")
    key_prefix = f"p{project_id}_"

    # Renderiza Bloco 1: Alternativas
    render_fuzzy_config_table(
        dict_name="fuzzy_number_alternatives", 
        next_id_key="next_fuzzy_alt_id_draft", 
        prefix="ALT", 
        title="Termos Linguísticos (Alternativas)",
        fuzzy_terms=st.session_state.fuzzy_number_alternatives_draft,
        key_prefix=key_prefix,
    )

    if st.button("➕ Adicionar", key=f"{key_prefix}add_fuzzy_alt"):
        add_fuzzy_term(
            st.session_state.fuzzy_number_alternatives_draft,
            "next_fuzzy_alt_id_draft",
            prefix="ALT",
        )
        st.rerun()
    if st.button("💾 Salvar Alterações", key=f"{key_prefix}save_fuzzy_alt"):
        errors = _validate_fuzzy_terms(st.session_state.fuzzy_number_alternatives_draft, "Alternativas")
        if errors:
            st.error("Há campos em branco. Corrija antes de salvar.")
            for msg in errors:
                st.caption(msg)
            return
        st.session_state.fuzzy_number_alternatives = copy.deepcopy(
            st.session_state.fuzzy_number_alternatives_draft
        )
        st.session_state.next_fuzzy_alt_id = st.session_state.next_fuzzy_alt_id_draft
        st.session_state.fuzzy_alt_draft_signature = _draft_signature(
            {
                "fuzzy_number_alternatives": st.session_state.fuzzy_number_alternatives,
                "next_fuzzy_alt_id": st.session_state.next_fuzzy_alt_id,
            }
        )
        save_current_project_snapshot()
        st.success("Alterações salvas com sucesso!")
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True) # Espaçamento
    
    # Renderiza Bloco 2: Pesos
    render_fuzzy_config_table(
        dict_name="fuzzy_number_weights", 
        next_id_key="next_fuzzy_weight_id_draft", 
        prefix="PESO", 
        title="Termos Linguísticos (Pesos)",
        fuzzy_terms=st.session_state.fuzzy_number_weights_draft,
        key_prefix=key_prefix,
    )

    if st.button("➕ Adicionar", key=f"{key_prefix}add_fuzzy_weight"):
        add_fuzzy_term(
            st.session_state.fuzzy_number_weights_draft,
            "next_fuzzy_weight_id_draft",
            prefix="PESO",
        )
        st.rerun()
    if st.button("💾 Salvar Alterações", key=f"{key_prefix}save_fuzzy_weight"):
        errors = _validate_fuzzy_terms(st.session_state.fuzzy_number_weights_draft, "Pesos")
        if errors:
            st.error("Há campos em branco. Corrija antes de salvar.")
            for msg in errors:
                st.caption(msg)
            return
        st.session_state.fuzzy_number_weights = copy.deepcopy(
            st.session_state.fuzzy_number_weights_draft
        )
        st.session_state.next_fuzzy_weight_id = st.session_state.next_fuzzy_weight_id_draft
        st.session_state.fuzzy_weight_draft_signature = _draft_signature(
            {
                "fuzzy_number_weights": st.session_state.fuzzy_number_weights,
                "next_fuzzy_weight_id": st.session_state.next_fuzzy_weight_id,
            }
        )
        save_current_project_snapshot()
        st.success("Alterações salvas com sucesso!")
        st.rerun()
