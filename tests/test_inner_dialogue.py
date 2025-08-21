import pytest
from udmm2.dialogue.dialogue_manager import DialogueManager, InnerUtterance
from udmm2.agent.agent import UDMMAgent
from udmm2.envs.natural_env import NaturalEnv
from udmm2.goals.attractor import AttractorModel

def test_inner_utterance_on_prediction_error():
    agent = UDMMAgent()
    dm = agent.dialogue
    utt = dm.on_prediction_error(pred_err=1.23, context={"expectation":"pos(0,0)","observed":"pos(1,2)"})
    assert isinstance(utt, InnerUtterance)
    assert "انحراف" in utt.text

def test_subgoal_completion_triggers_utterance():
    agent = UDMMAgent()
    attractor = AttractorModel(target_x=2.0, target_y=0.0)
    agent.set_hierarchical_attractor(attractor, n_steps=2)
    hi = agent.hierarchical_intent

    # Manually move agent to the first subgoal to trigger completion
    first_subgoal = hi.subgoals[0]
    agent.body.x = first_subgoal.target_x
    agent.body.y = first_subgoal.target_y

    # The check and dialogue hook are in select_action, so we call that
    agent.select_action()

    # Check that an utterance was generated
    assert len(agent.dialogue.inner_history) > 0
    last_utterance = agent.dialogue.inner_history[-1]
    assert last_utterance.trigger == "subgoal_completed"
    assert "أنجزت" in last_utterance.text
