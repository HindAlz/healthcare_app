"""Toy classifier only: two invented examples, no clinical validity."""
from sklearn.tree import DecisionTreeClassifier
import numpy as np

model = DecisionTreeClassifier(random_state=42)
model.fit(np.array([[1, 0, 1, 1], [0, 1, 0, 0]]), [1, 0])

def predict_risk(user_input):
    prediction = model.predict([user_input])[0]
    return f"Demo classification: {'High' if prediction == 1 else 'Low'} (unvalidated; not a health assessment)"
