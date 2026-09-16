# Maya 端模块改造：绞杀者模式 + 混合测试

maya_scene_module.py（3564 行，零真实测试）采用绞杀者模式：先建 maya.cmds/OpenMaya stub 层（CI 跑 orchestration 路径）+ 可选 mayapy 真机本地档（文档化、不卡 CI）；每个修复带回归测试；子模块拆分随修复触及区域增量进行，不做一次性大拆。

Status: accepted (2026-09-16)

## Considered Options
- 先修后拆：否决——无回归网下继续改单体，风险持续累积。
- 先拆后修：否决——对无测试的 3564 行做大拆分等于盲改。
- 真机 mayapy 上 CI：否决——许可/基建成本过高。

## Consequences
- stub 层数学必须语义正确（尤其 8 角点世界 bbox），否则测试假绿。
- aesthetic_engine.py 为纯 Python（零 Maya 依赖），可直接进 CI。
