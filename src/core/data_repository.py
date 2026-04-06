class CoreData:
    """
    Classe singleton (ou estática) para concentrar o acesso aos dados em tempo de execução
    sem depender diretamente de componentes de interface como st.session_state dentro da lógica de negócio.
    """
    def __init__(self):
        self.alternatives = {}
        self.fuzzy_number_alternatives = {}
        self.fuzzy_number_weights = {}
        self.classes = {}
        self.criteria = {}
        self.evaluations = {}
        self.criteria_weights = {}

    def update_from_state(self, state_dict: dict):
        """
        Sincroniza os dados do st.session_state para este objeto de negócio central.
        Isso permite isolamento da camada de interface (Streamlit).
        """
        if "alternatives" in state_dict:
            self.alternatives = state_dict["alternatives"].copy()
        
        if "fuzzy_number_alternatives" in state_dict:
            # Reconstruindo para fazer cópia profunda simples
            self.fuzzy_number_alternatives = {
                k: {"description": v["description"], "lmu": v["lmu"].copy()}
                for k, v in state_dict["fuzzy_number_alternatives"].items()
            }
            
        if "fuzzy_number_weights" in state_dict:
            self.fuzzy_number_weights = {
                k: {"description": v["description"], "lmu": v["lmu"].copy()}
                for k, v in state_dict["fuzzy_number_weights"].items()
            }
            
        if "classes" in state_dict:
            self.classes = {
                k: {"description": v["description"], "alternative_term": v["alternative_term"]}
                for k, v in state_dict["classes"].items()
            }
            
        if "criteria" in state_dict:
            import copy
            self.criteria = copy.deepcopy(state_dict["criteria"])
            
        if "evaluations" in state_dict:
            import copy
            self.evaluations = copy.deepcopy(state_dict["evaluations"])
            
        if "criteria_weights" in state_dict:
            import copy
            self.criteria_weights = copy.deepcopy(state_dict["criteria_weights"])

    def get_alternatives(self) -> dict:
        return self.alternatives

    def get_fuzzy_number_alternatives(self) -> dict:
        return self.fuzzy_number_alternatives
        
    def get_fuzzy_number_weights(self) -> dict:
        return self.fuzzy_number_weights
        
    def get_classes(self) -> dict:
        return self.classes

    def get_criteria(self) -> dict:
        return self.criteria

    def get_evaluations(self) -> dict:
        return self.evaluations

    def get_criteria_weights(self) -> dict:
        return self.criteria_weights

# Instância global que será usada pela regra de negócio
system_data = CoreData()
