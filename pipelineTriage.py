''' Script to triage pipeline and generate report '''
import os
import requests
import re
import datetime
from bs4 import BeautifulSoup
from functools import wraps

ERROR_CAPTURE_REGEX = '^.*{}.*(ERROR|(Exception.*Fail)).*(Traceback)?(.*)'


def error_grab(line, suite):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            regex = re.compile(ERROR_CAPTURE_REGEX.format(suite))
            if regex.match(line) and 'Got IOError' not in line:
                func(line)
        return wrapper
    return decorator


class InvalidStatusCodeException(Exception):
    ''' Exception class for invalid status code '''
    pass


class InvalidBuildRequestType(Exception):
    ''' InvalidBuildRequestType '''
    pass


class IncorrectResultFormatException(Exception):
    ''' IncorrectResultFormatException '''
    pass


class PipelineBuildDetails(object):
    ''' Class to triage pipeline '''

    BUILD_URLS = {
        'x': 'y'
    }
    BUILD_NUM_REGEX = re.compile(r'\#(?P<buildNumber>\d+)')
    BUILD_DATE_REGEX = re.compile(r'(?P<buildDate>\w+ \d+\, \d+ \d+\:\d+ \w+)')

    def __init__(self, buildType='integration'):
        try:
            self._url = self.BUILD_URLS[buildType]
        except KeyError:
            raise InvalidBuildRequestType('Invalid build type: %s' % buildType)
        self._res = self._get_page_content()
        self._soup = self._initialize_soup()

    def _get_page_content(self):
        ''' get_page_text '''
        res = requests.get(self._url)
        if res.status_code == 200:
            return res.content
        raise InvalidStatusCodeException(
            'Status code: %s for %s "INVALID"' % (res.status_code, self._url))

    def _initialize_soup(self):
        ''' _initialize_soup '''
        return BeautifulSoup(self._res, 'html.parser')

    def _get_build_details(self, regex, name):
        ''' Finds the build number present in page '''
        buildDetails = []
        for td in self._soup.findAll('td', class_='build-row-cell'):
            for anchor in td.findAll('a', href=True):
                match = regex.match(anchor.text)
                if match:
                    buildDetails.append(match.group(name))
        return buildDetails

    def get_build_details(self):
        buildNumbers =\
            self._get_build_details(self.BUILD_NUM_REGEX, 'buildNumber')
        buildDate = [
            datetime.datetime.strptime(date, '%b %d, %Y %I:%M %p').date() for
            date in self._get_build_details(self.BUILD_DATE_REGEX, 'buildDate')
        ]
        buildNumbers.sort(reverse=True)
        buildDate.sort(reverse=True)
        return zip(buildNumbers, buildDate)


class StateDispatcher(object):
    ''' State Dispatcher '''

    def __init__(self, state_attr='_state'):
        self.registry = {}
        self._state_attr = state_attr

    def __get__(self, instance, owner):
        if instance is None:
            return self
        method = self.registry[getattr(instance, self._state_attr)]
        return method.__get__(instance, owner)

    def register(self, state):
        def decorator(method):
            self.registry[state] = method
            return method
        return decorator


class StateMachine(object):
    ''' StateMachine '''

    REGEX = '^.*{}.*(ERROR|(Exception.*Fail)).*(Traceback)?(.*)'
    dispatch = StateDispatcher()
    _state = None

    def __init__(self):
        self.sprayer = []
        self.combine = []
        self.tractor = []
        self.tractor_SG4 = []
        self.tractor_SG4_4200 = []
        self.guidanceRegression = []

    @dispatch.register('sprayer_smoke_intake.py')
    def _(self, line):
        self.sprayer.append(line)

    @dispatch.register('combine_smoke_intake.py')
    def _(self, line):
        self.combine.append(line)

    @dispatch.register('tractor_smoke_intake.py')
    def _(self, line):
        self.tractor.append(line)

    @dispatch.register('tractor_smoke_intake_SG4.py')
    def _(self, line):
        self.tractor_SG4.append(line)

    @dispatch.register('tractor_smoke_intake_SG4_4200.py')
    def _(self, line):
        self.tractor_SG4_4200.append(line)

    @dispatch.register('Guidance_Regression_TC13882_Tractor_7R_FT4_IVT')
    def _(self, line):
        self.guidanceRegression.append(line)


class TriageBase(object):
    ''' Base class for triaging '''

    BASE_REGEX = '^.*({}).*$'
    SUITES = ''

    def __init__(self, buildNum):
        self.url = self._get_build_url(buildNum)
        self.pageContent = self._get_page_content()
        self.soup = self._initialize_soup()
        self.stateMachine = None

    def _get_build_url(self, buildNum):
        ''' returns url for particular build '''
        raise NotImplementedError

    def _get_page_content(self):
        ''' _get_page_content '''
        res = requests.get(self.url)
        if res.status_code == 200:
            return res.content
        raise InvalidStatusCodeException(
            'Status code: %s for %s "INVALID"' % (res.status_code, self.url))

    def _initialize_soup(self):
        ''' _initialize_soup '''
        return BeautifulSoup(self.pageContent, 'html.parser')

    def parse_page_content(self):
        ''' parse_page_content '''
        consoleData = self.soup.findAll('pre', class_='console-output')
        stringData = str(consoleData[0])
        for line in stringData.split('\n'):
            for suite in self.SUITES:
                regex = re.compile(self.BASE_REGEX.format(suite))
                if regex.match(line):
                    self.stateMachine._state = suite
                    error_grab(line, suite)(self.stateMachine.dispatch)()
        else:
            print 'Data Inappropriate'


class TriageIntegration(TriageBase):
    ''' TriageIntegration '''

    INTEGRATION_URL = ''
    SUITES = [
        'sprayer_smoke_intake.py',
        'combine_smoke_intake.py',
        'tractor_smoke_intake.py',
        'tractor_smoke_intake_SG4.py',
        'tractor_smoke_intake_SG4_4200.py',
        'Guidance_Regression_TC13882_Tractor_7R_FT4_IVT'
    ]

    def __init__(self, buildNum):
        super(TriageIntegration, self).__init__(buildNum)
        self.stateMachine = StateMachine()

    def _get_build_url(self, buildNum):
        ''' returns url for particular build '''
        return self.INTEGRATION_URL.format(str(buildNum))


class TriageDefault(TriageBase):
    ''' TriageIntegration '''

    DEFAULT_URL = ''
    SUITES = [
        'sprayer_smoke_intake.py',
        'combine_smoke_intake.py',
        'tractor_smoke_intake.py',
        'tractor_smoke_intake_SG4.py',
        'tractor_smoke_intake_SG4_4200.py'
    ]

    def __init__(self, buildNum):
        super(TriageDefault, self).__init__(buildNum)
        self.stateMachine = StateMachine()

    def _get_build_url(self, buildNum):
        ''' returns url for particular build '''
        return self.DEFAULT_URL.format(str(buildNum))


def main():
    today = datetime.datetime.today().date()
    # for pipeline in ['integration', 'default']:
    # @TODO : remove below time delta
    simulateDate = (today - datetime.timedelta(days=11))
    buildDetails = PipelineBuildDetails()
    finalResult = {}
    for buildNum, date in buildDetails.get_build_details():
        if simulateDate == date:
            default = TriageIntegration(buildNum)
            default.parse_page_content()
            result = {key: value for key, value in
                      default.stateMachine.__dict__.iteritems()
                      if not key.startswith('_') and value != []}
            finalResult = dict(finalResult.items() + result.items())
    return finalResult


class GenerateHTML(object):
    ''' Generate result HTML '''

    def __init__(self, result):
        if not isinstance(result, dict):
            raise IncorrectResultFormatException
        self.result = result

    def _write_tags(self, value, tag):
        ''' _write_tags '''
        if tag == 'td':
            return '<td>{}</td>'.format(value)
        return '<tr>{}</tr>'.format(value)

    def generate(self, result):
        ''' generate '''
        for key, values in result.iteritems():
            dataStr = ''
            for value in values:
                value = self._write_tags(value, 'td')
                dataStr += value

if __name__ == '__main__':
    main()


'''
{'guidanceRegression': ['<span class="timestamp"><b>16:28:24</b> </span>[Guidance_Regression_TC13882_Tractor_7R_FT4_IVT] 2018-06-25 16:28:20,947 - ERROR - Automazing.Common.utils.execute::_main - [\'Traceback (most recent call last):\\n\', \'  File "Automazing\\\\Common\\\\utils\\\\execute.py", line 311, in _main\\n    rc = engine.TestExecutionEngine(logger).run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 162, in run\\n    self._run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 154, in _run\\n    return self.execute_squish_test(testScript)\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\executeengine.py", line 80, in execute_squish_test\\n    rVal = SquishTargetTestExecution(path, logger=self.logger).run()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\squishtargettestexecution.py", line 58, in run\\n    stateMachine.go_next()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 78, in go_next\\n    self.currentState.go_next(self)\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 148, in go_next\\n    if not self._eval_conditions_execute_actions():\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\aftcommonlib\\\\statemachine.py", line 178, in _eval_conditions_execute_actions\\n    action()\\n\', \'  File "c:\\\\python27\\\\lib\\\\site-packages\\\\testexec\\\\squishtargettestexecution.py", line 367, in check_if_test_execution_failed\\n    raise TestExecutionFailure(os.environ[\\\'TEST_SCRIPT\\\'])\\n\', \'TestExecutionFailure: Test execution of Guidance_Regression_TC13882_Tractor_7R_FT4_IVT failed!\\n\']\r'], 'combine': ['<span class="timestamp"><b>12:14:37</b> </span>[combine_smoke_intake.py] 2018-06-25 12:14:36,802 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04ABA1D8&gt;, len(iData) = 1048576\r'], 'sprayer': ['<span class="timestamp"><b>12:14:30</b> </span>[sprayer_smoke_intake.py] 2018-06-25 12:14:29,513 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04A9F1D8&gt;, len(iData) = 1048576\r'], 'tractor': ['<span class="timestamp"><b>12:19:59</b> </span>[tractor_smoke_intake.py] 2018-06-25 12:19:55,782 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04B8B338&gt;, len(iData) = 1048576\r'], 'tractor_SG4_4200': ['<span class="timestamp"><b>13:58:59</b> </span>[tractor_smoke_intake_SG4_4200.py] 2018-06-25 13:58:59,717 - ERROR - aftreprogram.cleaninstall::_write - oFile = &lt;open file \'&lt;fdopen&gt;\', mode \'rb+\' at 0x04C0E390&gt;, len(iData) = 1048576\r']}
'''