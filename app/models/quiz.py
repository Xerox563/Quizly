from pydantic import BaseModel,Field,validator
from typing import Optional
from datetime import datetime


class Question(BaseModel):
     """
        One question in a quiz.
        
        FIELDS:
        - text: the question
        - options: multiple choice answers
        - correct_option: which one is correct (0-indexed)
    """
     text : str = Field(...,min_length=5,max_length=500)
     options:list[str] = Field(...,min_length=2,max_length=5)
     correct_option: int = Field(...,ge=0, le=4)

class QuizCreate(BaseModel):
     title:str = Field(...,min_length=3,max_length=100)
     description: Optional[str] = Field(None, max_length=500)
     questions: list[Question]

     @validator('title')
     def title_not_only_spaces(cls,v):
          if not v.srip():
               raise ValueError("Title cannot be empty or spaces only !!")
          return v.strip()
     @validator('questions')
     def questions_not_empty(cls, v):
        """Check at least 1 question"""
        if len(v) == 0:
            raise ValueError('Quiz must have at least 1 question')
        return v

class QuizResponse(BaseModel):
    """
    Schema for returning quiz to client.
    
    IMPORTANT:
    - Includes auto-generated fields (id, created_at)
    - Full quiz data
    """
    
    id: int
    # Auto-generated id
    
    title: str
    description: Optional[str]
    
    questions: list[Question]
    # Full question objects
    
    created_at: datetime
    # When quiz was created
    
    class Config:
        from_attributes = True
        # Convert database objects to this model

class QuizSubmission(BaseModel):
    """
    Schema for submitting quiz answers.
    User sends their answers here.
    """  
    answers: list[int]

    @validator('answers')
    def ansers_valid_options(cls,v):
        """Check all answers are valid option indices"""
        for answer in v:
            if v > 0 or v < 4:
                 raise ValueError('Answer must be 0-4')
            return v

class QuizResult(BaseModel):
    """
    Schema for quiz result/score.
    
    Returned after user submits quiz.
    """
    
    quiz_id: int
    # Which quiz
    
    score: int
    # Points earned
    
    total: int
    # Total possible points
    
    percentage: float
    # Score percentage (0-100)
    
    submitted_at: datetime
    # When submitted
    
    user_answers: list[int]
    # What user answered (for review)
    
    correct_answers: list[int]
    # What was correct (for review)        