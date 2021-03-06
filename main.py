from sklearn.model_selection import train_test_split, LeaveOneOut
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import math

UNUSED_FEATURES = {0, 1, 2, 3, 4, 5, 6, 12, 13, 14, 15}
DATA_FILE = "./Resources/dow_jones_index.data"
NUM_FEATURES, NUM_SAMPLES = 0, 0
NUM_CLASSES = 2
T_SIZE = .05

def main():
    '''  Evaluates Gaussian Naive Bayes, KNN, SVC, and KMeans classifiers  '''

    gnb_score, knn_score, svc_lscore, svc_p3score, svc_p5score, kmeans_score = 0, 0, 0, 0, 0, 0
    # Default: 1,  I made this variable and following loop for testing purposes to see averages

    knn_results = dict()
    X, y = preprocess()
    print('Number of "usable" samples: {}'.format(NUM_SAMPLES)) 
    # --When testing with LOOCV--
    # loo = LeaveOneOut()
    # for train_index, test_index in loo.split(X):
    #     X_train, X_test = X[train_index], X[test_index]
    #     y_train, y_test = y[train_index], y[test_index]
    num_tests = 1000
    for i in range(num_tests):
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=T_SIZE)
        gnb_score += gnb(X_train, y_train, X_test, y_test)
        knn_scores = knn(X_train, y_train, X_test, y_test)
        for i in knn_scores:
            if i[0] in knn_results:
                knn_results[i[0]] += i[1]
            else:
                knn_results[i[0]] = i[1]
        svc_temp = svm(X_train, y_train, X_test, y_test)
        svc_lscore += svc_temp[0][1]
        svc_p3score += svc_temp[1][1]
        svc_p5score += svc_temp[2][1]
        kmeans_score += kmeans(X_train, y_train, X_test, y_test)


    # On average, I was seeing 53% accuracy
    print("\nGaussian Naive Bayes")
    print(gnb_score/num_tests)
    # TODO -- Graph ROC again

    # On average, I was seeing 49~50% accuracy
    # N = 6 consistantly gave the highest performance of 51%
    print("\nK-Nearest Neighbors")
    knn_scores = []
    for neighbs, result in knn_results.items():
        knn_scores.append((neighbs, result))
    for result in sorted(knn_scores):
        print(result[0],' : ',result[1]/num_tests)

    # KNN Vs. GNB?
    # For this data, Gaussian NB outperforms KNN with a 4 percent difference

    # For this data, it seems that linear vs poly3 vs poly 5 slight difference
    # Polys tended to do better than linear
    # On average, I was seeing ~55% accuracy
    print("\nSupport Vector Machine Linear")
    print(svc_lscore/num_tests)
    print("\nSupport Vector Machine Poly 3")
    print(svc_p3score/num_tests)
    print("\nSupport Vector Machine Poly 5")
    print(svc_p5score/num_tests)

    # SVM seemed to be more consistant than the others in regards to accuracy %
    # KNN and GNB's accuracy fluctuated test-to-test

    # On average, I was seeing ~50% accuracy........
    print("\nK-Means")
    print(kmeans_score/num_tests)

    # Not sure how to interpret the KMeans labels against original labels.
    # However my 'accuracy' function consistantly gave an approx 50%

    # Overall for this data set, 


def preprocess():
    ''' Reads in data, transforms, imputes, and normalizes  
    Return: X, y
    '''

    features = np.array([]) # Feature Names-- placeholder
    data = []             # Feature Data-- placeholder
    y = np.array([])    # Labels    ->  0: Net Loss     1: Net Gain
    X = np.array([[]])  # Feature Data

    with open(DATA_FILE) as file:

        # Get number of samples
        file.seek(0)

        # First line has the name of each feature
        feature_line = file.readline()

        # Get those names and store them
        for i, f in enumerate(feature_line.strip().split(',')):
            if i in UNUSED_FEATURES:
                continue
            features = np.append(features, f)

        global NUM_FEATURES
        NUM_FEATURES = features.size
        # data = [['' for _ in range(NUM_FEATURES)] for _ in range(NUM_SAMPLES)]
        tmp_y = []

        # Extract feature data
        # Toss unused features
        # Label as ->  0: Net Loss      1: Net Gain
        num = 0
        for i, sample in enumerate(file):
            # current_feature_number = 0
            temp = []
            has_empty = False

            for j, feature_value in enumerate(sample.strip().split(',')):

                # Tossing unused data
                if j in UNUSED_FEATURES:
                    # Create our temp label
                    if j == 13:
                        # tmp_y[i] = feature_value
                        tmp_y.append(feature_value)
                    continue

                if feature_value == '':
                    # Case: Missing data-- will impute later
                    # data[i][current_feature_number] = None
                    has_empty = True
                    break

                else:
                    temp.append(feature_value.strip('$'))
                    # data[i][current_feature_number] = feature_value.strip('$')

                # current_feature_number += 1
            if has_empty:
                continue
            data.append(temp)
            num += 1

        global NUM_SAMPLES
        NUM_SAMPLES = num
        y = np.zeros( NUM_SAMPLES, dtype=int)

        # Compute actual labels; Net gain = 1, Net loss = 0
        positive_count, negative_count = 0, 0
        for i, entry in enumerate(tmp_y):
            if float(entry) > 0:
                y[i] = 1
                positive_count += 1
            else:
                y[i] = 0
                negative_count += 1
        print("Positive samples: {}".format(positive_count))
        print("Negative samples: {}".format(negative_count))

    imp = sklearn.preprocessing.Imputer(missing_values="NaN", strategy="mean", axis=0)
    X = imp.fit_transform(data)
    X = sklearn.preprocessing.normalize(X, norm='l2', axis=0)
    return(X, y)


def gnb(X_train, y_train, X_test, y_test):
    ''' Runs Guassian Naive Bayes
    Input: X, y, test_size
    Return: score, confusion_matrix
    '''

    clf = GaussianNB()
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)

    y_prob = clf.predict_proba(X_test)
    fpr, tpr, _ = sklearn.metrics.roc_curve(y_test, y_prob[:, 1], pos_label=1)

    plt.plot(fpr, tpr)
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    plt.title('Gaussian Naive Bayes ROC')
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.grid(True)
    # plt.show()

    return score


def knn(X_train, y_train, X_test, y_test):
    ''' Runs K-Nearest Neighbors
    Input: X, y, test_size
    Return: Dict of {n:score}
    '''

    results = []
    for neighbs in range(5, math.ceil(math.sqrt(NUM_SAMPLES))):
        clf = KNeighborsClassifier(n_neighbors=neighbs)
        clf.fit(X_train, y_train)
        prediction = clf.predict(X_test)
        score = sklearn.metrics.zero_one_loss(y_test, prediction)
        results.append((neighbs, score))
    return results


def svm(X_train, y_train, X_test, y_test):
    ''' Runs Suport Vector Classification
    Input: X, y, test_size
    Return: all_results=(kernel_name[& degree], result)
    '''

    all_kernels, all_results = [], []
    all_kernels.append(('linear', SVC(kernel='linear')))
    all_kernels.append(('poly-d3', SVC(kernel='poly', degree=3)))
    all_kernels.append(('poly-d5', SVC(kernel='poly', degree=5)))

    for name, clf in all_kernels:
        clf.fit(X_train, y_train)
        prediction = clf.predict(X_test)
        zero_one = sklearn.metrics.zero_one_loss(y_test, prediction)
        all_results.append((name, zero_one))

    return all_results


# TODO-- Fix KMeans
def kmeans(X_train, y_train, X_test, y_test):
    ''' Runs K-Means Clustering
    Input: X, y, test_size
    Return: result
    '''

    clf = KMeans(n_clusters=NUM_CLASSES, random_state=None)
    clf.fit(X_train)
    score = 0
    # print(y_train)
    # print(clf.labels_)
    for actual, predicted in zip(y_train, clf.labels_):
        if actual == predicted:
            score += 1
    score /= len(clf.labels_)

    return score


if __name__ == '__main__':
    main()
