import json
import logging
from os import statvfs_result
import gspread
from config import DefaultConfig
from datetime import datetime
from enum import Enum
from oauth2client.service_account import ServiceAccountCredentials

_logger = logging.getLogger(__name__)
CONFIG = DefaultConfig()

SPREADSHEET_FAQ_FILE = "Taiwan Bot FAQ"
SPREADSHEET_LOG_FILE = "Taiwan Bot Log"

class SpreadsheetContext(Enum):
    GENERAL = 1
    GOLDCARD = 2
    LAW = 3

CONTEXTS = {
    SpreadsheetContext.GENERAL: {
        "qa_file": SPREADSHEET_FAQ_FILE,
        "log_file": SPREADSHEET_LOG_FILE,
        "sheet": "General"
    },
    SpreadsheetContext.GOLDCARD: {
        "qa_file": SPREADSHEET_FAQ_FILE,
        "log_file": SPREADSHEET_LOG_FILE,
        "sheet": "GoldCard"
    },
    SpreadsheetContext.LAW: {
        "qa_file": SPREADSHEET_FAQ_FILE,
        "log_file": SPREADSHEET_LOG_FILE,
        "sheet": "Law"
    },
}

class TaiwanBotSheet:

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    service_account_info_dict = json.loads(
        CONFIG.GOOGLE_SERVICE_ACCOUNT, strict=False)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info_dict, scope)
    client = gspread.authorize(creds)
    context = SpreadsheetContext.GENERAL

    def __init__(self, context=SpreadsheetContext.GENERAL):
        _logger.info('Initiating TaiwanBotSheet')
        self.context = context

    def get_questions_answers(self, context=None):
        if context is None:
            context = self.context

        spreadsheet = self.client.open(SPREADSHEET_FAQ_FILE)
        sheet = spreadsheet.worksheet(CONTEXTS[context]["sheet"])
        # Each question can potentially be multiple lines
        question_multiples = list(map(str.splitlines, list(map(str.strip, sheet.col_values(1)[1:]))))
        non_duplicated_answers = list(map(str.strip, sheet.col_values(2)[1:]))

        # The end result is duplicate answers for each row in the spreadsheet
        # that has multiple questions
        questions = []
        answers = []
        for index in range(len(question_multiples)):
            question_multiple = question_multiples[index]
            answer = non_duplicated_answers[index]
            for question in question_multiple:
                questions.append(question)
                answers.append(answer)

        return [questions, answers]

    def log_answers(self, user_question, similar_question, answer, score, state):
        sheet = self.client.open(SPREADSHEET_LOG_FILE).worksheet(CONTEXTS[self.context]["sheet"])
        next_row = len(sheet.get_all_values()) + 1
        sheet.update( 'A' + str(next_row) , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        sheet.update( 'B' + str(next_row) , user_question)
        sheet.update( 'C' + str(next_row) , similar_question)
        sheet.update( 'D' + str(next_row) , answer)
        sheet.update( 'E' + str(next_row) , score)
        sheet.update( 'F' + str(next_row) , state)

    def get_context(self):
        return CONTEXTS[self.context];

    def set_context(self, context):
        if context in CONTEXTS:
            self.context = context;
        else:
            _logger.error("This context type does not exist. Setting the GENERAL context instead...")
            self.context = SpreadsheetContext.GENERAL;
