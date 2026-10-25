from backend.embeddings import embed_passages, embed_question
from sklearn.metrics.pairwise import cosine_similarity


passages = [
    "Batteries store electrical energy for use when generation is low.",
    "Solar panels convert sunlight into electricity and generate less on cloudy days.",
    "Wind turbines use moving air to generate electricity.",
    "An inverter converts direct current into alternating current.",
    "Battery capacity describes how much energy a battery can store.",
    "Battery power describes how quickly a battery can charge or discharge.",
    "Charging and discharging lose some energy, so batteries return less than they receive.",
    "Electricity can be imported from the grid when local generation is insufficient.",
    "Insulating a building reduces heat loss and can lower heating demand.",
    "Football teams try to score goals while preventing their opponents from scoring.",
    "Bread dough rises because yeast produces gas during fermentation.",
    "Regular watering helps plants grow, but excessive watering can damage their roots."
]

questions = [
    "How can we keep electricity for later?",
    "What happens to solar generation when clouds block the sun?",
    "How can moving air produce electrical power?",
    "Which equipment changes DC electricity into AC?",
    "What determines the amount of energy a battery can hold?",
    "What determines how fast stored energy can be delivered?",
    "Why don't we get back all the energy used to charge a battery?",
    "Where can a community get electricity when its own supply is too low?",
    "How can a home retain warmth?",
    "Why does dough expand before baking?",
    "Can giving a plant too much water harm it?",
    "How does a bicycle brake work?"
]

passage_vectors = embed_passages(passages)

for question in questions:
    question_vector = embed_question(question)
    scores = cosine_similarity(question_vector, passage_vectors)[0]

    results = []

    for passage, score in zip(passages, scores):
        results.append({
            "content": passage,
            "score": float(score)
        })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    print(f"\nQuestion: {question}")

    for rank, result in enumerate(results[:3], start=1):
        print(
            f"{rank}. {result['score']:.3f}: "
            f"{result['content']}"
        )