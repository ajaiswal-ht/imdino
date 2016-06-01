import npyscreen, math
import logging
from drawille import Canvas
from utils import ThreadJob
import threading


LOG_FILENAME = '/tmp/ui.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

class CustomMultiLineAction(npyscreen.MultiLineAction):
    '''
        Making custom MultiLineAction by adding the handlers
    '''
    learner = None
    gm = None
    def __init__(self,*args,**kwargs):

        super(CustomMultiLineAction,self).__init__(*args,**kwargs)
       
        
        self.add_handlers({
            "q" : self.quit
        })
        self.add_handlers({
            "^K" : self.save
            })
        self.add_handlers({
            "s": self.stop
            })

    def quit(self,*args,**kwargs):
        raise KeyboardInterrupt

    def save(self,*args,**kwargs):
        self.value = 'saved into file'
    
    def stop(self, *args, **kwargs):
        if CustomMultiLineAction.learner.state == 'STOP':
            CustomMultiLineAction.learner.state = 'LEARNING'
            CustomMultiLineAction.gm.focusGame()    
        else:
            CustomMultiLineAction.learner.state = 'STOP';
    


class MultiLineWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = npyscreen.MultiLineEdit


class MultiLineActionWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = CustomMultiLineAction


class WindowForm(npyscreen.FormBaseNew):
    '''
        Frameless Form
    '''
    def create(self, *args, **kwargs):
        super(WindowForm, self).create(*args, **kwargs)
    
    def while_waiting(self):
        pass


class UI(npyscreen.NPSApp):
    '''
        GUI class for ptop
    '''
    def __init__(self,gameManipulator, learner,stop_event):
        self.gm = gameManipulator
        self.learn = learner

        # Global stop event
        self.stop_event = stop_event
        # thread for updating
        self.update_thread = None

        # main form
        self.window = None 

        # widgets
        self.basic_stats = None
        self.network_chart = None
        self.logs_grid = None
        self.game_stats = None
        self.genome_stats = None
        self.actions = None

        # internal data structures
        # c.set(89,31) -- here the corner point will be set
        # the upper bounds are the excluded points
        self.CHART_HEIGHT = 16
        self.CHART_LENGTH = 180
        self.CHART_WIDTH = 20

        # logger
        #self.logger = logging.getLogger('dino.ui')

    def draw_chart(self,canvas,y):
        '''
            :param y: The next height to draw
            :param canvas: The canvas on which to draw
        '''
          
        chart_array = self.network_array
        SIZE_OFFSET = 3*self.CHART_WIDTH
        DISTANCE_OFFSET = self.CHART_WIDTH
        SPEED_OFFSET = 5*self.CHART_WIDTH
        ACTIVATION_OFFSET = 7*self.CHART_WIDTH

        
        for s in range(SIZE_OFFSET, SIZE_OFFSET+self.CHART_WIDTH):
            chart_array[s] = self.bar_length(y['size'])
        for d in range(DISTANCE_OFFSET, DISTANCE_OFFSET+self.CHART_WIDTH):
            chart_array[d] = self.bar_length(y['distance'])
        for s in range(SPEED_OFFSET, SPEED_OFFSET+self.CHART_WIDTH):
            chart_array[s] = self.bar_length(y['speed'])
        for s in range(ACTIVATION_OFFSET, ACTIVATION_OFFSET+self.CHART_WIDTH):
            chart_array[s] = self.bar_length(y['activation'])
        
        

        # now draw on the canvas
        for ctr in xrange(self.CHART_LENGTH):
            end_point = self.CHART_HEIGHT-chart_array[ctr]
            # end_point will be excluded
            
            for i in xrange(self.CHART_HEIGHT,end_point,-1):
                canvas.set(ctr,i)

        return canvas.frame(0,0,self.CHART_LENGTH,self.CHART_HEIGHT)
    def bar_length(self,y):
        return int(y*self.CHART_HEIGHT)


    def while_waiting(self):
        '''
            called periodically when user is not pressing any key
        '''
        if not self.update_thread:
            t = ThreadJob(self.update,self.stop_event,0.6)
            self.update_thread = t
            self.update_thread.start()
            #self.logger.info('Started GUI update thread')

    def update(self):
        '''
            Update the form in background
        '''
                # get the information
        try:
            
            # game Stats
            row1 = ['Status: %s'%(self.learn.state,), 'Fitness: %s '%( self.gm.points,),'GameStatus: %s '%(self.gm.gamestate, ),
            'Generation: %s : %s/%s' %(self.learn.generation, 
                 self.learn.genome, len(self.learn.genomes))]
            self.genome_stats.values = row1
            self.genome_stats.display()
            if self.gm.gameOutput:
                row2 = 'Action: %s \n Activation: %s \n' %(self.gm.gameOutputString, self.gm.gameOutput)
            
            else:
                row2 = 'Loading...'
            self.game_stats.value = row2
            self.game_stats.display()

            ### current state
            network_canvas = Canvas()
            y = {'size':self.gm.sensors[0].size,
            'distance':self.gm.sensors[0].value,
            'speed':self.gm.sensors[0].speed,
            'activation':self.gm.gameOutput}
            self.network_chart.value = (self.draw_chart(network_canvas,y)) + \
            '\n   %s     %s    %s    %s  \n     Distance         Size          Speed            Activation\n' % (self.gm.sensors[0].value,
                self.gm.sensors[0].size,self.gm.sensors[0].speed,self.gm.gameOutput)
            self.network_chart.display()
            #self.logger.info(self.gm.gameOutput)

        # catch the KeyError caused to c
        # cumbersome point of reading the stats data structures
        except KeyError:
            pass

    def main(self):
        npyscreen.setTheme(npyscreen.Themes.DefaultTheme)


        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10

        # setting the main window form
        self.window = WindowForm(parentApp=self,
                                 name="Dino stats ")

        #self.logger.info(self.window.curses_pad.getmaxyx())

        max_y,max_x = self.window.curses_pad.getmaxyx()

        self.Y_SCALING_FACTOR = float(max_y)/27
        self.X_SCALING_FACTOR = float(max_x)/104
        
        self.CHART_LENGTH = int(self.CHART_LENGTH*self.X_SCALING_FACTOR)
        self.CHART_HEIGHT = int(self.CHART_HEIGHT*self.Y_SCALING_FACTOR)
        self.CHART_WIDTH = int(self.CHART_LENGTH/9)
        self.network_array = [0]*self.CHART_LENGTH

        self.network_chart = self.window.add(MultiLineWidget,
                                           name="network stats",
                                           relx=1,
                                           rely=1,
                                           max_height=int(math.ceil(8*self.Y_SCALING_FACTOR)),
                                           max_width=int(100*self.X_SCALING_FACTOR)
                                           )
         
        network_canvas = Canvas()  
        #self.logger.info('yaa')  
        self.network_chart.value =  '\n\n    Distance      Size        Speed         Activation\n'
        #self.logger.info(self.network_chart.value)
        self.network_chart.entry_widget.editable = False
        self.network_chart.display()

        self.logs_grid = self.window.add(MultiLineWidget,
                                           name="Logs",
                                           relx=1,
                                           rely=int(math.ceil(8*self.Y_SCALING_FACTOR)+1),
                                           max_height=int(math.ceil(5*self.Y_SCALING_FACTOR)),
                                           max_width=int(100*self.X_SCALING_FACTOR)
                                           )
        self.logs_grid.value = "Reading genomes_dir"
        self.logs_grid.entry_widget.editable = False
        self.logs_grid.display()


        

        self.game_stats = self.window.add(MultiLineWidget,
                                               name="Game Stats",
                                               relx=1,
                                               rely=int(math.ceil(13*self.Y_SCALING_FACTOR)+3),
                                               max_height=int(6*self.Y_SCALING_FACTOR),
                                               max_width=int(48*self.X_SCALING_FACTOR)
                                               )

        self.game_stats.entry_widget.value=""
        self.game_stats.entry_widget.editable = False
        self.game_stats.display()

        self.genome_stats = self.window.add(MultiLineActionWidget,
                                               name="Genome Stats",
                                               relx=int(52*self.X_SCALING_FACTOR),
                                               rely=int(math.ceil(13*self.Y_SCALING_FACTOR)+3),
                                               max_height=int(6*self.Y_SCALING_FACTOR),
                                               max_width=int(48*self.X_SCALING_FACTOR)
                                               )
        
        self.genome_stats.entry_widget.values = []
        self.genome_stats.entry_widget.scroll_exit = False
        self.genome_stats.display()

        self.actions = self.window.add(npyscreen.FixedText,
                                       relx=1,
                                       rely=int(24*self.Y_SCALING_FACTOR),
                                       )
        
        self.actions.value = "^K : save in file S: to stop learning   q : quit "
        CustomMultiLineAction.gm = self.gm
        CustomMultiLineAction.learner = self.learn
        self.actions.display()
        self.actions.editable = False



        # fix for index error
        #self.network_array = [0]*self.CHART_LENGTH
        
        #self.logger.info('Now going to start the game yeaaaaaaaa')
        t = threading.Thread(target = self.startLearning)
        t.start()
        
        # add subwidgets to the parent widget
        self.window.edit()
    def startLearning(self):
        if self.learn.state == 'STOP':
            self.learn.state = 'LEARNING'
            self.gm.focusGame()
            self.learn.startLearning(self.stop_event)
        else:
            self.learn.state = 'STOP'

if __name__ == '__main__':
    try:
        
        global_stop_event = threading.Event()
        UI({},{},global_stop_event).run()

    except KeyboardInterrupt:
        global_stop_event.set()
        # clear log file
        with open('/tmp/ui.log','w'):
            pass
        raise SystemExit