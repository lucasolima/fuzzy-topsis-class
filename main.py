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

    def _show_projects_modal():
        @st.dialog("Projetos")
        def _modal_body():
            projects = list_projects()
            project_ids = list(projects.keys())
            current_project_id = st.session_state.current_project_id
            if current_project_id not in project_ids:
                current_project_id = project_ids[0]

            def _on_project_select():
                selected = st.session_state._project_selectbox
                if selected != st.session_state.current_project_id:
                    switch_project(selected)
                    st.session_state._modal_should_close = True

            st.selectbox(
                "Projeto Atual:",
                project_ids,
                index=project_ids.index(current_project_id),
                format_func=lambda pid: projects.get(pid, f"Projeto {pid}"),
                key="_project_selectbox",
                on_change=_on_project_select,
            )

            if st.session_state.get("_modal_should_close"):
                st.session_state._modal_should_close = False
                st.rerun()

            new_project_name = st.text_input(
                "Novo Projeto",
                placeholder="Nome do projeto",
                key="project_new_name",
            )
            if st.button("Criar Projeto", key="project_create"):
                if new_project_name.strip():
                    new_project_id = create_project(new_project_name.strip())
                    switch_project(new_project_id)
                    st.session_state._modal_should_close = True
                    st.rerun()
                else:
                    st.warning("Informe um nome para o projeto.")

            rename_value = st.text_input(
                "Renomear Projeto",
                value=projects.get(st.session_state.current_project_id, ""),
                key="rename_project_input",
            )
            if st.button("Renomear Projeto", key="project_rename"):
                if rename_value.strip():
                    rename_project(st.session_state.current_project_id, rename_value.strip())
                else:
                    st.warning("Informe um nome para o projeto.")

            if st.button("Excluir Projeto", key="project_delete"):
                next_project_id = delete_project(st.session_state.current_project_id)
                if next_project_id is not None:
                    switch_project(next_project_id)
                st.session_state._modal_should_close = True
                st.rerun()

        _modal_body()

    # Verifica se o projeto foi alterado após o modal fechar
    if st.session_state.get("_project_changed"):
        st.session_state._project_changed = False
        st.rerun()

    # Menu Lateral
    with st.sidebar:
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
        st.header("Projetos")
        if st.button("Gerenciar Projetos"):
            _show_projects_modal()

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
