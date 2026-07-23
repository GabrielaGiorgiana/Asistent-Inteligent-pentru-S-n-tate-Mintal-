"""
Antreneaza un model de clasificare a starii emotionale (negativ vs pozitiv)
pe un dataset public de propozitii in limba romana.

Dataset: dumitrescustefan/ro_sent (recenzii de produse si filme in romana,
adnotate cu 0 = negativ, 1 = pozitiv). Sursa: Hugging Face Datasets.
Paper: Dumitrescu et al., "The birth of Romanian BERT", 2020.

Ruleaza o singura data (necesita internet, pentru a descarca dataset-ul):
    python train_emotion_model.py
"""
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import joblib

print("Descarc dataset-ul ro_sent de pe Hugging Face...")
try:
    # Incercare normala (functioneaza pentru majoritatea dataset-urilor)
    dataset = load_dataset("dumitrescustefan/ro_sent")
except RuntimeError:
    # dataset-uri mai vechi, care foloseau un script .py de incarcare, nu
    # mai sunt acceptate direct de versiunile noi ale bibliotecii `datasets`.
    # HF pastreaza insa o versiune convertita automat in format Parquet,
    # pe un branch special - o folosim ca alternativa.
    print("Formatul vechi nu mai e suportat, incerc versiunea Parquet convertita automat...")
    dataset = load_dataset("dumitrescustefan/ro_sent", revision="refs/convert/parquet")

train_texts = dataset["train"]["sentence"]
train_labels = dataset["train"]["label"]
test_texts = dataset["test"]["sentence"]
test_labels = dataset["test"]["label"]

print(f"Exemple antrenare: {len(train_texts)} | Exemple test: {len(test_texts)}")

print("\nVectorizare text (TF-IDF, unigrame + bigrame)...")
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
X_train = vectorizer.fit_transform(train_texts)
X_test = vectorizer.transform(test_texts)

print("Antrenare model (Regresie Logistica)...")
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, train_labels)

print("\nEvaluare pe setul de test...")
predictions = model.predict(X_test)

accuracy = accuracy_score(test_labels, predictions)
precision, recall, f1, _ = precision_recall_fscore_support(
    test_labels, predictions, average="binary"
)

print("\n--- REZULTATE ---")
print(f"Acuratete: {accuracy:.4f}")
print(f"Precizie:  {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 score:  {f1:.4f}")
print("\nRaport detaliat pe clase:")
print(classification_report(test_labels, predictions, target_names=["negativ", "pozitiv"]))

joblib.dump(model, "emotion_model.joblib")
joblib.dump(vectorizer, "emotion_vectorizer.joblib")
print("\nModel salvat: emotion_model.joblib + emotion_vectorizer.joblib")
print("Poti copia aceste 2 fisiere ca dovada in livrabilul final (Cerinta 6).")
