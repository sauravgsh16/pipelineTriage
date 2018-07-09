import jinja2
import os
import json

data = {
    'guidanceRegression':  ['<span class="timestamp"><b>16:28:24</b> </span>[Guidance_Regression_TC13882_Tractor_7R_FT4_IVT] 2018-06-25 16:28:20,947 - ERROR - Automazing.Common.utils.execute::_main - [\'Traceback (most recent call last):\\n\', \'  File "Automazing\\\\Common\\\\utils\\\\execute.py", line 311, in _main\\n    rc = engine.TestExecutionEngine(logger).run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 162, in run\\n    self._run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 154, in _run\\n    return self.execute_squish_test(testScript)\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 80, in execute_squish_test\\n    rVal = SquishTargetTestExecution(path, logger=self.logger).run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\squishtargettestexecution.py", line 58, in run\\n    stateMachine.go_next()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 78, in go_next\\n    self.currentState.go_next(self)\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 148, in go_next\\n    if not self._eval_conditions_execute_actions():\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 178, in _eval_conditions_execute_actions\\n    action()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\squishtargettestexecution.py", line 367, in check_if_test_execution_failed\\n    raise TestExecutionFailure(os.environ[\\\'TEST_SCRIPT\\\'])\\n\', \'TestExecutionFailure: Test execution of Guidance_Regression_TC13882_Tractor_7R_FT4_IVT failed!\\n\']\r'],
    'combine': ['<span class="timestamp"><b>12:14:37</b> </span>[combine_smoke_intake.py] 2018-06-25 12:14:36,802 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04ABA1D8&gt;, len(iData) = 1048576\r'], 
    'sprayer': ['<span class="timestamp"><b>12:14:30</b> </span>[sprayer_smoke_intake.py] 2018-06-25 12:14:29,513 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04A9F1D8&gt;, len(iData) = 1048576\r'], 
    'tractor': ['<span class="timestamp"><b>12:19:59</b> </span>[tractor_smoke_intake.py] 2018-06-25 12:19:55,782 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04B8B338&gt;, len(iData) = 1048576\r'], 
    'tractor_SG4_4200': []
}
l = [1, 2, 3, 4 , 5]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def main(data):
    template = JINJA_ENVIRONMENT.get_template('index.html')
    output = template.render(contents=data, buildNumber=1000)
    with open('blah.html', 'w') as f:
        f.write(output)


if __name__ == '__main__':
    main(data)