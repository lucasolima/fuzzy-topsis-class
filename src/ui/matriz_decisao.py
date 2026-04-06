import streamlit as st
import pandas as pd
from src.core.data_repository import system_data

def render_matriz_decisao():
    st.header("Matriz de Decisão")
    st.markdown(
        "teste"
    )
    
    alternativas = system_data.get_alternativas()
    criterios = system_data.get_criterios()
    avaliacoes = system_data.get_avaliacoes()
    
    if not alternativas or not criterios:
        st.warning("É necessário cadastrar alternativas e critérios primeiro.")
        return
        
    if not avaliacoes:
        st.info("Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações.")
    else:
        # Onde iremos armazenar os dados para plotar no Pandas e Streamlit
        matriz_data = []

        # Iterar sobre todas as alternativas preenchidas
        for alt_id, alt_nome in alternativas.items():
            # Captura as respostas daquela alternativa, se houver
            respostas_alt = avaliacoes.get(alt_id, {})
            
            # Vamos inicializar a linha do DataFrame com o ID e/ou nome da alternativa
            row = {"Alternativa": f"{alt_nome}"}
            
            for cri_id, cri_data in criterios.items():
                nome_cri = cri_data.get('criterio', cri_id)
                desc_selecionada = respostas_alt.get(cri_id)
                
                # Buscar no critério qual é o termo_alternativa vinculado a esta descrição
                termo_encontrado = None
                if desc_selecionada:
                    # Procura a descrição dentro das descrições do critério
                    for d in cri_data.get("descricoes", []):
                        if d["descricao"] == desc_selecionada:
                            termo_encontrado = d.get("termo_alternativa")
                            break
                
                # Se não encontrou o termo (ou o usuário não avaliou aquele critério ainda)
                if not termo_encontrado:
                    termo_encontrado = "-"
                    
                row[nome_cri] = termo_encontrado
                
            matriz_data.append(row)
            
        df_matriz = pd.DataFrame(matriz_data)
        
        # Exibir a tabela
        st.dataframe(
            df_matriz,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.header("teste")
    st.markdown(
       "teste"
    )
    
    pesos_salvos = system_data.get_pesos_criterios()
    pesos_fuzzy = system_data.get_numero_fuzzy_pesos()
    
    if not pesos_salvos:
        st.info("Nenhum peso foi definido ainda. Vá para a aba de Pesos.")
        return
        
    row_pesos = {}
    
    for cri_id, cri_data in criterios.items():
        nome_cri = cri_data.get('criterio', cri_id)
        desc_selecionada = pesos_salvos.get(cri_id)
        
        termo_peso = None
        if desc_selecionada:
            # Encontrar no dicionario de pesos fuzzy qual é a chave (termo) dessa descrição
            for termo_key, p_data in pesos_fuzzy.items():
                if p_data["descricao"] == desc_selecionada:
                    termo_peso = termo_key
                    break
                    
        if not termo_peso:
            termo_peso = "-"
            
        row_pesos[nome_cri] = termo_peso

    df_pesos = pd.DataFrame([row_pesos])
    
    st.dataframe(
        df_pesos,
        use_container_width=True,
        hide_index=True
    )
