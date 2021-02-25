gfrom pipelines import pipeline

nlp = pipeline("e2e-qg", model="valhalla/t5-base-e2e-qg")
qg = pipeline("e2e-qg")
print("preload finished.")