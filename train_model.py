import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("⏳ Loading data...")
try:
    df = pd.read_csv('creditcard.csv')
    
    fraud = df[df['Class'] == 1]
    normal = df[df['Class'] == 0].sample(5000, random_state=42)
    
    data = pd.concat([fraud, normal])
    
    X = data.drop(columns=['Class', 'Time']) 
    y = data['Class']
    
    print(f"Ready! Total data: {len(data)}")

except FileNotFoundError:
    print("creditcard.csv")
    exit()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🧠 Training Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"\n🚀 Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(classification_report(y_test, y_pred))

joblib.dump(model, 'model_fraud.pkl')
print("💾 Model saved: model_fraud.pkl")
