gfrom pipeline import pipeline

nlp = pipeline("e2e-qg", model="valhalla/t5-base-e2e-qg")
qg = pipeline("e2e-qg")
qg2 = pipeline("multitask-qa-qg")
print("preload finished.")