import pm4py
from pm4py.algo.filtering.log.auto_filter import auto_filter
from pm4py.objects.petri.check_soundness import check_wfnet
from pm4py.algo.conformance.tokenreplay.algorithm import apply as token_replay

if __name__ == "__main__":
    log = pm4py.read_xes('../../../../../ProcessMining/git_log_sanitized.xes')
a
    print("Log count before filtering: " + str(len(log)))
    log_filtered = auto_filter.apply_auto_filter(log)
    print("Log count before filtering: " + str(len(log_filtered)))

    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log_filtered, noise_threshold=0.99)

    # Check petri net properties
    print("Initial Marking: ", initial_marking)
    print("Final Marking: ", final_marking)
    print("Number of places: ", len(net.places))
    print("List of places: ", net.places)
    print("Number of transitions: ", len(net.transitions))
    print("List of transitions: ", net.transitions)
    print("Number of arcs: ", len(net.arcs))
    print("List of arcs: ", net.arcs)
    print("Is WFNet: ", check_wfnet(net))

    # Token replay
    replayed_traces = token_replay(log_filtered, net, initial_marking, final_marking)
    print("Replayed traces: ", replayed_traces)

    pm4py.view_petri_net(net, initial_marking, final_marking, format="svg")
