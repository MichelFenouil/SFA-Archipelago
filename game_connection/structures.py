from ctypes import *

class Vector3s(BigEndianStructure):
    _fields_ = [
        ('x', c_short),
        ('y', c_short),
        ('z', c_short)
    ]

class Vector3f(BigEndianStructure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float)
    ]

class ObjPosData(BigEndianStructure):
    _fields_ = [
        ('rot', Vector3s),
        ('flags', c_int8 * 2),
        ('scale', c_float),
        ('pos', Vector3f)
    ]

class ObjData(BigEndianStructure):
    pass
ObjData._fields_ = [
        ('position', ObjPosData),
        ('prevPos', Vector3f),
        ('velocity', Vector3f),
        ('heldBy_ptr', c_uint32), # ObjInstance*
        ('map', c_uint8),
        ('mtxIdx', c_uint8),
        ('newOpacity', c_uint8),
        ('opacity', c_uint8),
        ('nextObj_ptr', c_uint32), # ObjInstance*
        ('camDistance', c_float),
        ('cullDistance', c_float),
        ('catId', c_uint16),
        ('defNo', c_uint16),
        ('defNo48', c_short),
        ('unk4A', c_short),
        ('objDef_ptr', c_uint32), # ObjDef*
        ('file_ptr', c_uint32), # ObjectFileStruct*
        ('hitstate_ptr', c_uint32), # HitState*
        ('hitboxMtx_ptr', c_uint32), # HitboxMatrix*
        ('unk5C_ptr', c_uint32),
        ('pEventName_ptr', c_uint32),
        ('shadow_ptr', c_uint32),
        ('dll_ptr', c_uint32),
        ('pVecs_ptr', c_uint32), # vec3f*
        ('pTextures_ptr', c_uint32), # Texture*
        ('focusPoints_ptr', c_uint32), # vec3f*
        ('unk78_ptr', c_uint32),
        ('models_ptr', c_uint32), # Model**
        ('oldPos', Vector3f),
        ('pos_0x8c', Vector3f),
        ('animTimer', c_float),
        ('animVal_9c', c_float),
        ('animId', c_int16),
        ('animVal_a2', c_int16),  # GameBit16
        ('cullOffset', c_float),
        ('cullDistance_a8', c_float),
        ('mapId', c_int8),  # MapId8
        ('curModel', c_uint8),
        ('slot', c_uint8),
        ('flags_0xaf', c_uint8),  # ObjInstance_FlagsAF 08 = dont render
        ('flags_0xb0', c_uint16),  # ObjInstance_FlagsB0
        ('objNo', c_int16), 
        ('curSeq', c_short),
        ('unkB6', c_short),
        ('state_ptr', c_uint32), # State*
        ('seqFn_ptr', c_uint32),  # ObjSeqFn*
        ('copyMtxFrom_ptr', c_uint32),  # ObjInstance*
        ('parent_ptr', c_uint32),  # ObjInstance*
        ('child_ptrs', c_uint32 * 3),  # ObjInstance*[3]
        ('unkD4_ptr', c_uint32),
        ('unkD8', c_uint32),
        ('msgQueue_ptr', c_uint32),  # ObjMsgQueue*
        ('unkE0', c_uint8),
        ('unkE1', c_uint8),
        ('unkE2', c_uint8),
        ('flags_e3', c_uint8),
        ('unkE4', c_uint8),
        ('flags_0xe5', c_uint8),
        ('unkE6', c_short),
        ('hintTextIdx', c_uint8),
        ('unkE9', c_uint8),
        ('unkEA', c_uint8),
        ('nChildren', c_uint8),
        ('colorEC', c_ubyte * 4),  # Color4b
        ('unkF0', c_uint8),
        ('brightness', c_uint8),
        ('colorIdx', c_uint8),
        ('unkF3', c_uint8),
        ('curveNoPlus1', c_int32),
        ('flags_0xf8', c_uint32),
        ('oldVel', Vector3f),
        ('cbAfterUpdateBones_ptr', c_uint32)  # objField108_func*
    ]


class ObjState(BigEndianStructure):
    _fields_ = [
        ('activeDistance', c_float),
        ('flag_id', c_uint16),
        ('unk6', c_uint16),
        ('unk8', c_uint32),
        ('flagC', c_uint8),
        ('flagD', c_uint8),
        ('flagE', c_uint8),
    ]