from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    alternatives = relationship("Alternative", back_populates="project", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="project", cascade="all, delete-orphan")
    fuzzy_terms = relationship("FuzzyTerm", back_populates="project", cascade="all, delete-orphan")
    criteria = relationship("Criterion", back_populates="project", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="project", cascade="all, delete-orphan")
    criteria_weights = relationship("CriteriaWeight", back_populates="project", cascade="all, delete-orphan")


class Alternative(Base):
    __tablename__ = "alternatives"
    __table_args__ = (UniqueConstraint("project_id", "code", name="uq_alternatives_project_code"),)

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)

    project = relationship("Project", back_populates="alternatives")
    evaluations = relationship("Evaluation", back_populates="alternative", cascade="all, delete-orphan")


class Class(Base):
    __tablename__ = "classes"
    __table_args__ = (UniqueConstraint("project_id", "code", name="uq_classes_project_code"),)

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)

    project = relationship("Project", back_populates="classes")
    criterion_thresholds = relationship(
        "CriterionClassThreshold",
        back_populates="class_",
        cascade="all, delete-orphan",
    )


class FuzzyTerm(Base):
    __tablename__ = "fuzzy_terms"
    __table_args__ = (
        UniqueConstraint("project_id", "code", "term_type", name="uq_fuzzy_terms_project_code_type"),
        CheckConstraint("l <= m AND m <= u", name="ck_fuzzy_terms_lmu_order"),
    )

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    l = Column(Numeric(10, 4), nullable=False)
    m = Column(Numeric(10, 4), nullable=False)
    u = Column(Numeric(10, 4), nullable=False)
    term_type = Column(Enum("alternative", "weight", name="term_type"), nullable=False)

    project = relationship("Project", back_populates="fuzzy_terms")


class Criterion(Base):
    __tablename__ = "criteria"
    __table_args__ = (UniqueConstraint("project_id", "code", name="uq_criteria_project_code"),)

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    kind = Column(Enum("beneficio", "custo", name="criterion_kind"), nullable=False)

    project = relationship("Project", back_populates="criteria")
    descriptions = relationship("CriterionDescription", back_populates="criterion", cascade="all, delete-orphan")
    class_thresholds = relationship(
        "CriterionClassThreshold",
        back_populates="criterion",
        cascade="all, delete-orphan",
    )
    evaluations = relationship("Evaluation", back_populates="criterion", cascade="all, delete-orphan")
    criteria_weights = relationship("CriteriaWeight", back_populates="criterion", cascade="all, delete-orphan")


class CriterionDescription(Base):
    __tablename__ = "criterion_descriptions"

    id = Column(BigInteger, primary_key=True)
    criterion_id = Column(BigInteger, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    alternative_term_id = Column(BigInteger, ForeignKey("fuzzy_terms.id", ondelete="SET NULL"))
    weight_term_id = Column(BigInteger, ForeignKey("fuzzy_terms.id", ondelete="SET NULL"))

    criterion = relationship("Criterion", back_populates="descriptions")


class CriterionClassThreshold(Base):
    __tablename__ = "criterion_class_thresholds"
    __table_args__ = (
        UniqueConstraint("criterion_id", "class_id", name="uq_criterion_class_threshold"),
    )

    id = Column(BigInteger, primary_key=True)
    criterion_id = Column(BigInteger, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(BigInteger, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    min_alternative_term_id = Column(BigInteger, ForeignKey("fuzzy_terms.id", ondelete="SET NULL"))

    criterion = relationship("Criterion", back_populates="class_thresholds")
    class_ = relationship("Class", back_populates="criterion_thresholds")


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (
        UniqueConstraint("project_id", "alternative_id", "criterion_id", name="uq_evaluations_project_alt_crit"),
    )

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    alternative_id = Column(BigInteger, ForeignKey("alternatives.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(BigInteger, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    criterion_description_id = Column(BigInteger, ForeignKey("criterion_descriptions.id", ondelete="SET NULL"))

    project = relationship("Project", back_populates="evaluations")
    alternative = relationship("Alternative", back_populates="evaluations")
    criterion = relationship("Criterion", back_populates="evaluations")


class CriteriaWeight(Base):
    __tablename__ = "criteria_weights"
    __table_args__ = (UniqueConstraint("project_id", "criterion_id", name="uq_criteria_weights_project_crit"),)

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(BigInteger, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    weight_term_id = Column(BigInteger, ForeignKey("fuzzy_terms.id", ondelete="SET NULL"))

    project = relationship("Project", back_populates="criteria_weights")
    criterion = relationship("Criterion", back_populates="criteria_weights")
