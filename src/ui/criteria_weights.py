import streamlit as st

def render_criteria_weights():
    st.header("Peso dos Critérios")
    st.markdown(
        "Nesta etapa, defina a importância de cada um dos critérios. "
        "A lista abaixo contém todos os critérios que você cadastrou."
    )
    
    criteria = st.session_state.get("criteria", {})
    fuzzy_weights = st.session_state.get("fuzzy_number_weights", {})
    
    if not criteria:
        st.warning("Nenhum critério cadastrado. Retorne à aba de Critérios.")
        return
        
    if not fuzzy_weights:
        st.warning("Não há termos linguísticos para pesos cadastrados. Retorne à aba de Números Fuzzy.")
        return

    # Garante a inicialização segura de pesos no session_state
    if "criteria_weights" not in st.session_state:
        st.session_state.criteria_weights = {}
        
    # Extrair apenas a descrição do dicionário de pesos para apresentar ao usuário
    weights_options = [dados["description"] for param, dados in fuzzy_weights.items()]
    
    # Prepara a lista de chaves de critérios para iterarmos aos pares
    cri_keys = list(criteria.keys())
    
    with st.form("form_pesos"):
        new_weights = {}
        
        # Itera de 2 em 2
        for i in range(0, len(cri_keys), 2):
            col1, col2 = st.columns(2)
            
            # Primeiro da dupla (sempre existirá dentro do loop normal)
            cri_id_1 = cri_keys[i]
            cri_data_1 = criteria[cri_id_1]
            nome_cri_1 = cri_data_1.get("criterion", 'Critério Sem Nome')
            
            with col1:
                st.subheader(nome_cri_1)
                valor_atual_1 = st.session_state.criteria_weights.get(cri_id_1, None)
                if valor_atual_1 not in weights_options:
                    valor_atual_1 = None
                    
                idx_atual_1 = weights_options.index(valor_atual_1) if valor_atual_1 is not None else None
                
                novo_peso_1 = st.selectbox(
                    label=f"Peso para o critério: {nome_cri_1}",
                    options=weights_options,
                    index=idx_atual_1,
                    placeholder="Selecione um nível de importância...",
                    key=f"peso_{cri_id_1}",
                    label_visibility="collapsed"
                )
                new_weights[cri_id_1] = novo_peso_1

            # Segundo da dupla (só se houver, caso quantidade ímpar)
            if i + 1 < len(cri_keys):
                cri_id_2 = cri_keys[i+1]
                cri_data_2 = criteria[cri_id_2]
                nome_cri_2 = cri_data_2.get("criterion", 'Critério Sem Nome')
                
                with col2:
                    st.subheader(nome_cri_2)
                    valor_atual_2 = st.session_state.criteria_weights.get(cri_id_2, None)
                    if valor_atual_2 not in weights_options:
                        valor_atual_2 = None
                        
                    idx_atual_2 = weights_options.index(valor_atual_2) if valor_atual_2 is not None else None
                    
                    novo_peso_2 = st.selectbox(
                        label=f"Peso para o critério: {nome_cri_2}",
                        options=weights_options,
                        index=idx_atual_2,
                        placeholder="Selecione um nível de importância...",
                        key=f"peso_{cri_id_2}",
                        label_visibility="collapsed"
                    )
                    new_weights[cri_id_2] = novo_peso_2
            
            st.markdown("---")

        cols = st.columns([1, 4])
        with cols[0]:
            submitted = st.form_submit_button("💾 Salvar Pesos", use_container_width=True)
            
        if submitted:
            for cid, val in new_weights.items():
                if val is not None:
                    st.session_state.criteria_weights[cid] = val
            st.rerun()
