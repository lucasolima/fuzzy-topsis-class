"""
Serviço responsável pela execução do algoritmo F-TOPSIS Class
seguindo os princípios de Clean Code, SOLID e Extreme Programming (Testabilidade, SRP).
"""
import copy

class FTopsisService:
    def __init__(
        self,
        criteria: dict,
        alternatives: dict,
        evaluations: dict,
        fuzzy_alternatives: dict,
        criteria_weights: dict = None,
        fuzzy_weights: dict = None,
        classes: dict = None
    ):
        self.criteria = criteria
        self.alternatives = alternatives
        self.evaluations = evaluations
        self.fuzzy_alternatives = fuzzy_alternatives
        self.criteria_weights = criteria_weights or {}
        self.fuzzy_weights = fuzzy_weights or {}
        self.classes = classes or {}

    def _get_fuzzy_value_for_evaluation(self, crit_id: str, selected_description: str) -> list[float]:
        """
        Extrai o número fuzzy (l, m, u) da avaliação selecionada de um critério.
        Retorna uma lista com os três pontos do número fuzzy triangular, ou None.
        """
        if not selected_description:
            return None
            
        criterion_data = self.criteria.get(crit_id, {})
        for index in criterion_data.get("descriptions", []):
            if index.get("description") == selected_description:
                term = index.get("alternative_term")
                if term and term in self.fuzzy_alternatives:
                    # Retorna [l, m, u]
                    return list(self.fuzzy_alternatives[term].get("lmu"))
        return None

    def build_decision_matrix(self) -> dict:
        """
        Constrói a matriz de decisão bruta (Alternativas x Critérios) com os valores fuzzy.
        Retorna:
            Dict com formato: { alt_id: { crit_id: [l, m, u] } }
        """
        matrix = {}
        for alt_id in self.alternatives.keys():
            matrix[alt_id] = {}
            answers_alt = self.evaluations.get(alt_id, {})
            
            for crit_id in self.criteria.keys():
                selected_desc = answers_alt.get(crit_id)
                fuzzy_val = self._get_fuzzy_value_for_evaluation(crit_id, selected_desc)
                
                # Assume-se que a matrix pode ter "None" se o usuário não finalizou a avaliação.
                matrix[alt_id][crit_id] = fuzzy_val
                
        return matrix

    def build_classes_matrix(self) -> dict:
        """
        Constrói a matriz de decisão bruta (Classes x Critérios) com os valores fuzzy.
        Retorna:
            Dict com formato: { class_id: { crit_id: [l, m, u] } }
        """
        matrix = {}
        for class_id in self.classes.keys():
            matrix[class_id] = {}
            for crit_id, crit_data in self.criteria.items():
                # Busca o term linguístico da classe para esse critério
                term = crit_data.get("classes", {}).get(class_id, {}).get("alternative_term")
                fuzzy_val = None
                if term and term in self.fuzzy_alternatives:
                    fuzzy_val = list(self.fuzzy_alternatives[term].get("lmu"))
                matrix[class_id][crit_id] = fuzzy_val
        return matrix

    def normalize_matrix(self, matrix: dict, ideal_values: dict = None) -> (dict, dict): # type: ignore
        """
        Aplica a normalização F-TOPSIS à matriz bruta extraída.
        Leva em consideração se o critério é de "benefício" ou "custo".
        Se ideal_values não for fornecido, calcula a partir da própria matrix.
        Retorna: (normalized_matrix, ideal_values_calculados)
        """
        if ideal_values is None:
            # 1. Encontrar o valor ideal de cada critério U*_j (benefício) e L-_j (custo)
            ideal_values = {}
            for crit_id, crit_data in self.criteria.items():
                tipo = crit_data.get("type", "benefício").lower()
                
                # Coleta os valores fuzzy preenchidos para este critério (apenas os válidos)
                criterion_values = []
                for entity_id in matrix:
                    val = matrix[entity_id].get(crit_id)
                    if val is not None:
                        criterion_values.append(val)
                
                if not criterion_values:
                    continue
                    
                if tipo == "benefício":
                    ideal_values[crit_id] = max(v[2] for v in criterion_values)
                else: # custo
                    ideal_values[crit_id] = min(v[0] for v in criterion_values)

        # 2. Computar a divisão criando a Nova Matriz R_ij
        normalized_matrix = copy.deepcopy(matrix)

        for ent_id, scores in matrix.items():
            for crit_id, lmu_val in scores.items():
                if not lmu_val:
                    continue # Célula vazia / não avaliada
                
                tipo = self.criteria[crit_id].get("type", "benefício").lower()
                ideal_val = ideal_values.get(crit_id)
                
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
                    
                normalized_matrix[ent_id][crit_id] = r_ij
                
        return normalized_matrix, ideal_values

    def get_global_ideal_values(self, matrix_alts: dict, matrix_classes: dict) -> dict:
        """
        Calcula os valores ideais (U*_j e L-_j) combinando alternatives e classes
        para garantir que todas sejam agrupadas sob o mesmo referencial.
        """
        ideal_values = {}
        for crit_id, crit_data in self.criteria.items():
            tipo = crit_data.get("type", "benefício").lower()
            
            criterion_values = []
            # Coleta valores das alternatives
            for alt_id in matrix_alts:
                val = matrix_alts[alt_id].get(crit_id)
                if val is not None:
                    criterion_values.append(val)
            
            # Coleta valores das classes
            for class_id in matrix_classes:
                val = matrix_classes[class_id].get(crit_id)
                if val is not None:
                    criterion_values.append(val)
            
            if not criterion_values:
                continue
                
            if tipo == "benefício":
                ideal_values[crit_id] = max(v[2] for v in criterion_values)
            else: # custo
                ideal_values[crit_id] = min(v[0] for v in criterion_values)
                
        return ideal_values

    def _get_fuzzy_weight_for_criterion(self, crit_id: str) -> list[float]:
        """
        Extrai o número fuzzy (l, m, u) do peso atribuído a um critério específico.
        """
        selected_desc = self.criteria_weights.get(crit_id)
        if not selected_desc:
            return None
            
        for term_key, w_data in self.fuzzy_weights.items():
            if w_data.get("description") == selected_desc:
                return list(w_data.get("lmu"))
        
        return None

    def weight_matrix(self, normalized_matrix: dict) -> dict:
        """
        Aplica os pesos na matriz já normalizada (V_ij = r_ij * W_j).
        Multiplica os componentes fuzzy: l*l_w, m*m_w, u*u_w.
        """
        weighted_matrix = copy.deepcopy(normalized_matrix)
        
        for alt_id, scores in normalized_matrix.items():
            for crit_id, r_ij in scores.items():
                if not r_ij:
                    continue
                    
                w_j = self._get_fuzzy_weight_for_criterion(crit_id)
                if not w_j:
                    weighted_matrix[alt_id][crit_id] = None
                    continue
                
                # F-TOPSIS Ponderação
                # Multiplicação term by term pois W_j = (w_l, w_m, w_u) e R_ij = (r_l, r_m, r_u)
                v_ij = [
                    round(r_ij[0] * w_j[0], 4),
                    round(r_ij[1] * w_j[1], 4),
                    round(r_ij[2] * w_j[2], 4)
                ]
                
                weighted_matrix[alt_id][crit_id] = v_ij
                
        return weighted_matrix

    def calculate_ideal_solution_from_classes(self, weighted_classes_matrix: dict) -> list:
        """
        Recebe a matriz ponderada das classes e retorna os agrupamentos:
        1: Primeira linha com a última
        2: Segunda linha com a última
        3: Última linha com a primeira
        """
        classes_keys = list(weighted_classes_matrix.keys())
        if not classes_keys:
            return []
            
        first = classes_keys[0]
        # Pega a segunda se existir, senão repete a primeira
        second = classes_keys[1] if len(classes_keys) > 1 else first
        last = classes_keys[-1]
        
        name_first = self.classes.get(first, {}).get("description", first)
        name_second = self.classes.get(second, {}).get("description", second)
        name_last = self.classes.get(last, {}).get("description", last)
        
        combinations = [
            (name_first, first, last),
            (name_second, second, last),
            (name_last, last, first)
        ]
        
        results = []
        for label, a_id, b_id in combinations:
            comb_line = {}
            for crit_id in self.criteria.keys():
                val_a = weighted_classes_matrix.get(a_id, {}).get(crit_id)
                val_b = weighted_classes_matrix.get(b_id, {}).get(crit_id)
                comb_line[crit_id] = (val_a, val_b)
                
            results.append({
                "label": label,
                "id_1": a_id,
                "id_2": b_id,
                "valores": comb_line
            })
            
        return results

    def calculate_distances_ideais(self, weighted_matrix: dict, ideal_solutions: list) -> dict:
        import math
        distances_results = {}
        for alt_id, scores in weighted_matrix.items():
            distances_results[alt_id] = {}
            for ideal_sol in ideal_solutions:
                label = ideal_sol["label"]
                ideal_values = ideal_sol["valores"]
                
                dp_sum = 0.0
                dn_sum = 0.0
                criteria_details = {}
                
                for crit_id, v_ij in scores.items():
                    if not v_ij:
                        continue
                        
                    val_a, val_b = ideal_values.get(crit_id, (None, None))
                    if not val_a or not val_b:
                        continue
                        
                    l_crit, m_crit, u_crit = v_ij
                    l_sol1, m_sol1, u_sol1 = val_a
                    l_sol2, m_sol2, u_sol2 = val_b
                    
                    dp = math.sqrt(((l_crit - l_sol1)**2 + (m_crit - m_sol1)**2 + (u_crit - u_sol1)**2) / 3.0)
                    dn = math.sqrt(((l_crit - l_sol2)**2 + (m_crit - m_sol2)**2 + (u_crit - u_sol2)**2) / 3.0)
                    
                    criteria_details[crit_id] = {
                        "d+": round(dp, 4),
                        "d-": round(dn, 4)
                    }
                    dp_sum += dp
                    dn_sum += dn
                    
                distances_results[alt_id][label] = {
                    "D+": round(dp_sum, 4),
                    "D-": round(dn_sum, 4),
                    "criteria": criteria_details
                }
                
        return distances_results

    def calculate_cci_ideais(self, distancias_ideais: dict) -> dict:
        """
        Calcula o CCi = D- / (D+ + D-) para cada alternativa em relação a cada agrupamento de referência.
        Retorna um dicionário: {alt_id: {label: cci_value}}
        """
        cci_results = {}
        for alt_id, info_dist in distancias_ideais.items():
            cci_results[alt_id] = {}
            for label, vals in info_dist.items():
                dp = vals["D+"]
                dn = vals["D-"]
                sum = dp + dn
                if sum > 0:
                    cci = round(dn / sum, 4)
                else:
                    cci = 0.0
                cci_results[alt_id][label] = cci
        return cci_results
