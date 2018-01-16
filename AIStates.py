from StateTemplates import *

class IdleState(State):
    pass

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
        if agent.target.get('hp') == 0:
            agent.cancel_target()
            agent.change_state(EnemyIdle)
            
        if agent.distance_to_target() > agent.get('attack_range'):
            agent.move_to_target()
        elif agent.get('hp') > 0:
            agent.attack(agent.target)
            agent.change_state(EnemyAttack)

class EnemyAttack(State):
    def Enter(agent):
        agent.change_animation('idle')

    def Execute(agent):
        if agent.target == None:
            agent.change_state(EnemyIdle)
            return 
        if agent.target.get('hp') == 0:
            agent.cancel_target()
            agent.change_state(EnemyIdle)
        if agent.distance_to_target() > agent.get('attack_range'):
            agent.change_state(EnemyGoToTarget)
        elif agent.target.get('hp') > 0:
            agent.attack(agent.target)


class SpawnerIdle(State):
    def Execute(agent):
        if agent.get('mana') >= agent.spell.manacost:
            agent.spell.cast(agent)
        return