from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
import json
from datetime import datetime

from isolate_wrapper import IsolateSandbox, SourceCode, Language, Verdict
from config import TIME_LIMIT, MEMORY_LIMIT, LANGUAGE, OUTPUT_MAX_LENGTH
from website.model import db, Task, Submission, TestcaseResult, User, Group

api_bp = Blueprint('api_bp', __name__)

def check_keyword_present(text, keyword):
    text = text.replace('\n', ' ')
    keyword_no_spaces = keyword.replace(' ', '')
    if keyword in text or keyword_no_spaces in text:
        return True
    return False

def check_keywords_in_output(output, keywords, is_ordered):
    output_lowered = output.lower()
    if not is_ordered:
        return all(keyword.lower() in output_lowered for keyword in keywords)
    else:
        i = 0
        for keyword in keywords:
            keyword_lowered = keyword.lower()
            if keyword_lowered in output_lowered[i:]:
                i += output_lowered[i:].index(keyword_lowered)
            else:
                return False
        return True

@api_bp.route('/submit-code', methods=['POST'])
def submit_code():
    req_json = json.loads(request.data)
    code = req_json.get('code')
    task_id = req_json.get('taskID')
    task = Task.query.get(task_id)
    
    if task is None:
        return '', 400
        
    if not all(check_keyword_present(code, keyword) for keyword in task.required_keywords):
        return '', 400
                
    sandbox = IsolateSandbox()
    source_code = SourceCode(code, Language.cast_from_document(LANGUAGE))
    results = []
    raw_verdicts = []
    current_time = datetime.utcnow()
    
    submission = Submission(
        user=current_user,
        task=task,
        time_submitted=current_time,
        source_code=code
    )
    
    testcases = task.testcases
    testcases.sort(key=lambda t: t.id)
    testcase_inputs = [tc.input for tc in testcases]
    for testcase, (output, result) in zip(
        testcases,
        sandbox.get_outputs(
            source_code,
            testcase_inputs,
            TIME_LIMIT,
            MEMORY_LIMIT
        )
    ):
        verdict = Verdict.AC
        if result.verdict == Verdict.AC:
            # AC status means code ran successfully. Now we see if output is correct.
            if not check_keywords_in_output(output, testcase.answer_keywords, testcase.is_ordered):
                verdict = Verdict.WA
        else:
            # TLE, MLE, etc.
            verdict = result.verdict
        
        results.append(
            {
                # 'output': output,
                'verdict': verdict.cast_to_document(),
                'message': result.message
            }
        )
        
        raw_verdicts.append(verdict)
        submission.testcase_results.append(
            TestcaseResult(
                testcase=testcase,
                verdict=verdict,
                output=output[:OUTPUT_MAX_LENGTH],
                message=result.message
            )
        )
    sandbox.cleanup()  # in case `testcases == []`, in which case the above loop will not run
    
    overall_verdict = sandbox.decide_final_verdict(raw_verdicts)
    
    submission.overall_verdict = overall_verdict
    db.session.add(submission)
    db.session.commit()
    
    response = {
        'time': current_time.strftime('%d/%m/%Y %H:%M'),
        'overallVerdict': overall_verdict.cast_to_document(),
        'results': results
    }
    return jsonify(response)

@api_bp.route('/get-submissions/<user_id>/<task_id>')
def get_submissions(user_id, task_id):
    if not current_user.is_admin:
        return '', 403
    
    submissions = Submission.query \
                            .filter_by(user_id=user_id, task_id=task_id) \
                            .order_by(Submission.time_submitted.desc()) \
                            .all()
    
    response = {
        'submissions': [
            {
                'id': submission.id,
                'overallVerdict': str(submission.overall_verdict),
                'timeSubmitted': submission.time_submitted.strftime('%d/%m/%Y %H:%M')
            }
            for submission in submissions
        ]
    }
    
    return jsonify(response)
