import pytest
from data_generator import generate_metric, RESOURCES

def test_generate_metric_normal():
    metric = generate_metric(spike=False)
    assert metric['resource_id'] in RESOURCES
    assert 10.0 <= metric['cpu_usage'] <= 40.0
    assert 'timestamp' in metric

def test_generate_metric_spike():
    metric = generate_metric(spike=True)
    assert metric['resource_id'] == 'ec2-worker-node'
    assert 800.0 <= metric['cpu_usage'] <= 1000.0
