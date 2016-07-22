import collections
import csv
import gc
import os

import psutil
from scipy import ndimage

import numpy as np
import tensorflow as tf
from tentacle.board import Board
from tentacle.data_set import DataSet


Datasets = collections.namedtuple('Dataset', ['train', 'validation', 'test'])

class RingBuffer():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, length):
        self.data = np.zeros(length, dtype='f')
        self.index = 0

    def extend(self, x):
        "adds array x to ring buffer"
        x_index = (self.index + np.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

    def get_average(self):
        return np.average(self.data)


class Pre(object):
    NUM_ACTIONS = Board.BOARD_SIZE_SQ
    NUM_LABELS = NUM_ACTIONS
    NUM_CHANNELS = 9

    BATCH_SIZE = 30
    PATCH_SIZE = 5
    DEPTH = 16
    NUM_HIDDEN = 256

    LEARNING_RATE = 0.002
    NUM_STEPS = 10000
    DATASET_CAPACITY = 300000

    TRAIN_DIR = '/home/splendor/fusor/brain/'
    SUMMARY_DIR = '/home/splendor/fusor/summary'
    STAT_FILE = '/home/splendor/glycogen/stat.npz'
    DATA_SET_FILE = 'dataset_9x9_dilated.txt'


    def __init__(self, is_train=True, is_revive=False):
        self.is_train = is_train
        self.is_revive = is_revive
        self._file_read_index = 0
        self._has_more_data = True
        self.ds = None
        self.gstep = 0
        self.loss_window = RingBuffer(10)

    def placeholder_inputs(self):
        states = tf.placeholder(tf.float32, [None, Board.BOARD_SIZE, Board.BOARD_SIZE, Pre.NUM_CHANNELS])  # NHWC
        actions = tf.placeholder(tf.float32, shape=(None, Pre.NUM_LABELS))
        return states, actions

    def model(self, states_pl, actions_pl):
        # HWC,outC
        ch1 = 20
        W_1 = tf.Variable(tf.truncated_normal([3, 3, Pre.NUM_CHANNELS, ch1], stddev=0.1))
        b_1 = tf.Variable(tf.zeros([ch1]))
        ch = 28
        W_2 = tf.Variable(tf.truncated_normal([3, 3, ch1, ch], stddev=0.1))
        b_2 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_21 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_21 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_22 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_22 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_23 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_23 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_24 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_24 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_25 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_25 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_26 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_26 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_27 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_27 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_28 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_28 = tf.Variable(tf.constant(1.0, shape=[ch]))
        W_29 = tf.Variable(tf.truncated_normal([3, 3, ch, ch], stddev=0.1))
        b_29 = tf.Variable(tf.constant(1.0, shape=[ch]))

#         print('state shape: ', states_pl.get_shape())
#         print('W_1 shape: ', W_1.get_shape())
#         print('W_2 shape: ', W_2.get_shape())
#         print('W_21 shape: ', W_21.get_shape())
#         print('W_31 shape: ', W_31.get_shape())

        h_conv1 = tf.nn.relu(tf.nn.conv2d(states_pl, W_1, [1, 2, 2, 1], padding='SAME') + b_1)
#         print('conv1 shape: ', h_conv1.get_shape())
        h_conv2 = tf.nn.relu(tf.nn.conv2d(h_conv1, W_2, [1, 1, 1, 1], padding='SAME') + b_2)
        h_conv21 = tf.nn.relu(tf.nn.conv2d(h_conv2, W_21, [1, 1, 1, 1], padding='SAME') + b_21)
        h_conv22 = tf.nn.relu(tf.nn.conv2d(h_conv21, W_22, [1, 1, 1, 1], padding='SAME') + b_22)
        h_conv23 = tf.nn.relu(tf.nn.conv2d(h_conv22, W_23, [1, 1, 1, 1], padding='SAME') + b_23)
        h_conv24 = tf.nn.relu(tf.nn.conv2d(h_conv23, W_24, [1, 1, 1, 1], padding='SAME') + b_24)
        h_conv25 = tf.nn.relu(tf.nn.conv2d(h_conv24, W_25, [1, 1, 1, 1], padding='SAME') + b_25)
        h_conv26 = tf.nn.relu(tf.nn.conv2d(h_conv25, W_26, [1, 1, 1, 1], padding='SAME') + b_26)
        h_conv27 = tf.nn.relu(tf.nn.conv2d(h_conv26, W_27, [1, 1, 1, 1], padding='SAME') + b_27)
        h_conv28 = tf.nn.relu(tf.nn.conv2d(h_conv27, W_28, [1, 1, 1, 1], padding='SAME') + b_28)
        h_conv29 = tf.nn.relu(tf.nn.conv2d(h_conv28, W_29, [1, 1, 1, 1], padding='SAME') + b_29)

        shape = h_conv29.get_shape().as_list()
        dim = np.cumprod(shape[1:])[-1]
        h_conv_out = tf.reshape(h_conv29, [-1, dim])

        W_3 = tf.Variable(tf.truncated_normal([dim, Pre.NUM_HIDDEN], stddev=0.1))
        b_3 = tf.Variable(tf.constant(1.0, shape=[Pre.NUM_HIDDEN]))

        W_4 = tf.Variable(tf.truncated_normal([Pre.NUM_HIDDEN, Pre.NUM_LABELS], stddev=0.1))
        b_4 = tf.Variable(tf.constant(1.0, shape=[Pre.NUM_LABELS]))

        hidden = tf.nn.relu(tf.matmul(h_conv_out, W_3) + b_3)

        predictions = tf.matmul(hidden, W_4) + b_4

#         prob = tf.nn.softmax(tf.matmul(hidden, W_4) + b_4)
#         loss = tf.reduce_mean(-tf.reduce_sum(action * tf.log(prob)), reduction_indices=1)

        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(predictions, actions_pl)
        self.loss = tf.reduce_mean(cross_entropy)
        tf.scalar_summary("loss", self.loss)

        self.optimizer = tf.train.GradientDescentOptimizer(Pre.LEARNING_RATE).minimize(self.loss)

        self.predict_probs = tf.nn.softmax(predictions)
        Z = tf.equal(tf.argmax(self.predict_probs, 1), tf.argmax(actions_pl, 1))
        self.eval_correct = tf.reduce_sum(tf.cast(Z, tf.int32))


    def prepare(self):
        self.states_pl, self.actions_pl = self.placeholder_inputs()
        self.model(self.states_pl, self.actions_pl)

        self.summary_op = tf.merge_all_summaries()

        self.saver = tf.train.Saver()

        init = tf.initialize_all_variables()
        self.sess = tf.Session()
        self.summary_writer = tf.train.SummaryWriter(Pre.SUMMARY_DIR, self.sess.graph)

        self.sess.run(init)
        print('Initialized')

    def load_from_vat(self):
        ckpt = tf.train.get_checkpoint_state(Pre.TRAIN_DIR)
        if ckpt and ckpt.model_checkpoint_path:
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)

    def fill_feed_dict(self, data_set, states_pl, actions_pl):
        states_feed, actions_feed = data_set.next_batch(Pre.BATCH_SIZE)
        feed_dict = {
            states_pl: states_feed,
            actions_pl: actions_feed,
        }
        return feed_dict

    def do_eval(self, eval_correct, states_pl, actions_pl, data_set):
        true_count = 0  # Counts the number of correct predictions.
        steps_per_epoch = data_set.num_examples // Pre.BATCH_SIZE
        num_examples = steps_per_epoch * Pre.BATCH_SIZE
        for _ in range(steps_per_epoch):
            feed_dict = self.fill_feed_dict(data_set, states_pl, actions_pl)
            true_count += self.sess.run(eval_correct, feed_dict=feed_dict)
        precision = true_count / num_examples
#         print('  Num examples: %d,  Num correct: %d,  Precision: %0.04f' % (num_examples, true_count, precision))
        return precision

    def get_move_probs(self, state):
        feed_dict = {
            self.states_pl: state.reshape(1, -1).reshape((-1, Board.BOARD_SIZE, Board.BOARD_SIZE, Pre.NUM_CHANNELS)),
            self.actions_pl: np.zeros((1, Pre.NUM_ACTIONS))
        }
        return self.sess.run(self.predict_probs, feed_dict=feed_dict)


    def train(self):
        stat = []
        for step in range(Pre.NUM_STEPS):
            feed_dict = self.fill_feed_dict(self.ds.train, self.states_pl, self.actions_pl)
            _, loss, _ = self.sess.run([self.optimizer, self.loss, self.eval_correct], feed_dict=feed_dict)
            self.loss_window.extend(loss)

            self.gstep += 1
            step += 1

            if (step % 100 == 0):
                summary_str = self.sess.run(self.summary_op, feed_dict=feed_dict)
                self.summary_writer.add_summary(summary_str, self.gstep)
                self.summary_writer.flush()

            if (step + 1) % 1000 == 0 or (step + 1) == Pre.NUM_STEPS:
                self.saver.save(self.sess, Pre.TRAIN_DIR + 'model.ckpt', global_step=self.gstep)
                train_accuracy = self.do_eval(self.eval_correct, self.states_pl, self.actions_pl, self.ds.train)
                validation_accuracy = self.do_eval(self.eval_correct, self.states_pl, self.actions_pl, self.ds.validation)
                stat.append((self.gstep, train_accuracy, validation_accuracy, 0.))
#                 print('step: ', self.gstep)

        test_accuracy = self.do_eval(self.eval_correct, self.states_pl, self.actions_pl, self.ds.test)
        print('test accuracy:', test_accuracy)

        np.savez(Pre.STAT_FILE, stat=np.array(stat))


    def adapt(self, filename):
        ds = []
        dat = pre.load_dataset(filename)
        for row in dat:
            s, a = self.forge(row)
            ds.append((s, a))

        ds = np.array(ds)
        print(ds[0, 0].shape, ds[0, 1].shape)

        np.random.shuffle(ds)

        size = ds.shape[0]
        train_size = int(size * 0.8)
        train = ds[:train_size, :]
        test = ds[train_size:, :]

        validation_size = int(train.shape[0] * 0.2)
        validation = train[:validation_size, :]
        train = train[validation_size:, :]

#         print(ds.shape, train.shape, validation.shape, test.shape)

        train = DataSet(np.vstack(train[:, 0]).reshape((-1, Board.BOARD_SIZE, Board.BOARD_SIZE, Pre.NUM_CHANNELS)), np.vstack(train[:, 1]))
        validation = DataSet(np.vstack(validation[:, 0]).reshape((-1, Board.BOARD_SIZE, Board.BOARD_SIZE, Pre.NUM_CHANNELS)), np.vstack(validation[:, 1]))
        test = DataSet(np.vstack(test[:, 0]).reshape((-1, Board.BOARD_SIZE, Board.BOARD_SIZE, Pre.NUM_CHANNELS)), np.vstack(test[:, 1]))

        print(train.images.shape, train.labels.shape)
        print(validation.images.shape, validation.labels.shape)
        print(test.images.shape, test.labels.shape)

        self.ds = Datasets(train=train, validation=validation, test=test)


    def load_dataset(self, filename):
        proc = psutil.Process(os.getpid())
        gc.collect()
        mem0 = proc.memory_info().rss

        del self.ds
        gc.collect()

        mem1 = proc.memory_info().rss
        print('gc(M): ', (mem1 - mem0) / 1024 ** 2)

        content = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for index, line in enumerate(reader):
                if index >= self._file_read_index:
                    if index < self._file_read_index + Pre.DATASET_CAPACITY:
                        content.append([float(i) for i in line])
                    else:
                        break
            if index == self._file_read_index + Pre.DATASET_CAPACITY:
                self._has_more_data = True
                self._file_read_index += Pre.DATASET_CAPACITY
            else:
                self._has_more_data = False

        content = np.array(content)

        print('load data:', content.shape)
#         print(content[:10, -5:])

        # unique board position
        a = content[:, :-4]
        b = np.ascontiguousarray(a).view(np.dtype((np.void, a.dtype.itemsize * a.shape[1])))
        _, idx = np.unique(b, return_index=True)
        unique_a = content[idx]
        print('unique:', unique_a.shape)
        return unique_a


    def _neighbor_count(self, board, who):
        footprint = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
        return ndimage.generic_filter(board, lambda r: np.count_nonzero(r == who), footprint=footprint, mode='constant')

    def forge(self, row):
        '''
            channel 1: black
            channel 2: white
            channel 3: valid move
            channel 4: black neighbors
            channel 5: white neighbors
            lable: best move
        '''
        board = row[:Board.BOARD_SIZE_SQ]
        black = (board == Board.STONE_BLACK).astype(float)
        white = (board == Board.STONE_WHITE).astype(float)
        valid = (board == Board.STONE_EMPTY).astype(float)
        bnc = self._neighbor_count(board.reshape(-1, Board.BOARD_SIZE), Board.STONE_BLACK)
        black_neighb1 = (bnc == 1).astype(np.float).ravel()
        black_neighb2 = (bnc == 2).astype(np.float).ravel()
        black_neighb3 = (bnc >= 3).astype(np.float).ravel()
        wnc = self._neighbor_count(board.reshape(-1, Board.BOARD_SIZE), Board.STONE_WHITE)
        white_neighb1 = (wnc == 1).astype(np.float).ravel()
        white_neighb2 = (wnc == 2).astype(np.float).ravel()
        white_neighb3 = (wnc >= 3).astype(np.float).ravel()
        image = np.dstack((black, white, valid,
                           black_neighb1, black_neighb2, black_neighb3,
                           white_neighb1, white_neighb2, white_neighb3)).flatten()
#         print(black.shape)
#         print(black)
        move = tuple(row[-4:-2].astype(int))
        one_hot = np.zeros((Board.BOARD_SIZE, Board.BOARD_SIZE))
        one_hot[move] = 1.
        one_hot = one_hot.flatten()

#         print(one_hot)
#         print(image.shape, one_hot.shape)
        return image, one_hot


    def close(self):
        if self.sess is not None:
            self.sess.close()

    def run(self):
        self.prepare()

        if self.is_revive:
            self.load_from_vat()

        if self.is_train:
            epoch = 0
            while self.loss_window.get_average() == 0.0 or self.loss_window.get_average() > 1.0:
                print('epoch: ', epoch)
                epoch += 1
                while self._has_more_data:
                    self.adapt(Pre.DATA_SET_FILE)
                    self.train()
                # reset
                self._file_read_index = 0
                self._has_more_data = True
#                 if epoch >= 1:
#                     break


if __name__ == '__main__':
    pre = Pre()
    pre.run()

