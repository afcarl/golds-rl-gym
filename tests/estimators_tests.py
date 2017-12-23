import numpy as np
import tensorflow as tf

from fed_gym.agents.a3c.estimators import GaussianPolicyEstimator, ValueEstimator, rnn_graph_lstm


class PolicyEstimatorTest(tf.test.TestCase):

    @classmethod
    def setUpClass(cls):
        super(PolicyEstimatorTest, cls).setUpClass()

        cls.batch_size = 16
        cls.num_actions = 3
        cls.input_size = 5
        cls.temporal_size = 7
        cls.T = 10

        cls.states = np.random.random((cls.batch_size, cls.input_size))
        cls.temporal_states = np.random.random((cls.batch_size, cls.T, cls.temporal_size))
        cls.advantage = np.random.random((cls.batch_size, )).astype('float32')
        cls.actions = np.random.random((cls.batch_size, cls.num_actions)).astype('float32')

    def gaussian_predict_test(self):
        estimator = GaussianPolicyEstimator(
            self.num_actions, static_size=self.input_size, temporal_size=self.temporal_size,
            shared_layer=lambda x: rnn_graph_lstm(x, 32, 2, True)
        )

        grads = [g for g, _ in estimator.grads_and_vars]

        with self.test_session() as sess:
            sess.run(tf.global_variables_initializer())

            # Run feeds
            feed_dict = {
                estimator.states: self.states,
                estimator.history: self.temporal_states,
                estimator.advantages: self.advantage,
                estimator.actions: self.actions
            }
            loss = sess.run(estimator.loss, feed_dict)
            pred = sess.run(estimator.predictions, feed_dict)

            # Assertions
            self.assertTrue(loss != 0.0)
            np.testing.assert_array_less(0., pred['sigma'])
            self.assertEqual(pred['mu'].shape[1], self.num_actions)
            self.assertEqual(pred['sigma'].shape[1], self.num_actions)

            grads_ = sess.run(grads, feed_dict)

            grad_feed_dict = { k: v for k, v in zip(grads, grads_) }
            _ = sess.run(estimator.train_op, grad_feed_dict)


class ValueEstimatorTest(tf.test.TestCase):

    @classmethod
    def setUpClass(cls):
        super(ValueEstimatorTest, cls).setUpClass()

        cls.batch_size = 16
        cls.num_actions = 3
        cls.input_size = 5
        cls.temporal_size = 7
        cls.T = 10

        cls.states = np.random.random((cls.batch_size, cls.input_size))
        cls.temporal_states = np.random.random((cls.batch_size, cls.T, cls.temporal_size))
        cls.targets = np.random.random((cls.batch_size, )).astype('float32')

    def predict_test(self):
        estimator = ValueEstimator(
            static_size=self.input_size, temporal_size=self.temporal_size,
            shared_layer=lambda x: rnn_graph_lstm(x, 32, 2, True),
        )

        grads = [g for g, _ in estimator.grads_and_vars]

        with self.test_session() as sess:
            sess.run(tf.global_variables_initializer())

            # Run feeds
            feed_dict = {
                estimator.states: self.states,
                estimator.history: self.temporal_states,
                estimator.targets: self.targets
            }
            loss = sess.run(estimator.loss, feed_dict)
            pred = sess.run(estimator.predictions, feed_dict)

            # Assertions
            self.assertTrue(loss != 0.0)
            self.assertEqual(pred['logits'].shape, (self.batch_size, ))

            grads_ = sess.run(grads, feed_dict)

            grad_feed_dict = { k: v for k, v in zip(grads, grads_) }
            _ = sess.run(estimator.train_op, grad_feed_dict)
