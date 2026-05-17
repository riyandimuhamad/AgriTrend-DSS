# Machine Learning Model Artifacts & Documentation

Repositori ini menyimpan *baseline model artifact* dan dokumentasi teknis untuk modul Machine Learning pada sistem **Agri-Trend DSS**.

---

## 📊 Performa Model
* **R-squared ($R^2$) Score**: **98.65%** ✅
* **Mean Absolute Error (MAE)**: **1.7595 ton/hektar**

---

## 📂 Struktur File
1. **`agri_trend_rf_model.joblib`**: Objek model Random Forest Regressor (Di-upload via Git LFS).
2. **`model_features.joblib`**: Python list urutan kolom pasca *One-Hot Encoding*.

---

## 💻 Contoh Integrasi Backend (Streamlit)
```python
import joblib
import pandas as pd

model = joblib.load('ml_models/agri_trend_rf_model.joblib')
model_features = joblib.load('ml_models/model_features.joblib')

