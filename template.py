""" 'Description'
    Inputs:
    Output:
"""

from Grasshopper import Instances
from System.Drawing import PointF
from System import Guid

put_data = [
    # ここに入力していく
]
recompute_doc_obj_id = []

def ParamInput(base_param, p_data):
    if type(p_data[1]) == list:
        child_param = getattr(base_param, p_data[0])
        for p_d in p_data[1]:
            ParamInput(child_param, p_d)
        return
    
    setattr(base_param, p_data[0], p_data[1])

def SetPersistentData(Param, Data):
    Param.SetPersistentData(Data)

def Callback(doc):
    for id in recompute_doc_obj_id:
        put_data[id][6].ExpireSolution(True)
    

def main():
    doc = ghenv.Component.OnPingDocument()
    u_server = doc.UndoServer
    u_server.RemoveRecord(u_server.UndoGuids[0])
    
    pivot = ghenv.Component.Attributes.Pivot
    for c in put_data:
        c_pivot = PointF(c[2][0] + pivot.X, c[2][1] + pivot.Y)
        if not (Instances
            .ActiveCanvas
            .Validator
            .CanCreateObject(Guid(c[1]), c_pivot)
        ):
            raise Exception("ERROR: Can Create Object.")
        Instances.ActiveCanvas.InstantiateNewObject(Guid(c[1]), c_pivot, False)
        c[6] = doc.Objects[doc.Objects.Count - 1]
        if c[0] == "Param":
            if c[3]: SetPersistentData(c[6], c[3])
            if c[4]:
                for c_params in c[4]:
                    ParamInput(c[6], c_params)
        elif c[0] == "Component":
            if c[3]:
                for c_param in c[3]:
                    ParamInput(c[6], c_param)
            if c[4]:
                for i, c_input in enumerate(c[4]):
                    if c_input[0]: SetPersistentData(c[6].Params.Input[i], c_input[0])
                    if c_input[1]:
                        for c_i in c_input[1]:
                            ParamInput(c[6].Params.Input[i], c_i)
            if c[5]:
                for i, c_output in enumerate(c[5]):
                    if c_output[0]:
                        for c_o in c_output[0]:
                            ParamInput(c[6].Params.Output[i], c_o)
    
    doc.DeselectAll()
    for c in put_data:
        c[6].Attributes.Selected = True
        if c[0] == "Param":
            if c[5]:
                for sid in c[5]:
                    if put_data[sid[0]][0] == "Param":
                        rid = put_data[sid[0]][6]
                    elif put_data[sid[0]][0] == "Component":
                        rid = put_data[sid[0]][6].Params.Input[sid[1]]
                    rid.AddSource(c[6])
        elif c[0] == "Component":
            for c_output in c[5]:
                sids = c_output[1]
                if sids:
                    for i, sid in enumerate(sids):
                        if put_data[sid[0]][0] == "Param":
                            rid = put_data[sid[0]][6]
                        elif put_data[sid[0]][0] == "Component":
                            rid = put_data[sid[0]][6].Params.Input[sid[1]]
                        rid.AddSource(c[6].Params.Output[i])
    
    doc.ScheduleSolution(1, Callback)
    doc.UndoUtil.MergeRecords(len(put_data))
    doc.RemoveObject(ghenv.Component, False)
    

if True:
    main()