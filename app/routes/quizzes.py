from fastapi import APIRouter, HTTPException,Query
from typing import List,Optional
import logging

from app.models.quiz import (
    QuizCreate,
    QuizResponse,
    QuizListItem,
    QuizListResponse,
    QuizSubmission,
    QuizResult
)

from app.utils.json_handler import (
    read_all_quizzes,
    read_quiz,
    create_quiz,
    update_quiz,
    delete_quiz,
    save_result,
    get_results_for_quiz
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)

@router.post("",response_model=QuizResponse,status_code=201)
async def create_quiz_endpoint(quiz : QuizCreate):
    try:
        quiz_dict = quiz.dict()  # Convert Pydantic model to dict for JSON storage
        created_quiz = create_quiz(quiz_dict)
        return created_quiz
    except Exception as e: 
        raise HTTPException(status_code=400,detail=str(e))   


@router.post("/{quiz_id}",response_model=QuizResponse)
async def get_single_quiz(quiz_id : int):
    try:
      if quiz_id:
          val = read_quiz(quiz_id)
          return val
    except Exception as e:  
        raise HTTPException(status_code=400 ,detail=str(e))  


# list quizzes
@router.get("", response_model=QuizListResponse)
async def list_quizzes_endpoint(
    difficulty: Optional[str] = Query(
        None, 
        description="Filter by difficulty: easy, medium, hard"
    ),
    topic: Optional[str] = Query(
        None,
        description="Filter by topic (partial match in title)"
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=100,
        description="Items per page (1-100)"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="How many items to skip (for pagination)"
    )
):
  try:
      quizzes = read_all_quizzes() # read all quizzess
      # filter results
      if difficulty:
          # filter by difficulty
          quizzes = [
                     q for q in quizzes
                     if q.get("difficulty",'').lower() == difficulty.lower()
                    ]
      # filter by topic
      if topic:
          quizzes = [
              q for q in quizzes
              if (topic.lower() in q.get('title','').lower() or
                  topic.lower() in q.get('description','').lower())
           ]    
      # toal len after filtering
      total = len(quizzes)

      if total > 0:
          total_pages = (total + limit - 1) // limit
      else:
          total_pages = 1      

      # applying pagination(skip + limit)
      paginated_quizzes = quizzes[skip:skip+limit]
      
      # current page number
      current_page = (skip//limit) + 1

      # has next : next page exists
      has_next = (skip + limit) < total

      # has prev : previous page exists
      has_prev = (skip > 0)

      # convert to list items
      quiz_items = []
      for quiz in paginated_quizzes:
            try:
                item = QuizListItem(
                    id=quiz['id'],
                    title=quiz['title'],
                    description=quiz.get('description'),
                    question_count=len(quiz.get('questions', [])),
                    created_at=quiz.get('created_at')
                )
                quiz_items.append(item)
            except KeyError as e:
                logger.warning(f"Skipping malformed quiz: {str(e)}")
                continue  

      # build response
      response = QuizListResponse(
            data=quiz_items,
            pagination={
                "skip": skip,
                "limit": limit,
                "total": total,
                "page": current_page,
                "pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        )
        
      logger.info(
            f"Listed quizzes: skip={skip}, limit={limit}, "
            f"total={total}, page={current_page}/{total_pages}"
      )      

  except Exception as e:
      raise HTTPException(status_code=400,detail=str(e))     
    
@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz_endpoint(
    quiz_id: int,
    submission: QuizSubmission
):
    try:
        quiz = read_quiz(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz {quiz_id} not found"
            )

        questions = quiz.get("questions", [])
        user_answers = submission.answers

        if len(user_answers) != len(questions):
            raise HTTPException(
                status_code=400,
                detail=f"Expected {len(questions)} answers, got {len(user_answers)}"
            )

        score = 0
        correct_answers = []

        for i, question in enumerate(questions):
            correct_option = question["correct_option"]
            correct_answers.append(correct_option)

            if user_answers[i] == correct_option:
                score += 1

        total = len(questions)
        percentage = (score / total * 100) if total > 0 else 0

        result_data = {
            "quiz_id": quiz_id,
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "user_answers": user_answers,
            "correct_answers": correct_answers
        }

        saved_result = save_result(result_data)

        logger.info(
            f"Quiz {quiz_id} submitted, score: {score}/{total}"
        )

        return saved_result

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{quiz_id}/results", response_model=List[QuizResult])
async def get_results_endpoint(quiz_id: int):
    try:
        quiz = read_quiz(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz {quiz_id} not found"
            )

        results = get_results_for_quiz(quiz_id)

        logger.info(
            f"Retrieved {len(results)} results for quiz {quiz_id}"
        )

        return results

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")