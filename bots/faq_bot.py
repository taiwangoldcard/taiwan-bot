from datetime import datetime, timezone
import re

import numpy as np

from taiwan_bot_sheet import TaiwanBotSheet, SpreadsheetContext
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext, ConversationState
from botbuilder.schema import ChannelAccount
from .conversation_data import ConversationData
from models.nlp_lite import UniversalSentenceEncoderLite

GOLD_CARD_REGEX = "gold card"
SESSION_TIMEOUT_SECONDS = 300

class FAQBot(ActivityHandler):
    """A model to find the most relevant answers for specific questions."""

    def __init__(self, bot_sheet: TaiwanBotSheet, conversation_state: ConversationState):
        self.bot_sheet = bot_sheet
        self.conversation_state = conversation_state
        self.conversation_data_accessor = self.conversation_state.create_property(
            "ConversationData")
        self.regex = re.compile(GOLD_CARD_REGEX, re.IGNORECASE)

        self.encoder_model = UniversalSentenceEncoderLite()
        self.questions = {}
        self.answers = {}
        self.questions_embeddings = {}
        for context in [SpreadsheetContext.GENERAL, SpreadsheetContext.GOLDCARD]:
            self.questions[context], self.answers[context] = self.bot_sheet.get_questions_answers(context=context)
            self.questions_embeddings[context] = self.encoder_model.extract_embeddings(self.questions[context])

    async def on_message_activity(self, turn_context: TurnContext):
        conversation_data = await self.conversation_data_accessor.get(
            turn_context, ConversationData
        )

        self.detect_context(turn_context, conversation_data)

        conversation_data.timestamp = turn_context.activity.timestamp

        conversation_data.channel_id = turn_context.activity.channel_id
        conversation_data.recipient_id = turn_context.activity.recipient.id

        question = turn_context.activity.text
        best_answer, most_similar_question, score = self._find_best_answer(question, conversation_data.context)
        self.bot_sheet.log_answers(question, most_similar_question, best_answer, score)

        return await turn_context.send_activity(
            MessageFactory.text(best_answer)
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

    def _find_best_answer(self, question, context):
        assert context in self.questions_embeddings

        question_embedding = self.encoder_model.extract_embedding(question)
        scores = self.encoder_model.get_similarity_scores(question_embedding, self.questions_embeddings[context])
        most_similar_id = np.argmax(scores)
        most_similar_question = self.questions[context][most_similar_id]
        best_answer = self.answers[context][most_similar_id]

        return best_answer, most_similar_question, float(scores[most_similar_id])