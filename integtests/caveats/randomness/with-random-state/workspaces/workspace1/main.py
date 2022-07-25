from sklearn.linear_model import LogisticRegression
from checkpointing import checkpoint

def build_model():
    X = [[i] for i in range(100)]
    y = [0 for _ in range(50)] + [1 for _ in range(50)]
    model = LogisticRegression(solver="saga", random_state=42)
    return model.fit(X, y) 

@checkpoint()
def predict(model):
    print("Running")
    X = [[0], [1], [99], [100]]
    return model.predict(X).tolist()

if __name__ == "__main__":
    model = build_model()
    prediction = predict(model)
    print(prediction)

