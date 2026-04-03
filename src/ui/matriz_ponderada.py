import streamlit as st
import pandas as pd
from src.core.data_repository import system_data
from src.services.ftopsis_service import FTopsisService

def render_matriz_ponderada():
    st.header("Matriz de Decisão Ponderada")
    st.markdown(
        "Esta aba apresenta a matriz de decisão já **normalizada e ponderada** "
        "com base nos pesos indicados para os critérios."
    )

    alternativas = system_data.get_alternativas()
    criterios = system_data.get_criterios()
    avaliacoes = system_data.get_avaliacoes()
    fuzzy_alternativas = system_data.get_numero_fuzzy_alternativas()
    pesos_criterios = system_data.get_pesos_criterios()
    fuzzy_pesos = system_data.get_numero_fuzzy_pesos()

    if not alternativas or not criterios:
        st.warning("É necessário cadastrar alternativas e critérios primeiro.")
        return

    if not avaliacoes:
        st.info("Nenhuma avaliação foi preenchida ainda. Vá para a aba de Avaliações.")
        return
        
    if not pesos_criterios:
        st.info("Nenhum peso definido ainda. Vá para a aba de Pesos.")
        return

    # Injeta a dependência no serviço
    servico_ftopsis = FTopsisService(
        criterios=criterios,
        alternativas=alternativas,
        avaliacoes=avaliacoes,
        fuzzy_alternativas=fuzzy_alternativas,
        pesos_criterios=pesos_criterios,
        fuzzy_pesos=fuzzy_pesos
    )

    # Passo 1: Matriz Bruta Fuzzy
    matriz_bruta = servico_ftopsis.build_decision_matrix()
    
    # Passo 2: Normalizar Matriz
    matriz_normalizada = servico_ftopsis.normalize_matrix(matriz_bruta)
    
    # Passo 3: Ponderar a Matriz Normalizada
    matriz_ponderada = servico_ftopsis.weight_matrix(matriz_normalizada)

    # Tabela 1: Resumo dos Pesos dos Critérios
    st.subheader("Pesos dos Critérios Aplicados")
    pesos_data = []
    for cri_id, cri_data in criterios.items():
        w_j = servico_ftopsis._get_fuzzy_weight_for_criterion(cri_id)
        pesos_data.append({
            "Critério": cri_data.get("criterio", cri_id),
            "Peso Fuzzy (l, m, u)": str(tuple(w_j)) if w_j else "Não Definido"
        })
    st.dataframe(pd.DataFrame(pesos_data), use_container_width=True, hide_index=True)

    # Tabela 2: Matriz Ponderada
    st.subheader("Valores Ponderados (V_ij)")
    matriz_data_rows = []

    for alt_id, alt_nome in alternativas.items():
        row = {"Alternativa": f"{alt_nome}"}
        
        for cri_id, cri_data in criterios.items():
            nome_cri = cri_data.get('criterio', cri_id)
            lmu_val = matriz_ponderada.get(alt_id, {}).get(cri_id)
            
            if lmu_val:
                # Formata a tupla fuzzy para 4 casas decimais para exibição limpa
                l, m, u = lmu_val
                row[nome_cri] = f"({l:.4f}, {m:.4f}, {u:.4f})"
            else:
                row[nome_cri] = "-"
                
        matriz_data_rows.append(row)

    df_matriz_pond = pd.DataFrame(matriz_data_rows)
    st.dataframe(df_matriz_pond, use_container_width=True, hide_index=True)

    with st.expander("Ver Matriz Normalizada (Sem os Pesos)"):
        st.markdown("Esta tabela apresenta os números normalizados antes da multiplicação pelos pesos.")
        matriz_norm_rows = []
        for alt_id, alt_nome in alternativas.items():
            row_norm = {"Alternativa": f"{alt_nome}"}
            for cri_id, cri_data in criterios.items():
                nome_cri = cri_data.get('criterio', cri_id)
                lmu_norm = matriz_normalizada.get(alt_id, {}).get(cri_id)
                if lmu_norm:
                    row_norm[nome_cri] = f"({lmu_norm[0]:.4f}, {lmu_norm[1]:.4f}, {lmu_norm[2]:.4f})"
                else:
                    row_norm[nome_cri] = "-"
            matriz_norm_rows.append(row_norm)
        
        st.dataframe(pd.DataFrame(matriz_norm_rows), use_container_width=True, hide_index=True)
