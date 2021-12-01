#Brenda Paola Castillo Torres - A01632227
# ACTIVIDAD INTEGRADORA 

# Util
import random

# Model
import agentpy as ap
import matplotlib.animation

# Visualization
import matplotlib.pyplot as plt
import IPython
import time

# Server
import client

#Direcciones válidas a las que se puede mover un auto
#como solo es una intersección con calles de un sentido, los carros pueden moverse hacia la derecha o hacia abajo
VALID_MOVES = {
    'RIGHT': (0, 1),
    'DOWN': (1, 0)
}

GREEN = 1
YELLOW = 2
RED = 3
BLUE = 4

COLOR_STRINGS = {
    GREEN: 'GREEN',
    YELLOW: 'YELLOW',
    RED: 'RED',
    BLUE: 'BLUE'
}

#Clase carro, encargada de inicializar sus atributos y la dirección a la que va a ir
class Car(ap.Agent):
    def setup(self):
        self.dir = random.choice(list(VALID_MOVES.keys())) #obtiene una dirección aleatoria a la que se puede mover un carro
        self.color = BLUE
        self.type = 'CAR'
    
    def get_dir(self):
        return VALID_MOVES[self.dir] if random.uniform(0, 1) > 0.1 else (0, 0)

    def get_dir_name(self):
        return self.dir

#Clase semáforo, encargada de incializar todos los semáforos en amarillo
class TrafficLight(ap.Agent):
    def setup(self):
        self.color = YELLOW
        self.type = 'TRAFFIC_LIGHT'

#Modelo intersección, encargado del movimiento de los carros y control de luces del semáforo
class Interseccion(ap.Model):
    #Función para añadir un nuevo carro al grid y definir la posición inicial donde empezará 
    #dependiendo de la dirección a la que se pueda mover
    def add_car(self):
        self.new_car = ap.AgentList(self, 1, Car)

        start_positions = {
            'LEFT': (self.v_pos, 0),
            'UP': (0, self.h_pos)
        }

        for car in self.new_car:
            dir_name = car.get_dir_name()

            if dir_name == 'RIGHT':
                position = [start_positions['LEFT']]
            elif dir_name == 'DOWN':
                position = [start_positions['UP']]

        self.grid.add_agents(self.new_car, position)
        self.car_count += 1

        # Add to database
        car = list(self.new_car)[0]
        car_id = car.id
        position = self.grid.positions[car]
        self.client.add_car(car_id, position)

    #Función que define si en el segmento de calle horizontal hay un carro aproximándose al semáforo
    def check_car_horizontal(self, a, b):
        started = False
        for neighbor in self.grid.neighbors(self.semaforos[a]):
            semaforo_pos = self.grid.positions[self.semaforos[a]]
            if self.grid.positions[neighbor][1] == semaforo_pos[1] - 1:
                self.semaforos[a].color = GREEN
                self.client.update_traffic_light(self.semaforos[a].id, COLOR_STRINGS[self.semaforos[a].color])
                self.semaforos[b].color = RED
                self.client.update_traffic_light(self.semaforos[b].id, COLOR_STRINGS[self.semaforos[b].color])
                self.duracion_semaforo = self.p.duracion_semaforo
                started = True
        return started

    #Función que define si en el segmento de calle vertical hay un carro aproximándose al semáforo
    def check_car_vertical(self, a, b):
        started = False
        for neighbor in self.grid.neighbors(self.semaforos[b]):
            semaforo_pos = self.grid.positions[self.semaforos[b]]
            if self.grid.positions[neighbor][0] == semaforo_pos[0] - 1:
                self.semaforos[b].color = GREEN
                self.client.update_traffic_light(self.semaforos[b].id, COLOR_STRINGS[self.semaforos[b].color])
                self.semaforos[a].color = RED
                self.client.update_traffic_light(self.semaforos[a].id, COLOR_STRINGS[self.semaforos[a].color])
                self.duracion_semaforo = self.p.duracion_semaforo
                started = True
        return started

    def setup(self):

        self.client = client.Client("http://localhost:8000/")
        
       # Definir el tamaño que tendrán las calles
        street_length = self.street_length = self.p.size
        self.h_pos = street_length // 2
        self.v_pos = street_length // 2

        # Crear dos semáforos para la intersección y añadirlos en la posición que les corresponde
        self.semaforos = ap.AgentList(self, 2, TrafficLight)
        self.status_semaforos = False
        posiciones_semaforos = [(self.v_pos, self.h_pos-1), (self.h_pos-1, self.v_pos)]
        nombres_semaforos = ['A', 'B', 'C', 'D']

        # semaforos[0]: horizontal
        # semaforos[1]: vertical

        i = 0
        for semaforo in self.semaforos:
            self.client.add_traffic_light(semaforo.id, COLOR_STRINGS[semaforo.color], nombres_semaforos[i])
            i += 1

        # Crear grid (calles)
        self.grid = ap.Grid(self, (self.p.size, self.p.size), track_empty=True)
        self.grid.add_agents(self.semaforos, posiciones_semaforos)

        # Counters
        self.step_count = 0 #define el tiempo máximo de steps que se harán
        self.car_count = 0 #define cuántos carros se pueden agregar a la simulación en tiempo de ejecución
        self.wait_time = 0


    def step(self):
        #Añadir un nuevo carro en tiempo de ejecución mientras no se tenga el número máximo de carros
        if self.car_count < self.p.n_cars:
            self.add_car()

        #Si ambos semáforos se encuentran en color amarilo, checar si en alguno de los dos hay un carro 
        #que quiera cruzar. Si si hay alguno, pone el semáforo con el carro más cercano en color verde y el 
        #otro en color rojo
        if self.semaforos[0].color == YELLOW and self.semaforos[1].color == YELLOW:
            started = self.check_car_horizontal(0,1)
            if not started:
                started = self.check_car_vertical(0,1)
        
        #Si el semáforo en calle horizontal ya está en verde, esperar 5 segundos en ese color y ver si
        # en el semáforo de la calle vertical hay un carro esperando para ponerlo en verde 
        elif self.semaforos[0].color == GREEN:
            self.duracion_semaforo -= 1
            if self.duracion_semaforo == 0:
                if not self.check_car_vertical(0,1):
                    self.semaforos[0].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[0].id, COLOR_STRINGS[self.semaforos[0].color])
                    self.semaforos[1].color = YELLOW  
                    self.client.update_traffic_light(self.semaforos[1].id, COLOR_STRINGS[self.semaforos[1].color])              

        #Si el semáforo en calle vertical ya está en verde, esperar 5 segundos en ese color y ver si
        # en el semáforo de la calle horizontal hay un carro esperando para ponerlo en verde 
        elif self.semaforos[1].color == GREEN:
            self.duracion_semaforo -= 1
            if self.duracion_semaforo == 0:
                if not self.check_car_horizontal(0,1):
                    self.semaforos[0].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[0].id, COLOR_STRINGS[self.semaforos[0].color])
                    self.semaforos[1].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[1].id, COLOR_STRINGS[self.semaforos[1].color])
        
        #Lógica para mover a los carros, si el semáforo de la calle donde se encuentran está en verde o si
        # el lugar al que se quieren mover NO hay un carro, entonces se mueven una posición
        for agent in list(self.grid.agents):
            agent_pos = self.grid.positions[agent]
            move = True
            if agent.type == 'CAR':
                for neighbor in self.grid.neighbors(agent):
                    if agent.get_dir_name() == 'RIGHT':
                        # si el vecino es el de uno en frente y corresponde a la misma calle (posición vertical)
                        if self.grid.positions[neighbor][1] == agent_pos[1] + 1 and self.grid.positions[neighbor][0] == \
                                agent_pos[0]:
                            if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED) or neighbor.type == 'CAR':
                                move = False
                                if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED):
                                    self.wait_time += 1
                                break
                    elif agent.get_dir_name() == 'DOWN':
                        if self.grid.positions[neighbor][0] == agent_pos[0] + 1 and self.grid.positions[neighbor][1] == \
                                agent_pos[1]:
                            if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED) or neighbor.type == 'CAR':
                                move = False
                                if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED):
                                    self.wait_time += 1
                                break
                if move:
                    self.grid.move_by(agent, agent.get_dir())
                    new_pos = self.grid.positions[agent]
                    self.client.update_car(agent.id, new_pos)
             
                #Si se llega al final de la calle, eliminar el carro
                if(self.grid.positions[agent] == (self.v_pos, self.h_pos *2 -1) or self.grid.positions[agent] == (self.v_pos*2-1, self.h_pos)):
                    self.grid.remove_agents(agent)
                    self.client.delete_car(agent.id)
             

        if self.p.time == self.step_count:
            self.stop()

        # upload changes to cloud
        self.client.commit()

        self.step_count += 1

        time.sleep(self.p.step_dur)

    def end(self):
        for agent in self.grid.agents:
            self.client.delete_car(agent.id)
            self.client.delete_traffic_light(agent.id)


def animation_plot(model, ax):
    attr_grid = model.grid.attr_grid('color')
    color_dict = {1: '#00ff00', 2: '#ffff00', 3: '#ff0000', 4: '#0000ff', None: '#eeeeee'}
    ap.gridplot(attr_grid, ax=ax, color_dict=color_dict, convert=True)
    ax.set_title(f"Simulación de una intersección de autos\n"
                 f"Time-step: {model.t} "
                 f"Wait time: {model.wait_time}")


parameters = {
    'size': 20, #tamaño del grid
    'n_cars': 8, #número total máximo de autos
    'time': 40, #tiempo total de ejecuión
    'step_dur': 0.3,
    'duracion_semaforo': 5 #plan de luces -> duración en color verde de cada semáforo
}

"""
fig, ax = plt.subplots()
model = Interseccion(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
IPython.display.HTML(animation.to_jshtml(fps=8))
"""

if __name__ == "__main__":
    model = Interseccion(parameters)
    model.run()
