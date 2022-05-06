'''
    The module contains functions for working with the database and
    handling various requests by the FastAPI server.
'''

from operator import itemgetter

from fastapi import FastAPI, Query, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp
from sqlalchemy.future import select
from dateutil.parser import parse
import pytz

from database import Base, engine, Session
from quiz_model import QuizModel
from log import logger

app = FastAPI()


@app.get("/quiz")
async def index():
    '''
        The root url request handler.
    '''

    return {"status": "success"}


THIRD_PARTY_API = "https://jservice.io/api/random?count={}"


async def third_party_request(http_session: aiohttp.ClientSession, url: str):
    '''
        The request to the passed third-party url.
    '''

    async with http_session.get(url, ssl=False) as response:
        return await response.json()


async def get_database():
    '''
        A database session as a dependency.
    '''

    logger.info("Creating a database session")

    async with Session() as database:
        yield database

 
def q_text_props(questions: list[dict]):
    '''
        Returns "question" property values from passed question object list.
    '''

    return map(itemgetter("question"), questions)


async def question_exists(question: str, db_session: Session):
    '''
        Checks if passed question is exists in database.
    '''

    query = select(QuizModel).where(QuizModel.question == question)
    executed_query = await db_session.execute(query)
    return bool(executed_query.one_or_none())


async def unique_questions(questions: list[dict], db_session: Session,
                           http_session: aiohttp.ClientSession,
                           third_party_url: str):
    '''
       Returns list of all questions they are not in the database, replacing
       existing ones with new ones as a result of additional requests.
    '''

    async def exist_filter(q_text: str):
        return await question_exists(q_text, db_session)

    # Get the question text props and check if any of them exist
    # in the database.

    texts = q_text_props(questions)
    exist_indexes = [index for index, text in enumerate(texts)
                     if await exist_filter(text)]

    # If none of them exist, then just return the source questions.

    if not exist_indexes:
        return questions

    # Otherwise, request new questions until all of them are missing
    # in database.

    logger.debug("At least one question exists, a repeat request")

    new_questions = []

    def not_enough_new_questions():
        return len(new_questions) < len(exist_indexes)

    while not_enough_new_questions():
        response = await third_party_request(http_session, third_party_url)
        question_texts = q_text_props(response)
        new_questions = [text for text in question_texts
                         if not await exist_filter(text)]

        if not_enough_new_questions():
            logger.debug("A repeat request")

    # Replacing existing questions with new ones.

    for index, new_question in zip(exist_indexes, new_questions):
        questions[index] = new_question

    return questions


async def write_questions(questions: list[dict], db_session: Session):
    '''
        Writes the passed question objects to the database.
    '''

    required_props = itemgetter("id", "question", "answer", "created_at")

    model_data = map(required_props, questions)

    for question_id, question, answer, was_created in model_data:
        was_created = parse(was_created).replace(tzinfo=pytz.utc)

        new_quiz = QuizModel(
            question_id=question_id,
            question=question,
            answer=answer,
            was_created=was_created
        )

        db_session.add(new_quiz)
        await db_session.commit()

 
@app.on_event("startup")
async def startup():
    '''
        The server startup event handler.
    '''

    logger.info("Starting up")

    async with engine.begin() as conn:
        logger.info("Creating tables in the database")
        await conn.run_sync(Base.metadata.create_all)


class RequestBody(BaseModel):
    '''
        The POST request body validation model.
    '''

    questions_num: int = Query(..., ge=1)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    '''
        The request validation exception handler.
    '''

    exc_msg = exc.errors()[0]["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc_msg}
    )


@app.post("/quiz")
async def post(request_body: RequestBody,
               db_session: Session = Depends(get_database)):
    '''
        The POST request handler - requests the new questions from third-party
        public API and writes them in database.
    '''

    third_party_url = THIRD_PARTY_API.format(request_body.questions_num)

    async with aiohttp.ClientSession() as http_session:
        response = await third_party_request(http_session, third_party_url)
        questions = await unique_questions(response, db_session,
                                           http_session, third_party_url)

        await write_questions(questions, db_session)

    logger.info("The questions were succefully written in the database")

    query = select(QuizModel).order_by(QuizModel.id.desc())

    executed_query = await db_session.execute(query)
    last_record = executed_query.fetchone()[0]

    return last_record
