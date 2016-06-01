'''
A Multilayer Perceptron implementation example using TensorFlow library.

'''
import copy
import tensorflow as tf
import numpy
import logging
logger = logging.getLogger('percp')
import time


class Perceptron(object):

    def __init__(self, n_input,n_hidden_1, n_output):
        self.n_input = n_input
        self.n_hidden_1 = n_hidden_1
        #self.n_hidden_2 = n_hidden_2
        self.n_output = n_output
        self.sess = None
        #self.sess = tf.Session()
        self.fitness = 0
        self.initialized = False
        self.weights = {'h1':None,  'out': None}
        self.biases = {'b1':None,  'out':None}
        self.fitness = 0
        self.weights_arr = []
        self.biases_arr = []
        
    

    def set_fitness(self, points):
        logger.info('fitness recorded: %d'%(points,))
        self.fitness = points

     # Create model
    def multilayer_perceptron(self, X, weights, biases):
        layer_1 = tf.sigmoid(tf.add(tf.matmul(X, weights['h1']), biases['b1']))
        #layer_2 = tf.sigmoid(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))

        return tf.sigmoid(tf.matmul(layer_1, weights['out']) + biases['out'])
   
        
    


    # tf Graph input
    
    def init1(self):
        self.weights = {
        'h1': tf.Variable(tf.random_normal([self.n_input, self.n_hidden_1])),
        
        'out': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_output]))
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([self.n_hidden_1])),
           
            'out': tf.Variable(tf.random_normal([self.n_output]))
        }
        self.x = tf.placeholder('float', [None, self.n_input])
        self.pred = self.multilayer_perceptron(self.x, self.weights, self.biases)
        #if not self.sess:
        self.sess = tf.Session()
        self.init = tf.initialize_all_variables()
        self.sess.run(self.init)
        self.get_dict()
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
        arr2 = tf.reshape(self.weights['out'],[self.n_hidden_1*self.n_output]).eval(session=self.sess)
        weight_arr = numpy.append(arr1, arr2)
        biases_arr = numpy.append(self.biases['b1'].eval(session=self.sess),self.biases['out'].eval(session=self.sess))
        self.weights_arr = weight_arr
        self.biases_arr = biases_arr
        self.as_dict = {"weights":weight_arr,"biases":biases_arr}

        return self.as_dict

    def reload(self):
        #logger.info('dict of genome %s %s' %(str(self),str(self.as_dict),))
        weights_arr = self.as_dict['weights']
        biases_arr = self.as_dict['biases']
        dim1 = self.n_input*self.n_hidden_1
        dim2 = self.n_hidden_1*self.n_output
        h1 = tf.convert_to_tensor(weights_arr[:dim1])
        out = tf.convert_to_tensor(weights_arr[dim1:])

        self.weights['h1'] = tf.reshape(h1,[self.n_input,self.n_hidden_1])
        self.weights['out'] = tf.reshape(out,[self.n_hidden_1,self.n_output])
        self.biases['b1'] = tf.convert_to_tensor(biases_arr[:self.n_hidden_1])
        self.biases['out'] = tf.convert_to_tensor(biases_arr[self.n_hidden_1:])
        self.x = tf.placeholder('float', [None, self.n_input])
        #if not self.sess:
        self.sess = tf.Session()
        self.init = tf.initialize_all_variables()
        self.sess.run(self.init)
        self.pred = self.multilayer_perceptron(self.x, self.weights, self.biases)
        self.initialized = True


    def copy(self):
        d = copy.deepcopy(self.as_dict)
        p = Perceptron(self.n_input,self.n_hidden_1,self.n_output)
        p.as_dict = d
        return p

    def __unicode__(self):
        return str(self.fitness)


    
        
   
    
if __name__ == '__main__':
    s1 = time.time()
    sess = tf.Session()
    p = Perceptron(3,4,1)
    
    print p.activate([[0.3,0.6,0.1]])
    print p.activate([[0.4,0.6,0.1]])
    print p.activate([[0.5,0.6,0.1]])
    d = p.get_dict()
    print len(d['weights'])
    print len(d['biases'])
    #sess = tf.Session()
    p1 = Perceptron(3,4,1)
    p1.as_dict = copy.deepcopy(d)
    p1.reload()
    print p1.activate([[0.3,0.6,0.1]])
    print p1.activate([[0.4,0.6,0.1]])
    print p1.activate([[0.5,0.6,0.1]])
    print time.time()-s1