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
    month_map = {'Jan':1, "Feb":2, "Mar":3, "Apr":4, "May":5, "June":6, 
            "Jul": '7', "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec": 12} 
    visitor_map = {"Returning_Visitor":1, "New_Visitor":0, "Other":0}  
    binary_map = {"TRUE": 1,"FALSE":0}
    type_map = {"Administrative":int(),"Administrative_Duration":float(),
        "Informational":int(),"Informational_Duration":float(),"ProductRelated":int(),"ProductRelated_Duration":float(),
        "BounceRates":float(),"ExitRates":float(),"PageValues":float(),"SpecialDay":float(),"Month":str(),
        "OperatingSystems":int(),"Browser":int(),"Region":int(),"TrafficType":int(),
        "VisitorType":int(),"Weekend" :int(),"Revenue":int()}

    # Initialize lists
    evidence = list()
    labels = list()

    # Open csv file in reading mode
    with open(filename, 'r') as data_file:
        reader = csv.DictReader(data_file)
        order = reader.fieldnames

        for data_row in reader:
            evidence_buffer = list()
            for key in order[:len(order)-1]:
                # Value of each key in the row
                value = data_row[key]

                # if inconsistent data types, i.e:
                if type(data_row[key]) != type_map[key]:
                    if key == "Month":
                        evidence_buffer.append(month_map[value])
                    elif key == "Weekend":
                        evidence_buffer.append(binary_map[value])
                    elif  key == "VisitorType":
                        evidence_buffer.append(visitor_map[value])
                    elif type(data_row[key]) == int:
                        evidence_buffer.append(int(value))
                    elif type(data_row == float):
                        evidence_buffer.append(float(value))
                else:
                    evidence_buffer.append(value)

            evidence.append(evidence_buffer)
            labels.append(binary_map[data_row["Revenue"]])

    return (evidence, labels)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # Return neigbors and distances after fitting evidence and labels
    return KNeighborsClassifier(n_neighbors=1).fit(evidence,labels)



def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # Initialize elements of confusion matrix
    true_positive = 0
    true_negative = 0
    false_positive = 0 
    false_negative = 0

    # Calculate the elements of confusion matrix
    for a, b in zip(labels, predictions):
        if a == 1 and a == b:
            true_positive += 1
        elif a == 1 and a != b:
            false_negative += 1
        elif a == 0 and a != b:
            false_positive += 1
        else:
            true_negative += 1

    # Calculate evaluation metrics 
    sensitivity = true_positive / (true_positive + false_negative)
    specificity = true_negative / (true_negative + false_positive)

    return sensitivity, specificity

if __name__ == "__main__":
    main()
