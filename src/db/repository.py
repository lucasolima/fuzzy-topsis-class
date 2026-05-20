from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select

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
    alt_term_by_code: dict[str, FuzzyTerm] = {}
    weight_term_by_code: dict[str, FuzzyTerm] = {}

    for code, data in fuzzy_alts.items():
        term = FuzzyTerm(
            project_id=project_id,
            code=code,
            description=data.get("description", ""),
            l=data.get("lmu", [0.0, 0.0, 0.0])[0],
            m=data.get("lmu", [0.0, 0.0, 0.0])[1],
            u=data.get("lmu", [0.0, 0.0, 0.0])[2],
            term_type="alternative",
        )
        session.add(term)
        alt_term_by_code[code] = term

    for code, data in fuzzy_weights.items():
        term = FuzzyTerm(
            project_id=project_id,
            code=code,
            description=data.get("description", ""),
            l=data.get("lmu", [0.0, 0.0, 0.0])[0],
            m=data.get("lmu", [0.0, 0.0, 0.0])[1],
            u=data.get("lmu", [0.0, 0.0, 0.0])[2],
            term_type="weight",
        )
        session.add(term)
        weight_term_by_code[code] = term

    alternatives = state.get("alternatives", {})
    alternative_by_code: dict[str, Alternative] = {}
    for code, name in alternatives.items():
        alt = Alternative(project_id=project_id, code=code, name=name)
        session.add(alt)
        alternative_by_code[code] = alt

    classes = state.get("classes", {})
    class_by_code: dict[str, Class] = {}
    for code, data in classes.items():
        cls = Class(project_id=project_id, code=code, description=data.get("description", ""))
        session.add(cls)
        class_by_code[code] = cls

    criteria_data = state.get("criteria", {})
    criterion_by_code: dict[str, Criterion] = {}
    for code, data in criteria_data.items():
        criterion = Criterion(
            project_id=project_id,
            code=code,
            name=data.get("criterion", ""),
            kind=_normalize_kind(data.get("type")),
        )
        session.add(criterion)
        criterion_by_code[code] = criterion

    session.flush()

    description_objects: list[CriterionDescription] = []
    for crit_code, crit_data in criteria_data.items():
        criterion = criterion_by_code.get(crit_code)
        if not criterion:
            continue
        for desc in crit_data.get("descriptions", []):
            alt_term = alt_term_by_code.get(desc.get("alternative_term") or "")
            weight_term = weight_term_by_code.get(desc.get("weight_term") or "")
            description = CriterionDescription(
                criterion_id=criterion.id,
                description=desc.get("description", ""),
                alternative_term_id=alt_term.id if alt_term else None,
                weight_term_id=weight_term.id if weight_term else None,
            )
            session.add(description)
            description_objects.append(description)

    for crit_code, crit_data in criteria_data.items():
        criterion = criterion_by_code.get(crit_code)
        if not criterion:
            continue
        for class_code, class_data in crit_data.get("classes", {}).items():
            class_row = class_by_code.get(class_code)
            if not class_row:
                continue
            term = alt_term_by_code.get(class_data.get("alternative_term") or "")
            threshold = CriterionClassThreshold(
                criterion_id=criterion.id,
                class_id=class_row.id,
                min_alternative_term_id=term.id if term else None,
            )
            session.add(threshold)

    session.flush()

    description_by_key = {
        (desc.criterion_id, desc.description): desc
        for desc in description_objects
    }
    weight_term_by_description = {
        term.description: term for term in weight_term_by_code.values()
    }

    criteria_weights = state.get("criteria_weights", {})
    for crit_code, weight_desc in criteria_weights.items():
        criterion = criterion_by_code.get(crit_code)
        term = weight_term_by_description.get(weight_desc)
        if not criterion or not term:
            continue
        session.add(
            CriteriaWeight(
                project_id=project_id,
                criterion_id=criterion.id,
                weight_term_id=term.id,
            )
        )

    evaluations = state.get("evaluations", {})
    for alt_code, crit_map in evaluations.items():
        alt = alternative_by_code.get(alt_code)
        if not alt:
            continue
        for crit_code, description_text in crit_map.items():
            criterion = criterion_by_code.get(crit_code)
            if not criterion or not description_text:
                continue
            desc = description_by_key.get((criterion.id, description_text))
            session.add(
                Evaluation(
                    project_id=project_id,
                    alternative_id=alt.id,
                    criterion_id=criterion.id,
                    criterion_description_id=desc.id if desc else None,
                )
            )
