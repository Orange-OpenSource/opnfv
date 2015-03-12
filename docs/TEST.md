# Testing

---
## Intro
In order to perform functional and performance testing, we use a dedicated VM.

    TODO: add test-tool VM in architecture and puppetise test-tool VM

On this VM, we install several tools:
* Rally: https://wiki.openstack.org/wiki/Rally
* RobotFramework: http://robotframework.org/
* SIPP http://sipp.sourceforge.net/



## Installation & Configuration

### Rally

* Log on the test-tool VM
* install rally (https://rally.readthedocs.org/en/latest/tutorial/step_0_installation.html)
* For Rally scenario, follow https://rally.readthedocs.org/en/latest/tutorial/step_1_setting_up_env_and_running_benchmark_from_samples.html
* For Tempest, follow the instructions https://www.mirantis.com/blog/rally-openstack-tempest-testing-made-simpler
* In first step Rally scenario were fine but Tempest scenarios failed due to configuration
Apply patch https://review.openstack.org/#/c/163330/
```bash
pip uninstall rally && cd ./rally && python setup.py install
```

You shall be able to run Rally towards your OpenStack






## Test description

### Rally

By default, the different Rally Scenarios are:
* authenticate
* ceilometer
* cinder
* designate
* dummy
* glance
* heat
* keystone
* mistral
* neutron
* nova
* quotas
* requests
* sahara
* tempest
* vm
* zaqar

tempest tests can be retrieved at https://github.com/openstack/tempest


## Results

### Rally
Rally includes a reporting tool
https://rally.readthedocs.org/en/latest/tutorial/step_1_setting_up_env_and_running_benchmark_from_samples.html

    TODO: put results of tempest and nova tests here + display Rally


## Automation
