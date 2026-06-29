from itl_devbench.envs.task_family_generator import TaskFamilyGenerator, load_generator_config


def test_aliased_food_has_same_observation_different_hidden_state_and_correct_action():
    config = load_generator_config("configs/itl_devbench_001c.yaml")
    pair = TaskFamilyGenerator(config).perceptual_aliasing_pair("aliased_food_v1")

    left, right = pair
    assert left.observation_signature == right.observation_signature
    assert left.hidden_rule["latent_type"] != right.hidden_rule["latent_type"]
    assert left.oracle_script[0] != right.oracle_script[0]
    assert left.hidden_rule["latent_type"] not in str(left.public_observation)
    assert right.hidden_rule["latent_type"] not in str(right.public_observation)
