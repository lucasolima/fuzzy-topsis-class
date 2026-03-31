import streamlit as st

def render_avaliacoes():
    st.header("Avaliações das Alternativas")
    st.markdown(
        "Para cada alternativa abaixo, selecione a descrição correspondente em relação a "
        "cada um dos critérios estabelecidos."
    )
    
    alternativas = st.session_state.get("alternativas", {})
    criterios = st.session_state.get("criterios", {})
    
    if not alternativas:
        st.warning("Nenhuma alternativa cadastrada. Retorne à aba de Alternativas.")
        return
        
    if not criterios:
        st.warning("Nenhum critério cadastrado. Retorne à aba de Critérios.")
        return

    # Garante a inicialização segura do bloco de avaliações no session_state
    if "avaliacoes" not in st.session_state:
        st.session_state.avaliacoes = {}
    
    with st.form("form_avaliacoes"):
        novas_avaliacoes = {}
        
        for alt_id, alt_nome in alternativas.items():
            if alt_id not in st.session_state.avaliacoes:
                st.session_state.avaliacoes[alt_id] = {}
                
            nome_da_alternativa = alt_nome if alt_nome.strip() else f"Alternativa Sem Nome"
            with st.expander(f"**{nome_da_alternativa}**", expanded=False):
                for cri_id, cri_data in criterios.items():
                    nome_cri = cri_data.get('criterio', '')
                    titulo_campo = nome_cri if nome_cri else "Critério Sem Nome"
                    
                    # Lista de descrições possíveis do critério
                    opcoes = [d["descricao"] for d in cri_data.get("descricoes", [])]
                    
                    valor_atual = st.session_state.avaliacoes[alt_id].get(cri_id, None)
                    # Verifica segurança caso as opções tenham sido apagadas na aba anterior
                    if valor_atual not in opcoes:
                        valor_atual = None
                        
                    idx_atual = opcoes.index(valor_atual) if valor_atual is not None else None
                    
                    novo_valor = st.selectbox(
                        label=titulo_campo,
                        options=opcoes,
                        index=idx_atual,
                        placeholder="Selecione uma opção...",
                        key=f"aval_{alt_id}_{cri_id}"
                    )
                    
                    novas_avaliacoes[(alt_id, cri_id)] = novo_valor

        st.markdown("---")
        cols = st.columns([1, 4])
        with cols[0]:
            submitted = st.form_submit_button("💾 Salvar Avaliações", type="primary", use_container_width=True)
            
        if submitted:
            for (aid, cid), val in novas_avaliacoes.items():
                if val is not None:
                    st.session_state.avaliacoes[aid][cid] = val
            st.rerun()
