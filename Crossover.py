from Objects import Member, Elevator
from Settings import Settings
from random import choice
from Tabu import Tabu


class Crossover:
    def __init__(self):
        self.settings = Settings()

    def get_offspring_path_move(self, move1: int, move2: int) -> int:
        if move1 == move2:
            return move1

        possible_moves = set(self.settings.path.path_possible_moves[move1]) - {move1}
        return choice(list(possible_moves))

    def append_offspring_elevator_move(self, elevator1: Elevator, elevator2: Elevator, offspring1: Elevator, offspring2: Elevator, index: int) -> None:
        # index does not mean that at given index move will be appended, it is just to get the move from parents
        move1 = elevator1.state.path[index]
        move2 = elevator2.state.path[index]

        offspring1.state.path.append(self.get_offspring_path_move(move1, move2))
        offspring2.state.path.append(self.get_offspring_path_move(move2, move1))

    def crossover_elevators(self, elevator1: Elevator, elevator2: Elevator, offspring1_elevator: Elevator, offspring2_elevator: Elevator) -> tuple[Elevator, Elevator]:
        for i in range(self.settings.algorithm.path_length):
            self.append_offspring_elevator_move(elevator1, elevator2, offspring1_elevator, offspring2_elevator, i)
        return offspring1_elevator, offspring2_elevator

    @staticmethod
    def fix_elevator_path(elevator: Elevator) -> None:
        tabu = Tabu(elevator.state.path, elevator.state.curr_position, elevator.state.last_move_from_prev_iteration)
        tabu.validate_and_repair_path()
        elevator.state.path = tabu.get_path()

    def create_elevator_offspring(self, elevator1: Elevator, elevator2: Elevator) -> tuple[Elevator, Elevator]:
        offspring1_elevator = elevator1.create_elevator_deepcopy()
        offspring2_elevator = elevator2.create_elevator_deepcopy()

        offspring1_elevator, offspring2_elevator = self.crossover_elevators(elevator1, elevator2, offspring1_elevator, offspring2_elevator)
        self.fix_elevator_path(offspring1_elevator)
        self.fix_elevator_path(offspring2_elevator)

        return offspring1_elevator, offspring2_elevator

    def crossover_members(self, parent1: Member, parent2: Member, offspring1: Member, offspring2: Member) -> tuple[Member, Member]:
        for i in range(self.settings.elevator_number):
            offspring1_elevator, offspring2_elevator = self.create_elevator_offspring(parent1.elevators[i], parent2.elevators[i])
            offspring1.add_elevator(offspring1_elevator)
            offspring2.add_elevator(offspring2_elevator)

        return offspring1, offspring2

    def create_offspring(self, parent1: Member, parent2: Member) -> tuple[Member, Member]:
        offspring1 = Member()
        offspring2 = Member()

        return self.crossover_members(parent1, parent2, offspring1, offspring2)

    def crossover_population(self, population: list[Member]) -> None:
        for i in range(0, self.settings.algorithm.population_size, 2):
            parent1 = population[i]
            parent2 = population[i + 1]

            offspring1, offspring2 = self.create_offspring(parent1, parent2)

            population.append(offspring1)
            population.append(offspring2)
