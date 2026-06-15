import streamlit as st
from src.core.state import (
    create_project,
    delete_project,
    initialize_state,
    list_projects,
    rename_project,
    switch_project,
)
from src.core.data_repository import system_data
from src.ui.alternatives import render_alternatives
from src.ui.fuzzy_alternatives import render_fuzzy_alternatives

# 1. Configuração da página (deve ser o primeiro comando do app)
st.set_page_config(
    page_title="FTOPSIS Class",
    page_icon="📊",
    layout="wide"  # Alterado para 'wide' para acomodar melhor a tabela de fuzzy
)

def main():
    initialize_state()

    projects = list_projects()
    current_project_id = st.session_state.current_project_id
    project_title = projects.get(current_project_id, "Projeto Ativo")

    st.title(project_title)

    # 2. Inicializa gerência de estado (regras e dados visuais)

    def _rename_project_modal():
        @st.dialog("Gerenciar Projeto")
        def _modal_body():
            projects = list_projects()
            current_name = projects.get(st.session_state.current_project_id, "")
            
            new_name = st.text_input(
                "Renomear projeto",
                value=current_name,
                key="rename_project_input_modal",
            )
            
            col_save = st.columns(1)[0]
            with col_save:
                if st.button("Salvar", key="save_project_rename", use_container_width=True):
                    if new_name.strip():
                        rename_project(st.session_state.current_project_id, new_name.strip())
                        st.session_state._project_changed = True
                        st.rerun()
                    else:
                        st.warning("Informe um nome para o projeto.")

        _modal_body()

    def _create_project_modal():
        @st.dialog("Criar Novo Projeto")
        def _modal_body():
            new_project_name = st.text_input(
                "Nome do Projeto",
                placeholder="Ex: Projeto de Expansão X",
                key="project_new_name_sidebar",
            )
            if st.button("Criar Projeto", key="sidebar_project_create_btn", use_container_width=True):
                if new_project_name.strip():
                    new_project_id = create_project(new_project_name.strip())
                    switch_project(new_project_id)
                    st.session_state._project_changed = True
                    st.rerun()
                else:
                    st.warning("Informe um nome para o projeto.")

        _modal_body()

    # Verifica se o projeto foi alterado após o modal fechar
    if st.session_state.get("_project_changed"):
        st.session_state._project_changed = False
        st.rerun()

    # Menu Lateral
    with st.sidebar:
        
        project_ids = list(projects.keys())
        if current_project_id not in project_ids and project_ids:
            current_project_id = project_ids[0]
            
        def _on_sidebar_project_select():
            selected = st.session_state._sidebar_project_selectbox
            if selected != st.session_state.current_project_id:
                switch_project(selected)
                
        st.write("**Projeto Ativo:**")
        col_list, col_add = st.columns([3, 1])
        with col_list:
            st.selectbox(
                "Projeto Ativo:",
                project_ids,
                index=project_ids.index(current_project_id) if project_ids else 0,
                format_func=lambda pid: projects.get(pid, f"Projeto {pid}"),
                key="_sidebar_project_selectbox",
                on_change=_on_sidebar_project_select,
                label_visibility="collapsed"
            )
        with col_add:
            if st.button("➕", key="sidebar_add_project", help="Criar Novo Projeto", use_container_width=True):
                _create_project_modal()

        col_edit, col_del = st.columns([1, 1])
        with col_edit:
            if st.button("✏️", key="sidebar_project_rename", help="Renomear Projeto Ativo", use_container_width=True):
                _rename_project_modal()
        with col_del:
            if st.button("❌", key="sidebar_project_delete", help="Excluir Projeto Ativo", use_container_width=True):
                next_project_id = delete_project(st.session_state.current_project_id)
                if next_project_id is not None:
                    switch_project(next_project_id)
                st.rerun()

        
        st.markdown("---")

        st.header("Menu Principal")
        
        secao = st.selectbox(
            "Selecione a Seção:",
            ["Parametrização do Modelo", "Avaliação das Alternativas", "Classificação Final"],
            key="sidebar_section",
        )
        
        if secao == "Parametrização do Modelo":
            selected_menu = st.radio(
                "Opções de Parametrização:",
                ["Alternativas e Classes", "Números Fuzzy", "Critérios"],
                key="sidebar_menu_param",
            )
        elif secao == "Avaliação das Alternativas":
            selected_menu = st.radio(
                "Opções de Avaliação:",
                ["Alternativas", "Pesos"],
                key="sidebar_menu_eval",
            )
        else:
            selected_menu = st.radio(
                "Opções de Classificação:",
                ["Matriz de Decisão", "Classificação Final"],
                key="sidebar_menu_classif",
            )
        
        st.markdown("---")

    # 2.1 Sincroniza estado da interface com a camada de regras de negócio estática
    system_data.update_from_state(st.session_state)

    # 3. Renderização Condicional da Navegação
    if selected_menu == "Alternativas e Classes":
        render_alternatives()
        
    elif selected_menu == "Números Fuzzy":
        render_fuzzy_alternatives()
        
    elif selected_menu == "Critérios":
        from src.ui.criteria_config import render_criteria
        render_criteria()
        
    elif selected_menu == "Alternativas":
        from src.ui.evaluations import render_evaluations
        render_evaluations()
        
    elif selected_menu == "Pesos":
        from src.ui.criteria_weights import render_criteria_weights
        render_criteria_weights()
        
    elif selected_menu == "Matriz de Decisão":
        from src.ui.decision_matrix import render_decision_matrix
        render_decision_matrix()
        
    elif selected_menu == "Classificação Final":
        from src.ui.weighted_matrix import render_weighted_matrix
        render_weighted_matrix()

if __name__ == "__main__":
    main()
