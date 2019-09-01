import re
import os
import pickle
from collections import Counter
import numpy as np
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity
import fasttext
import textstat
import sentencepiece as spm


use_tf = True

if use_tf:
    os.environ["TFHUB_CACHE_DIR"] = '/tmp/tfhub_modules'
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
    ("shame", "I'm sorry. I apologize. I feel regret, shame and embarrassment."),
    ("apocalyptic", "The end of the world is coming."),
]

sorts = [
    {"qs": "apocalyptic", "key": "apocalyptic", "display": "Most Apocalyptic"},
    {"qs": "chronological", "key": "created_at", "display": "Chronologically"},
    {"qs": "alphabetical", "key": "lower_text", "display": "Alphabetically"},
    {"qs": "favorites", "key": "favorites", "display": "Total Favorites"},
    {"qs": "retweets", "key": "retweets", "display": "Total Retweets"},
    {"qs": "length", "key": "length", "display": "Length"},
    {"qs": "hashtags", "key": "total_hashtags", "display": "Total Hashtags"},
    {"qs": "username", "key": "username", "display": "Alphabetically by Username"},
    {"qs": "userposts", "key": "total_userposts", "display": "Total User Posts"},
    {"qs": "marx", "key": "marx", "display": "Most Marxist"},
    {"qs": "kafka", "key": "kafka", "display": "Most Kafkaesque"},
    {"qs": "shame", "key": "shame", "display": "Shame"},
    {"qs": "ted", "key": "ted", "display": "TEDness"},
    {"qs": "emoji", "key": "total_emoji", "display": "Total Emoji"},
    {"qs": "nouns", "key": "total_noun", "display": "Noun Density"},
    {"qs": "verbs", "key": "total_verb", "display": "Verb Density"},
    {"qs": "adjectives", "key": "total_adj", "display": "Adjective Density"},
    {"qs": "numbers", "key": "total_num", "display": "Number of Numbers"},
    {
        "qs": "stop_words",
        "key": "total_stop",
        "display": "Density of Filler Words/Percentage of Words Which Are Filler Words",
    },
    {"qs": "named_entities", "key": "total_entities", "display": "Proper Noun Density"},
    {"qs": "antisemitism", "key": "antisemitism", "display": "Antisemitism"},
    {"qs": "eroticism", "key": "erotic", "display": "Eroticism"},
    # {
    #     "qs": "word_length",
    #     "key": "word_length",
    #     "display": "Average Word Length",
    # },
    {"qs": "drilism", "key": "__label__dril", "display": "dril-ism"},
    {"qs": "cop", "key": ["__label__CommissBratton"], "display": "Cop-Like"},
    {"qs": "goth", "key": "__label__sosadtoday", "display": "Gothness"},
    {
        "qs": "neoliberal",
        "key": ["__label__ThirdWayTweet", "__label__ChelseaClinton"],
        "display": "Neoliberalism",
    },
    {
        "qs": "advertising",
        "key": ["__label__amazon"],
        "display": "Similarity To Corporate Social Media Accounts",
    },
    {"qs": "gendered", "key": "total_gendered", "display": "Gendered"},
]

fast_model = fasttext.load_model("model_tweets.bin")
sentiment_analyzer = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 3000000


if use_tf:
    g = tf.Graph()
    with g.as_default():
        text_input = tf.sparse_placeholder(tf.int64, shape=[None, None])
        embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-lite/2")
        embedded_text = embed(
            inputs=dict(
                values=text_input.values,
                indices=text_input.indices,
                dense_shape=text_input.dense_shape,
            )
        )
        init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
    g.finalize()
    session = tf.Session(graph=g)
    session.run(init_op)

    spm_path = "/tmp/tfhub_modules/539544f0a997d91c327c23285ea00c37588d92cc/assets/universal_encoder_8k_spm.model"
    sp = spm.SentencePieceProcessor()
    sp.Load(spm_path)


def process_to_IDs_in_sparse_format(sp, sentences):
    # An utility method that processes sentences with the sentence piece processor
    # 'sp' and returns the results in tf.SparseTensor-similar format:
    # (values, indices, dense_shape)
    ids = [sp.EncodeAsIds(x) for x in sentences]
    max_len = max(len(x) for x in ids)
    dense_shape = (len(ids), max_len)
    values = [item for sublist in ids for item in sublist]
    indices = [[row, col] for row in range(len(ids)) for col in range(len(ids[row]))]
    return (values, indices, dense_shape)


def get_cosine_similarities(texts):
    for archetype, text in archetypes:
        texts.append(text)

    values, indices, dense_shape = process_to_IDs_in_sparse_format(sp, texts)

    text_embeddings = session.run(
        embedded_text,
        feed_dict={
            text_input.values: values,
            text_input.indices: indices,
            text_input.dense_shape: dense_shape,
        },
    )

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

        self.clean_text = re.sub(r"(https?:\/\/.*?|@.*?|RT:)( |$)", "", self.text)

        self.text = self.text.replace("&amp;", "&")
        self.lower_text = self.text.lower()
        self.doc = nlp(self.clean_text)
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

        if self.total_tokens > 2:
            parts = []
            for token in self.doc:
                parts.append(token.pos_.lower())
                if token.is_stop:
                    parts.append("stop")

            counter = Counter(parts)
            for key, val in counter.items():
                setattr(self, "total_" + key, val / self.total_tokens)

    def set_entity_count(self):
        self.total_entities = 0
        if self.total_tokens > 2:
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
    import sys
    import os
    import json
    import argparse

    parser = argparse.ArgumentParser(description='Other Orders sorts texts')

    parser.add_argument('filename')
    parser.add_argument('--sort', '-s', dest='sortname', required=True, help='Sort type', choices=sorted([s['qs'] for s in sorts]))
    parser.add_argument('--reverse', '-r', action='store_true', dest='reversed', required=False, default=False, help="Sort from high to low rather than low to high")

    args = parser.parse_args()

    filename = args.filename
    outname = filename + ".analysis.json"

    if not os.path.exists(outname):
        tagged_sentences = []

        with open(filename, "r") as infile:
            data = infile.read()

        doc = nlp(data)
        sentences = [s.text for s in doc.sents]
        sentences = [s.strip() for s in sentences]
        sentences = [s for s in sentences if s != "" and s != '"']
        results = analyze_lines(sentences)
        for i, r in enumerate(results):
            data = r.__dict__
            del data["doc"]
            data["created_at"] = i
            tagged_sentences.append(data)

        with open(outname, "w") as outfile:
            json.dump(tagged_sentences, outfile)
    else:
        with open(outname, "r") as infile:
            tagged_sentences = json.load(infile)

    sort_params = next((s for s in sorts if s["qs"] == args.sortname), sorts[0])

    if isinstance(sort_params["key"], list):
        tagged_sentences = sorted(
            tagged_sentences,
            key=lambda k: sum([k[keyname] for keyname in sort_params["key"]]),
            reverse=args.reversed,
        )
    else:
        tagged_sentences = sorted(
            tagged_sentences, key=lambda k: k[sort_params["key"]], reverse=args.reversed
        )

    for t in tagged_sentences:
        print(t["text"])

    # tests = [
    #     "this is a test",
    #     "god is dead",
    #     "he her she them",
    #     "israel is bad",
    #     "the police protect us",
    #     "where is hope?",
    # ]
    # results = analyze_lines(tests)
    # for r in results:
    #     print(r)
