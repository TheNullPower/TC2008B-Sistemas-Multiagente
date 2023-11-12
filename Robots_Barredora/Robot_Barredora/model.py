from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector


import numpy as np

xGrid = 0
yGrid = 0
class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad

class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cargas = 0

class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.cargaBaja = False

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos

    def seleccionar_nueva_pos(self, lista_de_vecinos):
        if (len(lista_de_vecinos) != 0):
            self.sig_pos = self.random.choice(lista_de_vecinos).pos
    
    def cargar(self, vecinos):
        x, y = self.pos
        objects = self.model.grid.get_cell_list_contents(self.pos)
        for obj in objects:
            if isinstance(obj, Celda):
                obj.sucia = False
        if x <= int(xGrid/2) and x - 1 >= 0:
            for vecino in vecinos:
                if vecino.pos == (x-1,y):
                    self.sig_pos = (x-1,y)
        elif x > int(xGrid/2) and x + 1 < xGrid:
            for vecino in vecinos:
                if vecino.pos == (x+1,y):
                    self.sig_pos = (x+1,y)
        
        if y <= int(yGrid/2) and y - 1 >= 0:
            for vecino in vecinos:
                if vecino.pos == (x,y-1):
                    self.sig_pos = (x,y-1)
        elif y > int(yGrid/2) and y + 1 < yGrid:
            for vecino in vecinos:
                if vecino.pos == (x,y+1):
                    self.sig_pos = (x,y+1)

    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias

    def step(self):
        
        vecindad = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        vecinos = list()
        for cell in vecindad:
                objects = self.model.grid.get_cell_list_contents(cell)
                for obj in objects:
                    if isinstance(obj, Celda):
                        vecinos.append(obj)
                    if isinstance(obj, Cargador):
                        if self.carga + 25 <= 100:
                            self.carga += 25
                        else:
                            obj.cargas += 1

        if self.carga < 35:
            self.cargaBaja = True
        elif self.carga > 75:
            self.cargaBaja = False
        
        if self.cargaBaja:
            self.cargar(vecinos)
        else:
            celdas_sucias = self.buscar_celdas_sucia(vecinos)

            if len(celdas_sucias) == 0:
                self.seleccionar_nueva_pos(vecinos)
            else:
                self.limpiar_una_celda(celdas_sucias)

    def advance(self):
        vecindad = self.model.grid.get_neighborhood(
            self.sig_pos, moore=True, include_center=False)
        for cell in vecindad:
            objects = self.model.grid.get_cell_list_contents(cell)
            for obj in objects:
                if isinstance(obj, RobotLimpieza):
                    if obj.sig_pos == self.sig_pos:
                        if obj.unique_id > self.unique_id:
                            self.sig_pos = self.pos

        if self.pos != self.sig_pos:
            if self.carga > 0:
                self.movimientos += 1
                self.carga -= 1
                self.model.grid.move_agent(self, self.sig_pos)

class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 ):
        global xGrid
        global yGrid
        xGrid = M
        yGrid = N
        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de Cargadores
        remove = [(1, N-2),(M-2, N-2), (1, 1), (M-2, 1)]
        for pos in remove:
            posiciones_disponibles.remove(pos)
            celda = Celda(int(f"{num_agentes}0") + 1, self, False)
            self.grid.place_agent(celda, pos)
        remove = [(0, N-1), (M-1, N-1), (0, 0), (M-1, 0)]
        for pos in remove:
            posiciones_disponibles.remove(pos)
        for y in range(1,yGrid-1):
            posiciones_disponibles.remove((0,y))
            posiciones_disponibles.remove((xGrid-1,y))
            self.grid.place_agent(Celda(int(f"{num_agentes}00") + 1, self, False), (0,y))
            self.grid.place_agent(Celda(int(f"{num_agentes}00") + 1, self, False), (xGrid-1,y))
        for x in range(1,xGrid-1):
            posiciones_disponibles.remove((x,0))
            posiciones_disponibles.remove((x,yGrid-1))
            self.grid.place_agent(Celda(int(f"{num_agentes}00") + 1, self, False), (x,0))
            self.grid.place_agent(Celda(int(f"{num_agentes}00") + 1, self, False), (x,yGrid-1))
        self.grid.place_agent(Cargador(int(f"{num_agentes}") + 1, self), (0, N-1))
        self.grid.place_agent(Cargador(int(f"{num_agentes}") + 2, self), (M-1, N-1))
        self.grid.place_agent(Cargador(int(f"{num_agentes}") + 3, self), (0, 0))
        self.grid.place_agent(Cargador(int(f"{num_agentes}") + 4, self), (M-1, 0))

         # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)

        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k=num_agentes)
        else:  # 'Fija'
            pos_inicial_robots = [(int(M/2), 0)] * num_agentes

        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas": get_cargas,
                             "CeldasSucias": get_sucias, "Movimientos": get_movimientos},
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if self.todoLimpio():
            self.running = False

    def todoLimpio(self):
        for cell in self.grid.coord_iter():
            if len(cell) == 3:
                content, x, y = cell
            elif len(cell) == 2:
                content, pos = cell
                x, y = pos
            else:
                raise ValueError("Unexpected format in coord_iter")

            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True


def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid


def get_cargas(model: Model) -> int:
    sum_cargas = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Cargador):
                sum_cargas += obj.cargas
    return sum_cargas


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias

def get_movimientos(model: Model) -> int:
    sum_movimientos = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                sum_movimientos += obj.movimientos

    return sum_movimientos