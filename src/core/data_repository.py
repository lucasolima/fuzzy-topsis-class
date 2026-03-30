class CoreData:
    """
    Classe singleton (ou estática) para concentrar o acesso aos dados em tempo de execução
    sem depender diretamente de componentes de interface como st.session_state dentro da lógica de negócio.
    """
    def __init__(self):
        self.alternativas = {}
        self.numero_fuzzy_alternativas = {}
        self.numero_fuzzy_pesos = {}
        self.classes = {}
        self.criterios = {}

    def update_from_state(self, state_dict: dict):
        """
        Sincroniza os dados do st.session_state para este objeto de negócio central.
        Isso permite isolamento da camada de interface (Streamlit).
        """
        if "alternativas" in state_dict:
            self.alternativas = state_dict["alternativas"].copy()
        
        if "numero_fuzzy_alternativas" in state_dict:
            # Reconstruindo para fazer cópia profunda simples
            self.numero_fuzzy_alternativas = {
                k: {"descricao": v["descricao"], "lmu": v["lmu"].copy()}
                for k, v in state_dict["numero_fuzzy_alternativas"].items()
            }
            
        if "numero_fuzzy_pesos" in state_dict:
            self.numero_fuzzy_pesos = {
                k: {"descricao": v["descricao"], "lmu": v["lmu"].copy()}
                for k, v in state_dict["numero_fuzzy_pesos"].items()
            }
            
        if "classes" in state_dict:
            self.classes = {
                k: {"descricao": v["descricao"], "termo_alternativa": v["termo_alternativa"]}
                for k, v in state_dict["classes"].items()
            }
            
        if "criterios" in state_dict:
            import copy
            self.criterios = copy.deepcopy(state_dict["criterios"])

    def get_alternativas(self) -> dict:
        return self.alternativas

    def get_numero_fuzzy_alternativas(self) -> dict:
        return self.numero_fuzzy_alternativas
        
    def get_numero_fuzzy_pesos(self) -> dict:
        return self.numero_fuzzy_pesos
        
    def get_classes(self) -> dict:
        return self.classes

    def get_criterios(self) -> dict:
        return self.criterios

# Instância global que será usada pela regra de negócio
system_data = CoreData()
