import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "fsp_pum_env"
BATTERY = SRC / "battery"
TRAJECTORY_SETS = SRC / "trajectory_sets.py"


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield ("import", alias.name, None)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                yield ("from", node.module or "", alias.name)


def test_battery_code_has_no_simulator_import_path_or_internal_symbol_reachability():
    battery_files = sorted(BATTERY.glob("*.py"))
    assert battery_files
    assert BATTERY / "graph_cache.py" in battery_files
    assert BATTERY / "rag_nn.py" in battery_files
    assert BATTERY / "obs_decoders.py" in battery_files
    assert BATTERY / "seq_models.py" in battery_files

    forbidden_text = {"controlled_theta", "response_distribution"}
    for path in battery_files:
        text = path.read_text(encoding="utf-8")
        assert not (forbidden_text & set(text.replace("(", " ").replace(")", " ").replace(".", " ").split()))
        for kind, module, name in _imports(path):
            assert module not in {"src.fsp_pum_env.simulator", "fsp_pum_env.simulator", ".simulator"}
            assert not module.endswith(".simulator")
            assert not (name or "").startswith("_")


def test_trajectory_sets_imports_only_public_simulator_surface():
    allowed_from_simulator = {"FspPumSimulator", "SimulatorVariant"}
    assert TRAJECTORY_SETS.exists()

    for kind, module, name in _imports(TRAJECTORY_SETS):
        if module in {"src.fsp_pum_env.simulator", "fsp_pum_env.simulator", ".simulator"} or module.endswith(".simulator"):
            assert name in allowed_from_simulator
        assert not (name or "").startswith("_")
