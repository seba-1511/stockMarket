#-*- coding: utf-8 -*-

import os
import pickle as pi
import scipy as sp
import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn import decomposition
from sklearn import lda
from sklearn import neighbors
from sklearn.metrics import precision_recall_curve
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.metrics import classification_report

#Gets content of p.pickle, performs the learning task and evaluates itself
print 'Openning files...'
file = open('dayFeatures.pi', 'rb')
dayFeatures = np.asarray(pi.load(file))
file = open('cvIds.pi', 'rb')
cvIds = pi.load(file)
file = open('testIds.pi', 'rb')
testIds = pi.load(file)
file = open('allAnswers.pi', 'rb')
allAnswers = pi.load(file)

#Scaling the features:
print 'Scaling features...'
for i in xrange(len(dayFeatures[0])):
    dayFeatures[:, i] = (dayFeatures[:, i] - np.average(dayFeatures[:, i])) / (np.amax(dayFeatures[:, i]) - np.amin(dayFeatures[:, i]))

#Building features inputs
allFeatures = []
print 'Building features inputs...'
for i in xrange(260, len(dayFeatures)):
    feature = np.array([])
    for j in xrange(0, 260):
        feature = np.append(feature, dayFeatures[i-j])
    allFeatures.append(feature)

#Shuffling data:
shuffled = dayFeatures
shuffled = np.hstack((shuffled, np.zeros((shuffled.shape[0], 1), dtype=shuffled.dtype)))
shuffled[:, -1] = allAnswers
np.random.shuffle(shuffled)
dayFeatures = shuffled[:, :-1]
allAnswers = shuffled[:, -1]

#Building Sets:
print 'Building sets...'
finalFeatures = []
testFeatures = []
cvFeatures = []
finalAnswers = []
testAnswers = []
cvAnswers = []
for i in xrange(0, len(allFeatures)):
    if i+260 in cvIds:
        cvAnswers.append(allAnswers[i])
        cvFeatures.append(allFeatures[i])
    elif i+260 in testIds:
    # if i+260 in testIds:
        testAnswers.append(allAnswers[i])
        testFeatures.append(allFeatures[i])
    else:
        finalAnswers.append(allAnswers[i])
        finalFeatures.append(allFeatures[i])

#Applying LDA:
print 'Applying LDA...'
n_components = 200
selLda = lda.LDA(n_components=n_components)
finalFeatures = selLda.fit_transform(finalFeatures, finalAnswers)
cvFeatures = selLda.transform(cvFeatures)
testFeatures = selLda.transform(testFeatures)

#Applying PCA:
# print 'Applying PCA...'
# n_components = 2000
# pca = decomposition.PCA(n_components=n_components)
# finalFeatures = pca.fit_transform(finalFeatures)
# cvFeatures = pca.transform(cvFeatures)
# testFeatures = pca.transform(testFeatures)
# print 'With ' + str(n_components) + ' components we have a conserved variance of ' + str(pca.explained_variance_ratio_)


##########################
# Plotting Training and Test errors:
##########################

lrTrainingError = []
lrTestingError = []
lrTrainIndices = []
lrTestIndices = []

svmTrainingError = []
svmTestingError = []
svmTrainIndices = []
svmTestIndices = []

knnTrainingError = []
knnTestingError = []
knnTrainIndices = []
knnTestIndices = []

testFeatures = np.asarray(testFeatures)
testAnswers = np.asarray(testAnswers)
finalFeatures = np.asarray(finalFeatures)
finalAnswers = np.asarray(finalAnswers)
cvFeatures = np.asarray(cvFeatures)
cvAnswers = np.asarray(cvAnswers)

lrLearner = LogisticRegression(penalty='l2', dual=True, C=1.0)
svmLearner = svm.SVC(C=1.0, kernel="poly", degree=5, gamma=0.0, probability=True)
knnLearner = neighbors.KNeighborsClassifier(n_neighbors=350)

print 'Calculating LR Errors...'
t = 10
s = 10
for i in xrange(len(allFeatures)):
    if not i+260 in cvIds and not i+260 in testIds:
        lrLearner.fit(finalFeatures[0:t+1], finalAnswers[0:t+1])
        error = lrLearner.score(finalFeatures[0:t+1], finalAnswers[0:t+1])
        lrTrainingError.append(1-error)
        lrTrainIndices.append(i+260)
        t += 1
    elif i+260 in testIds:
        error = lrLearner.score(testFeatures[0:s+1], testAnswers[0:s+1])
        lrTestIndices.append(i+260)
        lrTestingError.append(1-error)
        s += 1

print 'Final LR error is ' + str(lrLearner.score(testFeatures, testAnswers))


print 'Calculating SVM Errors...'
t = 10
s = 10
for i in xrange(len(allFeatures)):
    if not i+260 in cvIds and not i+260 in testIds:
        svmLearner.fit(finalFeatures[0:t+1], finalAnswers[0:t+1])
        error = svmLearner.score(finalFeatures[0:t+1], finalAnswers[0:t+1])
        svmTrainingError.append(1-error)
        svmTrainIndices.append(i+260)
        t += 1
    elif i+260 in testIds:
        error = svmLearner.score(testFeatures[0:s+1], testAnswers[0:s+1])
        svmTestIndices.append(i+260)
        svmTestingError.append(1-error)
        s += 1

print 'Final SVM error is ' + str(svmLearner.score(testFeatures, testAnswers))


print 'Calculating kNN Errors...'
t = 10
s = 10
for i in xrange(len(allFeatures)):
    if not i+260 in cvIds and not i+260 in testIds:
        knnLearner.fit(finalFeatures[0:t+1], finalAnswers[0:t+1])
        error = knnLearner.score(finalFeatures[0:t+1], finalAnswers[0:t+1])
        knnTrainingError.append(1-error)
        knnTrainIndices.append(i+260)
        t += 1
    elif i+260 in testIds:
        error = knnLearner.score(testFeatures[0:s+1], testAnswers[0:s+1])
        knnTestIndices.append(i+260)
        knnTestingError.append(1-error)
        s += 1

print 'Final kNN error is ' + str(knnLearner.score(testFeatures, testAnswers))

print 'Plotting the obtained results...'
curr_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
execfile(curr_dir + '/../Scripts/plot.py')

lrPrecDown, lrRecallDown, lrThresholdsDown = precision_recall_curve(testAnswers, lrLearner.predict_proba(testFeatures)[:, 0])
svmPrecDown, svmRecallDown, svmThresholdsDown = precision_recall_curve(testAnswers, svmLearner.predict_proba(testFeatures)[:, 0])
knnPrecDown, knnRecallDown, knnThresholdsDown = precision_recall_curve(testAnswers, knnLearner.predict_proba(testFeatures)[:, 0])

lrPrecUp, lrRecallUp, lrThresholdsUp = precision_recall_curve(testAnswers, lrLearner.predict_proba(testFeatures)[:, 1])
svmPrecUp, svmRecallUp, svmThresholdsUp = precision_recall_curve(testAnswers, svmLearner.predict_proba(testFeatures)[:, 1])
knnPrecUp, knnRecallUp, knnThresholdsUp = precision_recall_curve(testAnswers, knnLearner.predict_proba(testFeatures)[:, 1])

plotLines([[lrRecallDown], [lrPrecDown]], 'LR: Precision vs Recall(Down)', 'Recall', 'Precision')
plotLines([[svmRecallDown], [svmPrecDown]], 'SVM: Precision vs Recall(Down)', 'Recall', 'Precision')
plotLines([[knnRecallDown], [knnPrecDown]], 'kNN: Precision vs Recall(Down)', 'Recall', 'Precision')

plotLines([[lrRecallUp], [lrPrecUp]], 'LR: Precision vs Recall(Up)', 'Recall', 'Precision')
plotLines([[svmRecallUp], [svmPrecUp]], 'SVM: Precision vs Recall(Up)', 'Recall', 'Precision')
plotLines([[knnRecallUp], [knnPrecUp]], 'kNN: Precision vs Recall(Up)', 'Recall', 'Precision')

plotLines([[lrTrainIndices, lrTestIndices], [lrTrainingError, lrTestingError]], 'Errors:LogRegr', 'Dataset size', 'Error')
plotLines([[svmTrainIndices, svmTestIndices], [svmTrainingError, svmTestingError]], 'Errors:SVM', 'Dataset size', 'Error')
plotLines([[knnTrainIndices, knnTestIndices], [knnTrainingError, knnTestingError]], 'Errors:kNN', 'Dataset size', 'Error')

#Printing Classification Report:
print 'Report for Logistic Regression (Up):'
print classification_report(testAnswers, lrLearner.predict_proba(testFeatures)[:, 1] > 0.69, target_names=['Don\'t know', 'Will go up'])
print 'Report for Logistic Regression (Down):'
print classification_report(testAnswers, lrLearner.predict_proba(testFeatures)[:, 0] > 0.6, target_names=['Don\'t know', 'Will go Down'])

print 'Report for SVM (Up):'
print classification_report(testAnswers, svmLearner.predict_proba(testFeatures)[:, 1] > 0.53, target_names=['Don\'t know', 'Will go up'])
print 'Report for SVM (Down):'
print classification_report(testAnswers, svmLearner.predict_proba(testFeatures)[:, 0] > 0.46, target_names=['Don\'t know', 'Will go Down'])

print 'Report for kNN (Up):'
print classification_report(testAnswers, knnLearner.predict_proba(testFeatures)[:, 1] > 0.56, target_names=['Don\'t know', 'Will go up'])
print 'Report for kNN (Down):'
print classification_report(testAnswers, knnLearner.predict_proba(testFeatures)[:, 0] > 0.3, target_names=['Don\'t know', 'Will go Down'])