import streamlit as st

def render_pesos_criterios():
    st.header("Pesos dos Critérios")
    st.markdown(
        "Nesta etapa, defina a importância de cada um dos critérios. "
        "A lista abaixo contém todos os critérios que você cadastrou."
    )
    
    criterios = st.session_state.get("criterios", {})
    pesos_fuzzy = st.session_state.get("numero_fuzzy_pesos", {})
    
    if not criterios:
        st.warning("Nenhum critério cadastrado. Retorne à aba de Critérios.")
        return
        
    if not pesos_fuzzy:
        st.warning("Não há termos linguísticos para pesos cadastrados. Retorne à aba de Números Fuzzy.")
        return

    # Garante a inicialização segura de pesos no session_state
    if "pesos_criterios" not in st.session_state:
        st.session_state.pesos_criterios = {}
        
    # Extrair apenas a descrição do dicionário de pesos para apresentar ao usuário
    opcoes_pesos = [dados["descricao"] for param, dados in pesos_fuzzy.items()]
    
    # Prepara a lista de chaves de critérios para iterarmos aos pares
    cri_keys = list(criterios.keys())
    
    with st.form("form_pesos"):
        novos_pesos = {}
        
        # Itera de 2 em 2
        for i in range(0, len(cri_keys), 2):
            col1, col2 = st.columns(2)
            
            # Primeiro da dupla (sempre existirá dentro do loop normal)
            cri_id_1 = cri_keys[i]
            cri_data_1 = criterios[cri_id_1]
            nome_cri_1 = cri_data_1.get('criterio', 'Critério Sem Nome')
            
            with col1:
                st.subheader(nome_cri_1)
                valor_atual_1 = st.session_state.pesos_criterios.get(cri_id_1, None)
                if valor_atual_1 not in opcoes_pesos:
                    valor_atual_1 = None
                    
                idx_atual_1 = opcoes_pesos.index(valor_atual_1) if valor_atual_1 is not None else None
                
                novo_peso_1 = st.selectbox(
                    label=f"Peso para o critério: {nome_cri_1}",
                    options=opcoes_pesos,
                    index=idx_atual_1,
                    placeholder="Selecione um nível de importância...",
                    key=f"peso_{cri_id_1}",
                    label_visibility="collapsed"
                )
                novos_pesos[cri_id_1] = novo_peso_1

            # Segundo da dupla (só se houver, caso quantidade ímpar)
            if i + 1 < len(cri_keys):
                cri_id_2 = cri_keys[i+1]
                cri_data_2 = criterios[cri_id_2]
                nome_cri_2 = cri_data_2.get('criterio', 'Critério Sem Nome')
                
                with col2:
                    st.subheader(nome_cri_2)
                    valor_atual_2 = st.session_state.pesos_criterios.get(cri_id_2, None)
                    if valor_atual_2 not in opcoes_pesos:
                        valor_atual_2 = None
                        
                    idx_atual_2 = opcoes_pesos.index(valor_atual_2) if valor_atual_2 is not None else None
                    
                    novo_peso_2 = st.selectbox(
                        label=f"Peso para o critério: {nome_cri_2}",
                        options=opcoes_pesos,
                        index=idx_atual_2,
                        placeholder="Selecione um nível de importância...",
                        key=f"peso_{cri_id_2}",
                        label_visibility="collapsed"
                    )
                    novos_pesos[cri_id_2] = novo_peso_2
            
            st.markdown("---")

        cols = st.columns([1, 4])
        with cols[0]:
            submitted = st.form_submit_button("💾 Salvar Pesos", type="primary", use_container_width=True)
            
        if submitted:
            for cid, val in novos_pesos.items():
                if val is not None:
                    st.session_state.pesos_criterios[cid] = val
            st.rerun()
