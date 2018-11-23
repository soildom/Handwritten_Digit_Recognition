import numpy as np
import LoadData
import time


class Affine:
    def __init__(self, w, b):
        self.w = w
        self.b = b
        self.x = None
        self.dw = None
        self.db = None

    def forward(self, x):
        self.x = x
        return np.dot(x, self.w) + self.b

    def backward(self, dout):
        self.dw = np.dot(self.x.T, dout)
        self.db = np.sum(dout, axis=0)
        dx = np.dot(dout, self.w.T)
        return dx  # return dx


class Relu:
    def __init__(self):
        self.flag = None

    def forward(self, x):
        self.flag = x <= 0
        return np.maximum(x, 0)

    def backward(self, dout):
        dout[self.flag] = 0
        return dout  # return dx


class Sigmoid:
    def __init__(self):
        self.out = None

    def forward(self, x):
        self.out = 1.0 / (1 + np.exp(-x))
        return self.out

    def backward(self, dout):
        return dout * (1 - self.out) * self.out  # return dx


class SoftmaxWithLoss:
    def __init__(self):
        self.loss = None
        self.y = None  # one-hot
        self.t = None  # one-hot

    @staticmethod
    def softmax(x):
        max_xi = np.max(x, axis=1)
        # print(max_xi)
        exp_x = np.exp(x.T - max_xi)
        sum_exp_xi = np.sum(exp_x, axis=0)
        p = (exp_x / sum_exp_xi).T

        # exp_x = np.exp(x)
        # sum_exp_xi = np.sum(exp_x, axis=1)
        #
        # p = (exp_x.T - sum_exp_xi).T

        # print(p)
        return p

    @staticmethod
    def cross_entropy(y, t):
        delta = 1e-7
        return -np.sum(t * np.log(y + delta)) / t.shape[0]

    def forward(self, x, t):
        self.t = t  # one-hot
        self.y = self.softmax(x)
        self.loss = self.cross_entropy(self.y, self.t)
        return self.loss

    def backward(self, dout=1):
        dx = dout * (self.y - self.t) / self.t.shape[0]
        return dx


class Network:
    def __init__(self, sizes):
        self.X, self.Y, self.test_X, self.test_Y = LoadData.Load(one_hot=True).load_mnist()
        self.sizes = sizes
        self.layers_num = len(sizes) - 1

        # self.w = [np.ones((x, y)) for x, y in zip(sizes[:-1], sizes[1:])]
        # self.b = [np.ones((1, y)) for y in sizes[1:]]

        self.w = [np.random.randn(x, y) for x, y in zip(sizes[:-1], sizes[1:])]
        self.b = [np.zeros((1, y)) for y in sizes[1:]]

        self.layers = list()
        for i in range(self.layers_num - 1):
            self.layers.append(Affine(self.w[i], self.b[i]))
            self.layers.append(Relu())
        self.layers.append(Affine(self.w[-1], self.b[-1]))

        self.last_layer = SoftmaxWithLoss()

    def predict(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x  # m*10 Matrix

    def loss(self, x, t):
        y = self.predict(x)
        return self.last_layer.forward(y, t)

    def accuracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        t = np.argmax(t, axis=1)
        return np.sum(y == t) / t.shape[0]

    def gradient(self, x, t):
        l = self.loss(x, t)

        dout = 1
        dout = self.last_layer.backward(dout)

        layers = self.layers.copy()

        # print(layers)

        layers.reverse()

        # print(layers)
        # print(self.layers)

        for layer in layers:
            # print(layer)
            dout = layer.backward(dout)

        grad_w = [self.layers[2 * i].dw for i in range(self.layers_num)]
        grad_b = [self.layers[2 * i].db for i in range(self.layers_num)]

        return grad_w, grad_b

    def SGD(self):
        batch_size = 100
        train_size = self.X.shape[0]
        epoch_num = 10000
        lr = 0.1  # learning rate
        beta1 = 0.9
        beta2 = 0.999
        momentum = 1

        # v_w = [np.zeros_like(w) for w in self.w]
        # v_b = [np.zeros_like(b) for b in self.b]

        h_w = [np.zeros_like(w) for w in self.w]
        h_b = [np.zeros_like(b) for b in self.b]

        # m_w = v_w.copy()
        # m_b = v_b.copy()

        # flag = max(int(train_size / batch_size), 1)

        # train_loss_list = list()
        # train_acc_list = list()

        for i in range(epoch_num):
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = self.X[batch_mask]
            y_batch = self.Y[batch_mask]

            grad_w, grad_b = self.gradient(x_batch, y_batch)

            # tmp_lr = lr * np.sqrt(1 - beta2 ** (i + 1)) / (1 - beta1 ** (i + 1))

            for j in range(self.layers_num):
                # Adam
                # m_w[j] += (1 - beta1) * (grad_w[j] - m_w[j])
                # m_b[j] += (1 - beta1) * (grad_b[j] - m_b[j])
                #
                # v_w[j] += (1 - beta2) * (grad_w[j] ** 2 - v_w[j])
                # v_b[j] += (1 - beta2) * (grad_b[j] ** 2 - v_b[j])
                #
                # self.layers[2 * j].w -= tmp_lr * m_w[j] / (np.sqrt(v_w[j] - np.min(v_w[j])) + 1e-7)
                # self.layers[2 * j].b -= tmp_lr * m_b[j] / (np.sqrt(v_b[j] - np.min(v_b[j])) + 1e-7)

                # Momentum
                # v_w[j] = momentum * v_w[j] - lr * grad_w[j]
                # v_b[j] = momentum * v_b[j] - lr * grad_b[j]
                #
                # self.layers[2 * j].w += v_w[j]
                # self.layers[2 * j].b += v_b[j]

                # AdaGrad
                # lr=0.1
                h_w[j] += np.square(grad_w[j])
                h_b[j] += np.square(grad_b[j])

                self.layers[2 * j].w -= lr * grad_w[j] / (np.sqrt(h_w[j]) + 1e-7)
                self.layers[2 * j].b -= lr * grad_b[j] / (np.sqrt(h_b[j]) + 1e-7)

            # train_loss_list.append(self.loss(x_batch, y_batch))

            test_acc = self.accuracy(self.test_X, self.test_Y)
            # train_acc_list.append(test_acc)
            print("第", i, "轮，loss-->", self.loss(x_batch, y_batch), "acc-->", test_acc)

            # if i % flag == 0:
            #     test_acc = self.accuracy(self.test_X, self.test_Y)
            #     train_acc_list.append(test_acc)
            #     print("第", i, "轮，精确度：", test_acc)


t0 = time.clock()

net = Network([784, 50, 10])

net.SGD()
# print(net.accuracy(net.test_X, net.test_Y))

t = time.clock() - t0
print("\n耗时：", t, "s=", t / 60, "min")