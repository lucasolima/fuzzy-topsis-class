from __future__ import annotations

from typing import Any

from sqlalchemy import delete, insert, select

from src.db.models import (
    Alternative,
    Class,
    CriteriaWeight,
    Criterion,
    CriterionClassThreshold,
    CriterionDescription,
    Evaluation,
    FuzzyTerm,
    Project,
)
from src.db.session import SessionLocal, init_db


def list_projects() -> dict[int, str]:
    with SessionLocal() as session:
        projects = session.scalars(select(Project).order_by(Project.id)).all()
        return {project.id: project.name for project in projects}


def create_project(name: str) -> int:
    with SessionLocal() as session:
        project = Project(name=name)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project.id


def rename_project(project_id: int, name: str) -> None:
    with SessionLocal() as session:
        project = session.get(Project, project_id)
        if not project:
            return
        project.name = name
        session.commit()


def delete_project(project_id: int) -> None:
    with SessionLocal() as session:
        project = session.get(Project, project_id)
        if not project:
            return
        session.delete(project)
        session.commit()


def load_project_state(project_id: int) -> dict[str, Any]:
    with SessionLocal() as session:
        project = session.get(Project, project_id)
        if not project:
            return {
                "alternatives": {},
                "fuzzy_number_alternatives": {},
                "fuzzy_number_weights": {},
                "classes": {},
                "criteria": {},
                "evaluations": {},
                "criteria_weights": {},
            }

        alternatives_rows = session.scalars(
            select(Alternative)
            .where(Alternative.project_id == project_id)
            .order_by(Alternative.code)
        ).all()
        alternatives = {alt.code: alt.name for alt in alternatives_rows}
        alternative_by_id = {alt.id: alt for alt in alternatives_rows}

        classes_rows = session.scalars(
            select(Class)
            .where(Class.project_id == project_id)
            .order_by(Class.code)
        ).all()
        classes = {cls.code: {"description": cls.description, "alternative_term": None} for cls in classes_rows}
        class_by_id = {cls.id: cls for cls in classes_rows}

        criteria_rows = session.scalars(
            select(Criterion)
            .where(Criterion.project_id == project_id)
            .order_by(Criterion.code)
        ).all()
        criteria = {
            crit.code: {
                "criterion": crit.name,
                "type": "benefício" if crit.kind == "beneficio" else "custo",
                "descriptions": [],
                "classes": {},
            }
            for crit in criteria_rows
        }
        criterion_by_id = {crit.id: crit for crit in criteria_rows}
        criterion_ids = list(criterion_by_id.keys())

        terms_rows = session.scalars(
            select(FuzzyTerm)
            .where(FuzzyTerm.project_id == project_id)
            .order_by(FuzzyTerm.code)
        ).all()
        alt_terms: dict[str, dict[str, Any]] = {}
        weight_terms: dict[str, dict[str, Any]] = {}
        term_by_id = {term.id: term for term in terms_rows}
        for term in terms_rows:
            payload = {
                "description": term.description,
                "lmu": [float(term.l), float(term.m), float(term.u)],
            }
            if term.term_type == "alternative":
                alt_terms[term.code] = payload
            else:
                weight_terms[term.code] = payload

        descriptions_rows = []
        if criterion_ids:
            descriptions_rows = session.scalars(
                select(CriterionDescription)
                .where(CriterionDescription.criterion_id.in_(criterion_ids))
                .order_by(CriterionDescription.id)
            ).all()

        for desc in descriptions_rows:
            crit_code = criterion_by_id[desc.criterion_id].code
            alt_term = term_by_id.get(desc.alternative_term_id)
            weight_term = term_by_id.get(desc.weight_term_id)
            criteria[crit_code]["descriptions"].append(
                {
                    "description": desc.description,
                    "alternative_term": alt_term.code if alt_term else None,
                    "weight_term": weight_term.code if weight_term else None,
                }
            )

        thresholds_rows = []
        if criterion_ids:
            thresholds_rows = session.scalars(
                select(CriterionClassThreshold)
                .where(CriterionClassThreshold.criterion_id.in_(criterion_ids))
                .order_by(CriterionClassThreshold.id)
            ).all()

        for threshold in thresholds_rows:
            crit_code = criterion_by_id[threshold.criterion_id].code
            class_code = class_by_id[threshold.class_id].code
            term = term_by_id.get(threshold.min_alternative_term_id)
            criteria[crit_code]["classes"][class_code] = {
                "description": classes.get(class_code, {}).get("description", ""),
                "alternative_term": term.code if term else None,
            }

        for crit_data in criteria.values():
            for class_code, class_data in classes.items():
                crit_data["classes"].setdefault(
                    class_code,
                    {"description": class_data["description"], "alternative_term": None},
                )

        criteria_weights_rows = session.scalars(
            select(CriteriaWeight)
            .where(CriteriaWeight.project_id == project_id)
        ).all()
        weight_term_by_id = {term.id: term for term in terms_rows if term.term_type == "weight"}
        criteria_weights: dict[str, str] = {}
        for weight in criteria_weights_rows:
            crit = criterion_by_id.get(weight.criterion_id)
            term = weight_term_by_id.get(weight.weight_term_id)
            if crit and term:
                criteria_weights[crit.code] = term.description

        descriptions_by_id = {desc.id: desc for desc in descriptions_rows}
        evaluations_rows = session.scalars(
            select(Evaluation)
            .where(Evaluation.project_id == project_id)
        ).all()
        evaluations: dict[str, dict[str, str]] = {}
        for evaluation in evaluations_rows:
            alt = alternative_by_id.get(evaluation.alternative_id)
            crit = criterion_by_id.get(evaluation.criterion_id)
            desc = descriptions_by_id.get(evaluation.criterion_description_id)
            if not alt or not crit or not desc:
                continue
            evaluations.setdefault(alt.code, {})[crit.code] = desc.description

        return {
            "alternatives": alternatives,
            "fuzzy_number_alternatives": alt_terms,
            "fuzzy_number_weights": weight_terms,
            "classes": classes,
            "criteria": criteria,
            "evaluations": evaluations,
            "criteria_weights": criteria_weights,
        }


def save_project_state(project_id: int, state: dict[str, Any]) -> None:
    with SessionLocal() as session:
        project = session.get(Project, project_id)
        if not project:
            return

        _clear_project_data(session, project_id)
        _insert_project_state(session, project_id, state)
        session.commit()


def ensure_schema() -> None:
    init_db()


def _clear_project_data(session, project_id: int) -> None:
    criterion_ids = session.scalars(
        select(Criterion.id).where(Criterion.project_id == project_id)
    ).all()

    session.execute(delete(Evaluation).where(Evaluation.project_id == project_id))
    session.execute(delete(CriteriaWeight).where(CriteriaWeight.project_id == project_id))

    if criterion_ids:
        session.execute(
            delete(CriterionClassThreshold).where(
                CriterionClassThreshold.criterion_id.in_(criterion_ids)
            )
        )
        session.execute(
            delete(CriterionDescription).where(
                CriterionDescription.criterion_id.in_(criterion_ids)
            )
        )

    session.execute(delete(Alternative).where(Alternative.project_id == project_id))
    session.execute(delete(Class).where(Class.project_id == project_id))
    session.execute(delete(Criterion).where(Criterion.project_id == project_id))
    session.execute(delete(FuzzyTerm).where(FuzzyTerm.project_id == project_id))


def _normalize_kind(value: str | None) -> str:
    if not value:
        return "beneficio"
    value = value.lower().strip()
    return "beneficio" if value.startswith("benef") else "custo"


def _insert_project_state(session, project_id: int, state: dict[str, Any]) -> None:
    fuzzy_alts = state.get("fuzzy_number_alternatives", {})
    fuzzy_weights = state.get("fuzzy_number_weights", {})
    fuzzy_rows = []

    for code, data in fuzzy_alts.items():
        lmu = data.get("lmu", [0.0, 0.0, 0.0])
        fuzzy_rows.append(
            {
                "project_id": project_id,
                "code": code,
                "description": data.get("description", ""),
                "l": lmu[0],
                "m": lmu[1],
                "u": lmu[2],
                "term_type": "alternative",
            }
        )

    for code, data in fuzzy_weights.items():
        lmu = data.get("lmu", [0.0, 0.0, 0.0])
        fuzzy_rows.append(
            {
                "project_id": project_id,
                "code": code,
                "description": data.get("description", ""),
                "l": lmu[0],
                "m": lmu[1],
                "u": lmu[2],
                "term_type": "weight",
            }
        )

    alt_term_by_code: dict[str, int] = {}
    weight_term_by_code: dict[str, int] = {}
    weight_term_by_description: dict[str, int] = {}
    if fuzzy_rows:
        term_result = session.execute(
            insert(FuzzyTerm).returning(
                FuzzyTerm.id,
                FuzzyTerm.code,
                FuzzyTerm.description,
                FuzzyTerm.term_type,
            ),
            fuzzy_rows,
        )
        for term_id, code, description, term_type in term_result:
            if term_type == "alternative":
                alt_term_by_code[code] = term_id
            else:
                weight_term_by_code[code] = term_id
                weight_term_by_description[description] = term_id

    alternatives = state.get("alternatives", {})
    alternative_rows = [
        {"project_id": project_id, "code": code, "name": name}
        for code, name in alternatives.items()
    ]
    alternative_by_code: dict[str, int] = {}
    if alternative_rows:
        alt_result = session.execute(
            insert(Alternative).returning(Alternative.id, Alternative.code),
            alternative_rows,
        )
        alternative_by_code = {code: alt_id for alt_id, code in alt_result}

    classes = state.get("classes", {})
    class_rows = [
        {"project_id": project_id, "code": code, "description": data.get("description", "")}
        for code, data in classes.items()
    ]
    class_by_code: dict[str, int] = {}
    if class_rows:
        class_result = session.execute(
            insert(Class).returning(Class.id, Class.code),
            class_rows,
        )
        class_by_code = {code: class_id for class_id, code in class_result}

    criteria_data = state.get("criteria", {})
    criteria_rows = [
        {
            "project_id": project_id,
            "code": code,
            "name": data.get("criterion", ""),
            "kind": _normalize_kind(data.get("type")),
        }
        for code, data in criteria_data.items()
    ]
    criterion_by_code: dict[str, int] = {}
    if criteria_rows:
        criterion_result = session.execute(
            insert(Criterion).returning(Criterion.id, Criterion.code),
            criteria_rows,
        )
        criterion_by_code = {code: criterion_id for criterion_id, code in criterion_result}

    description_rows = []
    for crit_code, crit_data in criteria_data.items():
        criterion_id = criterion_by_code.get(crit_code)
        if not criterion_id:
            continue
        for desc in crit_data.get("descriptions", []):
            description_rows.append(
                {
                    "criterion_id": criterion_id,
                    "description": desc.get("description", ""),
                    "alternative_term_id": alt_term_by_code.get(desc.get("alternative_term") or ""),
                    "weight_term_id": weight_term_by_code.get(desc.get("weight_term") or ""),
                }
            )

    description_by_key: dict[tuple[int, str], int] = {}
    if description_rows:
        description_result = session.execute(
            insert(CriterionDescription).returning(
                CriterionDescription.id,
                CriterionDescription.criterion_id,
                CriterionDescription.description,
            ),
            description_rows,
        )
        description_by_key = {
            (criterion_id, description): description_id
            for description_id, criterion_id, description in description_result
        }

    threshold_rows = []
    for crit_code, crit_data in criteria_data.items():
        criterion_id = criterion_by_code.get(crit_code)
        if not criterion_id:
            continue
        for class_code, class_data in crit_data.get("classes", {}).items():
            class_id = class_by_code.get(class_code)
            if not class_id:
                continue
            threshold_rows.append(
                {
                    "criterion_id": criterion_id,
                    "class_id": class_id,
                    "min_alternative_term_id": alt_term_by_code.get(class_data.get("alternative_term") or ""),
                }
            )
    if threshold_rows:
        session.execute(insert(CriterionClassThreshold), threshold_rows)

    criteria_weights = state.get("criteria_weights", {})
    criteria_weight_rows = []
    for crit_code, weight_desc in criteria_weights.items():
        criterion_id = criterion_by_code.get(crit_code)
        term_id = weight_term_by_description.get(weight_desc)
        if not criterion_id or not term_id:
            continue
        criteria_weight_rows.append(
            {
                "project_id": project_id,
                "criterion_id": criterion_id,
                "weight_term_id": term_id,
            }
        )
    if criteria_weight_rows:
        session.execute(insert(CriteriaWeight), criteria_weight_rows)

    evaluations = state.get("evaluations", {})
    evaluation_rows = []
    for alt_code, crit_map in evaluations.items():
        alt_id = alternative_by_code.get(alt_code)
        if not alt_id:
            continue
        for crit_code, description_text in crit_map.items():
            criterion_id = criterion_by_code.get(crit_code)
            if not criterion_id or not description_text:
                continue
            desc_id = description_by_key.get((criterion_id, description_text))
            evaluation_rows.append(
                {
                    "project_id": project_id,
                    "alternative_id": alt_id,
                    "criterion_id": criterion_id,
                    "criterion_description_id": desc_id,
                }
            )
    if evaluation_rows:
        session.execute(insert(Evaluation), evaluation_rows)
