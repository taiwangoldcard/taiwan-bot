import datetime
import json

from taiwan_bot_sheet import SpreadsheetContext, CONTEXTS


class ConversationData:
    def __init__(
        self,
        timestamp: datetime = None,
        channel_id: str = None,
        recipient_id: str = None,
        context: SpreadsheetContext = SpreadsheetContext.GENERAL,
    ):
        self.timestamp = timestamp
        self.channel_id = channel_id
        self.recipient_id = recipient_id
        self.context = context

    def toJSON(self):
        return json.dumps({
            'context': CONTEXTS[self.context]['sheet'],
            'channel_id': self.channel_id,
            'recipient_id': self.recipient_id,
            'timestamp': self.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
        })