from taiwan_bot_sheet import SpreadsheetContext
import datetime


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
