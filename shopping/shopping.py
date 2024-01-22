import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # List to store evidence and labels
    evidence = []
    labels = []
    # Dictionary to convert non-numerical values to numerical values
    convert = {
            "Jan": 0,
            "Feb": 1,
            "Mar": 2,
            "Apr": 3,
            "May": 4,
            "June": 5,
            "Jul": 6,
            "Aug": 7,
            "Sep": 8,
            "Oct": 9,
            "Nov": 10,
            "Dec": 11,
            "Returning_Visitor": 1,
            "New_Visitor": 0,
            "Other": 0,
            "TRUE": 1,
            "FALSE": 0,
            }
    
    # Open and read file
    with open(filename, newline='') as file:
        reader = csv.reader(file)
        # Skip header row
        next(reader)
        
        # Iterate through every row
        for row in reader:
            counter = 0
            # List to store evidence from current row in
            erow = []
            # Iterate through every value in row
            for value in row:
                # Count on which value of row is operated on
                counter = counter + 1
                # 18th value of row is label, so append values to evidence and labels list
                if counter == 18:
                    evidence.append(erow)
                    labels.append(convert.get(value))
                # Convert non-numerical values to numerical values using convertion dictionary before adding to evidence list
                elif counter == 11 or counter == 16 or counter == 17:
                    erow.append(convert.get(value))
                # Append float value to list of evidence from current row
                elif counter == 2 or counter == 4 or 6 <= counter <= 10:
                    erow.append(float(value))
                # Append int value to list of evidence from current row
                else:
                    erow.append(int(value))
    
    # Return a tuple of evidence and labels
    return evidence, labels

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # Define and fit k-nearest neighbor model (k=1)
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    # Return model
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # Initialise count of positive and negative labels
    pos = 0
    neg = 0
    # Initialise sensitivity and specificitiy
    sensitivity = 0
    specificity = 0
    
    # Loop over every label and prediction
    for label, prediction in zip(labels, predictions):
        # Add 1 to positive label count if label positive
        if label == 1:
            pos += 1
            # Add 1 to sensitivity count if prediction is also positive
            if prediction == 1:
                sensitivity += 1
        # Add 1 to negative label count if label is negative
        else:
            neg += 1
            # Add 1 to specificity count if predictino is also negative
            if prediction == 0:
                specificity += 1
    
    # Divide sensitivity and specificity by number of positive and negative labels respectfully
    sensitivity = sensitivity / pos
    specificity = specificity / neg
    
    # Return sensitivity and specificity
    return (sensitivity, specificity)

if __name__ == "__main__":
    main()
