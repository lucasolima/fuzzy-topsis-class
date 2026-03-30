import streamlit as st

def add_criterio():
    cri_id = f"CRI{st.session_state.next_cri_id}"
    
    # Ao criar um novo critério, inicializar as classes com base nas que já existem no estado geral de classes
    imported_classes = {}
    if "classes" in st.session_state:
        for cid, cdata in st.session_state.classes.items():
            imported_classes[cid] = {"descricao": cdata["descricao"], "termo_alternativa": None}
            
    st.session_state.criterios[cri_id] = {
        "criterio": "",
        "tipo": "benefício",
        "descricoes": [],
        "classes": imported_classes
    }
    st.session_state.next_cri_id += 1

def update_criterio_field(cri_id: str, field: str, value):
    if cri_id in st.session_state.criterios:
        st.session_state.criterios[cri_id][field] = value

def delete_criterio(cri_id: str):
    if cri_id in st.session_state.criterios:
        del st.session_state.criterios[cri_id]

# Descrições
def add_criterio_descricao(cri_id: str):
    if cri_id in st.session_state.criterios:
        st.session_state.criterios[cri_id]["descricoes"].append({
            "descricao": "",
            "termo_alternativa": None,
            "termo_peso": None
        })

def update_criterio_descricao(cri_id: str, idx: int, field: str, value):
    if cri_id in st.session_state.criterios:
        if 0 <= idx < len(st.session_state.criterios[cri_id]["descricoes"]):
            st.session_state.criterios[cri_id]["descricoes"][idx][field] = value

def delete_criterio_descricao(cri_id: str, idx: int):
    if cri_id in st.session_state.criterios:
        if 0 <= idx < len(st.session_state.criterios[cri_id]["descricoes"]):
            st.session_state.criterios[cri_id]["descricoes"].pop(idx)

# Classes
def update_criterio_classe(cri_id: str, class_id: str, field: str, value):
    if cri_id in st.session_state.criterios:
        if "classes" in st.session_state.criterios[cri_id]:
            if class_id in st.session_state.criterios[cri_id]["classes"]:
                st.session_state.criterios[cri_id]["classes"][class_id][field] = value

def sync_classes_in_criterios():
    """Garante que se uma nova classe global foi adicionada ou deletada, 
       isso reflita na lista de classes de todos os critérios."""
    global_classes = st.session_state.get("classes", {})
    if "criterios" in st.session_state:
        for cri_data in st.session_state.criterios.values():
            if "classes" not in cri_data:
                cri_data["classes"] = {}
                
            # Deletar removidas
            for cid in list(cri_data["classes"].keys()):
                if cid not in global_classes:
                    del cri_data["classes"][cid]
                    
            # Adicionar ou atualizar as existentes (descrição)
            for cid, cdata in global_classes.items():
                if cid not in cri_data["classes"]:
                    cri_data["classes"][cid] = {"descricao": cdata["descricao"], "termo_alternativa": None}
                else:
                    # Sync global class description
                    cri_data["classes"][cid]["descricao"] = cdata["descricao"]
