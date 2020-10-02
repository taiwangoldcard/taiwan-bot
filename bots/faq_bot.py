from datetime import datetime, timezone
from taiwan_bot_sheet import SpreadsheetContext
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext, ConversationState
from botbuilder.schema import ChannelAccount
from .conversation_data import ConversationData
import re

GOLD_CARD_REGEX = "gold card"
SESSION_TIMEOUT_SECONDS = 300

class FAQBot(ActivityHandler):
    """A model to find the most relevant answers for specific questions."""

    def __init__(self, qa_model, conversation_state: ConversationState):
        self.qa_model = qa_model
        self.conversation_state = conversation_state
        self.conversation_data_accessor = self.conversation_state.create_property(
            "ConversationData")
        self.regex = re.compile(GOLD_CARD_REGEX, re.IGNORECASE)

    async def on_message_activity(self, turn_context: TurnContext):
        conversation_data = await self.conversation_data_accessor.get(
            turn_context, ConversationData
        )

        self.detect_context(turn_context, conversation_data)

        conversation_data.timestamp = turn_context.activity.timestamp

        conversation_data.channel_id = turn_context.activity.channel_id
        conversation_data.recipient_id = turn_context.activity.recipient.id

        # TODO: find_best_answer should be called on different set based on context
        return await turn_context.send_activity(
            MessageFactory.text(
                self.qa_model.find_best_answer(turn_context.activity.text)
            )
        )

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conversation_state.save_changes(turn_context)

    def detect_context(self, turn_context: TurnContext, conversation_data):
        if conversation_data.timestamp is not None:
            elapsed = datetime.now(timezone.utc) - conversation_data.timestamp

            if elapsed.total_seconds() > SESSION_TIMEOUT_SECONDS:
                conversation_data.context = SpreadsheetContext.GENERAL

        if re.search(self.regex, turn_context.activity.text) is not None:
            conversation_data.context = SpreadsheetContext.GOLDCARD
