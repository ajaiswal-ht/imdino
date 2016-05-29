'''
A Multilayer Perceptron implementation example using TensorFlow library.

'''

import tensorflow as tf
import numpy
import logging
logger = logging.getLogger('percp')

class Perceptron(object):

    def __init__(self, n_input,n_hidden_1, n_hidden_2, n_output):
        self.n_input = n_input
        self.n_hidden_1 = n_hidden_1
        self.n_hidden_2 = n_hidden_2
        self.n_output = n_output
        self.sess = None
        #self.sess = tf.Session()
        self.initialized = False
        self.weights = {'h1':None, 'h2':None, 'out': None}
        self.biases = {'b1':None, 'b2':None, 'out':None}
        self.fitness = 0
        
    

    def set_fitness(self, points):
        self.fitness = points

     # Create model
    def multilayer_perceptron(self, X, weights, biases):
        layer_1 = tf.sigmoid(tf.add(tf.matmul(X, weights['h1']), biases['b1']))
        layer_2 = tf.sigmoid(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))

        return tf.sigmoid(tf.matmul(layer_2, weights['out']) + biases['out'])
   
        
    


    # tf Graph input
    
    def init1(self):
        self.weights = {
        'h1': tf.Variable(tf.random_normal([self.n_input, self.n_hidden_1])),
        'h2': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_hidden_2])),
        'out': tf.Variable(tf.random_normal([self.n_hidden_2, self.n_output]))
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([self.n_hidden_1])),
            'b2': tf.Variable(tf.random_normal([self.n_hidden_2])),
            'out': tf.Variable(tf.random_normal([self.n_output]))
        }
        self.x = tf.placeholder('float', [None, self.n_input])
        self.pred = self.multilayer_perceptron(self.x, self.weights, self.biases)
        #if not self.sess:
        self.sess = tf.Session()
        self.init = tf.initialize_all_variables()
        self.sess.run(self.init)
        self.initialized = True
   
    # Store layers weight & bias
    def activate(self,inputs):
        logger.info('activating for input %s' %(str(inputs),))
        #i = tf.constant([inputs])
        if self.initialized is False:
            self.init1()
        outputs = self.sess.run(self.pred, feed_dict={self.x: inputs})
        return outputs

    def get_dict(self):
        #self.sess = tf.Session()
        arr1 = tf.reshape(self.weights['h1'], [self.n_input*self.n_hidden_1]).eval(session=self.sess)
        arr2 = tf.reshape(self.weights['h2'], [self.n_hidden_1*self.n_hidden_2]).eval(session=self.sess)
        arr3 = tf.reshape(self.weights['out'],[self.n_hidden_2*self.n_output]).eval(session=self.sess)
        weight_arr = numpy.append(numpy.append(arr1, arr2), arr3)
        biases_arr = numpy.append(numpy.append(self.biases['b1'].eval(session=self.sess),
            self.biases['b2'].eval(session=self.sess)),  
            self.biases['out'].eval(session=self.sess))

        return {"weights":weight_arr,"biases":biases_arr}

    def reload(self, param_dict):
        weights_arr = param_dict['weights']
        biases_arr = param_dict['biases']
        dim1 = self.n_input*self.n_hidden_1
        dim2 = self.n_hidden_1*self.n_hidden_2
        dim3 = self.n_hidden_2*self.n_output
        h1 = tf.convert_to_tensor(weights_arr[:dim1])
        h2 = tf.convert_to_tensor(weights_arr[dim1:dim1+dim2])
        out = tf.convert_to_tensor(weights_arr[dim1+dim2:])

        self.weights['h1'] = tf.reshape(h1,[self.n_input,self.n_hidden_1])
        self.weights['h2'] = tf.reshape(h2,[self.n_hidden_1,self.n_hidden_2])
        self.weights['out'] = tf.reshape(out,[self.n_hidden_2,self.n_output])
        self.biases['b1'] = tf.convert_to_tensor(biases_arr[:self.n_hidden_1])
        self.biases['b2'] = tf.convert_to_tensor(biases_arr[self.n_hidden_1:self.n_hidden_1+self.n_hidden_2])
        self.biases['out'] = tf.convert_to_tensor(biases_arr[self.n_hidden_1+self.n_hidden_2:])
        self.x = tf.placeholder('float', [None, self.n_input])
        #if not self.sess:
        self.sess = tf.Session()
        self.init = tf.initialize_all_variables()
        self.sess.run(self.init)
        self.pred = self.multilayer_perceptron(self.x, self.weights, self.biases)
        self.initialized = True

    def copy(self):
        d = self.get_dict()
        p = Perceptron(self.n_input,self.n_hidden_1, self.n_hidden_2, self.n_output)
        p.reload(d)
        return p

    def __unicode__(self):
        return str(self.fitness)


    
        
   
    
if __name__ == '__main__':
    with tf.Session() as sess:
        p = Perceptron(3,4,4,1,sess)
        
        print p.activate([[0.3,0.6,0.1]])
        print p.activate([[0.4,0.6,0.1]])
        print p.activate([[0.5,0.6,0.1]])
        d = p.get_dict()
        print len(d['weights'])
        print len(d['biases'])
        p1 = Perceptron(3,4,4,1,sess)
        p1.reload(d)
        print p1.activate([[0.3,0.6,0.1]])
        print p1.activate([[0.4,0.6,0.1]])
        print p1.activate([[0.5,0.6,0.1]])