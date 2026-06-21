"""add query indexes

Revision ID: 5b4e6d8f0c2a
Revises: ba02daaf3f6b
Create Date: 2026-06-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "5b4e6d8f0c2a"
down_revision: Union[str, Sequence[str], None] = "ba02daaf3f6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_alternatives_project_id", "alternatives", ["project_id"])
    op.create_index("ix_classes_project_id", "classes", ["project_id"])
    op.create_index("ix_criteria_project_id", "criteria", ["project_id"])
    op.create_index("ix_fuzzy_terms_project_id", "fuzzy_terms", ["project_id"])

    op.create_index("ix_criterion_descriptions_criterion_id", "criterion_descriptions", ["criterion_id"])
    op.create_index("ix_criterion_descriptions_alternative_term_id", "criterion_descriptions", ["alternative_term_id"])
    op.create_index("ix_criterion_descriptions_weight_term_id", "criterion_descriptions", ["weight_term_id"])

    op.create_index("ix_criterion_class_thresholds_criterion_id", "criterion_class_thresholds", ["criterion_id"])
    op.create_index("ix_criterion_class_thresholds_class_id", "criterion_class_thresholds", ["class_id"])
    op.create_index(
        "ix_criterion_class_thresholds_min_alternative_term_id",
        "criterion_class_thresholds",
        ["min_alternative_term_id"],
    )

    op.create_index("ix_evaluations_project_id", "evaluations", ["project_id"])
    op.create_index("ix_evaluations_alternative_id", "evaluations", ["alternative_id"])
    op.create_index("ix_evaluations_criterion_id", "evaluations", ["criterion_id"])
    op.create_index("ix_evaluations_criterion_description_id", "evaluations", ["criterion_description_id"])

    op.create_index("ix_criteria_weights_project_id", "criteria_weights", ["project_id"])
    op.create_index("ix_criteria_weights_criterion_id", "criteria_weights", ["criterion_id"])
    op.create_index("ix_criteria_weights_weight_term_id", "criteria_weights", ["weight_term_id"])


def downgrade() -> None:
    op.drop_index("ix_criteria_weights_weight_term_id", table_name="criteria_weights")
    op.drop_index("ix_criteria_weights_criterion_id", table_name="criteria_weights")
    op.drop_index("ix_criteria_weights_project_id", table_name="criteria_weights")

    op.drop_index("ix_evaluations_criterion_description_id", table_name="evaluations")
    op.drop_index("ix_evaluations_criterion_id", table_name="evaluations")
    op.drop_index("ix_evaluations_alternative_id", table_name="evaluations")
    op.drop_index("ix_evaluations_project_id", table_name="evaluations")

    op.drop_index("ix_criterion_class_thresholds_min_alternative_term_id", table_name="criterion_class_thresholds")
    op.drop_index("ix_criterion_class_thresholds_class_id", table_name="criterion_class_thresholds")
    op.drop_index("ix_criterion_class_thresholds_criterion_id", table_name="criterion_class_thresholds")

    op.drop_index("ix_criterion_descriptions_weight_term_id", table_name="criterion_descriptions")
    op.drop_index("ix_criterion_descriptions_alternative_term_id", table_name="criterion_descriptions")
    op.drop_index("ix_criterion_descriptions_criterion_id", table_name="criterion_descriptions")

    op.drop_index("ix_fuzzy_terms_project_id", table_name="fuzzy_terms")
    op.drop_index("ix_criteria_project_id", table_name="criteria")
    op.drop_index("ix_classes_project_id", table_name="classes")
    op.drop_index("ix_alternatives_project_id", table_name="alternatives")
