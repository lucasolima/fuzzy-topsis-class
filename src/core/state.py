import copy
import json
import os

import streamlit as st

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


def _build_default_project_state() -> dict:
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
        "next_fuzzy_alt_id": 1,
        "next_fuzzy_weight_id": 1,
        "classes": classes,
        "next_class_id": _next_id_from_mapping(classes, "CLA", 1),
        "criteria": criteria,
        "next_cri_id": _next_id_from_mapping(criteria, "CRI", 1),
        "evaluations": {},
        "criteria_weights": {},
    }


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


def initialize_projects():
    if "projects" not in st.session_state:
        default_state = _build_default_project_state()
        st.session_state.projects = {
            1: {
                "name": "Projeto Padrão",
                "state": default_state,
            }
        }
        st.session_state.current_project_id = 1
        st.session_state.next_project_id = 2

    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = sorted(st.session_state.projects.keys())[0]

    current_project_id = st.session_state.current_project_id
    if current_project_id in st.session_state.projects:
        _apply_project_snapshot(st.session_state.projects[current_project_id]["state"])
    _clear_drafts()


def list_projects() -> dict:
    return {pid: data["name"] for pid, data in st.session_state.projects.items()}


def create_project(name: str) -> int:
    project_id = st.session_state.next_project_id
    st.session_state.projects[project_id] = {
        "name": name,
        "state": _build_blank_project_state(),
    }
    st.session_state.next_project_id += 1
    return project_id


def rename_project(project_id: int, name: str):
    if project_id in st.session_state.projects:
        st.session_state.projects[project_id]["name"] = name


def delete_project(project_id: int) -> int | None:
    if project_id in st.session_state.projects:
        del st.session_state.projects[project_id]

    if not st.session_state.projects:
        return None

    return sorted(st.session_state.projects.keys())[0]


def save_current_project_snapshot():
    project_id = st.session_state.current_project_id
    if project_id in st.session_state.projects:
        st.session_state.projects[project_id]["state"] = _get_project_snapshot_from_state()


def switch_project(project_id: int):
    if project_id not in st.session_state.projects:
        return
    save_current_project_snapshot()
    st.session_state.current_project_id = project_id
    _apply_project_snapshot(st.session_state.projects[project_id]["state"])
    _clear_drafts()

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
