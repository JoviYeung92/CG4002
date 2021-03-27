import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt

from sklearn import svm
from sklearn.metrics import confusion_matrix, accuracy_score

def svm_classifier(X_train, y_train, X_test, y_test, labels, show):
    # Fitting SVM's with different kernel functions to the Training set
    linear = svm.SVC(kernel='linear', C=1, decision_function_shape='ovo').fit(X_train, y_train)
    rbf = svm.SVC(kernel='rbf', gamma=1, C=1, decision_function_shape='ovo').fit(X_train, y_train)
    poly = svm.SVC(kernel='poly', degree=3, C=1, decision_function_shape='ovo').fit(X_train, y_train)
    sig = svm.SVC(kernel='sigmoid', C=1, decision_function_shape='ovo').fit(X_train, y_train)

    print('SVM models trained')

    """
    #stepsize in the mesh, it alters the accuracy of the plotprint
    #to better understand it, just play with the value, change it and print it
    h = .01
    
    X = np.concatenate((X_train, X_test), axis=0)
    y = np.concatenate((y_train, y_test), axis=0)

    #create the mesh
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),np.arange(y_min, y_max, h))
    # create the title that will be shown on the plot
    titles = ['Linear kernel','RBF kernel','Polynomial kernel','Sigmoid kernel']

    
    for i, clf in enumerate((linear, rbf, poly, sig)):
        #defines how many plots: 2 rows, 2columns=> leading to 4 plots
        plt.subplot(2, 2, i + 1) #i+1 is the index
        #space between plots
        plt.subplots_adjust(wspace=0.4, hspace=0.4) 

        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        
        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        plt.contourf(xx, yy, Z, cmap=plt.cm.PuBuGn, alpha=0.7)
        
        # Plot also the training points
        plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.PuBuGn,     edgecolors='grey')
        
        #plt.xlabel('Sepal length')
        #plt.ylabel('Sepal width')
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        plt.xticks(())
        plt.yticks(())
        plt.title(titles[i])
        plt.show()
    """

    linear_pred = linear.predict(X_test)
    poly_pred = poly.predict(X_test)
    rbf_pred = rbf.predict(X_test)
    sig_pred = sig.predict(X_test)

    # retrieve the accuracy and print it for all 4 kernel functions
    accuracy_lin = linear.score(X_test, y_test)
    accuracy_poly = poly.score(X_test, y_test)
    accuracy_rbf = rbf.score(X_test, y_test)
    accuracy_sig = sig.score(X_test, y_test)
    
    # Confusion matrix
    print('Results of SVM Classifier-')

    print('Accuracy Linear Kernel: ', accuracy_lin)
    print('Accuracy Polynomial Kernel: ', accuracy_poly)
    print('Accuracy Radial Basis Kernel: ', accuracy_rbf)
    print('Accuracy Sigmoid Kernel: ', accuracy_sig)

    # creating a confusion matrix

    y_test = np.vectorize(labels.get)(y_test)
    if show == 'l':
        linear_pred = np.vectorize(labels.get)(linear_pred)
        df_cm = confusion_matrix(y_test, linear_pred)
    elif show == 'p':
        poly_pred = np.vectorize(labels.get)(poly_pred)
        df_cm = confusion_matrix(y_test, poly_pred)
    elif show == 'r':
        rbf_pred = np.vectorize(labels.get)(rbf_pred)
        df_cm = confusion_matrix(y_test, rbf_pred)
    elif show == 's':
        sig_pred = np.vectorize(labels.get)(sig_pred)
        df_cm = confusion_matrix(y_test, sig_pred)

    plt.figure(figsize = (12, 10))
    sn.heatmap(df_cm, annot=True)
