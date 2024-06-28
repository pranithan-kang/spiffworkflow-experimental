import json
import os
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
from SpiffWorkflow.spiff.parser import SpiffBpmnParser, VALIDATOR
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from uuid import uuid4

registry = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)
serializer = BpmnWorkflowSerializer(registry=registry)
parser = SpiffBpmnParser(validator=VALIDATOR)
script_engine = PythonScriptEngine()

def create_workflow(instance_id: str = uuid4()):
    with open('bpmn_files/test-form.bpmn', 'r') as f:
        with open('bpmn_files/test-subprocess.bpmn', 'r') as f2:
            # Parse the BPMN file
            parser.add_bpmn_io(f)
            parser.add_bpmn_io(f2)
        
            process_id = "test_process"
            spec = parser.get_spec(process_id)
            sp_specs = parser.get_subprocess_specs(process_id)

            # Create Workflow Object
            wf = BpmnWorkflow(spec, sp_specs, script_engine=script_engine)
            wf.set_data(
                instance_id=instance_id
            )

    # with open('wfdata/spec/test-form.json', 'w') as s:
    #     with open('wfdata/spec/test-subprocess.json', 'w') as s2:
    #         serializer.to_dict(spec)
    #         serializer.to_dict(sp_specs)
    #         json.dump(serializer.to_dict(spec), s, indent=2)
    #         json.dump(serializer.to_dict(sp_specs), s2, indent=2)
    
    return wf

def load_workflow(instance_id: str):
    if not os.path.exists(f'wfdata/instance/'):
        os.makedirs(f'wfdata/instance/')
    with open(f'wfdata/instance/{instance_id}.json', 'r') as f:
        json_instance = json.load(f)
        wf = serializer.from_dict(json_instance)
        return wf
    
def dump_workflow(wf: BpmnWorkflow):
    if not os.path.exists(f'wfdata/instance/'):
        os.makedirs(f'wfdata/instance/')
    with open(f'wfdata/instance/{wf.get_data("instance_id")}.json', 'w') as f:
        json_instance = serializer.to_dict(wf)
        json.dump(json_instance, f, indent=2)

def sample_route_1():
    wf = create_workflow()

    # Execute the workflow
    wf.do_engine_steps()

    tasks = wf.get_tasks(spec_name="task_1", state=TaskState.READY)
    if tasks:
        task = tasks[0]
    task.set_data(a=1)
    task.run()
    wf.do_engine_steps()

    dump_workflow(wf)
        
sample_route_1()

# def sample_route_2():
#     wf = create_workflow()

#     # Execute the workflow
#     wf.do_engine_steps()

#     tasks = wf.get_tasks(spec_name="task_1", state=TaskState.READY)
#     if not tasks:
#         raise Exception("Task not found")
#     task = tasks[0]
#     task.set_data(a=2)
#     task.run()
#     wf.do_engine_steps()

#     dump_workflow(wf)
#     return wf

# test_continue_wf = sample_route_2()

# def continue_sample_route_2():
#     wf = load_workflow(test_continue_wf.get_data("instance_id"))
#     tasks = wf.get_tasks(spec_name="sub_task_1", state=TaskState.READY)
#     if not tasks:
#         raise Exception("Task not found")
#     task = tasks[0]
#     task.run()
#     wf.do_engine_steps()

#     dump_workflow(wf)

# # continue_sample_route_2()