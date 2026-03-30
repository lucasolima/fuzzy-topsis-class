import streamlit as st
from src.core.criterios_state import (
    add_criterio, update_criterio_field, delete_criterio,
    add_criterio_descricao, update_criterio_descricao, delete_criterio_descricao,
    update_criterio_classe, sync_classes_in_criterios
)

def render_criterios():
    st.header("Configuração: Critérios")
    st.markdown("Cadastre os critérios (Benefício ou Custo), as descrições de valoração e os termos linguísticos mínimos aceitos por classe em relação a este critério.")
    
    # Sincroniza caso classes tenham sido adicionadas/removidas ou renomeadas na primeira aba
    sync_classes_in_criterios()

    termos_alt = list(st.session_state.get("numero_fuzzy_alternativas", {}).keys())
    termos_peso = list(st.session_state.get("numero_fuzzy_pesos", {}).keys())
    
    opcoes_alt = termos_alt if termos_alt else ["(Vazio)"]
    opcoes_peso = termos_peso if termos_peso else ["(Vazio)"]

    criterios = st.session_state.get("criterios", {})
    
    if not criterios:
        st.info("Nenhum critério cadastrado. Clique no botão abaixo para adicionar.")
    else:
        for cri_id, cri_data in criterios.items():
            nome_to_show = cri_data['criterio'] if cri_data['criterio'].strip() else "Novo Critério"
            
            with st.expander(f"{cri_id} - {nome_to_show}", expanded=False):
                # Campos principais do critério
                col_nome, col_tipo, col_del = st.columns([6, 3, 1])
                
                with col_nome:
                    new_nome = st.text_input(
                        "Nome do Critério", 
                        value=cri_data["criterio"], 
                        key=f"nome_{cri_id}"
                    )
                    if new_nome != cri_data["criterio"]:
                        update_criterio_field(cri_id, "criterio", new_nome)
                        
                with col_tipo:
                    tipos = ["benefício", "custo"]
                    idx_tipo = tipos.index(cri_data["tipo"]) if cri_data["tipo"] in tipos else 0
                    new_tipo = st.selectbox(
                        "Tipo", 
                        options=tipos, 
                        index=idx_tipo, 
                        key=f"tipo_{cri_id}"
                    )
                    if new_tipo != cri_data["tipo"]:
                        update_criterio_field(cri_id, "tipo", new_tipo)
                        
                with col_del:
                    st.write("") 
                    st.write("") 
                    if st.button("❌", key=f"del_cri_{cri_id}", help=f"Excluir {cri_id}", use_container_width=True):
                        delete_criterio(cri_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Descrições
                st.markdown("#### Descrições de Valoração")
                
                # Headers das descrições
                if len(cri_data["descricoes"]) > 0:
                    hd1, hd2, hd3, hd_del = st.columns([5, 2, 2, 1])
                    with hd1: st.write("**Descrição**")
                    with hd2: st.write("**Termo Alternativa**")
                    with hd3: st.write("**Termo Peso**")

                for i, desc in enumerate(cri_data["descricoes"]):
                    cd1, cd2, cd3, cd_del = st.columns([5, 2, 2, 1])
                    with cd1:
                        n_desc = st.text_input("Descrição", value=desc["descricao"], key=f"d_desc_{cri_id}_{i}", label_visibility="collapsed")
                        if n_desc != desc["descricao"]:
                            update_criterio_descricao(cri_id, i, "descricao", n_desc)
                            
                    with cd2:
                        t_alt_val = desc["termo_alternativa"]
                        if t_alt_val not in opcoes_alt and termos_alt:
                            t_alt_val = opcoes_alt[0]
                        idx_alt = opcoes_alt.index(t_alt_val) if t_alt_val in opcoes_alt else 0
                        
                        n_t_alt = st.selectbox("Termo Alt", options=opcoes_alt, index=idx_alt, key=f"d_talt_{cri_id}_{i}", label_visibility="collapsed")
                        if n_t_alt != desc["termo_alternativa"] and termos_alt:
                            update_criterio_descricao(cri_id, i, "termo_alternativa", n_t_alt)
                            
                    with cd3:
                        t_peso_val = desc["termo_peso"]
                        if t_peso_val not in opcoes_peso and termos_peso:
                            t_peso_val = opcoes_peso[0]
                        idx_peso = opcoes_peso.index(t_peso_val) if t_peso_val in opcoes_peso else 0
                        
                        n_t_peso = st.selectbox("Termo Peso", options=opcoes_peso, index=idx_peso, key=f"d_tpeso_{cri_id}_{i}", label_visibility="collapsed")
                        if n_t_peso != desc["termo_peso"] and termos_peso:
                            update_criterio_descricao(cri_id, i, "termo_peso", n_t_peso)
                            
                    with cd_del:
                        if st.button("🗑️", key=f"del_d_{cri_id}_{i}"):
                            delete_criterio_descricao(cri_id, i)
                            st.rerun()
                
                col_btn_add_d, _ = st.columns([3, 7])
                with col_btn_add_d:
                    if st.button("➕ Adicionar Descrição", key=f"add_d_{cri_id}"):
                        add_criterio_descricao(cri_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Classes
                st.markdown("#### Classes (Limiares do Critério)")
                if not cri_data["classes"]:
                    st.info("Não há classes cadastradas na primeira aba.")
                else:
                    ch1, ch2, _ = st.columns([5, 3, 2])
                    with ch1: st.write("**Classe**")
                    with ch2: st.write("**Termo Mínimo (Alternativa)**")
                    
                    for cid, cdata in cri_data["classes"].items():
                        cc1, cc2, _ = st.columns([5, 3, 2])
                        with cc1:
                            st.text_input("Classe", value=cdata["descricao"], disabled=True, key=f"c_desc_{cri_id}_{cid}", label_visibility="collapsed")
                        with cc2:
                            current_c_alt = cdata["termo_alternativa"]
                            if current_c_alt not in opcoes_alt and termos_alt:
                                current_c_alt = opcoes_alt[0]
                            idx_calt = opcoes_alt.index(current_c_alt) if current_c_alt in opcoes_alt else 0
                            
                            n_c_alt = st.selectbox("Termo Mínimo", options=opcoes_alt, index=idx_calt, key=f"c_talt_{cri_id}_{cid}", label_visibility="collapsed")
                            if n_c_alt != cdata["termo_alternativa"] and termos_alt:
                                update_criterio_classe(cri_id, cid, "termo_alternativa", n_c_alt)

    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Adicionar Critério", type="primary", use_container_width=True):
            add_criterio()
            st.rerun()
