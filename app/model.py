import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression # Changed model to LinearRegression
from sklearn.metrics import mean_squared_error # Changed metric to mean_squared_error

data=pd.read_csv('D:/climate test.csv')


X = data.drop('date', axis=1)
y = data['meantemp']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple Linear Regression model # Changed model to LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred) # Changed metric to mean_squared_error
print(f"Model Mean Squared Error: {mse:.2f}")

import pickle

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)





# Train a Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model to a Pickle file
with open('trained_model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Load the trained model from the Pickle file
with open('trained_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# Verify the type of the loaded model
print(type(loaded_model))  # Should be <class 'sklearn.linear_model._linear.LinearRegression'>

# Use the loaded model for predictions
predictions = loaded_model.predict(X_test)

# Print predictions
print(predictions)

# Evaluate the model using mean squared error
mse = mean_squared_error(y_test, predictions)
print(f"Model Mean Squared Error: {mse:.2f}")
