from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from config import DefaultConfig

CONFIG = DefaultConfig()

class FAQBot(ActivityHandler):
    """A model to find the most relevant answers for specific questions."""

    def __init__(self, qa_model):
        self.qa_model = qa_model
    
    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        return await turn_context.send_activity(
            MessageFactory.text(
                self.qa_model.find_best_answer(CONFIG.CONTEXT_GENERAL, turn_context.activity.text)
            )
        )
