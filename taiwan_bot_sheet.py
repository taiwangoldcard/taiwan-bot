import gspread, logging, json
from oauth2client.service_account import ServiceAccountCredentials
from config import DefaultConfig

_logger = logging.getLogger(__name__)
CONFIG = DefaultConfig()

class TaiwanBotSheet:

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    service_account_info_dict = json.loads(
        CONFIG.GOOGLE_SERVICE_ACCOUNT, strict=False)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info_dict, scope)

    client = gspread.authorize(creds)
    sheet = client.open("Taiwan Bot FAQ").worksheet("GoldCard FAQ")

    def __init__(self):
        _logger.info('Initiating TaiwanBotSheet')

    def get_questions_answers(self):
        sheet = self.client.open("Taiwan Bot FAQ").worksheet("GoldCard FAQ")
        questions = list(map(str.strip, sheet.col_values(1)[1:]))
        answers = list(map(str.strip, sheet.col_values(2)[1:]))

        return [questions, answers]

    def log_answers(self, question, answer, score):
        sheet = self.client.open("Taiwan Bot FAQ").worksheet("Log")

        next_row = len(sheet.get_all_values()) + 1
        sheet.update( 'A' + str(next_row) , question)
        sheet.update( 'B' + str(next_row) , answer)
        sheet.update( 'C' + str(next_row) , score)

