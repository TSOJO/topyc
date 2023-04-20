from flask import Blueprint, request, jsonify
import json
from datetime import datetime

from isolate_wrapper import IsolateSandbox, SourceCode, Language, Verdict
from config import TIME_LIMIT, MEMORY_LIMIT, LANGUAGE

api_bp = Blueprint('api_bp', __name__)

class KeywordTestcase:
    def __init__(self, input: str, answer_keywords: list):
        self.input = input
        self.answer_keywords = answer_keywords

class DebugTask:
    def __init__(self):
        self.title = 'Task 4.3: Age'
        self.required_keywords = ['if', 'elif', 'else']
        self.description = 'Ask the user for their age. If their age is greater than 50, print \'You are old\'. If their age is between 18 and 50, print \'You are an adult\'. If their age is below 18, print \'You are a child\'.'
        self.testcases = [
            KeywordTestcase(
                '15',
                ['child']
            ),
            KeywordTestcase(
                '20',
                ['adult']
            ),
            KeywordTestcase(
                '100',
                ['old']
            )
        ]

@api_bp.route('/run', methods=['POST'])
def run():
    req_json = json.loads(request.data)
    code = req_json.get('code')
    # task_id = req_json.get('taskID')
    task = DebugTask()
    
    print(code)
    sandbox = IsolateSandbox()
    source_code = SourceCode(code, Language.cast_from_document(LANGUAGE))
    results = []
    
    testcase_inputs = [tc.input for tc in task.testcases]
    passes = True
    for testcase, (output, status, message) in zip(
        task.testcases,
        sandbox.get_outputs(
            source_code,
            testcase_inputs,
            TIME_LIMIT,
            MEMORY_LIMIT)):
        verdict = Verdict.AC
        if status == Verdict.AC:
            # AC status means code ran successfully. Now we see if output is correct.
            for answer_keyword in testcase.answer_keywords:
                if answer_keyword not in output:
                    verdict = Verdict.WA
                    passes = False
                    break
        else:
            # TLE, MLE.
            verdict = status
            passes = False
        
        results.append(
            {
                # 'output': output,
                'verdict': verdict.cast_to_document(),
                'message': message
            }
        )
    response = {
        'time': datetime.utcnow().strftime('%a %-d %b %Y %H:%M'),
        'passes': passes,
        'results': results
    }
    # ! ADD TO DB HERE
    return jsonify(response)
