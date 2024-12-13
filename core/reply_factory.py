
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []
    current_question_id = session.get("current_question_id")
    
    # Initialize the quiz
    if current_question_id is None:
        session["current_question_id"] = -1
        session["score"] = 0  # Initialize score
        session.save()
        bot_responses.append(BOT_WELCOME_MESSAGE)
        next_question, _ = get_next_question(-1)
        bot_responses.append(next_question)
        return bot_responses

    # Validate and record the current answer
    success, error = record_current_answer(message, current_question_id, session)
    if not success:
        return [error]  # Invalid response

    # Fetch the next question
    next_question, next_question_id = get_next_question(current_question_id)
    if next_question:
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id
        session.save()
    else:
        # No more questions, generate the final response
        final_response = generate_final_response(session)
        bot_responses.append(final_response)
        session["current_question_id"] = None  # Reset for next quiz
        session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question in the Django session.
    """
    try:
        question = PYTHON_QUESTION_LIST[current_question_id]
        correct_answer = question["answer"]
        if answer.strip() == correct_answer:
            session["score"] = session.get("score", 0) + 1  # Increment score for correct answer
            session.save()
            return True, "Correct answer!"
        else:
            return True, "Wrong answer!"
    except IndexError:
        return False, "Invalid question ID."


def get_next_question(current_question_id):
    """
    Fetches the next question and its options from the PYTHON_QUESTION_LIST.
    """
    next_question_id = current_question_id + 1
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question = PYTHON_QUESTION_LIST[next_question_id]
        question_text = question["question_text"]
        options = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(question["options"])])
        full_question = f"{question_text}\nOptions:\n{options}"
        return full_question, next_question_id
    return None, None  # No more questions


def generate_final_response(session):
    """
    Creates a final result message, including the total score and number of correct answers.
    """
    score = session.get("score", 0)
    total_questions = len(PYTHON_QUESTION_LIST)
    return f"Quiz completed! Your total score is {score}/{total_questions}."