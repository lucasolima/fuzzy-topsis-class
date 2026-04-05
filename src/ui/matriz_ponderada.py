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
    classes = system_data.get_classes()

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
        fuzzy_pesos=fuzzy_pesos,
        classes=classes
    )

    # Passo 1: Matrizes Brutas Fuzzy
    matriz_bruta = servico_ftopsis.build_decision_matrix()
    matriz_bruta_classes = servico_ftopsis.build_classes_matrix()
    
    # Valores ideais globais
    ideal_values = servico_ftopsis.get_global_ideal_values(matriz_bruta, matriz_bruta_classes)
    
    # Passo 2: Normalizar Matrizes (Alternativas e Classes)
    matriz_normalizada, _ = servico_ftopsis.normalize_matrix(matriz_bruta, ideal_values)
    matriz_normalizada_classes, _ = servico_ftopsis.normalize_matrix(matriz_bruta_classes, ideal_values)
    
    # Passo 3: Ponderar a Matriz Normalizada
    matriz_ponderada = servico_ftopsis.weight_matrix(matriz_normalizada)
    matriz_ponderada_classes = servico_ftopsis.weight_matrix(matriz_normalizada_classes)

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
    st.subheader("Valores Ponderados (V_ij) das Alternativas")
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

    # Tabela 3: Matriz Ponderada das Classes
    st.subheader("Valores Ponderados (V_ij) dos Perfis das Classes (Referências)")
    classes_data_rows = []
    
    for class_id, class_data in classes.items():
        row = {"Classe/Perfil": class_data.get('descricao', class_id)}
        for cri_id, cri_data in criterios.items():
            nome_cri = cri_data.get('criterio', cri_id)
            lmu_val = matriz_ponderada_classes.get(class_id, {}).get(cri_id)
            
            if lmu_val:
                l, m, u = lmu_val
                row[nome_cri] = f"({l:.4f}, {m:.4f}, {u:.4f})"
            else:
                row[nome_cri] = "-"
        classes_data_rows.append(row)
        
    df_classes_pond = pd.DataFrame(classes_data_rows)
    st.dataframe(df_classes_pond, use_container_width=True, hide_index=True)

    # Tabela 4: Agrupamentos Ideais das Referências
    st.subheader("Configuração da Solução Ideal das Referências")
    st.markdown("Agrupamento direto entre as linhas das referências da Matriz de Classes, conforme requisitado.")
    
    agrupamentos = servico_ftopsis.calculate_ideal_solution_from_classes(matriz_ponderada_classes)
    if agrupamentos:
        agrupamentos_rows = []
        for agr in agrupamentos:
            row = {"Combinação": agr["label"]}
            for cri_id, cri_data in criterios.items():
                nome_cri = cri_data.get('criterio', cri_id)
                val_a, val_b = agr["valores"].get(cri_id, (None, None))
                str_a = f"({val_a[0]:.4f}, {val_a[1]:.4f}, {val_a[2]:.4f})" if val_a else "-"
                str_b = f"({val_b[0]:.4f}, {val_b[1]:.4f}, {val_b[2]:.4f})" if val_b else "-"
                row[nome_cri] = f"{str_a}  |  {str_b}"
            agrupamentos_rows.append(row)
        
        df_agrupamentos = pd.DataFrame(agrupamentos_rows)
        st.dataframe(df_agrupamentos, use_container_width=True, hide_index=True)

    with st.expander("Ver Matriz Normalizada (Sem os Pesos) - Alternativas e Classes"):
        st.markdown("Esta tabela apresenta os números normalizados antes da multiplicação pelos pesos.")
        matriz_norm_rows = []
        for alt_id, alt_nome in alternativas.items():
            row_norm = {"Referência/Alternativa": f"[ALT] {alt_nome}"}
            for cri_id, cri_data in criterios.items():
                nome_cri = cri_data.get('criterio', cri_id)
                lmu_norm = matriz_normalizada.get(alt_id, {}).get(cri_id)
                if lmu_norm:
                    row_norm[nome_cri] = f"({lmu_norm[0]:.4f}, {lmu_norm[1]:.4f}, {lmu_norm[2]:.4f})"
                else:
                    row_norm[nome_cri] = "-"
            matriz_norm_rows.append(row_norm)
            
        for class_id, class_data in classes.items():
            row_norm = {"Referência/Alternativa": f"[CLA] {class_data.get('descricao', class_id)}"}
            for cri_id, cri_data in criterios.items():
                nome_cri = cri_data.get('criterio', cri_id)
                lmu_norm = matriz_normalizada_classes.get(class_id, {}).get(cri_id)
                if lmu_norm:
                    row_norm[nome_cri] = f"({lmu_norm[0]:.4f}, {lmu_norm[1]:.4f}, {lmu_norm[2]:.4f})"
                else:
                    row_norm[nome_cri] = "-"
            matriz_norm_rows.append(row_norm)
            
        st.dataframe(pd.DataFrame(matriz_norm_rows), use_container_width=True, hide_index=True)

    # Tabela 5: Distâncias D+ e D- (Alternativas vs Soluções Ideais das Classes)
    st.subheader("Cálculo das Distâncias (D+ e D-) Mapeadas")
    st.markdown("Mostra os valores sumariados resultantes do mapeamento de cada alternativa em contraste com cada agrupamento de referência ideal.")
    
    distancias_ideais = servico_ftopsis.calculate_distances_ideais(matriz_ponderada, agrupamentos)
    if distancias_ideais:
        distancias_rows = []
        for alt_id, info_dist in distancias_ideais.items():
            alt_nome = alternativas.get(alt_id, alt_id)
            for label_combinacao, vals in info_dist.items():
                distancias_rows.append({
                    "Alternativa": alt_nome,
                    "Referência (Classe Ideal)": label_combinacao,
                    "Distância Positiva (D+)": vals["D+"],
                    "Distância Negativa (D-)": vals["D-"]
                })
        
        df_distancias = pd.DataFrame(distancias_rows)
        st.dataframe(df_distancias, use_container_width=True, hide_index=True)

    # Tabela 6: Coeficiente de Proximidade (CCi)
    st.subheader("Coeficiente de Proximidade (CCi)")
    st.markdown("Exibe o Coeficiente de Proximidade das alternativas em relação a cada agrupamento de referência das classes.")
    
    if distancias_ideais:
        cci_ideais = servico_ftopsis.calculate_cci_ideais(distancias_ideais)
        cci_rows = []
        for alt_id, info_cci in cci_ideais.items():
            alt_nome = alternativas.get(alt_id, alt_id)
            row = {"Alternativa": alt_nome}
            for label_combinacao, cci_val in info_cci.items():
                row[label_combinacao] = f"{cci_val:.4f}"
            cci_rows.append(row)
            
        df_cci = pd.DataFrame(cci_rows)
        st.dataframe(df_cci, use_container_width=True, hide_index=True)
