
def predict_with_confidence(model, text: str):
    # Get prediction probabilities
    probabilities = model.predict_proba([text])[0]

    # Find the class with the highest probability
    best_index = int(probabilities.argmax())

    prediction = str(model.classes_[best_index])

    confidence = round(
        float(probabilities[best_index]) * 100,
        2
    )

    return {
        "prediction": prediction,
        "confidence": confidence
    }
