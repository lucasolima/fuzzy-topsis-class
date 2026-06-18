import copy
import json
import os

import streamlit as st

from src.db.repository import (
    create_project as db_create_project,
    delete_project as db_delete_project,
    ensure_schema,
    list_projects as db_list_projects,
    load_project_state,
    rename_project as db_rename_project,
    save_project_state,
)

def load_data(filename):
    """Carrega dados de um arquivo JSON da pasta data/."""
    # Encontra o caminho absoluto da pasta data baseada na raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _next_id_from_mapping(mapping: dict, prefix: str, fallback: int = 1) -> int:
    max_id = 0
    for key in mapping.keys():
        if not key.startswith(prefix):
            continue
        suffix = key[len(prefix):]
        if suffix.isdigit():
            max_id = max(max_id, int(suffix))

    return max_id + 1 if max_id else fallback


PROJECT_STATE_KEYS = [
    "alternatives",
    "next_alt_id",
    "fuzzy_number_alternatives",
    "fuzzy_number_weights",
    "next_fuzzy_alt_id",
    "next_fuzzy_weight_id",
    "classes",
    "next_class_id",
    "criteria",
    "next_cri_id",
    "evaluations",
    "criteria_weights",
]


def _build_project_template_state() -> dict:
    alternatives = load_data("alternatives.json")
    fuzzy_number_alternatives = load_data("fuzzy_number_alternatives.json")
    fuzzy_number_weights = load_data("fuzzy_number_weights.json")
    classes = load_data("classes.json")
    criteria = load_data("criteria.json")

    return {
        "alternatives": alternatives,
        "next_alt_id": _next_id_from_mapping(alternatives, "ALT", 1),
        "fuzzy_number_alternatives": fuzzy_number_alternatives,
        "fuzzy_number_weights": fuzzy_number_weights,
        "next_fuzzy_alt_id": _next_id_from_mapping(fuzzy_number_alternatives, "ALT", 1),
        "next_fuzzy_weight_id": _next_id_from_mapping(fuzzy_number_weights, "PESO", 1),
        "classes": classes,
        "next_class_id": _next_id_from_mapping(classes, "CLA", 1),
        "criteria": criteria,
        "next_cri_id": _next_id_from_mapping(criteria, "CRI", 1),
        "evaluations": {},
        "criteria_weights": {},
    }


def _build_default_project_state() -> dict:
    state = _build_project_template_state()
    state["alternatives"] = {}
    state["next_alt_id"] = 1
    return state


def _build_blank_project_state() -> dict:
    return {
        "alternatives": {},
        "next_alt_id": 1,
        "fuzzy_number_alternatives": {},
        "fuzzy_number_weights": {},
        "next_fuzzy_alt_id": 1,
        "next_fuzzy_weight_id": 1,
        "classes": {},
        "next_class_id": 1,
        "criteria": {},
        "next_cri_id": 1,
        "evaluations": {},
        "criteria_weights": {},
    }


def _clear_drafts():
    draft_keys = [
        "alternatives_draft",
        "classes_draft",
        "next_alt_id_draft",
        "next_class_id_draft",
        "alternatives_classes_draft_signature",
        "classes_draft_signature",
        "fuzzy_number_alternatives_draft",
        "fuzzy_number_weights_draft",
        "next_fuzzy_alt_id_draft",
        "next_fuzzy_weight_id_draft",
        "fuzzy_alt_draft_signature",
        "fuzzy_weight_draft_signature",
        "criteria_draft",
        "next_cri_id_draft",
        "criteria_draft_signature",
        "evaluation_draft",
        "evaluation_draft_signature",
    ]

    for key in draft_keys:
        if key in st.session_state:
            del st.session_state[key]


def _clear_widget_state():
    prefixes = (
        "input_",
        "class_desc_",
        "class_del_",
        "term_",
        "desc_",
        "l_",
        "m_",
        "u_",
        "del_",
        "add_",
        "save_",
        "nome_",
        "tipo_",
        "del_cri_",
        "d_desc_",
        "d_talt_",
        "d_tpeso_",
        "del_d_",
        "c_desc_",
        "c_talt_",
        "aval_",
        "peso_",
    )
    exact_keys = {
        "_project_selectbox",
        "_modal_should_close",
        "project_new_name",
        "rename_project_input",
    }

    for key in list(st.session_state.keys()):
        if key in exact_keys or key.startswith(prefixes):
            del st.session_state[key]


def _preserve_ui_state() -> dict:
    keys = (
        "authenticated",
        "auth_error",
        "selected_section",
        "sidebar_menu_param",
        "sidebar_menu_eval",
        "sidebar_menu_classif",
    )
    return {key: st.session_state[key] for key in keys if key in st.session_state}


def _reset_session_state(preserved: dict) -> None:
    # Ignora chaves internas de widgets que estão ativos na tela para evitar StreamlitAPIException
    ignored_widget_keys = {"_sidebar_project_selectbox", "_sidebar_sec_selectbox"}
    for key in list(st.session_state.keys()):
        if key not in preserved and key not in ignored_widget_keys:
            del st.session_state[key]
    st.session_state.update(preserved)


def _get_project_snapshot_from_state() -> dict:
    snapshot = {}
    for key in PROJECT_STATE_KEYS:
        if key in st.session_state:
            snapshot[key] = copy.deepcopy(st.session_state[key])
    return snapshot


def _apply_project_snapshot(snapshot: dict):
    for key in PROJECT_STATE_KEYS:
        if key in snapshot:
            st.session_state[key] = copy.deepcopy(snapshot[key])


def _hydrate_project_state(state: dict) -> dict:
    return {
        **state,
        "next_alt_id": _next_id_from_mapping(state.get("alternatives", {}), "ALT", 1),
        "next_fuzzy_alt_id": _next_id_from_mapping(state.get("fuzzy_number_alternatives", {}), "ALT", 1),
        "next_fuzzy_weight_id": _next_id_from_mapping(state.get("fuzzy_number_weights", {}), "PESO", 1),
        "next_class_id": _next_id_from_mapping(state.get("classes", {}), "CLA", 1),
        "next_cri_id": _next_id_from_mapping(state.get("criteria", {}), "CRI", 1),
    }


def initialize_projects():
    ensure_schema()
    projects = db_list_projects()
    if not projects:
        default_state = _build_default_project_state()
        project_id = db_create_project("Novo Projeto")
        save_project_state(project_id, default_state)
        projects = db_list_projects()

    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = sorted(projects.keys())[0]
    elif st.session_state.current_project_id not in projects:
        st.session_state.current_project_id = sorted(projects.keys())[0]

    current_project_id = st.session_state.current_project_id
    loaded_project_id = st.session_state.get("loaded_project_id")
    if loaded_project_id != current_project_id:
        snapshot = load_project_state(current_project_id)
        _apply_project_snapshot(_hydrate_project_state(snapshot))
        _clear_drafts()
        st.session_state.loaded_project_id = current_project_id


def list_projects() -> dict:
    return db_list_projects()


def create_project(name: str) -> int:
    project_id = db_create_project(name)
    save_project_state(project_id, _build_default_project_state())
    return project_id


def rename_project(project_id: int, name: str):
    db_rename_project(project_id, name)


def delete_project(project_id: int) -> int | None:
    db_delete_project(project_id)
    projects = db_list_projects()
    if not projects:
        return create_project("Novo Projeto")
    return sorted(projects.keys())[0]


def save_current_project_snapshot():
    project_id = st.session_state.current_project_id
    if project_id:
        save_project_state(project_id, _get_project_snapshot_from_state())


def switch_project(project_id: int):
    projects = db_list_projects()
    if project_id not in projects:
        return
    save_current_project_snapshot()
    snapshot = load_project_state(project_id)
    preserved = _preserve_ui_state()
    _reset_session_state(preserved)
    st.session_state.current_project_id = project_id
    _apply_project_snapshot(_hydrate_project_state(snapshot))
    _clear_drafts()
    st.session_state.loaded_project_id = project_id
    st.session_state._project_changed = True

def initialize_state():
    """Inicializa as variáveis de sessão necessárias da aplicação usando Data-Driven config."""
    initialize_projects()

def add_alternative():
    """Adiciona uma nova alternativa vazia no final do dicionário."""
    alt_id = f"ALT{st.session_state.next_alt_id}"
    st.session_state.alternatives[alt_id] = ""
    st.session_state.next_alt_id += 1

def update_alternative(alt_id: str, new_value: str):
    """Atualiza o valor de uma alternativa existente."""
    st.session_state.alternatives[alt_id] = new_value

def delete_alternative(alt_id: str):
    """Deleta uma alternativa pelo seu identificador (ex: ALT1)."""
    if alt_id in st.session_state.alternatives:
        del st.session_state.alternatives[alt_id]
