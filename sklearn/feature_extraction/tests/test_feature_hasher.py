import numpy as np
import scipy.sparse as sp

from sklearn.feature_extraction import FeatureHasher

from nose.tools import assert_raises, assert_true
from numpy.testing import assert_array_equal, assert_equal
from sklearn.utils.testing import assert_in


def test_feature_hasher_strings():
    raw_X = [[u"foo", "bar", "baz", "foo"],    # note: duplicate
             [u"bar", "baz", "quux"]]

    for lg_n_features in (7, 9, 11, 16, 22):
        n_features = 2 ** lg_n_features

        it = (x for x in raw_X)                 # iterable

        h = FeatureHasher(n_features, non_negative=True, input_type="strings")
        X = h.transform(it)

        assert_equal(X.shape[0], len(raw_X))
        assert_equal(X.shape[1], n_features)

        assert_true(np.all(X.data > 0))
        assert_equal(X[0].sum(), 4)
        assert_equal(X[1].sum(), 3)

        assert_equal(X.nnz, sum(len(set(x)) for x in raw_X))


def test_feature_hasher_pairs():
    raw_X = (d.iteritems() for d in [{"foo": 1, "bar": 2},
                                     {"baz": 3, "quux": 4, "foo": -1}])
    h = FeatureHasher(n_features=4096)
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert_equal([1, 2], x1_nz)
    assert_equal([1, 3, 4], x2_nz)


def test_hash_empty_input():
    n_features = 16
    raw_X = [[], (), xrange(0)]

    h = FeatureHasher(n_features=n_features, input_type="strings")
    X = h.transform(raw_X)

    assert_array_equal(X.A, np.zeros((len(raw_X), n_features)))


def test_hasher_invalid_input():
    assert_raises(ValueError, FeatureHasher,
                  input_type="gobbledygook", n_features=256)
    assert_raises(ValueError, FeatureHasher, n_features=-1)
    assert_raises(ValueError, FeatureHasher, n_features=0)
    assert_raises(TypeError, FeatureHasher, n_features='ham')

    h = FeatureHasher(n_features=np.uint16(2**6))
    assert_raises(ValueError, h.transform, [])
    assert_raises(TypeError, h.transform, [[5.5]])
    assert_raises(TypeError, h.transform, [[None]])
