import re
import pickle
from collections import Counter
import numpy as np
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity
import fasttext
import textstat

use_tf = True

if use_tf:
    import tensorflow as tf
    import tensorflow_hub as hub

# with open("capitol.txt", "r") as infile:
#     marx = "\n".join(infile.readlines()[0:200])
#
# with open("before_the_law.txt", "r") as infile:
#     kafka = infile.read()
#
# with open("ted.txt", "r") as infile:
#     ted = "\n".join(infile.readlines()[0:10])

archetypes = [
    ("marx", "Workers must seize the means of production."),
    ("kafka", "Hope exists, but not for us. My father judges me."),
    ("ted", "Technology will save the world."),
    (
        "erotic",
        "They ceased to be three bodies. They became all mouths and fingers and tongues and senses. Their mouths sought another mouth, a nipple, a clitoris. They lay entangled, moving very slowly. They kissed until the kissing became a torture and the body grew restless. Their hands always found yielding flesh, an opening.",
    ),
    ("shame", ". I'm sorry. I apologize. I feel regret, shame and embarrassment."),
]

fast_model = fasttext.load_model("model_tweets.bin")
sentiment_analyzer = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_sm")


if use_tf:
    g = tf.Graph()
    with g.as_default():
        text_input = tf.placeholder(dtype=tf.string, shape=[None])
        embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")
        embedded_text = embed(text_input)
        init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
    g.finalize()
    session = tf.Session(graph=g)
    session.run(init_op)


def get_cosine_similarities(texts):
    for archetype, text in archetypes:
        texts.append(text)

    text_embeddings = session.run(embedded_text, feed_dict={text_input: texts})

    similarity_matrix = cosine_similarity(np.array(text_embeddings))

    out = []

    for archetype, text in archetypes:
        index = texts.index(text)
        vals = np.array(similarity_matrix[index, :])
        out.append(vals)

    return out


def get_classifications(texts):
    out = []
    clean_texts = []
    for t in texts:
        t = re.sub(r"(https?:\/\/.*?|@.*?|RT:)( |$)", "", t)
        t = re.sub(r"[\U00010000-\U0010ffff]", "", t)
        t = t.replace("&amp;", "&").replace("#", "").replace("\n", " ")
        t = t.strip()
        clean_texts.append(t)

    all_labels, all_preds = fast_model.predict(clean_texts, k=len(fast_model.labels))
    all_preds = all_preds.tolist()
    return list(zip(all_labels, all_preds))


def analyze_lines(lines, textkey=None):
    out = []

    lines = [Weirdsort(l, key=textkey) for l in lines]
    texts = [l.text for l in lines]
    if use_tf:
        similarities = get_cosine_similarities(texts)
    classifications = get_classifications(texts)

    for index, line in enumerate(lines):
        if use_tf:
            line.apply_similarities(similarities, index)
        line.apply_classifications(classifications[index])

    return lines


class Weirdsort:
    def __init__(self, text, key=None):
        self.original = text

        if key is None:
            self.text = text
        else:
            self.text = text.get(key)

        self.text = self.text.replace('&amp;', '&')
        self.lower_text = self.text.lower()
        self.doc = nlp(self.text)
        self.total_tokens = len(self.doc)
        self.length = len(self.text)

        self.set_pos_count()
        self.set_sentiment()
        self.set_readability_score()
        self.set_gendered()
        self.set_emoji_count()
        self.set_entity_count()
        self.rank_antisemitism()
        self.set_hashtag_count()

    def set_pos_count(self):
        self.total_noun = 0
        self.total_verb = 0
        self.total_adj = 0
        self.total_num = 0
        self.total_stop = 0

        parts = []
        for token in self.doc:
            parts.append(token.pos_.lower())
            if token.is_stop:
                parts.append("stop")

        counter = Counter(parts)
        for key, val in counter.items():
            setattr(self, "total_" + key, val / self.total_tokens)

    def set_entity_count(self):
        self.total_entities = len(self.doc.ents) / self.total_tokens

    def set_hashtag_count(self):
        self.total_hashtags = self.text.count("#")

    def set_readability_score(self, mode="average"):
        clean_text = re.sub(r"(https?:\/\/.*?|@.*?|RT:)( |$)", "", self.text)
        self.grade_level = textstat.text_standard(clean_text, float_output=True)

    def set_sentiment(self):
        self.sentiment = sentiment_analyzer.polarity_scores(self.doc.text)

    def set_gendered(self):
        gendered_words = re.findall(
            r"\b(mr|ms|mr\.|ms\.|mrs|mrs\.|woman|man|lady|guy|girl|boy|gal|she|he|her|him|waitress|actress|hostess|landlady|mankind|congressman|congresswoman|policeman|mailman|prince|princess|queen|king)\b",
            self.text.lower(),
        )
        self.total_gendered = len(gendered_words)

    def set_emoji_count(self):
        self.total_emoji = len(re.findall(r"[\U00010000-\U0010ffff]", self.text))

    def rank_antisemitism(self):
        self.antisemitism = -1
        if "israel" in self.text.lower():
            self.antisemitism = self.sentiment["neg"]

    def apply_classifications(self, classifications):
        for label in fast_model.labels:
            setattr(self, label, 0)

        for label, val in zip(classifications[0], classifications[1]):
            setattr(self, label, val)

    def apply_similarities(self, similarities, index):
        # similarities = similarities.to_list()
        for i, archetype in enumerate(archetypes):
            setattr(self, archetype[0], similarities[i][index].item())

    def __repr__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    tests = [
        "this is a test",
        "god is dead",
        "he her she them",
        "israel is bad",
        "the police protect us",
        "where is hope?",
    ]
    results = analyze_lines(tests)
    for r in results:
        print(r)
