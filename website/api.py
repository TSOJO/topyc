from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
import json
from datetime import datetime

from isolate_wrapper import IsolateSandbox, SourceCode, Language, Verdict
from config import TIME_LIMIT, MEMORY_LIMIT, LANGUAGE
from website.model import db, Task, Submission, TestcaseResult, User, Group

api_bp = Blueprint('api_bp', __name__)

def check_keyword_present(text, keyword):
    text = text.replace('\n', ' ')
    if ' ' + keyword in text:
        return True
    if text.startswith(keyword):
        return True
    return False

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
    testcases.sort(key=lambda t: t.number)
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
            for answer_keyword in testcase.answer_keywords:
                if answer_keyword.lower() not in output.lower():
                    verdict = Verdict.WA
                    break
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
                output=output,
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
