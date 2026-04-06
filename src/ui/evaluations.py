import streamlit as st

def render_evaluations():
    st.header("Avaliação das Alternativas")
    st.markdown(
        "Para cada alternativa abaixo, selecione a descrição correspondente em relação a "
        "cada um dos critérios estabelecidos."
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
    
    with st.form("form_evaluations"):
        new_evaluations = {}
        
        for alt_id, alt_name in alternatives.items():
            if alt_id not in st.session_state.evaluations:
                st.session_state.evaluations[alt_id] = {}
                
            alternative_name = alt_name if alt_name.strip() else f"Alternativa Sem Nome"
            with st.expander(f"**{alternative_name}**", expanded=False):
                for crit_id, crit_data in criteria.items():
                    crit_name = crit_data.get("criterion", '')
                    title_field = crit_name if crit_name else "Critério Sem Nome"
                    
                    # Lista de descrições possíveis do critério
                    options = [d["description"] for d in crit_data.get("descriptions", [])]
                    
                    current_value = st.session_state.evaluations[alt_id].get(crit_id, None)
                    # Verifica segurança caso as opções tenham sido apagadas na aba anterior
                    if current_value not in options:
                        current_value = None
                        
                    current_idx = options.index(current_value) if current_value is not None else None
                    
                    new_value = st.selectbox(
                        label=title_field,
                        options=options,
                        index=current_idx,
                        placeholder="Selecione uma opção...",
                        key=f"aval_{alt_id}_{crit_id}"
                    )
                    
                    new_evaluations[(alt_id, crit_id)] = new_value

        st.markdown("---")
        cols = st.columns([1, 4])
        with cols[0]:
            submitted = st.form_submit_button("💾 Salvar Avaliações", use_container_width=True)
            
        if submitted:
            for (aid, cid), val in new_evaluations.items():
                if val is not None:
                    st.session_state.evaluations[aid][cid] = val
            st.rerun()
