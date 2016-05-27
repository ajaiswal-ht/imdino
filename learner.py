from tfperceptron import Perceptron
import numpy as np
import logging
from threading import Thread
import random

logger = logging.getLogger('dino.learner')
class Learner():

    def __init__(self, gameManip, ui, genomeUnits, selection, mutationProb):
        self.gm = gameManip
        self.genomes = []
        self.state = 'STOP'
        self.genome = 0
        self.generation = 0
        self.shouldCheckExperience = False
        self.genomeUnits = genomeUnits
        self.selection = selection
        self.mutationProb = mutationProb
        self.sess = tf.Session()



    // Build genomes before calling executeGeneration.
    def startLearning(self):

        // Build genomes if needed
        while (self.genomes.length < self.genomeUnits):
            self.genomes.push(self.buildGenome(3, 1))
  
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
  

        self.generation++;
        logger.info('Executing generation '+self.generation);

        self.genome = 0;

        
        self.current_thread = Thread(target = self.executeGenome)
        self.next_thread = None
        self.current_thread.start()
        self.current_thread.join()
        if self.next_thread:
            self.next_thread.join()
    
    def genify(self):

        # Kill worst genomes
        self.genomes = self.selectBestGenomes(self.selection);

        # Copy best genomes
        bestGenomes = _.clone(Learn.genomes);

        # Cross Over ()
        while (self.genomes.length < self.genomeUnits - 2):
             // Get two random Genomes
            genA = _.sample(bestGenomes).toJSON();
            genB = _.sample(bestGenomes).toJSON();

            // Cross over and Mutate
            newGenome = self.mutate(self.crossOver(genA, genB));

            // Add to generation
            self.genomes.push(Network.fromJSON(newGenome));
    

        // Mutation-only
        while (self.genomes.length < self.genomeUnits) {
            // Get two random Genomes
            gen = _.sample(bestGenomes).toJSON();

      // Cross over and Mutate
            newGenome = Learn.mutate(gen);

      // Add to generation
            self.genomes.push(Network.fromJSON(newGenome));
    

        logger.info('Completed generation '+Learn.generation);

    // Execute next generation
        self.executeGeneration();



    # Sort all the genomes, and delete the worst one
    # untill the genome list has selectN elements.
    def selectBestGenomes(self):
        selected = _.sortBy(self.genomes, 'fitness').reverse();
        while (selected.length > self.selection) {
            selected.pop();
        logger.info('Fitness: '+_.pluck(selected, 'fitness').join(','));
        return selected;



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
        # Learn.ui.logger.log('Executing genome '+Learn.genome);
        
        # Check if genome has AT LEAST some experience
        if (self.shouldCheckExperience): 
            if not self.checkExperience(genome):
                genome.fitness = 0;
                #Learn.ui.logger.log('Genome '+Learn.genome+' has no min. experience');
                return next();
    
  

        self.gm.startNewGame(function (){

         # Reads sensor data, and apply network
        self.gm.onSensorData = function (){
            var inputs = [
            self.gm.sensors[0].value,
            self.gm.sensors[0].size,
            self.gm.sensors[0].speed,
        ]
        logger.info(inputs)
        # Apply to network
        outputs = genome.activate(inputs);

        self.gm.setGameOutput(outputs[0][0]);

        # Wait game end, and compute fitness
        self.gm.onGameEnd = lambda points: genome.fitness = points
            

      // Go to next genome
        if self.genome < 12:
            self.current_thread = Thread(target = self.executeGenome)
            self.current_thread.start()




    # Validate if any acction occur uppon a given input (in this case, distance).
    # genome only keeps a single activation value for any given input,
    #it will return false
    def checkExperience(self, genome):
  
        step, start, stop = (0.1, 0.0, 1)

        // Inputs are default. We only want to test the first index
        inputs = [[0.0, 0.3, 0.2]]
        outputs = {}

        for k in np.arange(start,stop,step):
            inputs[0][0] = k;

            activation = genome.activate(inputs[0][0])
            state = self.gm.getDiscreteState(activation)
    
            outputs.update(state:true)
           # Count states, and return true if greater than 1
        if len(outputs.keys())>1:
            return True
        return False



    # Load genomes saved from saver
    def loadGenomes(self, genomes, deleteOthers):
        if deleteOthers:
            self.genomes = []
  
        loaded = 0
        for (var k in genomes):
            self.genomes.push(self.saver.genomes[k]));
            loaded +=1
  

        logger.log('Loaded '+loaded+' genomes!');



    # Builds a new genome based on the 
    # expected number of inputs and outputs
    def buildGenome(self, inputs, outputs):
        logger.log('Build genome '+(self.genomes.length+1));

        network = Perceptron(inputs, 4, 4, outputs, self.sess);

        return network;



    #SPECIFIC to Neural Network.
    #Those two methods convert from JSON to Array, and from Array to JSON
    def crossOver(self, netA, netB):
        #Swap (50% prob.)
        if (Math.random() > 0.5) {
            var tmp = netA;
            netA = netB;
            netB = tmp;
  

      // Clone network
      netA = _.cloneDeep(netA);
      netB = _.cloneDeep(netB);

      // Cross over data keys
      Learn.crossOverDataKey(netA.neurons, netB.neurons, 'bias');

      return netA;
}


// Does random mutations across all
// the biases and weights of the Networks
// (This must be done in the JSON to
// prevent modifying the current one)
Learn.mutate = function (net){
  // Mutate
  Learn.mutateDataKeys(net.neurons, 'bias', Learn.mutationProb);
  
  Learn.mutateDataKeys(net.connections, 'weight', Learn.mutationProb);

  return net;
}


# // Given an Object A and an object B, both Arrays
# // of Objects:
# // 
# // 1) Select a cross over point (cutLocation)
# //    randomly (going from 0 to A.length)
# // 2) Swap values from `key` one to another,
# //    starting by cutLocation
    def crossOverDataKey(self, a, b, key) {
        cutLocation = int(len(a) * random.random());

  var tmp;
        for (var k = cutLocation; k < a.length; k++) {
            // Swap
            tmp = a[k][key];
            a[k][key] = b[k][key];
            b[k][key] = tmp;
  



// Given an Array of objects with key `key`,
// and also a `mutationRate`, randomly Mutate
// the value of each key, if random value is
// lower than mutationRate for each element.
Learn.mutateDataKeys = function (a, key, mutationRate){
  for (var k = 0; k < a.length; k++) {
    // Should mutate?
    if (Math.random() > mutationRate) {
      continue;
    }

    a[k][key] += a[k][key] * (Math.random() - 0.5) * 3 + (Math.random() - 0.5);
  }
}