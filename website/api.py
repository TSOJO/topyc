from flask import Blueprint, request, jsonify
import json
from datetime import datetime

from isolate_wrapper import IsolateSandbox, SourceCode, Language, Verdict
from config import TIME_LIMIT, MEMORY_LIMIT, LANGUAGE
from website.model import Task

api_bp = Blueprint('api_bp', __name__)

def check_keyword_present(text, keyword):
    text = text.replace('\n', ' ')
    if ' ' + keyword in text:
        return True
    if text.startswith(keyword):
        return True
    return False

@api_bp.route('/submit-code', methods=['POST'])
def run():
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
    
    testcases = task.testcases
    testcase_inputs = [tc.input for tc in testcases]
    for testcase, (output, status, message) in zip(
        testcases,
        sandbox.get_outputs(
            source_code,
            testcase_inputs,
            TIME_LIMIT,
            MEMORY_LIMIT
        )
    ):
        verdict = Verdict.AC
        if status == Verdict.AC:
            # AC status means code ran successfully. Now we see if output is correct.
            for answer_keyword in testcase.answer_keywords:
                if answer_keyword not in output:
                    verdict = Verdict.WA
                    break
        else:
            # TLE, MLE, etc.
            verdict = status
        
        results.append(
            {
                # 'output': output,
                'verdict': verdict.cast_to_document(),
                'message': message
            }
        )
        raw_verdicts.append(verdict)
    
    overall_verdict = sandbox.decide_final_verdict(raw_verdicts)
            
    response = {
        'time': datetime.utcnow().strftime('%a %-d %b %Y %H:%M'),
        'overallVerdict': overall_verdict.cast_to_document(),
        'results': results
    }
    # ! ADD TO DB HERE
    return jsonify(response)
