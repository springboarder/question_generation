from pipelines import pipeline

nlp = pipeline("multitask-qa-qg")
qg = pipeline("e2e-qg")
print("preload finished.")