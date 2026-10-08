"""
    Spatial navigation system for PyQt widgets allowing direction-based traversal.
"""

from typing import Dict, List, Optional, Set, Union, Callable
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton


class JumpingMachine:
    """
        Mixin class enabling spatial keyboard and cursor navigation across hierarchical PyQt UI layers.

        Integrates with PyQt widgets to form a logical layer graph. A designated global cursor moves
        between sibling widgets on the same layer (using W/A/S/D directional bounds) or navigates
        inward/outward through parent-child layers (using IN/OUT commands).
    """

    layer_index: int
    layer_max_index: int = 6
    ID: int = 0
    active_instance_of_class: Set['JumpingMachine'] = set()
    movement_cursor: Optional['JumpingMachine'] = None
    FLAG_is_connection_generate: bool = False

    def __init__(
        self,
        parentJP: Optional[Union['JumpingMachine', QWidget]] = None,
        instanceJP: Optional[object] = None,
    ) -> None:
        """
            Initialize navigation properties and register the instance into the active node registry.

            :param parentJP: Parent UI container establishing layer context, defaults to None.
            :param instanceJP: Reference instance hook, defaults to None.
        """
        self.FLAG_is_object_selected: bool = False
        self.parent: Optional[Union['JumpingMachine', QWidget]] = parentJP

        self.sideA: int = 0
        self.sideD: int = 0
        self.sideW: int = 0
        self.sideS: int = 0

        JumpingMachine.set_ID(self)

        self.map_connection: Dict[str, Optional[Union['JumpingMachine', Callable[[], None]]]] = {
            'W': None,
            'S': None,
            'A': None,
            'D': None,
            'IN': None,
            'OUT': None,
        }

        print(f"<< Create JumpingMachine: ID {self.ID}, parent {self.parent}, layer {self.layer_index}")

    @classmethod
    def set_ID(cls, subject: 'JumpingMachine') -> None:
        """
            Assign a unique ID and layer hierarchy index to a new widget node.

            :param subject: Target instance being registered into the system.
            :raises ValueError: If the widget nesting depth exceeds `layer_max_index`.
        """
        subject.ID = cls.ID
        cls.ID += 1
        cls.active_instance_of_class.add(subject)

        if isinstance(subject.parent, QMainWindow):
            subject.layer_index = 0
        else:
            if subject.parent is not None and hasattr(subject.parent, 'layer_index'):
                assert subject.parent.layer_index < cls.layer_max_index, "Maximum layer exceeded"
                subject.layer_index = subject.parent.layer_index + 1
            else:
                subject.layer_index = 0

    @classmethod
    def set_cursor(cls, subject: 'JumpingMachine') -> None:
        """
            Move the active selection cursor to a target navigation node.

            :param subject: Widget node receiving active focus.
        """
        prev = cls.movement_cursor

        cls.movement_cursor = subject
        cls.movement_cursor.FLAG_is_object_selected = True
        if isinstance(cls.movement_cursor, QWidget):
            cls.movement_cursor.update()

        if isinstance(prev, JumpingMachine):
            prev.FLAG_is_object_selected = False
            if isinstance(prev, QWidget):
                prev.update()

    @classmethod
    def generate_connection(cls) -> None:
        """
            Calculate spatial boundaries and generate relative directional connections for all registered nodes.
        """

        def create_connection_of_all_objects_in_section(
            sectionParent: Optional[Union['JumpingMachine', QWidget]],
            sectionChildren: List['JumpingMachine'],
        ) -> None:

            def find_min_to_side_XY(
                subject: 'JumpingMachine',
                searchSub: List['JumpingMachine'],
                typeXY: str,
                modeLR: str,
            ) -> Optional['JumpingMachine']:
                """Find the closest neighbor widget along a specified axis and directional vector."""
                arr_obj: List[Optional['JumpingMachine']] = [None]

                # Phase 1: Filter candidates lying on the target side
                for sub in searchSub:
                    if typeXY == "Y":
                        if modeLR == "L" and (subject.sideW > sub.sideW or subject.sideW > sub.sideS):
                            arr_obj.append(sub)
                        elif modeLR == "R" and (subject.sideS < sub.sideW or subject.sideS < sub.sideS):
                            arr_obj.append(sub)
                    elif typeXY == "X":
                        if modeLR == "L" and (subject.sideA > sub.sideA or subject.sideA > sub.sideD):
                            arr_obj.append(sub)
                        elif modeLR == "R" and (subject.sideD < sub.sideA or subject.sideD < sub.sideD):
                            arr_obj.append(sub)

                if len(arr_obj) <= 2:
                    return arr_obj[-1]

                # Phase 2: Narrow candidate range using perpendicular bounds
                brr_obj: List[Optional['JumpingMachine']] = [None]
                for sub_candidate in arr_obj[1:]:
                    if sub_candidate is None:
                        continue
                    if typeXY == "Y":
                        if (subject.sideA <= sub_candidate.sideA < subject.sideD or
                                subject.sideA < sub_candidate.sideD <= subject.sideD):
                            brr_obj.append(sub_candidate)
                    elif typeXY == "X":
                        if (subject.sideW <= sub_candidate.sideW < subject.sideS or
                                subject.sideW < sub_candidate.sideS <= subject.sideS):
                            brr_obj.append(sub_candidate)

                if len(brr_obj) == 1:
                    brr_obj = arr_obj
                elif len(brr_obj) == 2:
                    return brr_obj[-1]

                # Phase 3: Select the geometrically closest node
                extreme_case: Optional['JumpingMachine'] = None
                for sub_node in brr_obj[1:]:
                    if sub_node is None:
                        continue
                    if extreme_case is None:
                        extreme_case = sub_node
                        continue

                    if typeXY == "Y":
                        if modeLR == "L":
                            if extreme_case.sideS < sub_node.sideS:
                                extreme_case = sub_node
                            elif extreme_case.sideS == sub_node.sideS and extreme_case.sideA > sub_node.sideA:
                                extreme_case = sub_node
                        elif modeLR == "R":
                            if extreme_case.sideW > sub_node.sideW:
                                extreme_case = sub_node
                            elif extreme_case.sideW == sub_node.sideW and extreme_case.sideA > sub_node.sideA:
                                extreme_case = sub_node
                    elif typeXY == "X":
                        if modeLR == "L":
                            if extreme_case.sideD < sub_node.sideD:
                                extreme_case = sub_node
                            elif extreme_case.sideD == sub_node.sideD and extreme_case.sideW > sub_node.sideW:
                                extreme_case = sub_node
                        elif modeLR == "R":
                            if extreme_case.sideA > sub_node.sideA:
                                extreme_case = sub_node
                            elif extreme_case.sideA == sub_node.sideA and extreme_case.sideW > sub_node.sideW:
                                extreme_case = sub_node

                return extreme_case

            outdrop: Optional['JumpingMachine'] = None

            for subject in sectionChildren:
                if isinstance(subject.parent, JumpingMachine):
                    subject.map_connection["OUT"] = subject.parent

                if outdrop is None:
                    outdrop = subject
                else:
                    if subject.sideW < outdrop.sideW:
                        outdrop = subject
                    elif subject.sideW == outdrop.sideW and subject.sideA < outdrop.sideA:
                        outdrop = subject

                searchSub: List['JumpingMachine'] = sectionChildren.copy()
                searchSub.remove(subject)

                if len(searchSub) != 0:
                    subject.map_connection["W"] = find_min_to_side_XY(subject, searchSub, "Y", "L")
                    subject.map_connection["S"] = find_min_to_side_XY(subject, searchSub, "Y", "R")
                    subject.map_connection["A"] = find_min_to_side_XY(subject, searchSub, "X", "L")
                    subject.map_connection["D"] = find_min_to_side_XY(subject, searchSub, "X", "R")

            if outdrop is not None and isinstance(outdrop.parent, JumpingMachine):
                outdrop.parent.map_connection['IN'] = outdrop

        segments_per_parent: Dict[Optional[Union['JumpingMachine', QWidget]], List['JumpingMachine']] = {}

        for obj in cls.active_instance_of_class:
            if isinstance(obj, QWidget):
                obj.sideA = obj.x()
                obj.sideD = obj.x() + obj.width()
                obj.sideW = obj.y()
                obj.sideS = obj.y() + obj.height()

            if obj.parent in segments_per_parent:
                segments_per_parent[obj.parent].append(obj)
            else:
                segments_per_parent[obj.parent] = [obj]

        for parent, children in segments_per_parent.items():
            create_connection_of_all_objects_in_section(parent, children)

        cls.FLAG_is_connection_generate = True

    @classmethod
    def refresh_button(cls) -> None:
        """
            Bind click triggers for `QPushButton` instances to their respective 'IN' connections.
        """
        for subject in cls.active_instance_of_class:
            if isinstance(subject, QPushButton):
                subject.map_connection["IN"] = subject.click

    def jump(self, move_tag: str) -> None:
        """
            Trigger navigation jump toward a designated direction tag.

            :param move_tag: Direction key identifying the navigation jump ('W', 'S', 'A', 'D', 'IN', 'OUT').
        """
        print(f"<< Jump >> {move_tag} {self}")

        if move_tag in self.map_connection:
            target = self.map_connection[move_tag]

            if move_tag == "IN" and callable(target):
                target()
                return

            if isinstance(target, JumpingMachine):
                JumpingMachine.set_cursor(target)