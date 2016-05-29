from tfperceptron import Perceptron
import numpy as np
import logging
import tensorflow as tf
from threading import Thread
import random
from collections import OrderedDict
import collections
import copy
import time

logger = logging.getLogger('dino.learner')
class Learner(object):

    def __init__(self, gameManip, genomeUnits, selection, mutationProb):
        self.gm = gameManip
        self.genomes = []
        self.state = 'STOP'
        self.genome = 0
        self.generation = 0
        self.shouldCheckExperience = False
        self.genomeUnits = genomeUnits
        self.selection = selection
        self.mutationProb = mutationProb
        #self.sess = tf.Session()
        #self.saver = tf.train.Saver()



    # Build genomes before calling executeGeneration.
    def startLearning(self):

        # Build genomes if needed
        while (len(self.genomes) < self.genomeUnits):
            self.genomes.append(self.buildGenome(3, 1))
  
        self.executeGeneration()
  



# Given the entire generation of genomes (An array),
# applyes method `executeGenome` for each element.
# After all elements have completed executing:
# 
# 1) Select best genomes
# 2) Does cross over (except for 2 genomes)
# 3) Does Mutation-only on remaining genomes
# 4) Execute generation (recursivelly)
    def executeGeneration(self):
        if (self.state == 'STOP'):
            return
  

        self.generation += 1
        logger.info('Executing generation %d'%(self.generation,))

        self.genome = 0

        while(self.genome< len(self.genomes)):
            t= Thread(target=self.executeGenome)
            t.start()
            while t.is_alive():
                time.sleep(5)
        self.genify()
        #self.current_thread = Thread(target = self.executeGenome)
        #self.next_thread = None
        #self.current_thread.start()
        #self.current_thread.join()
        #if self.next_thread:
        #    self.next_thread.join()
    
    def genify(self):

        # Kill worst genomes
        self.genomes = self.selectBestGenomes()

        # Copy best genomes
        bestGenomes = copy.copy(self.genomes)

        # Cross Over ()
        while len(self.genomes) <= self.genomeUnits - 2:
            # Get two random Genomes
            genA = random.choice(bestGenomes).copy()
            genB = random.choice(bestGenomes).copy()
            #logger.info('weights' + str(genA.weights)+str(genB.weights))
            #Cross over and Mutate
            newGenome = self.mutate(self.crossOver(genA, genB))

            #Add to generation
            self.genomes.append(newGenome)
    

        # Mutation-only
        while len(self.genomes) <= self.genomeUnits:
            # Get two random Genomes
            gen = random.choice(bestGenomes).copy()

            # Cross over and Mutate
            newGenome = self.mutate(gen);

            # Add to generation
            self.genomes.append(newGenome);
    

        logger.info('Completed generation %d' %(self.generation,))

        #Execute next generation
        self.executeGeneration();



    # Sort all the genomes, and delete the worst one
    # untill the genome list has selectN elements.
    def selectBestGenomes(self):
        d = dict(enumerate(self.genomes))
        f = []
        s = []
        selected = OrderedDict(sorted(d.items(), key= lambda t: t[1].fitness, reverse=True)).values()
        selected = selected[:self.selection]
        for select in selected:
            s.append(select.copy())
            f.append(select.fitness)
        selected = None
        logger.info('Fitness: %s' %(str(f),))
        return s
    
   



  # Waits the game to end, and start a new one, then:
  # 1) Set's listener for sensorData
  # 2) On data read, applyes the neural network, and
  #    set it's output
  # 3) When the game has ended and compute the fitness
    def executeGenome(self):
        if (self.state == 'STOP'):
            return
  
        genome = self.genomes[self.genome]
        self.genome += 1
        logger.info('Executing genome %d' %(self.genome,))
        
        # Check if genome has AT LEAST some experience
        if (self.shouldCheckExperience): 
            if not self.checkExperience(genome):
                genome.fitness = 0;
                logger.info('Genome %d has no min. experience'%(self.genome))
                return
    
  
        #Reads sensor data, and apply network
        self.gm.startNewGame(genome)
        logger.info('starter at 149 in learner')
        #Go to next genome
        #if self.genome < len(self.genomes):
        #    self.current_thread = Thread(target = self.executeGenome)
        #    self.current_thread.start()
        #else:
        #    self.genify()

        


    # Validate if any acction occur uppon a given input (in this case, distance).
    # genome only keeps a single activation value for any given input,
    #it will return false
    def checkExperience(self, genome):
  
        step, start, stop = (0.1, 0.0, 1)

        #: Inputs are default. We only want to test the first index
        inputs = [[0.0, 0.3, 0.2]]
        outputs = {}

        for k in np.arange(start,stop,step):
            inputs[0][0] = k;

            activation = genome.activate(inputs[0][0])
            state = self.gm.getDiscreteState(activation)
    
            outputs.update({state:true})
           # Count states, and return true if greater than 1
        if len(outputs.keys())>1:
            return True
        return False



    # Load genomes saved from saver
    def loadGenomes(self, genomes, deleteOthers):
        if deleteOthers:
            self.genomes = []
  
        loaded = 0
        for k in genomes:
            self.genomes.append(genome)
            loaded +=1
  

        logger.info('Loaded %d genomes!' %(loaded,))



    # Builds a new genome based on the 
    # expected number of inputs and outputs
    def buildGenome(self, inputs, outputs):
        logger.info('Build genome %d' %(len(self.genomes)+1,))

        network = Perceptron(inputs, 4, 4, outputs)

        return network;



    #SPECIFIC to Neural Network.
    # Crossover two networks
    def crossOver(self, netA, netB):
        #Swap (50% prob.)
        if (random.random() > 0.5):
            netA, netB = netB, netA
  
        # get dict from net
        netA_dict = netA.get_dict()
        netB_dict = netB.get_dict()

        # Cross over bias
        netA_biases = netA_dict['biases']
        netB_biases = netB_dict['biases']
        cutLocation = int(len(netA_biases) * random.random())
        netA_updated_biases = np.append(netA_biases[(range(0,cutLocation)),],
            netB_biases[(range(cutLocation, len(netB_biases))),]) 
        netB_updated_biases = np.append(netB_biases[(range(0,cutLocation)),],
            netA_biases[(range(cutLocation, len(netA_biases))),]) 
        netA_dict['biases'] = netA_updated_biases
        netB_dict['biases'] = netB_updated_biases
        netA.reload(netA_dict)
        netB.reload(netB_dict)

        return netA



  # Does random mutations across all
  # the biases and weights of the Networks
  # (This must be done in the JSON to
  # prevent modifying the current one)
    def mutate(self, net):
        # Mutate
        # get dict from net
        net_dict = net.get_dict()
        self.mutateDataKeys(net_dict, 'biases', self.mutationProb)
        self.mutateDataKeys(net_dict, 'weights', self.mutationProb)
        net.reload(net_dict)
        return net




  



    # Given an Array of objects with key `key`,
    # and also a `mutationRate`, randomly Mutate
    # the value of each key, if random value is
    # lower than mutationRate for each element.
    def mutateDataKeys(self, a, key, mutationRate):
        for k in range(0,len(a[key])):
        # Should mutate?
            if (random.random() > mutationRate):
                continue
            a[key][k] += a[key][k] * (random.random() - 0.5) * 3 + (random.random() - 0.5)
  
