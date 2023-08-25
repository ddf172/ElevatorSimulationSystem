import copy
import random


class Elevator:
    def __init__(self, position, capacity, last_move=0):
        self.people = []
        self.fitness = 0
        self.position = position
        self.capacity = capacity
        self.path = []
        self.last_move = last_move


class Person:
    person_id = 0

    def __init__(self, start_pos, destination):
        self.id = self.person_id
        self.person_id += 1
        self.start_pos = start_pos
        self.destination = destination


class Member:
    def __init__(self):
        self.elevators = []
        self.fitness = 0


class Algorithm:
    # Fitness
    move_penalty = -1
    door_movement = -1
    no_move = 0
    no_move_with_passenger = -10
    missed_destination_floor = -100
    drop_out = 100
    pick_up = 10
    waiting_time = -2
    journey_time = -1

    # Algorith configuration
    population_size = 200
    generations = 100
    mutation_rate = 50  # 0 - 1000
    mutation_amount = 2
    path_length = 10
    
    def __init__(self, elevators, people, floor_number):
        self.elevators = elevators
        self.people = people
        self.floor_number = floor_number
        self.population = []
        self.best_member = None

    def generate_population(self):
        for i in range(self.population_size):
            member = Member()
            for j in range(len(self.elevators)):
                elevator = Elevator(self.elevators[j].position, self.elevators[j].capacity)
                elevator.last_move = self.elevators[j].last_move
                elevator.people = copy.deepcopy(self.elevators[j].people)
                for k in range(self.path_length):
                    move = random.randint(-1, 2)
                    elevator.path.append(move)
                member.elevators.append(elevator)
            self.population.append(member)

    def validate_population(self):
        for member in self.population:
            for elevator in member.elevators:
                possibilites = {
                    -1: [-1, 2],
                    0: [-1, 0, 1, 2],
                    1: [1, 2],
                    2: [-1, 0, 1],
                }
                curr_floor = elevator.position
                original_last_move = elevator.last_move

                for i in range(self.path_length):
                    if elevator.path[i] not in possibilites[elevator.last_move]:
                        elevator.path[i] = random.choice(possibilites[elevator.last_move])

                    if elevator.path[i] <= 1 and (curr_floor + elevator.path[i] < 0 or curr_floor + elevator.path[i] >= floor_number):
                        if elevator.last_move == 2:
                            elevator.path[i] *= -1
                        else:
                            elevator.path[i] = 2

                    if elevator.path[i] <= 1:
                        curr_floor += elevator.path[i]

                    elevator.last_move = elevator.path[i]

                elevator.last_move = original_last_move

    def crossover_population(self):
        for i in range(0, self.population_size, 2):
            new_member1 = Member()
            new_member2 = Member()
            for j in range(len(self.elevators)):
                parent1 = self.population[i].elevators[j]
                parent2 = self.population[i+1].elevators[j]

                child1 = Elevator(parent1.position, parent1.capacity, parent1.last_move)
                child1.people = copy.deepcopy(parent1.people)
                child2 = Elevator(parent2.position, parent2.capacity, parent2.last_move)
                child2.people = copy.deepcopy(parent2.people)

                total_fitness = max(parent1.fitness, 0) + max(parent2.fitness, 0)
                if total_fitness == 0:
                    probabilities = [0.5, 0.5]
                else:
                    probabilities = [parent1.fitness / total_fitness, parent2.fitness / total_fitness]

                for k in range(self.path_length):
                    if parent1.path[k] == parent2.path[k]:
                        child1.path.append(parent1.path[k])
                        child2.path.append(parent1.path[k])
                    else:
                        child1.path.append(random.choices([parent1.path[k], parent2.path[k]], probabilities, k=1))
                        child2.path.append(random.choices([parent1.path[k], parent2.path[k]], probabilities, k=1))
                new_member1.elevators.append(child1)
                new_member2.elevators.append(child2)

            self.population.append(new_member1)
            self.population.append(new_member2)

    def select_population(self):
        self.population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        self.population = self.population[0:self.population_size]

    def evaluate_population(self):
        for member in self.population:
            people_copy = copy.deepcopy(self.people)
            member.fitness = 0

            elevators_copy = copy.deepcopy(member.elevators)
            for index in range(self.path_length):
                for elevator in member.elevators:
                    move = elevator.path[index]

                    if move == 1 or move == -1:
                        missed_count = 0
                        for person in elevator.people:
                            if person.destination == elevator.position:
                                missed_count += 1

                        elevator.fitness += missed_count * self.missed_destination_floor
                        elevator.fitness += self.journey_time * len(elevator.people)
                        elevator.fitness += self.move_penalty

                        elevator.position += move

                    elif move == 0:
                        elevator.fitness += self.no_move
                        elevator.fitness += len(elevator.people) * self.no_move_with_passenger
                        elevator.fitness += len(elevator.people) * self.journey_time

                    else:
                        elevator.fitness += self.door_movement
                        people_to_remove = []
                        for person_index, person in enumerate(elevator.people):
                            if person.destination == elevator.position:
                                people_to_remove.append(person_index)

                        people_to_remove = sorted(people_to_remove, reverse=True)

                        for person_index in people_to_remove:
                            elevator.people.pop(person_index)
                            elevator.fitness += self.drop_out

                        elevator.fitness += len(elevator.people) * self.journey_time

                        people_entering_elevator = []
                        for person_index, person in enumerate(people_copy):
                            if len(elevator.people) == elevator.capacity:
                                break
                            if person.start_pos == elevator.position:
                                people_entering_elevator.append(person_index)
                                elevator.people.append(person)
                                elevator.fitness += self.pick_up

                        people_entering_elevator = sorted(people_entering_elevator, reverse=True)
                        for person_index in people_entering_elevator:
                            people_copy.pop(person_index)

                member.fitness += len(people_copy) * self.waiting_time

            for elevator in member.elevators:
                member.fitness += elevator.fitness

            member.elevators = elevators_copy

    def save_best_member(self):
        if self.best_member is None or self.best_member.fitness < self.population[0].fitness:
            self.best_member = self.population[0]

    def mutate_population(self):
        for member in self.population:
            for elevator in member.elevators:
                for i in range(self.path_length):
                    if random.randint(0, 1000) < self.mutation_rate:
                        elevator.path[i] = random.randint(-1, 2)


elevators_data = [
    Elevator(position=0, capacity=5),
    Elevator(position=2, capacity=5)
]

people_data = [
    Person(start_pos=0, destination=5),
    Person(start_pos=3, destination=1),
    Person(start_pos=6, destination=0),
    Person(start_pos=1, destination=4),
    Person(start_pos=2, destination=0),
    # Dodaj więcej osób...
]

floor_number = 10

algorithm = Algorithm(elevators_data, people_data, floor_number)

iterations = 80
algorithm.generate_population()
while iterations > 0:
    iterations -= 1
    algorithm.crossover_population()
    algorithm.mutate_population()
    algorithm.validate_population()
    algorithm.evaluate_population()
    algorithm.select_population()
    algorithm.save_best_member()

print(123)

