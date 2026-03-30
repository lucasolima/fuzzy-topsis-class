import streamlit as st

def add_class():
    """Adiciona uma nova classe vazia com ID auto-incrementado."""
    class_id = f"CLA{st.session_state.next_class_id}"

    st.session_state.classes[class_id] = {
        "descricao": "",
        "termo_alternativa": None
    }
    st.session_state.next_class_id += 1

def update_class_value(class_id: str, field: str, value: str):
    """Atualiza a descrição ou o termo linguístico associado à classe."""
    if class_id in st.session_state.classes:
        st.session_state.classes[class_id][field] = value

def delete_class(class_id: str):
    """Deleta uma classe."""
    if class_id in st.session_state.classes:
        del st.session_state.classes[class_id]
