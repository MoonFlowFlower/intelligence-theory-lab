from itl_devbench.envs.developmental_grid import DevelopmentalGridEnv


def test_same_config_seed_stage_rule_seed_and_actions_replay_identically():
    config = {"width": 7, "height": 7, "max_ticks": 30}
    actions = ["up", "left", "eat", "right", "inspect", "down", "wait"]

    def rollout():
        env = DevelopmentalGridEnv(config, seed=11)
        observations = [env.reset(stage=6, rule_seed=3).to_dict()]
        rewards = []
        dones = []
        infos = []
        for action in actions:
            obs, reward, done, info = env.step(action)
            observations.append(obs.to_dict())
            rewards.append(reward)
            dones.append(done)
            infos.append(info)
        return observations, rewards, dones, infos

    assert rollout() == rollout()
