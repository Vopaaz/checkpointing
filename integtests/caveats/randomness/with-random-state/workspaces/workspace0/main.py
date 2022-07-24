from sklearn.linear_model import LogisticRegression
from checkpointing import checkpoint

def build_model():
    X = [[0], [1], [10], [11]]
    y = [0, 0, 1, 1]
    model = LogisticRegression(solver="saga", random_state=42)
    return model.fit(X, y) 

@checkpoint()
def predict(model):
    print("Running")
    X = [[0], [1], [10], [11]]
    return model.predict(X).tolist()

if __name__ == "__main__":
    model = build_model()
    prediction = predict(model)
    print(prediction)

