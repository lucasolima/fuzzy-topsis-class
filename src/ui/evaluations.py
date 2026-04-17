import streamlit as st
import copy
import json


def _evaluation_signature(values: dict) -> str:
    return json.dumps(values, sort_keys=True, ensure_ascii=False)

def render_evaluations():
    st.header("Avaliação das Alternativas")
    st.markdown(
        "Preencha a matriz abaixo selecionando, para cada alternativa, a descrição correspondente "
        "em cada critério. As alterações só são aplicadas ao clicar em **Salvar Avaliações**."
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
    
    current_signature = _evaluation_signature(st.session_state.evaluations)
    if (
        "evaluation_draft" not in st.session_state
        or st.session_state.get("evaluation_draft_signature") != current_signature
    ):
        st.session_state.evaluation_draft = copy.deepcopy(st.session_state.evaluations)
        st.session_state.evaluation_draft_signature = current_signature

    crit_items = list(criteria.items())
    alt_items = list(alternatives.items())

    if not any(crit_data.get("descriptions", []) for _, crit_data in crit_items):
        st.warning("Nenhum critério possui descrições cadastradas para avaliação.")
        return

    header_cols = st.columns([3] + [2 for _ in crit_items])
    with header_cols[0]:
        st.markdown("**Alternativa**")
    for col, (_, crit_data) in zip(header_cols[1:], crit_items):
        label = crit_data.get("criterion", "") or "Critério Sem Nome"
        with col:
            st.markdown(f"**{label}**")

    placeholder = "Selecione..."

    with st.container(height=520, border=True):
        for alt_id, alt_name in alt_items:
            if alt_id not in st.session_state.evaluation_draft:
                st.session_state.evaluation_draft[alt_id] = {}

            alternative_name = alt_name.strip() if alt_name.strip() else "Alternativa sem nome"
            row_cols = st.columns([3] + [2 for _ in crit_items])
            with row_cols[0]:
                st.write(alternative_name)

            for idx, (crit_id, crit_data) in enumerate(crit_items, start=1):
                crit_name = crit_data.get("criterion", "") or "Critério Sem Nome"
                options = [d["description"] for d in crit_data.get("descriptions", []) if d.get("description")]

                current_value = st.session_state.evaluation_draft[alt_id].get(crit_id)
                if current_value not in options:
                    current_value = placeholder

                with row_cols[idx]:
                    if options:
                        select_options = [placeholder] + options
                        current_idx = select_options.index(current_value)
                        new_value = st.selectbox(
                            label=f"{alternative_name} - {crit_name}",
                            options=select_options,
                            index=current_idx,
                            key=f"aval_{alt_id}_{crit_id}",
                            label_visibility="collapsed"
                        )
                        if new_value == placeholder:
                            st.session_state.evaluation_draft[alt_id].pop(crit_id, None)
                        else:
                            st.session_state.evaluation_draft[alt_id][crit_id] = new_value
                    else:
                        st.caption("Sem descrições")
                        st.session_state.evaluation_draft[alt_id].pop(crit_id, None)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("💾 Salvar Avaliações", use_container_width=True):
            st.session_state.evaluations = copy.deepcopy(st.session_state.evaluation_draft)
            st.session_state.evaluation_draft_signature = _evaluation_signature(st.session_state.evaluations)
            st.success("Avaliações salvas com sucesso!")
            st.rerun()
