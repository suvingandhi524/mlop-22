 #Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# License: BSD 3 clause


# PART: library dependencies -- sklear, torch, tensorflow, numpy, transformers

# Standard scientific Python imports
import matplotlib.pyplot as plt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split


def preprocess_digits(dataset):
    n_samples = len(dataset.images)
    data = dataset.images.reshape((n_samples, -1))
    label = dataset.target
    return data, label


def data_viz(dataset):
    # PART: sanity check visualization of the data
    _, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
    for ax, image, label in zip(axes, dataset.images, dataset.target):
        ax.set_axis_off()
        ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
        ax.set_title("Training: %i" % label)


def train_dev_test_split(data, label, train_frac, dev_frac):

    dev_test_frac = 1 - train_frac
    x_train, x_dev_test, y_train, y_dev_test = train_test_split(
        data, label, test_size=dev_test_frac, shuffle=True
    )
    x_test, x_dev, y_test, y_dev = train_test_split(
        x_dev_test, y_dev_test, test_size=(dev_frac) / dev_test_frac, shuffle=True
    )

    return x_train, y_train, x_dev, y_dev, x_test, y_test


def h_param_tuning(h_param_comb, clf, x_train, y_train, x_dev, y_dev, metric):
    best_metric = -1.0
    best_model = None
    best_h_params = None
    # 2. For every combination-of-hyper-parameter values
    for cur_h_params in h_param_comb:

        # PART: setting up hyperparameter
        hyper_params = cur_h_params
        clf.set_params(**hyper_params)

        # PART: Train model
        # 2.a train the model
        # Learn the digits on the train subset
        clf.fit(x_train, y_train)

        # print(cur_h_params)
        # PART: get dev set predictions
        predicted_dev = clf.predict(x_dev)

        # 2.b compute the accuracy on the validation set
        cur_metric = metric(y_pred=predicted_dev, y_true=y_dev)

        # 3. identify the combination-of-hyper-parameter for which validation set accuracy is the highest.
        if cur_metric > best_metric:
            best_metric = cur_metric
            best_model = clf
            best_h_params = cur_h_params
            print("Found new best metric with :" + str(cur_h_params))
            print("New best val metric:" + str(cur_metric))
    return best_model, best_metric, best_h_params

# 1. set the ranges of hyper parameters
gamma_list = [0.01, 0.005, 0.001, 0.0005, 0.0001]
c_list = [0.1, 0.2, 0.5, 0.7, 1, 2, 5, 7, 10]

h_param_comb = [{"gamma": g, "C": c} for g in gamma_list for c in c_list]

assert len(h_param_comb) == len(gamma_list) * len(c_list)

train_frac = 0.8
test_frac = 0.1
dev_frac = 0.1

# PART: load dataset -- data from csv, tsv, jsonl, pickle
digits = datasets.load_digits()
data_viz(digits)
data, label = preprocess_digits(digits)
# housekeeping
del digits



# [1,2,3,4,5,6,7,8,9]

# other types of preprocessing
# - image : 8x8 : resize 16x16, 32x32, 4x4 : flatteing
# - normalize data: mean normalization: [x - mean(X)]
#                 - min-max normalization
# - smoothing the image: blur on the image


# PART: define train/dev/test splits of experiment protocol
# train to train model
# dev to set hyperparameters of the model
# test to evaluate the performance of the model

x_train, y_train, x_dev, y_dev, x_test, y_test = train_dev_test_split(
    data, label, train_frac, dev_frac
)

# PART: Define the model
# Create a classifier: a support vector classifier
clf = svm.SVC()
metric=metrics.accuracy_score
best_model, best_metric, best_h_params = h_param_tuning(h_param_comb, clf, x_train, y_train, x_dev, y_dev, metric)

# PART: Get test set predictions
# Predict the value of the digit on the test subset
predicted = best_model.predict(x_test)

# PART: Sanity check of predictions
_, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
for ax, image, prediction in zip(axes, x_test, predicted):
    ax.set_axis_off()
    image = image.reshape(8, 8)
    ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
    ax.set_title(f"Prediction: {prediction}")

# 4. report the test set accurancy with that best model.
# PART: Compute evaluation metrics
print(
    f"Classification report for classifier {clf}:\n"
    f"{metrics.classification_report(y_test, predicted)}\n"
)

print("Best hyperparameters were:")
print(best_h_params)
