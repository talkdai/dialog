import logging

from sklearn.feature_extraction.text import CountVectorizer

from .helpers import stopwords

logger = logging.getLogger(__name__)


async def categorize_conversation_history(psql_memory) -> None:
    """
    Categories conversation history in background
    """
    messages = [m.content for m in psql_memory.messages]
    vetorizer = CountVectorizer(max_df=0.85, stop_words=stopwords)
    vetorizer.fit_transform(messages)
    keywords = ", ".join(vetorizer.vocabulary_.keys())
    logger.info(f"keywords: {keywords}")
    psql_memory.add_tags(keywords)
