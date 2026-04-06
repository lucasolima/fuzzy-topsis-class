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
        novas_evaluations = {}
        
        for alt_id, alt_nome in alternatives.items():
            if alt_id not in st.session_state.evaluations:
                st.session_state.evaluations[alt_id] = {}
                
            nome_da_alternativa = alt_nome if alt_nome.strip() else f"Alternativa Sem Nome"
            with st.expander(f"**{nome_da_alternativa}**", expanded=False):
                for crit_id, crit_data in criteria.items():
                    crit_name = crit_data.get("criterion", '')
                    titulo_campo = crit_name if crit_name else "Critério Sem Nome"
                    
                    # Lista de descrições possíveis do critério
                    opcoes = [d["description"] for d in crit_data.get("descriptions", [])]
                    
                    valor_atual = st.session_state.evaluations[alt_id].get(crit_id, None)
                    # Verifica segurança caso as opções tenham sido apagadas na aba anterior
                    if valor_atual not in opcoes:
                        valor_atual = None
                        
                    idx_atual = opcoes.index(valor_atual) if valor_atual is not None else None
                    
                    novo_valor = st.selectbox(
                        label=titulo_campo,
                        options=opcoes,
                        index=idx_atual,
                        placeholder="Selecione uma opção...",
                        key=f"aval_{alt_id}_{crit_id}"
                    )
                    
                    novas_evaluations[(alt_id, crit_id)] = novo_valor

        st.markdown("---")
        cols = st.columns([1, 4])
        with cols[0]:
            submitted = st.form_submit_button("💾 Salvar Avaliações", type="primary", use_container_width=True)
            
        if submitted:
            for (aid, cid), val in novas_evaluations.items():
                if val is not None:
                    st.session_state.evaluations[aid][cid] = val
            st.rerun()
