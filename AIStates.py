from StateTemplates import *

class EnemyIdle(State):
    def Execute(agent):
        if agent.target != None:
            agent.change_state(EnemyHunting)
        else:
            agent.update_target()

class EnemyHunting(State):
    def Execute(agent):
        if agent.target.hp == 0:
            agent.cancel_target()
            agent.change_state(EnemyIdle)
            
        if agent.distance_to_target() > agent.get_attack_distance():
            agent.move_to_target()
        elif agent.target.hp > 0:
            agent.attack_target()

                



class SpawnerIdle(State):
    def Execute(agent):
        agent.current_tick = (agent.current_tick + 1) % agent.ticks
        if agent.current_tick == 0:
            agent.spawn()