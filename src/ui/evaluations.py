import streamlit as st


def _build_editor_rows(alternatives: dict, criteria: dict) -> list[dict]:
    rows = []
    for alt_id, alt_name in alternatives.items():
        row = {
            "Alternativa": alt_name.strip() if alt_name.strip() else "Alternativa sem nome",
        }
        for crit_id, crit_data in criteria.items():
            crit_name = crit_data.get("criterion", "") or "Critério Sem Nome"
            current_value = st.session_state.evaluations.get(alt_id, {}).get(crit_id)
            row[crit_name] = current_value if current_value is not None else "Selecione..."
        rows.append(row)
    return rows

def render_evaluations():
    st.header("Avaliação das Alternativas")
    st.markdown(
        "Preencha a matriz abaixo selecionando, para cada alternativa, a descrição correspondente "
        "em cada critério. O quadro possui rolagem interna e cabeçalho fixo."
    )
    
    alternatives = st.session_state.get("alternatives", {})
    criteria = st.session_state.get("criteria", {})
    
    if not alternatives:
        st.warning("Nenhuma alternativa cadastrada. Retorne à aba de Alternativas.")
        return
        
    if not criteria:
        st.warning("Nenhum critério cadastrado. Retorne à aba de Critérios.")
        return

    # Garante a inicialização segura do bloco de avaliações no session_state
    if "evaluations" not in st.session_state:
        st.session_state.evaluations = {}

    crit_items = list(criteria.items())
    alt_items = list(alternatives.items())

    if not any(crit_data.get("descriptions", []) for _, crit_data in crit_items):
        st.warning("Nenhum critério possui descrições cadastradas para avaliação.")
        return

    editor_rows = _build_editor_rows(alternatives, criteria)
    column_config = {
        "Alternativa": st.column_config.TextColumn("Alternativa", disabled=True),
    }

    for _, crit_data in crit_items:
        crit_name = crit_data.get("criterion", "") or "Critério Sem Nome"
        options = [d["description"] for d in crit_data.get("descriptions", []) if d.get("description")]
        column_config[crit_name] = st.column_config.SelectboxColumn(
            crit_name,
            options=["Selecione..."] + options,
            required=False,
        )

    edited_rows = st.data_editor(
        editor_rows,
        hide_index=True,
        use_container_width=True,
        height=520,
        column_config=column_config,
        key="evaluations_matrix_editor",
    )

    if st.button("💾 Salvar Avaliações", use_container_width=True):
        for (alt_id, _), row in zip(alt_items, edited_rows):
            if alt_id not in st.session_state.evaluations:
                st.session_state.evaluations[alt_id] = {}

            for crit_id, crit_data in crit_items:
                crit_name = crit_data.get("criterion", "") or "Critério Sem Nome"
                value = row.get(crit_name)
                if value in (None, "", "Selecione..."):
                    st.session_state.evaluations[alt_id].pop(crit_id, None)
                else:
                    st.session_state.evaluations[alt_id][crit_id] = value

        st.rerun()
