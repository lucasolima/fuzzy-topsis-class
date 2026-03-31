import streamlit as st

def initialize_state():
    """Inicializa as variáveis de sessão necessárias da aplicação com a estrutura desejada."""
    if 'alternativas' not in st.session_state:
        # Já inicializando com os dados de exemplo solicitados para facilitar.
        st.session_state.alternativas = {
            "ALT1": "SIPAC - Autenticação pelo gov.br",
            "ALT2": "SIPAC - Migração dos módulos de Patrimônio e Inventário para o SIADS",
            "ALT3": "SIPAC - Implantação do módulo de Bolsas",	
            "ALT4": "SIGRH - Aprimoramento PID/RID - Progressão docente",
            "ALT5": "SIGAA - Implantação do Módulo de Pesquisa",
            "ALT6": "SIGAA - Implantação do Módulo Assistência Estudantil",
            "ALT7": "SIGAA - Central de Estágios",
            "ALT8": "SIGAA - Processos Seletivos",
            "ALT9": "SIGAA - Emissão, guarda e integração do serviço de diploma digital com a RNP",
        }
    if 'next_alt_id' not in st.session_state:
        st.session_state.next_alt_id = 10

    if 'numero_fuzzy_alternativas' not in st.session_state:
        st.session_state.numero_fuzzy_alternativas = {
            "MB": {"descricao": "Muito Baixo", "lmu": [1.0, 1.0, 2.0]},
            "B": {"descricao": "Baixo", "lmu": [1.0, 2.0, 3.0]},
            "M": {"descricao": "Médio", "lmu": [2.0, 3.0, 4.0]},
            "A": {"descricao": "Alto", "lmu": [3.0, 4.0, 5.0]},
            "MA": {"descricao": "Muito Alto", "lmu": [4.0, 5.0, 6.0]},
        }
    
    if 'numero_fuzzy_pesos' not in st.session_state:
        st.session_state.numero_fuzzy_pesos = {
            "MBI": {"descricao": "Muito Baixa Importância", "lmu": [0.1, 0.1, 0.2]},
            "BI": {"descricao": "Baixa Importância", "lmu": [0.1, 0.2, 0.3]},
            "IM": {"descricao": "Importância Média", "lmu": [0.2, 0.3, 0.4]},
            "AI": {"descricao": "Alta Importância", "lmu": [0.3, 0.4, 0.5]},
            "MAI": {"descricao": "Muito Alta Importância", "lmu": [0.4, 0.5, 0.6]},
        }

    if 'classes' not in st.session_state:
        st.session_state.classes = {
            "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": None},
            "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": None},
            "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": None},
        }
    
    if 'next_fuzzy_alt_id' not in st.session_state:
        st.session_state.next_fuzzy_alt_id = 1

    if 'next_fuzzy_peso_id' not in st.session_state:
        st.session_state.next_fuzzy_peso_id = 1

    if 'next_class_id' not in st.session_state:
        st.session_state.next_class_id = 4

    if 'criterios' not in st.session_state:
        st.session_state.criterios = {
            "CRI1": {
                "criterio": "Alinhamento estratégico PEI, PDI, PDTIC e EGD",
                "tipo": "benefício",
                "descricoes": [
                    {"descricao": "Prioridade explícita da alta gestão", "termo_alternativa": "MA", "termo_peso": "MAI"},
                    {"descricao": "Alinhado a estratégias governamentais (EGD)", "termo_alternativa": "A", "termo_peso": "AI"},
                    {"descricao": "Previsto em PDTIC anterior", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "Previsto em planos estratégicos", "termo_alternativa": "B", "termo_peso": "BI"},
                    {"descricao": "Não está previsto em nenhum plano", "termo_alternativa": "MB", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "A"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "B"},
                }
            },
            "CRI2": {
                "criterio": "Exigência legal / regulatória",
                "tipo": "benefício",
                "descricoes": [
                    {"descricao": "Mais de uma exigência legal/regulatória externa", "termo_alternativa": "MA", "termo_peso": "MAI"},
                    {"descricao": "Mais de uma exigência legal / regulatória interna", "termo_alternativa": "A", "termo_peso": "AI"},
                    {"descricao": "Uma exigência legal / regulatória externa", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "Uma exigência legal / regulatória interna", "termo_alternativa": "B", "termo_peso": "BI"},
                    {"descricao": "Não é uma exigência legal / regulatória", "termo_alternativa": "MB", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "A"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "MB"},
                }
            },
            "CRI3": {
                "criterio": "Abrangência na comunidade universitária",
                "tipo": "benefício",
                "descricoes": [
                    {"descricao": "Universidade e a sociedade", "termo_alternativa": "MA", "termo_peso": "MAI"},
                    {"descricao": "Maioria ou toda a Comunidade Acadêmica", "termo_alternativa": "A", "termo_peso": "AI"},
                    {"descricao": "Maioria dos técnicos-administrativos e/ou a maioria dos discentes e/ou docentes", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "Centros, órgãos suplementares ou pró-reitorias isoladamente", "termo_alternativa": "B", "termo_peso": "BI"},
                    {"descricao": "Afeta apenas um departamento ou setor", "termo_alternativa": "MB", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "A"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "B"},
                }
            },
            "CRI4": {
                "criterio": "Complexidade",
                "tipo": "custo",
                "descricoes": [
                    {"descricao": "Baixíssima complexidade (Requisitos claramente definidos e precisos, mínima interdependência entre sistemas, poucas partes interessadas, muito baixo risco de mudanças)", "termo_alternativa": "MB", "termo_peso": "MAI"},
                    {"descricao": "Baixa complexidade (Requisitos relativamente claros e precisos, interdependência limitada entre sistemas, algumas partes interessadas, baixo risco de mudanças)", "termo_alternativa": "B", "termo_peso": "AI"},
                    {"descricao": "Média complexidade (Requisitos moderadamente complexos e claros, interdependência entre sistemas, algumas partes interessadas, risco moderado de mudanças)", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "Alta complexidade (requisitos complexos e ambíguos, significativa interdependência entre sistemas, muitas partes interessadas, risco moderado a alto de mudanças)", "termo_alternativa": "A", "termo_peso": "BI"},
                    {"descricao": "Altíssima complexidade (requisitos extremamente complexos e ambíguos, alta interdependência entre sistemas, muitas partes interessadas com necessidades conflitantes, alto risco de mudanças)", "termo_alternativa": "MA", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "B"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "MA"},
                }
            },
            "CRI5": {
                "criterio": "Esforço",
                "tipo": "custo",
                "descricoes": [
                    {"descricao": "Baixíssimo esforço (tarefas simples que envolvem um único desenvolvedor por um curto período)", "termo_alternativa": "MB", "termo_peso": "MAI"},
                    {"descricao": "Baixo esforço (customização pontual, envolvendo um desenvolvedor, tarefas claramente definidas e de baixa complexidade)", "termo_alternativa": "B", "termo_peso": "AI"},
                    {"descricao": "Médio esforço (customização que pode envolver um ou mais desenvolvedores, tarefas de complexidade média e algumas interdependências)", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "Alto esforço (customização que envolve dois ou mais desenvolvedores, tarefas de complexidade média a alta, requerendo coordenação entre desenvolvedores e possivelmente algumas outras áreas)", "termo_alternativa": "A", "termo_peso": "BI"},
                    {"descricao": "Altíssimo esforço (customização e integração de alta complexidade, envolvendo mais de um setor e dois ou mais desenvolvedores, com interdependências significativas e coordenação necessária entre equipes)", "termo_alternativa": "MA", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "B"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "MA"},
                }
            },
            "CRI6": {
                "criterio": "Tempo total",
                "tipo": "custo",
                "descricoes": [
                    {"descricao": "Até 1 mês", "termo_alternativa": "MB", "termo_peso": "MAI"},
                    {"descricao": "De 1 a 3 meses", "termo_alternativa": "B", "termo_peso": "AI"},
                    {"descricao": "De 3 a 6 meses", "termo_alternativa": "M", "termo_peso": "IM"},
                    {"descricao": "De 6 meses a 1 ano", "termo_alternativa": "A", "termo_peso": "BI"},
                    {"descricao": "Mais de um ano", "termo_alternativa": "MA", "termo_peso": "MBI"},
                ],
                "classes": {
                    "CLA1": {"descricao": "Alta Prioridade", "termo_alternativa": "MB"},
                    "CLA2": {"descricao": "Média Prioridade", "termo_alternativa": "M"},
                    "CLA3": {"descricao": "Baixa Prioridade", "termo_alternativa": "MA"},
                }
            }
        }

    if 'next_cri_id' not in st.session_state:
        st.session_state.next_cri_id = 7

    if 'avaliacoes' not in st.session_state:
        st.session_state.avaliacoes = {}

    if 'pesos_criterios' not in st.session_state:
        st.session_state.pesos_criterios = {}

def add_alternative():
    """Adiciona uma nova alternativa vazia no final do dicionário."""
    alt_id = f"ALT{st.session_state.next_alt_id}"
    st.session_state.alternativas[alt_id] = ""
    st.session_state.next_alt_id += 1

def update_alternative(alt_id: str, new_value: str):
    """Atualiza o valor de uma alternativa existente."""
    st.session_state.alternativas[alt_id] = new_value

def delete_alternative(alt_id: str):
    """Deleta uma alternativa pelo seu identificador (ex: ALT1)."""
    if alt_id in st.session_state.alternativas:
        del st.session_state.alternativas[alt_id]
