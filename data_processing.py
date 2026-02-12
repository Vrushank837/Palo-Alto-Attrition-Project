import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

def process_data():
    # Load
    df = pd.read_csv('data/Palo Alto Networks.csv')

    # Feature Engineering
    df['Income_Experience_Ratio'] = df['MonthlyIncome'] / (df['TotalWorkingYears'] + 1)
    df['Engagement_Score'] = (df['JobInvolvement'] + df['JobSatisfaction'] + 
                              df['EnvironmentSatisfaction'] + df['RelationshipSatisfaction']) / 4
    df['Promotion_Delay_Ratio'] = df['YearsSinceLastPromotion'] / (df['YearsAtCompany'] + 1)

    # Encoding
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Model Training (Logistic Regression for high Recall)
    X = df.drop('Attrition', axis=1)
    y = df['Attrition']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(class_weight='balanced', random_state=42)
    model.fit(X_scaled, y)

    # Generate Probabilities
    df['Attrition_Probability'] = model.predict_proba(X_scaled)[:, 1]
    
    # Categorize
    def categorize(p):
        if p < 0.3: return 'Low Risk'
        elif p < 0.6: return 'Medium Risk'
        else: return 'High Risk'
    
    df['Risk_Category'] = df['Attrition_Probability'].apply(categorize)
    
    # Save processed data
    df.to_csv('data/Employee_Risk_Scores.csv', index=False)
    print("Success: Employee_Risk_Scores.csv generated in data folder.")

if __name__ == "__main__":
    process_data()