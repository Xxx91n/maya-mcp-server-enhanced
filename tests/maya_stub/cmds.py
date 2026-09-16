"""Fake maya.cmds over the stub Scene.

Implements the subset of cmds used by maya_scene_module and generated
scene_tools code. Long names, type filters, connections, keyframes,
file ops and constraints are all recorded on the Scene for assertions.
"""

from __future__ import annotations

import json
import math

from . import runtime
from .scene import LIGHT_TYPES, SHAPE_TYPES


def _s():
    if runtime.scene is None:
        raise RuntimeError("maya stub not installed")
    return runtime.scene


_TYPE_FILTERS = {
    "transform": lambda n: n.type == "transform",
    "mesh": lambda n: n.type == "mesh",
    "camera": lambda n: n.type == "camera",
    "locator": lambda n: n.type == "locator",
    "nurbsCurve": lambda n: n.type == "nurbsCurve",
    "joint": lambda n: n.type == "joint",
    "light": lambda n: n.type in LIGHT_TYPES,
    "shadingEngine": lambda n: n.type == "shadingEngine",
}

_MATERIAL_TYPES = {"lambert", "phong", "blinn", "surfaceShader", "aiStandardSurface"}


def ls(*args, **kwargs):
    sc = _s()
    ntype = kwargs.get("type")
    long_ = kwargs.get("long") or kwargs.get("l")
    materials = kwargs.get("materials")

    if args and isinstance(args[0], (list, tuple)):
        names = []
        for nm in args[0]:
            try:
                node = sc.resolve(nm)
            except RuntimeError:
                continue
            if materials and node.type not in _MATERIAL_TYPES:
                continue
            names.append(sc.long_name(node) if long_ else node.name)
        return names or None

    nodes = sc.all_nodes()
    if ntype is not None:
        if isinstance(ntype, (list, tuple)):
            preds = [_TYPE_FILTERS.get(t) or (lambda n, t=t: n.type == t) for t in ntype]
            nodes = [n for n in nodes if any(p(n) for p in preds)]
        else:
            pred = _TYPE_FILTERS.get(ntype) or (lambda n: n.type == ntype)
            nodes = [n for n in nodes if pred(n)]
    if materials:
        nodes = [n for n in nodes if n.type in _MATERIAL_TYPES]

    out = [sc.long_name(n) if long_ else n.name for n in nodes]
    return out if out else None


def objExists(ref):
    sc = _s()
    ref = str(ref)
    if "." in ref:
        node_ref, attr = ref.split(".", 1)
        try:
            node = sc.resolve(node_ref)
        except RuntimeError:
            return False
        return attr.split("[")[0] in node.attrs
    return sc.exists(ref)


def nodeType(ref):
    return _s().resolve(ref).type


def listRelatives(ref, parent=False, children=False, type=None, fullPath=False, shapes=False, **kw):
    sc = _s()
    node = sc.resolve(ref)
    if parent:
        if node.parent is None:
            return None
        return [sc.long_name(node.parent) if fullPath else node.parent.name]
    if children or shapes:
        kids = list(node.children)
        if type is not None:
            pred = _TYPE_FILTERS.get(type) or (lambda n: n.type == type)
            kids = [k for k in kids if pred(k)]
        if shapes:
            kids = [k for k in kids if k.type in SHAPE_TYPES]
        out = [sc.long_name(k) if fullPath else k.name for k in kids]
        return out if out else None
    return None


def listConnections(ref, type=None, **kwargs):
    sc = _s()
    ref = str(ref)
    node_ref, attr = ref.split(".", 1) if "." in ref else (ref, "")
    try:
        node = sc.resolve(node_ref)
    except RuntimeError:
        return None

    if attr.startswith("instObjGroups"):
        targets = []
        cand = [node] if node.type in SHAPE_TYPES else []

        def walk(n):
            for c in n.children:
                if c.type in SHAPE_TYPES:
                    cand.append(c)
                walk(c)

        walk(node)
        for c in cand:
            for t in sc.connections.get(c.name + "." + attr, []):
                if type is None or sc.resolve(t).type == type:
                    targets.append(t)
        return targets or None

    targets = sc.connections.get(node.name + "." + attr, [])
    if type is not None:
        targets = [t for t in targets if sc.resolve(t).type == type]
    return targets or None


def sets(ref, query=False, **kwargs):
    sc = _s()
    if query:
        return sc.set_members.get(sc.resolve(ref).name, []) or None
    return None


def getAttr(ref):
    sc = _s()
    node_ref, attr = str(ref).split(".", 1)
    node = sc.resolve(node_ref)
    attr = attr.split("[")[0]
    if attr in node.attrs:
        v = node.attrs[attr]
        if isinstance(v, tuple):
            return [v]
        return v
    raise RuntimeError("No attribute: " + ref)


def currentUnit(query=False, linear=False, angle=False, time=False, **kw):
    sc = _s()
    if linear:
        return sc.linear_unit
    if angle:
        return sc.angular_unit
    if time:
        return sc.time_unit
    return sc.linear_unit


def upAxis(query=False, axis=False, **kw):
    return _s().up_axis


def about(version=False, **kw):
    return "2024.0-stub" if version else "MayaStub"


def file(*args, **kwargs):
    """Stub cmds.file.

    exportAll writes a REAL file (//Maya ASCII header + serialized scene)
    so checkpoint tests exercise actual disk state; open restores the
    scene graph from it and raises on non-ASCII content, like real Maya.
    """
    sc = _s()
    sc.file_calls.append({"args": args, "kwargs": dict(kwargs)})
    if kwargs.get("query") or kwargs.get("q"):
        if (kwargs.get("sceneName") or kwargs.get("sn")
                or kwargs.get("expandName") or kwargs.get("exn")
                or kwargs.get("absoluteName") or kwargs.get("an")):
            return sc.scene_path
        return None
    if kwargs.get("rename"):
        sc.scene_path = kwargs["rename"]
        return sc.scene_path
    if kwargs.get("open") or kwargs.get("o"):
        path = args[0]
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if "//Maya ASCII" not in text[:2048]:
            raise RuntimeError(f"Cannot open {path}: not a Maya ASCII file")
        sc.restore(json.loads(text.split("\n", 1)[1]))
        sc.scene_path = path
        return sc.scene_path
    if kwargs.get("exportAll"):
        path = args[0]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("//Maya ASCII 2024 scene (stub)\n")
            fh.write(json.dumps(sc.serialize()))
        return path
    if kwargs.get("save") or kwargs.get("saveAs"):
        sc.scene_path = args[0] if args else sc.scene_path
        return sc.scene_path
    return None


def workspace(**kwargs):
    """Stub cmds.workspace — returns the scene's workspace dir."""
    sc = _s()
    if kwargs.get("query") or kwargs.get("q"):
        want_dir = (kwargs.get("rootDirectory") or kwargs.get("rd")
                    or kwargs.get("directory") or kwargs.get("dir"))
        if want_dir:
            return sc.workspace_dir
    return sc.workspace_dir


def move(x, y=None, z=None, *objects, **kwargs):
    sc = _s()
    if y is None and z is None:
        x, y, z = x
    for o in (objects or sc.selection):
        sc.resolve(o).t = [x, y, z]


def rotate(x, y, z, *objects, **kwargs):
    sc = _s()
    for o in (objects or sc.selection):
        sc.resolve(o).r = [x, y, z]


def scale(x, y, z, *objects, **kwargs):
    sc = _s()
    for o in (objects or sc.selection):
        sc.resolve(o).s = [x, y, z]


def xform(ref, query=False, q=False, ws=False, t=False, ro=False, **kw):
    sc = _s()
    node = sc.resolve(ref)
    if q or query:
        if t:
            m = sc.inclusive_matrix(node)
            return [m[12], m[13], m[14]]
        if ro:
            return list(sc.world_rotation(node))
    return None


def camera(name="camera1", focalLength=35.0, **kw):
    sc = _s()
    tr = sc.add_transform(name)
    sh = sc.add_shape(name + "Shape", "camera", tr)
    sh.attrs["focalLength"] = focalLength
    return [tr.name, sh.name]


def spaceLocator(name="locator1", **kw):
    sc = _s()
    tr = sc.add_transform(name)
    sc.add_shape(name + "Shape", "locator", tr)
    return [tr.name, tr.name + "Shape"]


def rename(ref, new_name):
    sc = _s()
    node = sc.resolve(ref)
    lst = sc.nodes.get(node.name, [])
    if node in lst:
        lst.remove(node)
        if not lst:
            del sc.nodes[node.name]
    new_name = sc._unique_name(new_name)
    node.name = new_name
    sc.nodes.setdefault(new_name, []).append(node)
    return new_name


def select(*args, **kwargs):
    sc = _s()
    flat = []
    for a in args:
        flat.extend(a if isinstance(a, (list, tuple)) else [a])
    sc.selection = flat


def aimConstraint(*args, **kwargs):
    """Record the constraint AND apply the equivalent static aim rotation.

    Real Maya evaluates constraints every refresh; the stub computes the
    same orientation once so tests can assert the camera actually aims.
    A None target raises, matching Maya.
    """
    sc = _s()
    target = args[0] if args else None
    if target is None:
        raise RuntimeError("aimConstraint: target cannot be None")
    tnode = sc.resolve(target)
    constrained = sc.resolve(args[1])
    sc.constraints.append({"target": tnode.name, "constrained": constrained.name,
                           "kwargs": dict(kwargs)})
    tp = sc.world_position(tnode)
    cp = sc.world_position(constrained)
    dx, dy, dz = tp[0] - cp[0], tp[1] - cp[1], tp[2] - cp[2]
    dist_xz = math.sqrt(dx * dx + dz * dz)
    if dist_xz > 1e-9 or abs(dy) > 1e-9:
        ry = math.degrees(math.atan2(-dx, -dz))
        rx = math.degrees(math.atan2(dy, dist_xz)) if dist_xz > 1e-9 else (-90 if dy > 0 else 90)
        constrained.r = [rx, ry, 0.0]
    return [constrained.name + "_aimConstraint1"]


def currentTime(t=None, edit=False, **kw):
    sc = _s()
    if edit and t is not None:
        sc.current_time = t
    return sc.current_time


def setKeyframe(ref, attribute=None, **kw):
    _s().keyed.append((str(ref), attribute))


def keyTangent(*args, **kwargs):
    return None


def playbackOptions(min=None, max=None, **kw):
    sc = _s()
    if min is not None or max is not None:
        sc.playback_range = [
            min if min is not None else sc.playback_range[0],
            max if max is not None else sc.playback_range[1],
        ]
    return sc.playback_range


def group(*args, name="group1", **kw):
    sc = _s()
    g = sc.add_transform(name)
    for a in args:
        node = sc.resolve(a)
        if node.parent is not None:
            node.parent.children.remove(node)
        elif node in sc.roots:
            sc.roots.remove(node)
        node.parent = g
        g.children.append(node)
    return g.name


def delete(*args):
    sc = _s()
    for a in args:
        node = sc.resolve(a)
        if node.parent is not None:
            node.parent.children.remove(node)
        elif node in sc.roots:
            sc.roots.remove(node)
        lst = sc.nodes.get(node.name, [])
        if node in lst:
            lst.remove(node)
            if not lst:
                del sc.nodes[node.name]
        sc.deleted.append(node.name)


def warning(msg):
    """Maya cmds.warning — surface a non-fatal warning."""
    _s().warnings.append(str(msg))
