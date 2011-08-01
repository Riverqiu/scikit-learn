from time import time

from collections import defaultdict

import numpy as np
from numpy import random as nr

from scikits.learn.cluster.k_means_ import KMeans, MiniBatchKMeans


def compute_bench(samples_range, features_range):

    it = 0
    iterations = 200
    results = defaultdict(lambda: [])
    chunk = 100

    max_it = len(samples_range) * len(features_range)
    for n_samples in samples_range:
        for n_features in features_range:
            it += 1
            print '=============================='
            print 'Iteration %03d of %03d' %(it, max_it)
            print '=============================='
            print ''
            data = nr.random_integers(-50, 50, (n_samples, n_features))

            print 'K-Means'
            tstart = time()
            kmeans = KMeans(init='k-means++',
                            k=10).fit(data)

            delta = time() - tstart
            print "Speed: %0.3fs" % delta
            print "Inertia: %0.5f" % kmeans.inertia_
            print ''

            results['kmeans_speed'].append(delta)
            results['kmeans_quality'].append(kmeans.inertia_)

            print 'Fast K-Means'
            # let's prepare the data in small chunks
            mbkmeans = MiniBatchKMeans(init='k-means++',
                                      k=10,
                                      chunk_size=chunk)
            tstart = time()
            mbkmeans.fit(data)
            delta = time() - tstart
            print "Speed: %0.3fs" % delta
            print "Inertia: %f" % mbkmeans.inertia_
            print ''
            print ''

            results['minibatchkmeans_speed'].append(delta)
            results['minibatchkmeans_quality'].append(mbkmeans.inertia_)

    return results


def compute_bench_2(chunks):
    results = defaultdict(lambda: [])
    n_features = 50000
    means = np.array([[1, 1], [-1, -1], [1, -1], [-1, 1],
                      [0.5, 0.5], [0.75, -0.5], [-1, 0.75], [1, 0]])
    X = np.empty((0, 2))
    for i in xrange(8):
        X = np.r_[X, means[i] + 0.8 * np.random.randn(n_features, 2)]
    max_it = len(chunks)
    it = 0
    for chunk in chunks:
        it += 1
        print '=============================='
        print 'Iteration %03d of %03d' %(it, max_it)
        print '=============================='
        print ''

        print 'Fast K-Means'
        tstart = time()
        mbkmeans = MiniBatchKMeans(init='k-means++',
                                    k=8,
                                    chunk_size=chunk)

        mbkmeans.fit(X)
        delta = time() - tstart
        print "Speed: %0.3fs" % delta
        print "Inertia: %0.3fs" % mbkmeans.inertia_
        print ''

        results['minibatchkmeans_speed'].append(delta)
        results['minibatchkmeans_quality'].append(mbkmeans.inertia_)

    return results


if __name__ == '__main__':
    from mpl_toolkits.mplot3d import axes3d # register the 3d projection
    import matplotlib.pyplot as plt

    samples_range = np.linspace(50, 150, 5).astype(np.int)
    features_range = np.linspace(150, 50000, 5).astype(np.int)
    chunks = np.linspace(500, 10000, 15).astype(np.int)

    results = compute_bench(samples_range, features_range)
    results_2 = compute_bench_2(chunks)

    max_time = max([max(i) for i in [t for (label, t) in results.iteritems()
                         if "speed" in label]])
    max_inertia = max([max(i) for i in [
                        t for (label, t) in results.iteritems()
                            if "speed" not in label]])

    fig = plt.figure()
    for c, (label, timings) in zip('brcy',
                                    sorted(results.iteritems())):
        if 'speed' in label:
            ax = fig.add_subplot(2, 2, 1, projection='3d')
            ax.set_zlim3d(0.0, max_time * 1.1)
        else:
            ax = fig.add_subplot(2, 2, 2, projection='3d')
            ax.set_zlim3d(0.0, max_inertia * 1.1)

        X, Y = np.meshgrid(samples_range, features_range)
        Z = np.asarray(timings).reshape(samples_range.shape[0],
                                        features_range.shape[0])
        ax.plot_surface(X, Y, Z.T, cstride=1, rstride=1, color=c, alpha=0.5)
        ax.set_xlabel('n_samples')
        ax.set_ylabel('n_features')


    i = 0
    for c, (label, timings) in zip('br',
                                   sorted(results_2.iteritems())):
        i += 1
        ax = fig.add_subplot(2, 2, i + 2)
        y = np.asarray(timings)
        ax.plot(chunks, y, color=c, alpha=0.8)
        ax.set_xlabel('chunks')
        ax.set_ylabel(label)


    plt.show()
