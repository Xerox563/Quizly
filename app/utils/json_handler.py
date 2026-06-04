# app/utils/json_handler.py
# PURPOSE: All JSON file operations

import json
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# ============================================
# CONSTANTS
# ============================================

DATA_FILE = "data/quizzes.json"
# Path to JSON file where quizzes stored

# ============================================
# INITIALIZE FILE
# ============================================

def initialize_json_file():
    """
    CREATE empty JSON file if doesn't exist.
    
    WHEN TO USE:
    - App startup
    - First time running
    
    HOW IT WORKS:
    - Check if file exists
    - If not: create with empty structure
    - If yes: do nothing
    
    WHY:
    - Prevents "file not found" errors
    - Ensures file always exists
    """
    
    # Check if file exists
    if not os.path.exists(DATA_FILE):
        logger.info(f"Creating {DATA_FILE}")
        
        # Create empty structure
        empty_data = {
            "quizzes": [],
            "results": []  # Store quiz results here too
        }
        
        # Create data folder if doesn't exist
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # Write empty structure to file
        with open(DATA_FILE, 'w') as f:
            json.dump(empty_data, f, indent=2)
        
        logger.info(f"{DATA_FILE} created successfully")

# ============================================
# READ FROM JSON
# ============================================

def read_all_quizzes() -> List[Dict[str, Any]]:
    """
    READ all quizzes from JSON file.
    
    WHEN TO USE:
    - List all quizzes
    - Filter quizzes
    - Get total count
    
    HOW IT WORKS:
    1. Open file
    2. Parse JSON
    3. Extract quizzes list
    4. Return list
    
    RETURNS:
    - List of quiz dictionaries
    - Example: [{"id": 1, "title": "Python"}, ...]
    
    WHY:
    - Single source of truth
    - All quizzes from one place
    """
    
    try:
        # Open file in read mode
        with open(DATA_FILE, 'r') as f:
            # Parse JSON string to Python dict
            data = json.load(f)
        
        # Extract quizzes list
        quizzes = data.get('quizzes', [])
        # .get('quizzes', []) = if 'quizzes' missing, return empty list
        
        logger.info(f"Read {len(quizzes)} quizzes from file")
        
        return quizzes
    
    except FileNotFoundError:
        """File doesn't exist yet"""
        logger.error(f"{DATA_FILE} not found")
        raise ValueError(f"Data file not found: {DATA_FILE}")
    
    except json.JSONDecodeError:
        """File corrupted (invalid JSON)"""
        logger.error(f"{DATA_FILE} is corrupted")
        raise ValueError(f"Corrupted JSON file: {DATA_FILE}")

# ============================================
# READ SINGLE QUIZ
# ============================================

def read_quiz(quiz_id: int) -> Dict[str, Any]:
    """
    READ single quiz by ID.
    
    WHEN TO USE:
    - Get /quizzes/{quiz_id}
    - Need specific quiz details
    
    HOW IT WORKS:
    1. Read all quizzes
    2. Find one with matching id
    3. Return it
    
    RETURNS:
    - Single quiz dict
    - Example: {"id": 1, "title": "Python", ...}
    - None if not found
    
    WHY:
    - Reuse read_all_quizzes()
    - Search in memory
    - Fast lookup
    """
    
    quizzes = read_all_quizzes()
    
    # Loop through all quizzes
    for quiz in quizzes:
        # If id matches, return this quiz
        if quiz['id'] == quiz_id:
            logger.info(f"Found quiz {quiz_id}")
            return quiz
    
    # Not found
    logger.warning(f"Quiz {quiz_id} not found")
    return None

# ============================================
# CREATE QUIZ
# ============================================

def create_quiz(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    CREATE new quiz and save to JSON.
    
    WHEN TO USE:
    - POST /quizzes
    - User creates new quiz
    
    HOW IT WORKS:
    1. Read existing quizzes
    2. Generate new ID (max id + 1)
    3. Add timestamp
    4. Append to quizzes list
    5. Write back to file
    6. Return created quiz
    
    IMPORTANT:
    - Must read before write (don't overwrite)
    - Generate unique ID
    - Preserve all existing quizzes
    
    WHY:
    - Atomic operation (read + write together)
    - Don't lose data
    - ID auto-generated
    """
    
    try:
        # Step 1: Read existing quizzes
        quizzes = read_all_quizzes()
        
        # Step 2: Generate new ID (max existing + 1)
        if quizzes:
            # If quizzes exist, get max id
            max_id = max(q['id'] for q in quizzes)
            new_id = max_id + 1
        else:
            # If no quizzes, start with 1
            new_id = 1
        
        # Step 3: Add id to quiz data
        quiz_data['id'] = new_id
        
        # Step 4: Add created_at timestamp
        from datetime import datetime
        quiz_data['created_at'] = datetime.now().isoformat()
        # .isoformat() = converts datetime to string (JSON-compatible)
        
        # Step 5: Append to list
        quizzes.append(quiz_data)
        
        # Step 6: Write back to file
        with open(DATA_FILE, 'w') as f:
            # Read full data structure
            with open(DATA_FILE, 'r') as fr:
                full_data = json.load(fr)
            
            # Update quizzes in full_data
            full_data['quizzes'] = quizzes
            
            # Write back
            json.dump(full_data, f, indent=2)
        
        logger.info(f"Created quiz with id {new_id}")
        
        return quiz_data
    
    except Exception as e:
        """Any error during save"""
        logger.error(f"Error creating quiz: {str(e)}")
        raise ValueError(f"Failed to create quiz: {str(e)}")

# ============================================
# UPDATE QUIZ
# ============================================

def update_quiz(quiz_id: int, updated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    UPDATE existing quiz.
    
    WHEN TO USE:
    - PUT /quizzes/{quiz_id}
    - User edits quiz
    
    HOW IT WORKS:
    1. Read all quizzes
    2. Find quiz with matching id
    3. Update its fields
    4. Write back
    5. Return updated quiz
    
    IMPORTANT:
    - Only update provided fields
    - Don't remove other fields
    - Preserve id and created_at
    """
    
    try:
        quizzes = read_all_quizzes()
        
        # Find and update
        for i, quiz in enumerate(quizzes):
            if quiz['id'] == quiz_id:
                # Found it, update fields
                # Only update what's provided
                for key, value in updated_data.items():
                    quiz[key] = value
                
                # Update modified timestamp
                from datetime import datetime
                quiz['updated_at'] = datetime.now().isoformat()
                
                # Write back
                with open(DATA_FILE, 'r') as f:
                    full_data = json.load(f)
                
                full_data['quizzes'] = quizzes
                
                with open(DATA_FILE, 'w') as f:
                    json.dump(full_data, f, indent=2)
                
                logger.info(f"Updated quiz {quiz_id}")
                return quiz
        
        # Not found
        logger.warning(f"Quiz {quiz_id} not found for update")
        return None
    
    except Exception as e:
        logger.error(f"Error updating quiz: {str(e)}")
        raise ValueError(f"Failed to update quiz: {str(e)}")

# ============================================
# DELETE QUIZ
# ============================================

def delete_quiz(quiz_id: int) -> bool:
    """
    DELETE quiz from file.
    
    WHEN TO USE:
    - DELETE /quizzes/{quiz_id}
    - User removes quiz
    
    HOW IT WORKS:
    1. Read all quizzes
    2. Remove one with matching id
    3. Write back
    4. Return success/failure
    
    RETURNS:
    - True if deleted
    - False if not found
    """
    
    try:
        quizzes = read_all_quizzes()
        
        original_count = len(quizzes)
        
        # Remove quiz with matching id
        quizzes = [q for q in quizzes if q['id'] != quiz_id]
        # This creates new list without the deleted quiz
        
        # If count changed, quiz was deleted
        if len(quizzes) < original_count:
            # Write back
            with open(DATA_FILE, 'r') as f:
                full_data = json.load(f)
            
            full_data['quizzes'] = quizzes
            
            with open(DATA_FILE, 'w') as f:
                json.dump(full_data, f, indent=2)
            
            logger.info(f"Deleted quiz {quiz_id}")
            return True
        else:
            # Quiz not found
            logger.warning(f"Quiz {quiz_id} not found for delete")
            return False
    
    except Exception as e:
        logger.error(f"Error deleting quiz: {str(e)}")
        raise ValueError(f"Failed to delete quiz: {str(e)}")

# ============================================
# RESULTS OPERATIONS
# ============================================

def save_result(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SAVE quiz result (when user submits quiz).
    
    WHEN TO USE:
    - POST /quizzes/{quiz_id}/submit
    - User finishes quiz
    
    HOW IT WORKS:
    - Similar to create_quiz
    - Append to results list
    - Track score, answers, timestamp
    """
    
    try:
        with open(DATA_FILE, 'r') as f:
            full_data = json.load(f)
        
        results = full_data.get('results', [])
        
        # Generate result id
        result_id = len(results) + 1
        result_data['id'] = result_id
        
        from datetime import datetime
        result_data['submitted_at'] = datetime.now().isoformat()
        
        results.append(result_data)
        
        full_data['results'] = results
        
        with open(DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=2)
        
        logger.info(f"Saved result for quiz {result_data.get('quiz_id')}")
        
        return result_data
    
    except Exception as e:
        logger.error(f"Error saving result: {str(e)}")
        raise ValueError(f"Failed to save result: {str(e)}")

def get_results_for_quiz(quiz_id: int) -> List[Dict[str, Any]]:
    """
    GET all results for a specific quiz.
    
    WHEN TO USE:
    - GET /quizzes/{quiz_id}/results
    - View past submissions
    
    HOW IT WORKS:
    - Read all results
    - Filter by quiz_id
    - Return filtered list
    """
    
    try:
        with open(DATA_FILE, 'r') as f:
            full_data = json.load(f)
        
        results = full_data.get('results', [])
        
        # Filter results for this quiz
        quiz_results = [r for r in results if r.get('quiz_id') == quiz_id]
        
        logger.info(f"Found {len(quiz_results)} results for quiz {quiz_id}")
        
        return quiz_results
    
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise ValueError(f"Failed to get results: {str(e)}")