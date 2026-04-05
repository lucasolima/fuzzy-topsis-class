"""
Serviço responsável pela execução do algoritmo F-TOPSIS Class
seguindo os princípios de Clean Code, SOLID e Extreme Programming (Testabilidade, SRP).
"""
import copy

class FTopsisService:
    def __init__(
        self,
        criterios: dict,
        alternativas: dict,
        avaliacoes: dict,
        fuzzy_alternativas: dict,
        pesos_criterios: dict = None,
        fuzzy_pesos: dict = None,
        classes: dict = None
    ):
        self.criterios = criterios
        self.alternativas = alternativas
        self.avaliacoes = avaliacoes
        self.fuzzy_alternativas = fuzzy_alternativas
        self.pesos_criterios = pesos_criterios or {}
        self.fuzzy_pesos = fuzzy_pesos or {}
        self.classes = classes or {}

    def _get_fuzzy_value_for_evaluation(self, cri_id: str, descricao_selecionada: str) -> list[float]:
        """
        Extrai o número fuzzy (l, m, u) da avaliação selecionada de um critério.
        Retorna uma lista com os três pontos do número fuzzy triangular, ou None.
        """
        if not descricao_selecionada:
            return None
            
        criterio_data = self.criterios.get(cri_id, {})
        for index in criterio_data.get("descricoes", []):
            if index.get("descricao") == descricao_selecionada:
                termo = index.get("termo_alternativa")
                if termo and termo in self.fuzzy_alternativas:
                    # Retorna [l, m, u]
                    return list(self.fuzzy_alternativas[termo].get("lmu"))
        return None

    def build_decision_matrix(self) -> dict:
        """
        Constrói a matriz de decisão bruta (Alternativas x Critérios) com os valores fuzzy.
        Retorna:
            Dict com formato: { alt_id: { cri_id: [l, m, u] } }
        """
        matrix = {}
        for alt_id in self.alternativas.keys():
            matrix[alt_id] = {}
            respostas_alt = self.avaliacoes.get(alt_id, {})
            
            for cri_id in self.criterios.keys():
                desc_selecionada = respostas_alt.get(cri_id)
                fuzzy_val = self._get_fuzzy_value_for_evaluation(cri_id, desc_selecionada)
                
                # Assume-se que a matrix pode ter "None" se o usuário não finalizou a avaliação.
                matrix[alt_id][cri_id] = fuzzy_val
                
        return matrix

    def build_classes_matrix(self) -> dict:
        """
        Constrói a matriz de decisão bruta (Classes x Critérios) com os valores fuzzy.
        Retorna:
            Dict com formato: { class_id: { cri_id: [l, m, u] } }
        """
        matrix = {}
        for class_id in self.classes.keys():
            matrix[class_id] = {}
            for cri_id, cri_data in self.criterios.items():
                # Busca o termo linguístico da classe para esse critério
                termo = cri_data.get("classes", {}).get(class_id, {}).get("termo_alternativa")
                fuzzy_val = None
                if termo and termo in self.fuzzy_alternativas:
                    fuzzy_val = list(self.fuzzy_alternativas[termo].get("lmu"))
                matrix[class_id][cri_id] = fuzzy_val
        return matrix

    def normalize_matrix(self, matrix: dict, ideal_values: dict = None) -> (dict, dict): # type: ignore
        """
        Aplica a normalização F-TOPSIS à matriz bruta extraída.
        Leva em consideração se o critério é de "benefício" ou "custo".
        Se ideal_values não for fornecido, calcula a partir da própria matrix.
        Retorna: (matriz_normalizada, ideal_values_calculados)
        """
        if ideal_values is None:
            # 1. Encontrar o valor ideal de cada critério U*_j (benefício) e L-_j (custo)
            ideal_values = {}
            for cri_id, cri_data in self.criterios.items():
                tipo = cri_data.get("tipo", "benefício").lower()
                
                # Coleta os valores fuzzy preenchidos para este critério (apenas os válidos)
                valores_criterio = []
                for entity_id in matrix:
                    val = matrix[entity_id].get(cri_id)
                    if val is not None:
                        valores_criterio.append(val)
                
                if not valores_criterio:
                    continue
                    
                if tipo == "benefício":
                    ideal_values[cri_id] = max(v[2] for v in valores_criterio)
                else: # custo
                    ideal_values[cri_id] = min(v[0] for v in valores_criterio)

        # 2. Computar a divisão criando a Nova Matriz R_ij
        normalized_matrix = copy.deepcopy(matrix)

        for ent_id, scores in matrix.items():
            for cri_id, lmu_val in scores.items():
                if not lmu_val:
                    continue # Célula vazia / não avaliada
                
                tipo = self.criterios[cri_id].get("tipo", "benefício").lower()
                ideal_val = ideal_values.get(cri_id)
                
                if not ideal_val:
                    continue
                
                l, m, u = lmu_val
                
                if tipo == "benefício":
                    # Fórmula Benefício: R_ij = (l/u*, m/u*, u/u*)
                    r_ij = [
                        round(l / ideal_val, 4),
                        round(m / ideal_val, 4),
                        round(u / ideal_val, 4)
                    ]
                else: 
                    # Fórmula Custo: R_ij = (l-/u, l-/m, l-/l)
                    r_ij = [
                        round(ideal_val / u, 4) if u != 0 else 0.0,
                        round(ideal_val / m, 4) if m != 0 else 0.0,
                        round(ideal_val / l, 4) if l != 0 else 0.0
                    ]
                    
                normalized_matrix[ent_id][cri_id] = r_ij
                
        return normalized_matrix, ideal_values

    def get_global_ideal_values(self, matrix_alts: dict, matrix_classes: dict) -> dict:
        """
        Calcula os valores ideais (U*_j e L-_j) combinando alternativas e classes
        para garantir que todas sejam agrupadas sob o mesmo referencial.
        """
        ideal_values = {}
        for cri_id, cri_data in self.criterios.items():
            tipo = cri_data.get("tipo", "benefício").lower()
            
            valores_criterio = []
            # Coleta valores das alternativas
            for alt_id in matrix_alts:
                val = matrix_alts[alt_id].get(cri_id)
                if val is not None:
                    valores_criterio.append(val)
            
            # Coleta valores das classes
            for class_id in matrix_classes:
                val = matrix_classes[class_id].get(cri_id)
                if val is not None:
                    valores_criterio.append(val)
            
            if not valores_criterio:
                continue
                
            if tipo == "benefício":
                ideal_values[cri_id] = max(v[2] for v in valores_criterio)
            else: # custo
                ideal_values[cri_id] = min(v[0] for v in valores_criterio)
                
        return ideal_values

    def _get_fuzzy_weight_for_criterion(self, cri_id: str) -> list[float]:
        """
        Extrai o número fuzzy (l, m, u) do peso atribuído a um critério específico.
        """
        desc_selecionada = self.pesos_criterios.get(cri_id)
        if not desc_selecionada:
            return None
            
        for termo_key, p_data in self.fuzzy_pesos.items():
            if p_data.get("descricao") == desc_selecionada:
                return list(p_data.get("lmu"))
        
        return None

    def weight_matrix(self, normalized_matrix: dict) -> dict:
        """
        Aplica os pesos na matriz já normalizada (V_ij = r_ij * W_j).
        Multiplica os componentes fuzzy: l*l_w, m*m_w, u*u_w.
        """
        weighted_matrix = copy.deepcopy(normalized_matrix)
        
        for alt_id, scores in normalized_matrix.items():
            for cri_id, r_ij in scores.items():
                if not r_ij:
                    continue
                    
                w_j = self._get_fuzzy_weight_for_criterion(cri_id)
                if not w_j:
                    weighted_matrix[alt_id][cri_id] = None
                    continue
                
                # F-TOPSIS Ponderação
                # Multiplicação term by term pois W_j = (w_l, w_m, w_u) e R_ij = (r_l, r_m, r_u)
                v_ij = [
                    round(r_ij[0] * w_j[0], 4),
                    round(r_ij[1] * w_j[1], 4),
                    round(r_ij[2] * w_j[2], 4)
                ]
                
                weighted_matrix[alt_id][cri_id] = v_ij
                
        return weighted_matrix

    def calculate_ideal_solution_from_classes(self, matriz_classes_ponderada: dict) -> list:
        """
        Recebe a matriz ponderada das classes e retorna os agrupamentos:
        1: Primeira linha com a última
        2: Segunda linha com a última
        3: Última linha com a primeira
        """
        classes_keys = list(matriz_classes_ponderada.keys())
        if not classes_keys:
            return []
            
        primeira = classes_keys[0]
        # Pega a segunda se existir, senão repete a primeira
        segunda = classes_keys[1] if len(classes_keys) > 1 else primeira
        ultima = classes_keys[-1]
        
        nome_primeira = self.classes.get(primeira, {}).get("descricao", primeira)
        nome_segunda = self.classes.get(segunda, {}).get("descricao", segunda)
        nome_ultima = self.classes.get(ultima, {}).get("descricao", ultima)
        
        combinacoes = [
            (nome_primeira, primeira, ultima),
            (nome_segunda, segunda, ultima),
            (nome_ultima, ultima, primeira)
        ]
        
        resultados = []
        for label, a_id, b_id in combinacoes:
            linha_comb = {}
            for cri_id in self.criterios.keys():
                val_a = matriz_classes_ponderada.get(a_id, {}).get(cri_id)
                val_b = matriz_classes_ponderada.get(b_id, {}).get(cri_id)
                linha_comb[cri_id] = (val_a, val_b)
                
            resultados.append({
                "label": label,
                "id_1": a_id,
                "id_2": b_id,
                "valores": linha_comb
            })
            
        return resultados

    def calculate_distances_ideais(self, matriz_ponderada: dict, solucoes_ideais: list) -> dict:
        import math
        resultados_distancias = {}
        for alt_id, scores in matriz_ponderada.items():
            resultados_distancias[alt_id] = {}
            for sol_ideal in solucoes_ideais:
                label = sol_ideal["label"]
                valores_ideais = sol_ideal["valores"]
                
                soma_dp = 0.0
                soma_dn = 0.0
                detalhes_criterios = {}
                
                for cri_id, v_ij in scores.items():
                    if not v_ij:
                        continue
                        
                    val_a, val_b = valores_ideais.get(cri_id, (None, None))
                    if not val_a or not val_b:
                        continue
                        
                    l_crit, m_crit, u_crit = v_ij
                    l_sol1, m_sol1, u_sol1 = val_a
                    l_sol2, m_sol2, u_sol2 = val_b
                    
                    dp = math.sqrt(((l_crit - l_sol1)**2 + (m_crit - m_sol1)**2 + (u_crit - u_sol1)**2) / 3.0)
                    dn = math.sqrt(((l_crit - l_sol2)**2 + (m_crit - m_sol2)**2 + (u_crit - u_sol2)**2) / 3.0)
                    
                    detalhes_criterios[cri_id] = {
                        "d+": round(dp, 4),
                        "d-": round(dn, 4)
                    }
                    soma_dp += dp
                    soma_dn += dn
                    
                resultados_distancias[alt_id][label] = {
                    "D+": round(soma_dp, 4),
                    "D-": round(soma_dn, 4),
                    "criterios": detalhes_criterios
                }
                
        return resultados_distancias

    def calculate_cci_ideais(self, distancias_ideais: dict) -> dict:
        """
        Calcula o CCi = D- / (D+ + D-) para cada alternativa em relação a cada agrupamento de referência.
        Retorna um dicionário: {alt_id: {label: cci_value}}
        """
        cci_resultados = {}
        for alt_id, info_dist in distancias_ideais.items():
            cci_resultados[alt_id] = {}
            for label, vals in info_dist.items():
                dp = vals["D+"]
                dn = vals["D-"]
                soma = dp + dn
                if soma > 0:
                    cci = round(dn / soma, 4)
                else:
                    cci = 0.0
                cci_resultados[alt_id][label] = cci
        return cci_resultados
