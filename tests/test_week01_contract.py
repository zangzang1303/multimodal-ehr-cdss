"""Cross-check the contracts handed off between the three week 1 members."""

from pathlib import Path

import yaml

from src.api.schemas import DiseaseLabel, TabularFeatures


ROOT = Path(__file__).resolve().parents[1]


def test_model_and_data_contract_agree():
    data = yaml.safe_load((ROOT / "configs/data_schema.yaml").read_text(encoding="utf-8"))
    model = yaml.safe_load((ROOT / "configs/model_config.yaml").read_text(encoding="utf-8"))

    numeric = {field["name"] for field in data["features"]["numerical"]}
    categorical = {field["name"] for field in data["features"]["categorical"]}
    assert len(numeric) == 9
    assert len(categorical) == 4
    assert numeric | categorical == set(TabularFeatures.model_fields)
    assert list(data["targets"]["labels"].values()) == [d.value for d in DiseaseLabel]
    assert data["targets"]["num_classes"] == model["training"]["num_classes"] == 4

    for field in data["features"]["numerical"]:
        schema_field = TabularFeatures.model_fields[field["name"]]
        constraints = {type(item).__name__: item for item in schema_field.metadata}
        assert constraints["Ge"].ge == field["min"]
        assert constraints["Le"].le == field["max"]
