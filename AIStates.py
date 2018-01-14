from StateTemplates import *

class EnemyIdle(State):
    def Enter(agent):
        agent.change_animation('idle')

    def Execute(agent):
        if agent.target != None:
            agent.change_state(EnemyGoToTarget)
        else:
            agent.update_target()

class EnemyGoToTarget(State):
    def Enter(agent):
        agent.change_animation('move')

    def Execute(agent):
        if agent.target == None:
            agent.change_state(EnemyIdle)
            return
        if agent.target.hp == 0:
            agent.cancel_target()
            agent.change_state(EnemyIdle)
            
        if agent.distance_to_target() > agent.get_attack_distance():
            agent.move_to_target()
        elif agent.target.hp > 0:
            agent.attack_target()
            agent.change_state(EnemyAttack)

class EnemyAttack(State):
    def Enter(agent):
        agent.change_animation('idle')

    def Execute(agent):
        if agent.target == None:
            agent.change_state(EnemyIdle)
            return 
        if agent.target.hp == 0:
            agent.cancel_target()
            agent.change_state(EnemyIdle)
        if agent.distance_to_target() > agent.get_attack_distance():
            agent.change_state(EnemyGoToTarget)
        elif agent.target.hp > 0:
            agent.attack_target()


class SpawnerIdle(State):
    def Execute(agent):
        agent.current_tick = (agent.current_tick + 1) % agent.ticks
        if agent.current_tick == 0:
            agent.spawn()