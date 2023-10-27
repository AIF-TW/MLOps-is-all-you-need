flower_classes = ["setosa", "versicolor", "virginica"]

def iris_classes(preds):
    res = [flower_classes[i] for i in preds]
    return res