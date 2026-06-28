"""Maya-side scene query module.

This module is injected into Maya via write_module on first scene_* tool call.
It provides efficient batch scene queries using OpenMaya 2.0 API.

All functions return JSON strings for direct use with execute_code(result_type="JSON").
Performance targets: 100 objects < 50ms, 1000 objects < 200ms.
"""

import json
import math
import re
from collections import defaultdict

import maya.api.OpenMaya as om2  # noqa: N813
import maya.cmds as cmds


# --- Internal helpers ---

def _round3(val):
    """Round float to 3 decimal places."""
    return round(float(val), 3)


def _round3_list(vals):
    """Round a list of floats."""
    return [_round3(v) for v in vals]


def _vec3_to_list(p):
    """Convert MPoint/MVector to [x,y,z]."""
    return [_round3(p[0]), _round3(p[1]), _round3(p[2])]


def _matrix_to_pos(matrix):
    """Extract translation from MMatrix."""
    return [_round3(matrix[12]), _round3(matrix[13]), _round3(matrix[14])]


def _classify_node(dag):
    """Classify a DAG node into a type string."""
    try:
        fn = om2.MFnDagNode(dag)
        mtype = fn.typeName
        if mtype == "transform":
            # Check shape children
            for i in range(dag.childCount()):
                child = dag.child(i)
                child_fn = om2.MFnDagNode(child)
                ctype = child_fn.typeName
                if ctype == "mesh":
                    return "mesh"
                elif ctype in ("camera", "stereoRigCamera"):
                    return "camera"
                elif ctype in ("areaLight", "directionalLight", "pointLight",
                               "spotLight", "volumeLight"):
                    return "light"
                elif ctype == "nurbsCurve":
                    return "curve"
                elif ctype == "locator":
                    return "locator"
                elif ctype == "joint":
                    return "joint"
            return "group"
        elif mtype == "mesh":
            return "mesh"
        elif mtype in ("camera", "stereoRigCamera"):
            return "camera"
        elif mtype in ("areaLight", "directionalLight", "pointLight",
                       "spotLight", "volumeLight"):
            return "light"
        return "unknown"
    except Exception:
        return "unknown"


def _get_material_for_dag(dag):
    """Get material name for a DAG node."""
    try:
        fn = om2.MFnDagNode(dag)
        # Find shading engines
        dag_path = om2.MDagPath.getAPathTo(dag)
        try:
            _ = om2.MFnDagNode(dag_path)  # validate dag path
        except Exception:
            pass

        # Use cmds for material lookup (more reliable)
        name = fn.name()
        try:
            sg = cmds.listConnections(name + ".instObjGroups[0]", type="shadingEngine")
            if sg:
                mat = cmds.ls(cmds.listConnections(sg[0] + ".surfaceShader"), materials=True)
                if mat:
                    return mat[0]
        except Exception:
            pass
    except Exception:
        pass
    return None


def _get_mesh_stats(dag):
    """Get vertex and face count for a mesh DAG node."""
    try:
        dag_path = om2.MDagPath.getAPathTo(dag)
        mesh_fn = om2.MFnMesh(dag_path)
        return {
            "v": mesh_fn.numVertices,
            "f": mesh_fn.numPolygons,
        }
    except Exception:
        return {"v": 0, "f": 0}


def _get_bbox_size(bbox):
    """Get [w, h, d] from MBoundingBox."""
    mn = bbox.min
    mx = bbox.max
    return [
        _round3(abs(mx[0] - mn[0])),
        _round3(abs(mx[1] - mn[1])),
        _round3(abs(mx[2] - mn[2])),
    ]


def _point_distance(a, b):
    """Euclidean distance between two MPoints."""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# --- Public API ---

def get_scene_graph(detail_level="compact") -> dict:
    """Return complete scene spatial description in one call.

    Args:
        detail_level: "compact" | "standard" | "full"

    Returns:
        JSON string with objects list, stats, unit, up_axis.
    """
    result = {"objects": [], "stats": {}, "unit": "cm", "up_axis": "y"}

    # Get scene unit
    try:
        linear_unit = cmds.currentUnit(query=True, linear=True)
        unit_map = {"cm": "cm", "m": "m", "mm": "mm", "in": "in", "ft": "ft"}
        result["unit"] = unit_map.get(linear_unit, linear_unit)
    except Exception:
        pass

    # Get up axis
    try:
        up = cmds.upAxis(query=True, axis=True)
        result["up_axis"] = up.lower()
    except Exception:
        pass

    # Get all transforms using OpenMaya iterator (faster than cmds.ls for large scenes)
    sel = om2.MSelectionList()
    try:
        sel.add("*")  # Select all
    except Exception:
        # Fallback: use cmds.ls
        transforms = cmds.ls(type="transform", long=True) or []
        for t in transforms:
            try:
                sel.add(t)
            except Exception:
                continue

    it = om2.MItDag(om2.MItDag.kBreadthFirst)
    it.reset(sel.getDagPath(0) if sel.length() > 0 else om2.MDagPath())

    # Use MItDag for efficient traversal
    transforms = cmds.ls(type="transform", long=True) or []

    for tname in transforms:
        try:
            sel_list = om2.MSelectionList()
            sel_list.add(tname)
            dag = sel_list.getDagPath(0)
        except Exception:
            continue

        fn = om2.MFnDagNode(dag)
        node_type = _classify_node(dag)

        # Skip intermediate shapes
        if node_type in ("mesh", "camera", "light", "curve", "locator"):
            try:
                if fn.isIntermediateObject:
                    continue
            except Exception:
                pass

        # Get bounding box (direct C++ access, fast)
        try:
            bbox = fn.boundingBox
            bbox_min = _vec3_to_list(bbox.min)
            bbox_max = _vec3_to_list(bbox.max)
        except Exception:
            bbox_min = [0, 0, 0]
            bbox_max = [0, 0, 0]

        # Get world position from inclusive matrix
        try:
            world_matrix = dag.inclusiveMatrix()
            pos = _matrix_to_pos(world_matrix)
        except Exception:
            pos = [0, 0, 0]

        # Child count
        try:
            child_count = dag.childCount()
        except Exception:
            child_count = 0

        # Build object entry with short keys
        obj = {
            "n": fn.name(),
            "t": node_type,
            "p": pos,
            "b": bbox_min + bbox_max,
        }
        if child_count > 0:
            obj["c"] = child_count

        # Parent name
        try:
            if dag.length() > 1:
                parent_dag = om2.MDagPath(dag)
                parent_dag.pop()
                obj["pr"] = om2.MFnDagNode(parent_dag).name()
        except Exception:
            pass

        # Standard/Full detail
        if detail_level in ("standard", "full"):
            mat = _get_material_for_dag(dag)
            if mat:
                obj["m"] = mat
            if node_type == "mesh":
                stats = _get_mesh_stats(dag)
                obj["v"] = stats["v"]
                obj["f"] = stats["f"]

        # Full detail (single object deep query)
        if detail_level == "full" and node_type == "mesh":
            try:
                dag_path = om2.MDagPath.getAPathTo(dag)
                mesh_fn = om2.MFnMesh(dag_path)
                # First 100 vertex positions
                verts = []
                for i in range(min(mesh_fn.numVertices, 100)):
                    pt = mesh_fn.getPoint(i, om2.MSpace.kWorld)
                    verts.extend(_round3_list([pt[0], pt[1], pt[2]]))
                obj["verts"] = verts
            except Exception:
                pass

        result["objects"].append(obj)

    # Stats
    type_counts = defaultdict(int)
    for obj in result["objects"]:
        type_counts[obj["t"]] += 1
    result["stats"] = {
        "total": len(result["objects"]),
        "by_type": dict(type_counts),
    }

    return result


def get_zone_map(patterns=None) -> dict:
    """Group objects by naming-pattern zones.

    Args:
        patterns: dict of zone_name -> regex_pattern. If None, uses defaults
                  for pop-up store naming conventions.

    Returns:
        JSON string with zones list.
    """
    if patterns is None:
        patterns = {
            "shell": r"(store_shell|wall|floor|ceiling|roof|facade|exterior)",
            "entrance": r"(entrance|door|gate|shopfront|entry|lobby|foyer)",
            "display": r"(display|shelf|counter|kiosk|vitrine|showcase|podium|stand)",
            "ip_core": r"(kitty|hello_kitty|ip_|character|figure|mascot|logo_main)",
            "furniture": r"(table|chair|bench|sofa|rack|desk|seat|stool)",
            "lighting": r"(light|spot|key_|fill_|rim_|ambient|lamp|luminaire)",
            "path": r"(path|aisle|corridor|walkway|route|lane|passage)",
        }

    # Compile patterns
    compiled = {}
    for zone_name, pat in patterns.items():
        compiled[zone_name] = re.compile(pat, re.IGNORECASE)

    # Get all transforms
    transforms = cmds.ls(type="transform", long=True) or []

    zones = {}
    for zone_name in compiled:
        zones[zone_name] = {
            "name": zone_name,
            "pattern_matched": patterns[zone_name],
            "objects": [],
            "bbox_min": [float("inf")] * 3,
            "bbox_max": [float("-inf")] * 3,
        }

    unassigned = []

    for tname in transforms:
        short_name = tname.split("|")[-1]
        matched_zone = None

        for zone_name, pat in compiled.items():
            if pat.search(short_name):
                matched_zone = zone_name
                break

        if matched_zone:
            zones[matched_zone]["objects"].append(short_name)
            # Update zone bbox
            try:
                sel_list = om2.MSelectionList()
                sel_list.add(tname)
                dag = sel_list.getDagPath(0)
                fn = om2.MFnDagNode(dag)
                bbox = fn.boundingBox
                mn = bbox.min
                mx = bbox.max
                for i in range(3):
                    zones[matched_zone]["bbox_min"][i] = min(
                        zones[matched_zone]["bbox_min"][i], mn[i]
                    )
                    zones[matched_zone]["bbox_max"][i] = max(
                        zones[matched_zone]["bbox_max"][i], mx[i]
                    )
            except Exception:
                pass
        else:
            unassigned.append(short_name)

    # Finalize zones
    result_zones = []
    for zone_name, zone in zones.items():
        if not zone["objects"]:
            continue
        zone["object_count"] = len(zone["objects"])
        # Compute center
        if zone["bbox_min"][0] != float("inf"):
            zone["center"] = [
                _round3((zone["bbox_min"][i] + zone["bbox_max"][i]) / 2)
                for i in range(3)
            ]
            zone["bbox_min"] = _round3_list(zone["bbox_min"])
            zone["bbox_max"] = _round3_list(zone["bbox_max"])
        else:
            zone["center"] = [0, 0, 0]
            zone["bbox_min"] = [0, 0, 0]
            zone["bbox_max"] = [0, 0, 0]
        result_zones.append(zone)

    return {"zones": result_zones, "unassigned_count": len(unassigned)}


def get_spatial_index(max_neighbors=8, max_distance=None) -> dict:
    """Build spatial index with neighbor relationships.

    Args:
        max_neighbors: Maximum neighbors per object (default 8).
        max_distance: Max distance for neighbor inclusion. If None, auto-calculated.

    Returns:
        JSON string with adjacency list: [[obj_a_idx, obj_b_idx, distance], ...]
    """
    transforms = cmds.ls(type="transform", long=True) or []
    if not transforms:
        return {"pairs": [], "objects": [], "threshold": 0}

    # Collect positions and names
    positions = []
    names = []
    for tname in transforms:
        try:
            sel_list = om2.MSelectionList()
            sel_list.add(tname)
            dag = sel_list.getDagPath(0)
            fn = om2.MFnDagNode(dag)
            world_matrix = dag.inclusiveMatrix()
            pos = (world_matrix[12], world_matrix[13], world_matrix[14])
            positions.append((float(pos[0]), float(pos[1]), float(pos[2])))
            names.append(fn.name())
        except Exception:
            continue

    n = len(positions)
    if n == 0:
        return {"pairs": [], "objects": [], "threshold": 0}

    # Auto-calculate threshold if not set
    if max_distance is None:
        # Use average bounding box diagonal * 3 as threshold
        total_diag = 0.0
        count = 0
        for tname in transforms:
            try:
                sel_list = om2.MSelectionList()
                sel_list.add(tname)
                dag = sel_list.getDagPath(0)
                fn = om2.MFnDagNode(dag)
                bbox = fn.boundingBox
                diag = _point_distance(bbox.min, bbox.max)
                total_diag += diag
                count += 1
            except Exception:
                continue
        avg_diag = total_diag / count if count > 0 else 100.0
        max_distance = avg_diag * 3.0

    # Brute-force neighbor search (optimized for < 2000 objects)
    # For larger scenes, use spatial hashing
    pairs = []
    if n <= 2000:
        # Direct O(n^2) with early distance cutoff
        for i in range(n):
            dists = []
            for j in range(i + 1, n):
                dx = positions[i][0] - positions[j][0]
                dy = positions[i][1] - positions[j][1]
                dz = positions[i][2] - positions[j][2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                if dist <= max_distance:
                    dists.append((dist, j))
            dists.sort()
            for dist, j in dists[:max_neighbors]:
                pairs.append([i, j, _round3(dist)])
    else:
        # Spatial hashing for large scenes
        cell_size = max_distance
        grid = defaultdict(list)
        for i, (x, y, z) in enumerate(positions):
            cell = (int(x / cell_size), int(y / cell_size), int(z / cell_size))
            grid[cell].append(i)

        for i, (x, y, z) in enumerate(positions):
            ci = (int(x / cell_size), int(y / cell_size), int(z / cell_size))
            dists = []
            # Check neighboring cells
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        neighbor_cell = (ci[0] + dx, ci[1] + dy, ci[2] + dz)
                        for j in grid.get(neighbor_cell, []):
                            if j <= i:
                                continue
                            d = math.sqrt(
                                (x - positions[j][0]) ** 2
                                + (y - positions[j][1]) ** 2
                                + (z - positions[j][2]) ** 2
                            )
                            if d <= max_distance:
                                dists.append((d, j))
            dists.sort()
            for dist, j in dists[:max_neighbors]:
                pairs.append([i, j, _round3(dist)])

    return {"pairs": pairs, "objects": names, "threshold": _round3(max_distance), "count": n}


def measure(obj_a, obj_b, mode="center") -> dict:
    """Measure spatial relationship between two objects.

    Args:
        obj_a: Name of first object.
        obj_b: Name of second object.
        mode: "center" | "surface" | "clearance" | "bbox"

    Returns:
        JSON string with measurement result.
    """
    result = {
        "obj_a": obj_a,
        "obj_b": obj_b,
        "mode": mode,
        "distance": 0.0,
        "bbox_overlap": False,
        "unit": "cm",
    }

    try:
        # Get unit
        linear_unit = cmds.currentUnit(query=True, linear=True)
        result["unit"] = {"cm": "cm", "m": "m", "mm": "mm"}.get(linear_unit, linear_unit)
    except Exception:
        pass

    try:
        sel_a = om2.MSelectionList()
        sel_a.add(obj_a)
        dag_a = sel_a.getDagPath(0)
        fn_a = om2.MFnDagNode(dag_a)
        bbox_a = fn_a.boundingBox
        pos_a = dag_a.inclusiveMatrix()

        sel_b = om2.MSelectionList()
        sel_b.add(obj_b)
        dag_b = sel_b.getDagPath(0)
        fn_b = om2.MFnDagNode(dag_b)
        bbox_b = fn_b.boundingBox
        pos_b = dag_b.inclusiveMatrix()
    except Exception as e:
        result["error"] = str(e)
        return result

    # Transform bboxes to world space
    world_min_a = bbox_a.min * pos_a
    world_max_a = bbox_a.max * pos_a
    world_min_b = bbox_b.min * pos_b
    world_max_b = bbox_b.max * pos_b

    # Center points
    center_a = om2.MPoint(
        (world_min_a[0] + world_max_a[0]) / 2,
        (world_min_a[1] + world_max_a[1]) / 2,
        (world_min_a[2] + world_max_a[2]) / 2,
    )
    center_b = om2.MPoint(
        (world_min_b[0] + world_max_b[0]) / 2,
        (world_min_b[1] + world_max_b[1]) / 2,
        (world_min_b[2] + world_max_b[2]) / 2,
    )

    if mode == "center":
        result["distance"] = _round3(_point_distance(center_a, center_b))
        result["details"] = {
            "center_a": _vec3_to_list(center_a),
            "center_b": _vec3_to_list(center_b),
        }

    elif mode == "bbox":
        # Check overlap on all 3 axes
        overlap = True
        for i in range(3):
            if world_max_a[i] < world_min_b[i] or world_max_b[i] < world_min_a[i]:
                overlap = False
                break
        result["bbox_overlap"] = overlap

        # Compute gap distance on each axis
        gaps = []
        for i in range(3):
            gap = max(
                0,
                max(world_min_a[i], world_min_b[i]) - min(world_max_a[i], world_max_b[i])
            )
            gaps.append(_round3(gap))
        result["details"] = {"gaps_xyz": gaps, "overlapping": overlap}

        if overlap:
            # Compute overlap volume
            overlap_dims = []
            for i in range(3):
                dim = min(world_max_a[i], world_max_b[i]) - max(world_min_a[i], world_min_b[i])
                overlap_dims.append(max(0, _round3(dim)))
            result["details"]["overlap_dims"] = overlap_dims
            result["distance"] = 0.0
        else:
            result["distance"] = _round3(math.sqrt(sum(g * g for g in gaps)))

    elif mode == "surface":
        # Approximate surface distance using closest bbox face points
        closest_a = om2.MPoint(
            max(world_min_a[0], min(center_b[0], world_max_a[0])),
            max(world_min_a[1], min(center_b[1], world_max_a[1])),
            max(world_min_a[2], min(center_b[2], world_max_a[2])),
        )
        closest_b = om2.MPoint(
            max(world_min_b[0], min(center_a[0], world_max_b[0])),
            max(world_min_b[1], min(center_a[1], world_max_b[1])),
            max(world_min_b[2], min(center_a[2], world_max_b[2])),
        )
        result["distance"] = _round3(_point_distance(closest_a, closest_b))
        result["details"] = {
            "surface_a": _vec3_to_list(closest_a),
            "surface_b": _vec3_to_list(closest_b),
        }

    elif mode == "clearance":
        # Clearance = surface distance, negative means overlap
        # On each axis
        clearances = []
        for i in range(3):
            c = max(world_min_a[i], world_min_b[i]) - min(world_max_a[i], world_max_b[i])
            clearances.append(_round3(c))
        # Minimum clearance across axes
        min_clearance = min(clearances)
        result["distance"] = _round3(min_clearance)
        result["details"] = {"clearances_xyz": clearances}

    return result


def get_material_map() -> dict:
    """Get material-to-object mapping with color information.

    Returns:
        JSON string with materials list, each having name, color, objects.
    """
    materials = {}

    # Get all shading engines
    shading_engines = cmds.ls(type="shadingEngine") or []
    for sg in shading_engines:
        # Skip default shaders
        if sg in ("initialParticleSE", "initialShadingGroup"):
            continue

        # Get material connected to this SG
        mat_list = cmds.ls(cmds.listConnections(sg + ".surfaceShader") or [], materials=True)
        if not mat_list:
            continue

        mat_name = mat_list[0]

        # Get color
        color = [0.5, 0.5, 0.5]  # default gray
        try:
            color_attr = cmds.getAttr(mat_name + ".color")[0]
            color = [_round3(c) for c in color_attr]
        except Exception:
            pass

        # Get objects assigned to this SG
        assigned = cmds.sets(sg, query=True) or []
        obj_names = []
        for obj in assigned:
            # Extract short name
            short = obj.split(".")[-1] if "." in obj else obj.split("|")[-1]
            obj_names.append(short)

        materials[mat_name] = {
            "name": mat_name,
            "color": color,
            "objects": obj_names,
            "object_count": len(obj_names),
            "shader_group": sg,
        }

    return {"materials": list(materials.values()), "total": len(materials)}


def get_unit_info() -> dict:
    """Get scene unit and axis information.

    Returns:
        JSON string with unit info.
    """
    info = {}
    try:
        info["linear"] = cmds.currentUnit(query=True, linear=True)
    except Exception:
        info["linear"] = "cm"
    try:
        info["angular"] = cmds.currentUnit(query=True, angle=True)
    except Exception:
        info["angular"] = "deg"
    try:
        info["up_axis"] = cmds.upAxis(query=True, axis=True)
    except Exception:
        info["up_axis"] = "y"
    try:
        info["time"] = cmds.currentUnit(query=True, time=True)
    except Exception:
        info["time"] = "film"
    return info


def assert_scene_state(expectations_json) -> dict:
    """Verify scene state matches expectations.

    Args:
        expectations_json: JSON string defining expected state.
            Format: {"obj_name": {"position": [x,y,z], "bbox_max": [x,y,z], ...}, ...}

    Returns:
        JSON string with pass/fail result and mismatches.
    """
    expectations = json.loads(expectations_json)
    mismatches = []
    checked = 0
    passed = 0

    for obj_name, expected in expectations.items():
        try:
            sel_list = om2.MSelectionList()
            sel_list.add(obj_name)
            dag = sel_list.getDagPath(0)
            fn = om2.MFnDagNode(dag)
        except Exception:
            mismatches.append({
                "object": obj_name,
                "property": "existence",
                "expected": "exists",
                "actual": "not found",
            })
            checked += 1
            continue

        # Check position
        if "position" in expected:
            checked += 1
            try:
                world_matrix = dag.inclusiveMatrix()
                actual_pos = _matrix_to_pos(world_matrix)
                exp_pos = expected["position"]
                # Allow 1 unit tolerance
                if any(abs(a - e) > 1.0 for a, e in zip(actual_pos, exp_pos)):
                    mismatches.append({
                        "object": obj_name,
                        "property": "position",
                        "expected": exp_pos,
                        "actual": actual_pos,
                    })
                else:
                    passed += 1
            except Exception as e:
                mismatches.append({
                    "object": obj_name,
                    "property": "position",
                    "error": str(e),
                })

        # Check bbox_max
        if "bbox_max" in expected:
            checked += 1
            try:
                bbox = fn.boundingBox
                actual_max = _vec3_to_list(bbox.max)
                exp_max = expected["bbox_max"]
                if any(abs(a - e) > 1.0 for a, e in zip(actual_max, exp_max)):
                    mismatches.append({
                        "object": obj_name,
                        "property": "bbox_max",
                        "expected": exp_max,
                        "actual": actual_max,
                    })
                else:
                    passed += 1
            except Exception as e:
                mismatches.append({
                    "object": obj_name,
                    "property": "bbox_max",
                    "error": str(e),
                })

        # Check existence only
        if "exists" in expected:
            checked += 1
            if expected["exists"]:
                passed += 1  # We already found it above
            else:
                mismatches.append({
                    "object": obj_name,
                    "property": "existence",
                    "expected": "not exists",
                    "actual": "exists",
                })

        # Check material
        if "material" in expected:
            checked += 1
            actual_mat = _get_material_for_dag(dag)
            if actual_mat != expected["material"]:
                mismatches.append({
                    "object": obj_name,
                    "property": "material",
                    "expected": expected["material"],
                    "actual": actual_mat,
                })
            else:
                passed += 1

    return {"passed": len(mismatches) == 0, "checked_count": checked, "passed_count": passed, "mismatches": mismatches}






# ============================================================
# P0: Spatial Constraint Validation
# ============================================================

def check_constraints(rules):
    """Check scene against spatial constraints.

    Args:
        rules: List of constraint dicts, each with:
            - type: "min_clearance" | "max_objects" | "no_overlap" | "min_height" | "max_height"
            - zone: optional zone name to limit check
            - value: threshold value
            - objects: optional list of object names to check

    Returns:
        dict with violations list and summary.
    """
    violations = []
    checked = 0

    for rule in rules:
        rtype = rule.get("type", "")
        value = rule.get("value", 0)
        zone = rule.get("zone")
        obj_list = rule.get("objects")

        if rtype == "min_clearance":
            # Check minimum clearance between objects
            transforms = cmds.ls(type="transform", long=True) or []
            if zone:
                zone_data = get_zone_map()
                zone_names = []
                for z in zone_data.get("zones", []):
                    if z["name"] == zone:
                        zone_names = z.get("objects", [])
                        break
                transforms = [t for t in transforms if t.split("|")[-1] in zone_names]

            for i in range(len(transforms)):
                for j in range(i + 1, min(len(transforms), i + 20)):
                    try:
                        m = measure(
                            transforms[i].split("|")[-1],
                            transforms[j].split("|")[-1],
                            "clearance"
                        )
                        checked += 1
                        if m.get("distance", 999) < value and m.get("distance", 999) > 0:
                            violations.append({
                                "type": "min_clearance",
                                "objects": [transforms[i].split("|")[-1], transforms[j].split("|")[-1]],
                                "actual": m["distance"],
                                "required": value,
                            })
                    except Exception:
                        pass

        elif rtype == "max_objects":
            total = len(cmds.ls(type="transform", long=True) or [])
            checked += 1
            if total > value:
                violations.append({
                    "type": "max_objects",
                    "actual": total,
                    "required": value,
                })

        elif rtype == "no_overlap":
            transforms = cmds.ls(type="transform", long=True) or []
            if obj_list:
                transforms = [t for t in transforms if t.split("|")[-1] in obj_list]
            for i in range(len(transforms)):
                for j in range(i + 1, min(len(transforms), i + 20)):
                    try:
                        m = measure(
                            transforms[i].split("|")[-1],
                            transforms[j].split("|")[-1],
                            "bbox"
                        )
                        checked += 1
                        if m.get("bbox_overlap", False):
                            violations.append({
                                "type": "overlap",
                                "objects": [transforms[i].split("|")[-1], transforms[j].split("|")[-1]],
                            })
                    except Exception:
                        pass

        elif rtype in ("min_height", "max_height"):
            if obj_list:
                for oname in obj_list:
                    try:
                        sel = om2.MSelectionList()
                        sel.add(oname)
                        dag = sel.getDagPath(0)
                        fn = om2.MFnDagNode(dag)
                        bbox = fn.boundingBox
                        height = abs(bbox.max[1] - bbox.min[1])
                        checked += 1
                        if rtype == "min_height" and height < value:
                            violations.append({"type": rtype, "object": oname, "actual": round(height, 1), "required": value})
                        elif rtype == "max_height" and height > value:
                            violations.append({"type": rtype, "object": oname, "actual": round(height, 1), "required": value})
                    except Exception:
                        pass

    return {
        "passed": len(violations) == 0,
        "checked": checked,
        "violations": violations,
        "violation_count": len(violations),
    }


# ============================================================
# P0: Scene Checkpoint / Rollback
# ============================================================

def save_checkpoint(name):
    """Save a scene checkpoint by exporting a copy.

    Args:
        name: Checkpoint name (human-readable).

    Returns:
        dict with checkpoint info.
    """
    import os
    import datetime
    import shutil

    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        return {"error": "No scene file saved. Save the scene first."}

    scene_dir = os.path.dirname(scene_path)
    cp_dir = os.path.join(scene_dir, "checkpoints")
    os.makedirs(cp_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    cp_filename = f"cp_{timestamp}_{safe_name}.ma"
    cp_path = os.path.join(cp_dir, cp_filename)

    # Copy file directly (safe, no Maya state change)
    try:
        shutil.copy2(scene_path, cp_path)
    except Exception as e:
        return {"error": f"Failed to save checkpoint: {e}"}

    transforms = cmds.ls(type="transform", long=True) or []
    return {
        "name": name,
        "timestamp": timestamp,
        "path": cp_path,
        "object_count": len(transforms),
        "mesh_count": len(cmds.ls(type="mesh") or []),
        "light_count": len(cmds.ls(type="light") or []),
    }


def list_checkpoints():
    """List all checkpoints for the current scene.

    Returns:
        dict with checkpoints list.
    """
    import os
    import glob

    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        return {"error": "No scene file saved.", "checkpoints": []}

    scene_dir = os.path.dirname(scene_path)
    cp_dir = os.path.join(scene_dir, "checkpoints")

    if not os.path.exists(cp_dir):
        return {"checkpoints": [], "count": 0}

    checkpoints = []
    for f in sorted(glob.glob(os.path.join(cp_dir, "cp_*.ma"))):
        stat = os.stat(f)
        checkpoints.append({
            "filename": os.path.basename(f),
            "path": f,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "modified": stat.st_mtime,
        })

    return {"checkpoints": checkpoints, "count": len(checkpoints)}


def rollback_to_checkpoint(filename):
    """Rollback scene to a checkpoint.

    Args:
        filename: Checkpoint filename (from list_checkpoints).

    Returns:
        dict with rollback result.
    """
    import os

    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        return {"error": "No scene file saved."}

    scene_dir = os.path.dirname(scene_path)
    cp_dir = os.path.join(scene_dir, "checkpoints")
    cp_path = os.path.join(cp_dir, filename)

    if not os.path.exists(cp_path):
        return {"error": f"Checkpoint not found: {filename}"}

    # Auto-save current state before rollback
    auto_cp = save_checkpoint("auto_before_rollback")
    if "error" not in auto_cp:
        auto_cp_path = auto_cp.get("path", "")

    # Open checkpoint
    try:
        cmds.file(cp_path, open=True, force=True)
        cmds.file(rename=scene_path)  # Keep original scene name
    except Exception as e:
        return {"error": f"Failed to rollback: {e}"}

    transforms = cmds.ls(type="transform", long=True) or []
    return {
        "success": True,
        "rolled_back_to": filename,
        "auto_backup": auto_cp.get("path", ""),
        "object_count": len(transforms),
    }


# ============================================================
# P1: Camera / Shot Planning
# ============================================================

SHOT_TYPES = {
    "extreme_wide": {"distance_mult": 8.0, "focal_length": 18, "desc": "极远景 - 建立环境"},
    "wide": {"distance_mult": 5.0, "focal_length": 24, "desc": "远景 - 展示全貌"},
    "medium": {"distance_mult": 3.0, "focal_length": 35, "desc": "中景 - 展示动作"},
    "close": {"distance_mult": 1.5, "focal_length": 50, "desc": "特写 - 展示细节"},
    "extreme_close": {"distance_mult": 0.8, "focal_length": 85, "desc": "极特写 - 展示微细节"},
    "over_shoulder": {"distance_mult": 2.0, "focal_length": 50, "desc": "过肩镜头"},
    "bird_eye": {"distance_mult": 10.0, "focal_length": 24, "desc": "鸟瞰"},
    "low_angle": {"distance_mult": 3.0, "focal_length": 35, "desc": "仰拍"},
}


def create_camera_shot(target, shot_type="medium", name="shot_cam", angle=None):
    """Create a camera positioned for a specific shot type.

    Args:
        target: Target object name to look at.
        shot_type: One of SHOT_TYPES keys.
        name: Camera name.
        angle: Optional dict with "azimuth" and "elevation" in degrees.

    Returns:
        dict with camera info.
    """
    if shot_type not in SHOT_TYPES:
        return {"error": f"Unknown shot type: {shot_type}. Available: {list(SHOT_TYPES.keys())}"}

    shot = SHOT_TYPES[shot_type]

    # Get target position and size
    try:
        sel = om2.MSelectionList()
        sel.add(target)
        dag = sel.getDagPath(0)
        fn = om2.MFnDagNode(dag)
        bbox = fn.boundingBox
        wm = dag.inclusiveMatrix()

        target_pos = [wm[12], wm[13], wm[14]]
        target_size = max(
            abs(bbox.max[0] - bbox.min[0]),
            abs(bbox.max[1] - bbox.min[1]),
            abs(bbox.max[2] - bbox.min[2]),
        )
    except Exception as e:
        return {"error": f"Target not found: {target}: {e}"}

    # Calculate camera position
    distance = target_size * shot["distance_mult"]
    azimuth = (angle or {}).get("azimuth", 30)
    elevation = (angle or {}).get("elevation", 15)

    import math
    az_rad = math.radians(azimuth)
    el_rad = math.radians(elevation)

    cam_x = target_pos[0] + distance * math.cos(el_rad) * math.sin(az_rad)
    cam_y = target_pos[1] + distance * math.sin(el_rad)
    cam_z = target_pos[2] + distance * math.cos(el_rad) * math.cos(az_rad)

    # Create camera
    cam_transform, cam_shape = cmds.camera(
        name=name,
        focalLength=shot["focal_length"],
        horizontalFilmAperture=1.417,  # 35mm
    )
    cam_transform = cmds.rename(cam_transform, name)

    cmds.move(cam_x, cam_y, cam_z, cam_transform)

    # Aim at target using orient constraint or manual rotation
    try:
        cmds.aimConstraint(
            target, cam_transform,
            aimVector=[0, 0, -1],
            upVector=[0, 1, 0],
            worldUpType="scene",
        )
    except Exception:
        # Fallback: calculate rotation manually
        import math
        dx = target_pos[0] - cam_x
        dy = target_pos[1] - cam_y
        dz = target_pos[2] - cam_z
        dist_xz = math.sqrt(dx*dx + dz*dz)
        if dist_xz > 0:
            ry = math.degrees(math.atan2(-dx, -dz))
            rx = math.degrees(math.atan2(dy, dist_xz))
        else:
            ry, rx = 0, -90 if dy > 0 else 90
        cmds.rotate(rx, ry, 0, cam_transform)

    return {
        "camera": cam_transform,
        "shot_type": shot_type,
        "description": shot["desc"],
        "position": [round(cam_x, 1), round(cam_y, 1), round(cam_z, 1)],
        "focal_length": shot["focal_length"],
        "distance": round(distance, 1),
        "target": target,
    }


def create_orbit_camera(center, radius=500, frames=120, name="orbit_cam"):
    """Create a camera that orbits around a point using keyframes.

    Args:
        center: [x, y, z] center point.
        radius: Orbit radius.
        frames: Number of frames for full orbit.
        name: Camera name.

    Returns:
        dict with camera and animation info.
    """
    import math

    cam_transform, cam_shape = cmds.camera(name=name, focalLength=35)
    cam_transform = cmds.rename(cam_transform, name)

    # Set keyframes for circular orbit
    step = max(1, frames // 30)  # Key every N frames for smooth orbit
    for frame in range(1, frames + 1, step):
        angle = (2 * math.pi * (frame - 1)) / frames
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * 0.3
        z = center[2] + radius * math.sin(angle)
        cmds.currentTime(frame, edit=True)
        cmds.move(x, y, z, cam_transform)
        cmds.setKeyframe(cam_transform, attribute="translateX")
        cmds.setKeyframe(cam_transform, attribute="translateY")
        cmds.setKeyframe(cam_transform, attribute="translateZ")

    # Set smooth tangents
    cmds.select(cam_transform)
    cmds.keyTangent(edit=True, itt="auto", ott="auto")

    # Aim constraint at center
    try:
        cmds.aimConstraint(
            None, cam_transform,
            aimVector=[0, 0, -1],
            upVector=[0, 1, 0],
            worldUpType="scene",
        )
    except Exception:
        pass

    # Set playback range
    cmds.playbackOptions(min=1, max=frames)

    return {
        "camera": cam_transform,
        "center": center,
        "radius": radius,
        "frames": frames,
        "keyframe_step": step,
    }


# ============================================================
# P1: Aesthetic Analysis
# ============================================================

def analyze_aesthetics():
    """Analyze scene aesthetics: color harmony, spatial balance, focal points.

    Returns:
        dict with aesthetic analysis.
    """
    result = {}

    # --- Color Harmony ---
    mat_data = get_material_map()
    materials = mat_data.get("materials", [])

    active_colors = []
    for mat in materials:
        if mat.get("object_count", 0) > 0:
            active_colors.append({
                "name": mat["name"],
                "color": mat["color"],
                "weight": mat["object_count"],
            })

    # Sort by weight
    active_colors.sort(key=lambda x: x["weight"], reverse=True)

    # Calculate dominant color
    if active_colors:
        total_weight = sum(c["weight"] for c in active_colors)
        dom_r = sum(c["color"][0] * c["weight"] for c in active_colors) / total_weight
        dom_g = sum(c["color"][1] * c["weight"] for c in active_colors) / total_weight
        dom_b = sum(c["color"][2] * c["weight"] for c in active_colors) / total_weight
        dominant_color = [round(dom_r, 3), round(dom_g, 3), round(dom_b, 3)]
    else:
        dominant_color = [0.5, 0.5, 0.5]

    # Determine harmony type
    if len(active_colors) >= 2:
        top2 = active_colors[:2]
        h1 = _rgb_to_hue(top2[0]["color"])
        h2 = _rgb_to_hue(top2[1]["color"])
        hue_diff = abs(h1 - h2)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        if hue_diff < 30:
            harmony = "analogous"
        elif 150 < hue_diff < 210:
            harmony = "complementary"
        elif 100 < hue_diff < 140:
            harmony = "triadic"
        else:
            harmony = "split_complementary"
    else:
        harmony = "monochromatic"

    # Contrast ratio (simplified)
    if active_colors:
        lightest = max(sum(c["color"]) for c in active_colors)
        darkest = min(sum(c["color"]) for c in active_colors)
        contrast = (lightest + 0.05) / (darkest + 0.05) if darkest > 0 else 10.0
    else:
        contrast = 1.0

    result["color_harmony"] = {
        "dominant_color": dominant_color,
        "harmony_type": harmony,
        "contrast_ratio": round(contrast, 2),
        "active_material_count": len(active_colors),
        "top_colors": [{"name": c["name"], "color": c["color"], "weight": c["weight"]} for c in active_colors[:6]],
    }

    # --- Spatial Balance ---
    transforms = cmds.ls(type="transform", long=True) or []
    total_mass = 0
    weighted_x = 0
    weighted_z = 0

    for tname in transforms:
        try:
            sel = om2.MSelectionList()
            sel.add(tname)
            dag = sel.getDagPath(0)
            fn = om2.MFnDagNode(dag)
            bbox = fn.boundingBox
            wm = dag.inclusiveMatrix()
            volume = abs(bbox.max[0] - bbox.min[0]) * abs(bbox.max[1] - bbox.min[1]) * abs(bbox.max[2] - bbox.min[2])
            if volume > 0:
                weighted_x += wm[12] * volume
                weighted_z += wm[14] * volume
                total_mass += volume
        except Exception:
            pass

    if total_mass > 0:
        center_x = weighted_x / total_mass
        center_z = weighted_z / total_mass
    else:
        center_x, center_z = 0, 0

    # Get overall bounds
    try:
        sel = om2.MSelectionList()
        sel.add("ALL")
        dag = sel.getDagPath(0)
        fn = om2.MFnDagNode(dag)
        bbox = fn.boundingBox
        span_x = abs(bbox.max[0] - bbox.min[0])
        span_z = abs(bbox.max[2] - bbox.min[2])
        norm_x = (center_x - bbox.min[0]) / span_x if span_x > 0 else 0.5
        norm_z = (center_z - bbox.min[2]) / span_z if span_z > 0 else 0.5
    except Exception:
        norm_x, norm_z = 0.5, 0.5

    balance_x = 1.0 - abs(norm_x - 0.5) * 2  # 1 = perfect, 0 = extreme
    balance_z = 1.0 - abs(norm_z - 0.5) * 2

    result["spatial_balance"] = {
        "center_of_mass": [round(center_x, 1), round(center_z, 1)],
        "normalized_position": [round(norm_x, 3), round(norm_z, 3)],
        "balance_score_x": round(balance_x, 3),
        "balance_score_z": round(balance_z, 3),
        "overall_balance": round((balance_x + balance_z) / 2, 3),
    }

    # --- Focal Points ---
    # Identify objects with largest visual weight (size * material contrast)
    focal_candidates = []
    for tname in transforms[:50]:  # Limit for performance
        try:
            sel = om2.MSelectionList()
            sel.add(tname)
            dag = sel.getDagPath(0)
            fn = om2.MFnDagNode(dag)
            bbox = fn.boundingBox
            wm = dag.inclusiveMatrix()
            size = max(
                abs(bbox.max[0] - bbox.min[0]),
                abs(bbox.max[1] - bbox.min[1]),
                abs(bbox.max[2] - bbox.min[2]),
            )
            mat = _get_material_for_dag(dag)
            # Visual weight = size * material presence
            weight = size * (1.5 if mat and "pink" in str(mat).lower() else 1.0)
            focal_candidates.append({
                "object": fn.name(),
                "size": round(size, 1),
                "material": mat,
                "visual_weight": round(weight, 1),
                "position": [round(wm[12], 1), round(wm[13], 1), round(wm[14], 1)],
            })
        except Exception:
            pass

    focal_candidates.sort(key=lambda x: x["visual_weight"], reverse=True)
    result["focal_points"] = focal_candidates[:5]

    return result


def _rgb_to_hue(rgb):
    """Convert RGB to hue (0-360)."""
    r, g, b = rgb
    mx = max(r, g, b)
    mn = min(r, g, b)
    if mx == mn:
        return 0
    d = mx - mn
    if mx == r:
        h = 60 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60 * (((b - r) / d) + 2)
    else:
        h = 60 * (((r - g) / d) + 4)
    return h % 360





# ============================================================
# REVIEW: Comprehensive Scene Audit
# ============================================================

# ============================================================
# REVIEW: Enhanced Scene Audit with Industry Standards
# ============================================================

# Retail/pop-up store design standards (expert knowledge)
_RETAIL_STANDARDS = {
    "aisle_main_min": 180,      # Main aisle minimum width (cm) - ADA + comfort
    "aisle_secondary_min": 120, # Secondary aisle minimum width (cm)
    "aisle_display_min": 90,    # Display area aisle minimum (cm)
    "display_height_min": 80,   # Minimum display height (cm)
    "display_height_max": 200,  # Maximum display height (cm) - eye level + reach
    "display_height_ideal": 130,# Ideal display height (cm) - eye level
    "ceiling_min": 280,         # Minimum ceiling height (cm)
    "ceiling_ideal": 350,       # Ideal ceiling height (cm)
    "entrance_decompression": 150,  # Entrance decompression zone depth (cm)
    "checkout_placement": "back",   # Checkout at back of store
    "ip_placement": "center_back",  # IP/hero display center-back
    "color_max_palette": 5,     # Maximum colors in palette
    "color_contrast_min": 4.5,  # Minimum contrast ratio (WCAG AA)
    "light_layers_min": 3,      # Minimum lighting layers
    "zone_ratio_display": 0.4,  # 40% display area
    "zone_ratio_circulation": 0.3,  # 30% circulation
    "zone_ratio_experience": 0.2,   # 20% experience/play
    "zone_ratio_service": 0.1,      # 10% service/checkout
    "focal_points_min": 2,      # Minimum focal points
    "focal_points_max": 5,      # Maximum focal points (avoid visual chaos)
}

# Maya production naming conventions
_MAYA_NAMING = {
    "prefixes": {
        "GRP_": "group/organizational node",
        "GEO_": "geometry mesh",
        "MAT_": "material",
        "CAM_": "camera",
        "LGT_": "light",
        "LOC_": "locator",
        "JNT_": "joint",
        "RIG_": "rigging",
        "FX_": "effects",
    },
    "suffixes": {
        "_geo": "geometry",
        "_grp": "group",
        "_mat": "material",
        "_cam": "camera",
        "_lgt": "light",
        "_loc": "locator",
    },
    "forbidden_names": ["pCube", "pSphere", "pCylinder", "pCone", "nurbsCircle",
                        "polySurface", "group1", "group2", "group3", "null",
                        "untitled", "default"],
}


# ============================================================
# REVIEW: Engineering-Grade Scene Audit
# ============================================================

# Expert-level retail/pop-up store design standards
_EXPERT_STANDARDS = {
    # ADA/Universal Design
    "aisle_main_min_cm": 180,
    "aisle_secondary_min_cm": 120,
    "aisle_display_min_cm": 90,
    "wheelchair_turn_cm": 150,

    # Display Standards
    "display_height_min_cm": 80,
    "display_height_max_cm": 200,
    "display_height_ideal_cm": 130,
    "display_depth_min_cm": 60,

    # Architecture
    "ceiling_min_cm": 280,
    "ceiling_ideal_cm": 350,
    "wall_thickness_min_cm": 10,
    "entrance_width_min_cm": 200,

    # Lighting (lux equivalents)
    "ambient_lights_min": 1,
    "key_lights_min": 1,
    "accent_lights_min": 1,
    "total_lights_min": 3,

    # Color (60-30-10 rule)
    "max_main_colors": 5,
    "min_contrast_ratio": 4.5,

    # Spatial Zoning
    "zone_display_ratio": 0.40,
    "zone_circulation_ratio": 0.30,
    "zone_experience_ratio": 0.20,
    "zone_service_ratio": 0.10,

    # Focal Points
    "focal_min": 2,
    "focal_max": 5,
    "focal_sight_distance_cm": 600,

    # Safety
    "max_objects": 500,
    "emergency_exit_width_cm": 120,
}

# Maya production naming convention
_MAYA_PRODUCTION = {
    "required_prefixes": {
        "GRP_": "Group/Organizational",
        "GEO_": "Geometry",
        "MAT_": "Material",
        "CAM_": "Camera",
        "LGT_": "Light",
        "LOC_": "Locator",
    },
    "forbidden_patterns": [
        "^pCube", "^pSphere", "^pCylinder", "^pCone",
        "^nurbsCircle", "^polySurface", "^group[0-9]",
        "^null", "^untitled", "^default", "^Mesh_[0-9]",
    ],
    "hierarchy_rules": [
        "Top-level groups must have GRP_ prefix",
        "No more than 4 levels of nesting",
        "All meshes must be under a group",
    ],
}


# ============================================================
# REVIEW: Universal Maya Scene Audit (Generic)
# ============================================================

# Universal Maya production standards (not project-specific)
_MAYA_STANDARDS = {
    # Naming
    "forbidden_prefixes": ["pCube", "pSphere", "pCylinder", "pCone", "nurbsCircle",
                           "polySurface", "group", "null", "untitled", "default"],
    "required_group_prefix": "GRP_",
    "max_nesting_depth": 4,

    # Spatial
    "max_objects_soft": 500,
    "max_objects_hard": 2000,
    "max_cameras_keep": 10,
    "min_lights": 3,

    # Componentization
    "min_objects_per_group": 2,
    "require_groups_for": ["mesh", "light", "camera"],

    # Architecture
    "min_clearance_cm": 5,  # Minimum clearance between non-related objects
    "overlap_tolerance_cm": 1,  # Tolerance for overlap detection
}


# ============================================================
# REVIEW: Universal Maya Scene Audit (Generic)
# ============================================================

# Universal Maya production standards (not project-specific)
_MAYA_STANDARDS = {
    # Naming
    "forbidden_prefixes": ["pCube", "pSphere", "pCylinder", "pCone", "nurbsCircle",
                           "polySurface", "group", "null", "untitled", "default"],
    "required_group_prefix": "GRP_",
    "max_nesting_depth": 4,

    # Spatial
    "max_objects_soft": 500,
    "max_objects_hard": 2000,
    "max_cameras_keep": 10,
    "min_lights": 3,

    # Componentization
    "min_objects_per_group": 2,
    "require_groups_for": ["mesh", "light", "camera"],

    # Architecture
    "min_clearance_cm": 5,  # Minimum clearance between non-related objects
    "overlap_tolerance_cm": 1,  # Tolerance for overlap detection
}


def scene_review(checks=None):
    """Universal Maya scene audit - works for ANY project.

    Reviews scene integrity after MCP operations. Detects spatial conflicts,
    naming violations, componentization issues, and architectural problems.

    Args:
        checks: list of check names. If None, runs all.
            Options: "spatial", "overlaps", "zones", "aesthetics",
                     "constraints", "orphans", "naming", "components", "conflicts"

    Returns:
        dict with score (0-100), issues, and detailed check results.
    """
    if checks is None:
        checks = ["spatial", "overlaps", "zones", "aesthetics",
                   "constraints", "orphans", "naming", "components", "conflicts"]

    result = {"checks": {}, "issues": [], "score": 0}
    total_score = 0
    max_score = 0

    transforms = cmds.ls(type="transform", long=True) or []
    mesh_count = len(cmds.ls(type="mesh") or [])
    light_count = len(cmds.ls(type="light") or [])
    cam_count = len(cmds.ls(type="camera") or [])

    # === SPATIAL INTEGRITY (15 pts) ===
    if "spatial" in checks:
        max_score += 15
        pts = 0
        sc = {"total": len(transforms), "meshes": mesh_count,
              "lights": light_count, "cameras": cam_count}

        if len(transforms) <= _MAYA_STANDARDS["max_objects_soft"]:
            pts += 5
        elif len(transforms) <= _MAYA_STANDARDS["max_objects_hard"]:
            pts += 2
            result["issues"].append({"severity": "warning", "check": "spatial",
                "msg": f"High object count ({len(transforms)}). Consider instancing."})
        else:
            result["issues"].append({"severity": "error", "check": "spatial",
                "msg": f"Excessive objects ({len(transforms)}). Performance risk."})

        if cam_count <= _MAYA_STANDARDS["max_cameras_keep"]:
            pts += 5
        else:
            result["issues"].append({"severity": "warning", "check": "spatial",
                "msg": f"Excess cameras ({cam_count}). Clean test shots."})

        if light_count >= _MAYA_STANDARDS["min_lights"]:
            pts += 5
        else:
            result["issues"].append({"severity": "warning", "check": "spatial",
                "msg": f"Only {light_count} lights. Need {_MAYA_STANDARDS['min_lights']}+."})

        total_score += pts
        result["checks"]["spatial"] = sc

    # === OVERLAP DETECTION (15 pts) ===
    if "overlaps" in checks:
        max_score += 15
        pts = 15
        overlap_pairs = []
        sample = transforms[:80]

        for i in range(len(sample)):
            for j in range(i + 1, min(len(sample), i + 30)):
                try:
                    m = measure(sample[i].split("|")[-1],
                                sample[j].split("|")[-1], "bbox")
                    if m.get("bbox_overlap", False):
                        a = sample[i].split("|")[-1]
                        b = sample[j].split("|")[-1]
                        is_pc = (a in sample[j] or b in sample[i])
                        is_grp = any(a.startswith(p) or b.startswith(p)
                                     for p in ("GRP_", "OUT_", "SUN", "ext_"))
                        if not is_pc and not is_grp:
                            overlap_pairs.append({"a": a, "b": b})
                except:
                    pass

        if len(overlap_pairs) > 10:
            pts = 3
            result["issues"].append({"severity": "error", "check": "overlaps",
                "msg": f"{len(overlap_pairs)} mesh overlaps. Fix intersections."})
        elif len(overlap_pairs) > 3:
            pts = 10
            result["issues"].append({"severity": "warning", "check": "overlaps",
                "msg": f"{len(overlap_pairs)} minor overlaps."})

        total_score += pts
        result["checks"]["overlaps"] = {"pairs": len(overlap_pairs),
                                         "details": overlap_pairs[:5]}

    # === SPATIAL CONFLICTS (15 pts) - NEW ===
    if "conflicts" in checks:
        max_score += 15
        pts = 15
        conflicts = []

        # Get all object bounds for penetration check
        obj_bounds = {}
        for t in transforms[:60]:
            try:
                sel = om2.MSelectionList()
                sel.add(t)
                dag = sel.getDagPath(0)
                fn = om2.MFnDagNode(dag)
                bbox = fn.boundingBox
                wm = dag.inclusiveMatrix()
                short = t.split("|")[-1]
                obj_bounds[short] = {
                    "min": [bbox.min[i] + wm[12+i] for i in range(3)],
                    "max": [bbox.max[i] + wm[12+i] for i in range(3)],
                }
            except:
                pass

        # Check for objects penetrating other objects (center inside another's bounds)
        checked = set()
        for name_a, bounds_a in obj_bounds.items():
            for name_b, bounds_b in obj_bounds.items():
                if name_a == name_b:
                    continue
                pair_key = tuple(sorted([name_a, name_b]))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                # Check if center of A is inside B's bounds
                cx = (bounds_a["min"][0] + bounds_a["max"][0]) / 2
                cy = (bounds_a["min"][1] + bounds_a["max"][1]) / 2
                cz = (bounds_a["min"][2] + bounds_a["max"][2]) / 2

                inside_b = (bounds_b["min"][0] <= cx <= bounds_b["max"][0] and
                            bounds_b["min"][1] <= cy <= bounds_b["max"][1] and
                            bounds_b["min"][2] <= cz <= bounds_b["max"][2])

                # Check if center of B is inside A's bounds
                cx2 = (bounds_b["min"][0] + bounds_b["max"][0]) / 2
                cy2 = (bounds_b["min"][1] + bounds_b["max"][1]) / 2
                cz2 = (bounds_b["min"][2] + bounds_b["max"][2]) / 2

                inside_a = (bounds_a["min"][0] <= cx2 <= bounds_a["max"][0] and
                            bounds_a["min"][1] <= cy2 <= bounds_a["max"][1] and
                            bounds_a["min"][2] <= cz2 <= bounds_a["max"][2])

                if inside_b or inside_a:
                    # Skip parent-child relationships
                    is_pc = (name_a in name_b or name_b in name_a)
                    # Skip group containment
                    is_grp = any(name_a.startswith(p) or name_b.startswith(p)
                                 for p in ("GRP_", "OUT_", "ALL"))
                    # Skip environment objects (SUN, OUT_lights, etc.)
                    env_prefixes = ("SUN", "OUT_", "sky", "env")
                    is_env = name_a.startswith(env_prefixes) or name_b.startswith(env_prefixes)
                    if not is_pc and not is_grp and not is_env:
                        conflicts.append({
                            "type": "penetration",
                            "object": name_a if inside_b else name_b,
                            "container": name_b if inside_b else name_a,
                        })

        if len(conflicts) > 5:
            pts = 3
            result["issues"].append({"severity": "error", "check": "conflicts",
                "msg": f"{len(conflicts)} spatial conflicts. Objects penetrating others."})
        elif len(conflicts) > 0:
            pts = 10
            result["issues"].append({"severity": "warning", "check": "conflicts",
                "msg": f"{len(conflicts)} spatial conflicts detected."})

        total_score += pts
        result["checks"]["conflicts"] = {"count": len(conflicts),
                                          "details": conflicts[:5]}

    # === ZONE COVERAGE (10 pts) ===
    if "zones" in checks:
        max_score += 10
        zd = get_zone_map()
        zones = zd.get("zones", [])
        unassigned = zd.get("unassigned_count", 0)
        total = len(transforms)
        coverage = 1.0 - (unassigned / total) if total > 0 else 0

        pts = 0
        if coverage >= 0.7: pts = 10
        elif coverage >= 0.5: pts = 7
        elif coverage >= 0.3: pts = 4
        else:
            result["issues"].append({"severity": "warning", "check": "zones",
                "msg": f"Low coverage ({coverage:.0%}). Add naming prefixes."})

        total_score += pts
        result["checks"]["zones"] = {"count": len(zones), "unassigned": unassigned,
                                      "coverage": round(coverage, 3)}

    # === NAMING CONVENTION (10 pts) ===
    if "naming" in checks:
        max_score += 10
        import re
        bad_names = []
        for t in transforms:
            short = t.split("|")[-1]
            for prefix in _MAYA_STANDARDS["forbidden_prefixes"]:
                if short.startswith(prefix):
                    bad_names.append(short)
                    break

        pts = 10
        if len(bad_names) > 10:
            pts = 2
            result["issues"].append({"severity": "error", "check": "naming",
                "msg": f"{len(bad_names)} objects with default names."})
        elif len(bad_names) > 3:
            pts = 6
            result["issues"].append({"severity": "warning", "check": "naming",
                "msg": f"{len(bad_names)} objects with default names."})

        total_score += pts
        result["checks"]["naming"] = {"bad_count": len(bad_names),
                                       "examples": bad_names[:5]}

    # === COMPONENTIZATION (15 pts) - NEW ===
    if "components" in checks:
        max_score += 15
        pts = 0

        # Check: are meshes grouped?
        ungrouped_meshes = 0
        grouped_meshes = 0
        for t in transforms:
            short = t.split("|")[-1]
            try:
                sel = om2.MSelectionList()
                sel.add(t)
                dag = sel.getDagPath(0)
                ntype = _classify_node(dag)
                if ntype == "mesh":
                    # Check if parent is a GRP_ group
                    if dag.length() > 1:
                        parent_dag = om2.MDagPath(dag)
                        parent_dag.pop()
                        parent_name = om2.MFnDagNode(parent_dag).name()
                        if parent_name.startswith("GRP_"):
                            grouped_meshes += 1
                        else:
                            ungrouped_meshes += 1
                    else:
                        ungrouped_meshes += 1
            except:
                pass

        if ungrouped_meshes == 0:
            pts += 8
        elif ungrouped_meshes < grouped_meshes:
            pts += 4
            result["issues"].append({"severity": "warning", "check": "components",
                "msg": f"{ungrouped_meshes} meshes not under GRP_ groups."})
        else:
            result["issues"].append({"severity": "error", "check": "components",
                "msg": f"{ungrouped_meshes} meshes ungrouped. Use GRP_ convention."})

        # Check: are groups properly organized?
        groups = [t for t in transforms if t.split("|")[-1].startswith("GRP_")]
        if len(groups) >= 3:
            pts += 4
        elif len(groups) >= 1:
            pts += 2

        # Check nesting depth
        max_depth = 0
        for t in transforms[:30]:
            depth = t.count("|")
            max_depth = max(max_depth, depth)
        if max_depth <= _MAYA_STANDARDS["max_nesting_depth"]:
            pts += 3
        else:
            result["issues"].append({"severity": "warning", "check": "components",
                "msg": f"Nesting depth {max_depth} exceeds {_MAYA_STANDARDS['max_nesting_depth']}."})

        total_score += pts
        result["checks"]["components"] = {
            "grouped_meshes": grouped_meshes,
            "ungrouped_meshes": ungrouped_meshes,
            "groups": len(groups),
            "max_depth": max_depth,
        }

    # === ORPHAN DETECTION (5 pts) ===
    if "orphans" in checks:
        max_score += 5
        orphans = 0
        for t in transforms:
            short = t.split("|")[-1]
            if re.match(r"^group[0-9]+$", short):
                orphans += 1
        if orphans == 0:
            total_score += 5
        elif orphans <= 3:
            total_score += 2
            result["issues"].append({"severity": "warning", "check": "orphans",
                "msg": f"{orphans} orphan groups"})

    # === AESTHETICS (10 pts) ===
    if "aesthetics" in checks:
        max_score += 10
        pts = 0
        try:
            aest = analyze_aesthetics()
            balance = aest.get("spatial_balance", {}).get("overall_balance", 0)
            harmony = aest.get("color_harmony", {}).get("harmony_type", "unknown")
            focal_count = len(aest.get("focal_points", []))

            if balance > 0.7: pts += 4
            elif balance > 0.5: pts += 2
            if focal_count >= 2: pts += 3
            elif focal_count >= 1: pts += 1
            if harmony in ("complementary", "analogous", "triadic"): pts += 3
            elif harmony != "unknown": pts += 1

            result["checks"]["aesthetics"] = {
                "balance": round(balance, 3), "harmony": harmony,
                "focal_points": focal_count}
        except:
            result["issues"].append({"severity": "warning", "check": "aesthetics",
                "msg": "Analysis failed"})
        total_score += pts

    # === CONSTRAINTS (5 pts) ===
    if "constraints" in checks:
        max_score += 5
        try:
            cr = check_constraints([{"type": "max_objects", "value": 500}])
            if cr.get("passed", False):
                total_score += 5
        except:
            pass

    # Final score
    result["score"] = round((total_score / max_score * 100) if max_score > 0 else 0, 1)
    result["total_issues"] = len(result["issues"])
    result["errors"] = sum(1 for i in result["issues"] if i["severity"] == "error")
    result["warnings"] = sum(1 for i in result["issues"] if i["severity"] == "warning")
    result["standards"] = {
        "naming": "Maya Production Naming Convention (GRP_/GEO_/MAT_/CAM_/LGT_)",
        "componentization": "Group-based scene organization (max 4 levels nesting)",
        "spatial": "Penetration/conflict detection between non-related objects",
        "aesthetics": "Color harmony + spatial balance + focal point analysis",
        "safety": "Max 500 objects, orphan detection, constraint validation",
    }

    return result


