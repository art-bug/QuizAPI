'''
    The module contains all necessary SQLAlchemy models of database tables.
'''

import sqlalchemy as sa
from sqlalchemy import Table, Column
from sqlalchemy.sql import func

from database import Base


class QuizModel(Base):
    '''
        Describes the Quiz table model.
    '''

    __tablename__ = "Quiz"

    id = Column(sa.Integer, primary_key=True)
    question_id = Column(sa.Integer, unique=True, nullable=False)
    question = Column(sa.String, unique=True, index=True, nullable=False)
    answer = Column(sa.String, nullable=False)
    was_created = Column(sa.DateTime(timezone=True), default=func.now())
