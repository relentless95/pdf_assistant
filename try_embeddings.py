from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

passages = [
    "Batteries store energy for later use.",
    "Football players score goals on a pitch.",
    "Solar panels convert sunlight into electricity.",
]


question = "How can we keep electrical power for use later?"


passage_vectors = model.encode(passages, normalize_embeddings=True)


question_vector = model.encode(
    ["Represent this sentence for searching relevant passages: " + question],
    normalize_embeddings=True,
)

scores = cosine_similarity(question_vector, passage_vectors)[0]

results = []

for passage, score in zip(passages, scores):
    results.append({"content": passage, "score": float(score)})


results.sort(key=lambda result: result["score"], reverse=True)


print("Passage vectors shape:", passage_vectors.shape)
print("Question vector shape:", question_vector.shape)

for result in results:
    print(f"{result['score']: .3f} {result['content']}")
