from datetime import datetime, timezone
import re
import numpy as np
from tensorflow.python.ops.variables import _UNKNOWN

from taiwan_bot_sheet import TaiwanBotSheet, SpreadsheetContext
from botbuilder.adapters.slack import SlackRequestBody
from botbuilder.core import ActivityHandler, TurnContext, ConversationState
from .conversation_data import ConversationData
from models.nlp_lite import UniversalSentenceEncoderLite

GOLD_CARD_REGEX = "gold card"
SESSION_TIMEOUT_SECONDS = 300
UNKNOWN_ANSWER = "Sorry, I can't help with that yet. Try to ask another question!"
UNKNOWN_THRESHOLD = 0.5
NON_TEXT_QUESTION_REPLY = "Sorry, I only understand English. Please try again."
DEFAULT_WELCOME_MESSAGE = "Greetings! You may ask me anything about taiwan and I'll do my best to answer your questions 🧙 For starters, you may select a question from below 👇"
WELCOME_QUICK_REPLIES = ["Gold Card?",
                         "How's the rent?", "Tax in Taiwan?"]


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
            self.questions[context], self.answers[context] = self.bot_sheet.get_questions_answers(
                context=context)
            self.questions_embeddings[context] = self.encoder_model.extract_embeddings(
                self.questions[context])

    async def on_message_activity(self, turn_context: TurnContext):
        activity = turn_context.activity

        # TODO: looks like it's almost time to create an abstraction layer to handle channel-specific
        # already 2 use cases here: facebook + slack

        if activity.channel_id == "facebook":
            channel_data = activity.channel_data
            if "postback" in channel_data and channel_data["postback"]["payload"] == "get_started":
                def to_quick_reply(s):
                    return {
                        "content_type": "text",
                        "title": s,
                        "payload": s
                    }
                quick_replies = list(
                    map(to_quick_reply, WELCOME_QUICK_REPLIES))

                channel_data = {
                    "text": DEFAULT_WELCOME_MESSAGE,
                    "quick_replies": quick_replies
                }

                reply_activity = activity.create_reply(
                    DEFAULT_WELCOME_MESSAGE)
                reply_activity.channel_data = channel_data
                reply_activity.text = None

                return await turn_context.send_activity(reply_activity)

        conversation_data = await self.conversation_data_accessor.get(
            turn_context, ConversationData
        )
        self._copy_activity_details_to_conversation_data(activity, conversation_data)

        # We currently only support text-based conversations; no text, no service
        question = activity.text
        if question is not None:
            question = self._clean_question(question)
            question = self._detect_and_set_context(question, conversation_data)
            best_answer, most_similar_question, score = self._find_best_answer(
                question, conversation_data.context)
            if score < UNKNOWN_THRESHOLD:
                best_answer = UNKNOWN_ANSWER

            self.bot_sheet.log_answers(
                question, most_similar_question, best_answer, score, conversation_data.toJSON())
        else:
            best_answer = NON_TEXT_QUESTION_REPLY
            self.bot_sheet.log_answers(
                "non-text question", "N/A", best_answer, 0.0, conversation_data.toJSON())

        body = activity.channel_data

        reply_activity = activity.create_reply(
            best_answer
        )

        # TODO: we really need an acceptance test suite:
        # - checks if we are in a slack channel
        # - checks whether in are already in a thread
        if activity.channel_id == "slack" and body["SlackMessage"] is not None:
            slack_message = SlackRequestBody(**body["SlackMessage"])

            if slack_message.event.thread_ts is None:
                channel_data = {
                    "text": best_answer,
                    "thread_ts": slack_message.event.ts
                }

                reply_activity.channel_data = channel_data
                reply_activity.text = None

        return await turn_context.send_activity(
            reply_activity
        )

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conversation_state.save_changes(turn_context)

    def _clean_question(self, text: str):
        clean_text = text.replace("@taiwan-bot", "")
        return clean_text

    def _detect_and_set_context(self, text: str, conversation_data):
        if conversation_data.timestamp is not None:
            elapsed = datetime.now(timezone.utc) - conversation_data.timestamp

            if elapsed.total_seconds() > SESSION_TIMEOUT_SECONDS:
                conversation_data.context = SpreadsheetContext.GENERAL

        if re.search(self.regex, text) is not None:
            conversation_data.context = SpreadsheetContext.GOLDCARD

        ## allow for possibility of declaring contexts by prepending <gc> or <general>
        tokenized_text = text.split()               #split tokens (if any)
        if len(tokenized_text) > 0:                 #catch empty token list error
            if tokenized_text[0].lower() == "<gc>":         #context: gold card
                conversation_data.context = SpreadsheetContext.GOLDCARD
                text = " ".join(tokenized_text[1:])
            elif tokenized_text[0].lower() == "<general>":  #context: general
                conversation_data.context = SpreadsheetContext.GENERAL
                text = " ".join(tokenized_text[1:])
        return text
 
    def _find_best_answer(self, question, context):
        assert context in self.questions_embeddings

        question_embedding = self.encoder_model.extract_embedding(question)
        scores = self.encoder_model.get_similarity_scores(
            question_embedding, self.questions_embeddings[context])
        most_similar_id = np.argmax(scores)
        most_similar_question = self.questions[context][most_similar_id]
        best_answer = self.answers[context][most_similar_id]
        score = float(scores[most_similar_id])

        return best_answer, most_similar_question, score

    def _copy_activity_details_to_conversation_data(self, activity, conversation_data):
        conversation_data.timestamp = activity.timestamp
        conversation_data.channel_id = activity.channel_id
        conversation_data.recipient_id = activity.recipient.id
