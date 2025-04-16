from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Placeholder model for demo purposes
model = DecisionTreeClassifier()
X = np.array([[1, 0, 1, 1], [0, 1, 0, 0]])  # symptoms etc.
y = [1, 0]
model.fit(X, y)

def predict_risk(user_input):
    pred = model.predict([user_input])
    return "High risk of diabetes" if pred[0] == 1 else "Low risk"
