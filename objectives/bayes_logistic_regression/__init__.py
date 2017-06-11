import tensorflow as tf
from objectives import Energy


class BayesianLogisticRegression(Energy):
    def __init__(self, data, labels, batch_size=None,
                 loc=0.0, scale=1.0):
        """
        Bayesian Logistic Regression model (assume Normal prior)
        :param data: data for Logistic Regression task
        :param labels: label for Logistic Regression task
        :param batch_size: batch size for Logistic Regression; setting it to None
        adds flexibility at the cost of speed.
        :param loc: mean of the Normal prior
        :param scale: std of the Normal prior
        """
        super(BayesianLogisticRegression, self).__init__()
        self.x_dim = data.shape[1]
        self.y_dim = labels.shape[1]
        self.dim = self.x_dim * self.y_dim + self.y_dim
        self.mu_prior = tf.ones([self.dim]) * loc
        self.sig_prior = tf.ones([self.dim]) * scale

        self.data = tf.constant(data, tf.float32)
        self.labels = tf.constant(labels, tf.float32)

        if batch_size:
            self.data = tf.reshape(self.data, [batch_size, -1, self.x_dim])
            self.labels = tf.reshape(self.labels, [batch_size, -1, self.y_dim])
        self.z = tf.placeholder(tf.float32, [batch_size, self.dim])

    def _vector_to_model(self, v):
        w = v[:, :-self.y_dim]
        b = v[:, -self.y_dim:]
        w = tf.reshape(w, [-1, self.x_dim, self.y_dim])
        b = tf.reshape(b, [-1, 1, self.y_dim])
        return w, b

    def energy_fn(self, v, x, y):
        w, b = self._vector_to_model(v)
        logits = tf.matmul(x, w) + b
        ll = tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=logits)
        ll = tf.reduce_sum(ll, axis=[1, 2])
        pr = tf.square((v - self.mu_prior) / self.sig_prior)
        pr = tf.reduce_sum(pr, axis=1)
        return ll + pr

    def __call__(self, v):
        return self.energy_fn(v, self.data, self.labels)
