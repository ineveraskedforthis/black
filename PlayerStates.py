from StateTemplates import *

class PlayerIdle(State):
    def Enter(agent):
        pass

    def Execute(agent):
        if agent.key_pressed == 'LEFT':
            agent.change_state(PlayerMoveLeft)
        if agent.key_pressed == 'RIGHT':
            agent.change_state(PlayerMoveRight)


class PlayerMoveLeft(State):
    def Enter(agent):
        agent.set_orientation('L')

    def Execute(agent):
        agent.step_left()
        if agent.key_pressed == 'NONE':
            agent.change_state(PlayerIdle)
        if agent.key_pressed == 'RIGHT':
            agent.change_state(PlayerMoveRight)



class PlayerMoveRight(State):
    def Enter(agent):
        agent.set_orientation('R')

    def Execute(agent):
        agent.step_right()
        if agent.key_pressed == 'NONE':
            agent.change_state(PlayerIdle)
        if agent.key_pressed == 'LEFT':
            agent.change_state(PlayerMoveLeft)