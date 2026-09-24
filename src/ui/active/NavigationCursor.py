"""
    Spatial navigation system for PyQt widgets allowing direction-based traversal.
"""

from typing import Dict, List, Optional, Set, Union, Callable, TypeAlias
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton

from src.utils.Logs import Logs

_T_NavigationObject: TypeAlias = 'NavigationCursor | QWidget | None'


class NavigationCursor:
    """
        Mixin class enabling spatial keyboard and cursor navigation across hierarchical PyQt UI layers.

        Integrates with PyQt widgets to form a logical layer graph. A designated global cursor moves
        between sibling widgets on the same layer (using W/A/S/D directional bounds) or navigates
        inward/outward through parent-child layers (using IN/OUT commands).
    """

    layer_index: int
    MAX_LAYER_INDEX: int = 6
    ID: int = 0

    active_instance_of_class: Set['NavigationCursor'] = set()
    movement_cursor: 'NavigationCursor' = None

    FLAG_is_connection_generate: bool = False

    CONNECTION_PATTER = {
        1:'W',
        2:'S',
        3:'A',
        4:'D',
        5:'IN',
        6:'OUT',
    }

    @classmethod
    def set_ID(cls, object: 'NavigationCursor') -> None:
        """
            Assign a unique ID and layer hierarchy index to a new widget node.

            :param object: Target instance being registered into the system.
            :raises ValueError: If the widget nesting depth exceeds `layer_max_index`.
        """
        object.ID = cls.ID
        cls.ID += 1
        cls.active_instance_of_class.add(object)

        if isinstance(object.navigation_parent, QMainWindow):
            # root
            object.layer_index = 0
        else:
            if object.navigation_parent is not None and hasattr(object.navigation_parent, 'layer_index'):
                if object.navigation_parent.layer_index >= cls.MAX_LAYER_INDEX:
                    raise ValueError("Maximum navigation layer exceeded")
                # increment layer index
                object.layer_index = object.navigation_parent.layer_index + 1
            else:
                object.layer_index = 0

    def __init__(
        self,
        navigation_parent: _T_NavigationObject = None,
    ) -> None:
        """
            Initialize navigation properties and register the instance into the active node registry.

            :param navigation_parent: Parent UI container establishing layer context, defaults to None.
        """
        self.FLAG_is_object_selected: bool = False
        self.navigation_parent: _T_NavigationObject = navigation_parent

        # Object-space rectangle boundaries
        self.sideA: int = 0
        self.sideD: int = 0
        self.sideW: int = 0
        self.sideS: int = 0

        NavigationCursor.set_ID(self)

        self.map_connection: Dict[str, Optional[Union['NavigationCursor', Callable[[], None]]]] = {
            'W': None,
            'S': None,
            'A': None,
            'D': None,
            'IN': None,
            'OUT': None,
        }

        Logs.print(f"[INFO] Create {self.__class__}: ID {self.ID}, parent {self.navigation_parent}, layer {self.layer_index}")

    @classmethod
    def generate_connection(cls) -> None:
        """
            Calculate spatial boundaries and generate directional connections
            between all registered navigation nodes.

            W -> left
            S -> right
            A -> up
            D -> down

            IN  -> first child in the navigation layer
            OUT -> navigation parent
        """

        def create_connection_of_all_objects_in_section(
                section_parent: NavigationCursor | QWidget | None,
                section_children: list[NavigationCursor],
        ) -> None:
            """
            Generate spatial navigation connections for all nodes in a section.

            :param section_parent: Parent defining the current navigation section.
            :param section_children: Navigation nodes belonging to the section.
            """

            def find_min_to_side_xy(
                    subject: NavigationCursor,
                    search_nodes: list[NavigationCursor],
                    type_xy: str,
                    mode_lr: str,
            ) -> NavigationCursor | None:
                """Find the closest neighbor along the specified axis and direction."""
                candidates: list[NavigationCursor] = []

                # Filter candidates lying on the target side
                for node in search_nodes:
                    if type_xy == "Y":
                        if mode_lr == "L" and (subject.sideW > node.sideW or subject.sideW > node.sideS):
                            candidates.append(node)
                        elif mode_lr == "R" and (subject.sideS < node.sideW or subject.sideS < node.sideS):
                            candidates.append(node)

                    elif type_xy == "X":
                        if mode_lr == "L" and (subject.sideA > node.sideA or subject.sideA > node.sideD):
                            candidates.append(node)
                        elif mode_lr == "R" and (subject.sideD < node.sideA or subject.sideD < node.sideD):
                            candidates.append(node)

                if not candidates:
                    return None

                if len(candidates) == 1:
                    return candidates[0]

                # Prefer candidates overlapping the perpendicular axis
                overlapping: list[NavigationCursor] = []

                for node in candidates:
                    if type_xy == "Y":
                        if subject.sideA <= node.sideA < subject.sideD or subject.sideA < node.sideD <= subject.sideD:
                            overlapping.append(node)

                    elif type_xy == "X":
                        if subject.sideW <= node.sideW < subject.sideS or subject.sideW < node.sideS <= subject.sideS:
                            overlapping.append(node)

                if not overlapping:
                    overlapping = candidates

                if len(overlapping) == 1:
                    return overlapping[0]

                # Select the geometrically closest node
                closest: NavigationCursor | None = None

                for node in overlapping:
                    if closest is None:
                        closest = node
                        continue

                    if type_xy == "Y":
                        if mode_lr == "L":
                            if closest.sideS < node.sideS or (
                                    closest.sideS == node.sideS and closest.sideA > node.sideA
                            ):
                                closest = node

                        elif mode_lr == "R":
                            if closest.sideW > node.sideW or (
                                    closest.sideW == node.sideW and closest.sideA > node.sideA
                            ):
                                closest = node

                    elif type_xy == "X":
                        if mode_lr == "L":
                            if closest.sideD < node.sideD or (
                                    closest.sideD == node.sideD and closest.sideW > node.sideW
                            ):
                                closest = node

                        elif mode_lr == "R":
                            if closest.sideA > node.sideA or (
                                    closest.sideA == node.sideA and closest.sideW > node.sideW
                            ):
                                closest = node

                return closest

            # =============================================================
            # calculate
            # =============================================================

            first_node: NavigationCursor | None = None

            for subject in section_children:
                if isinstance(subject.navigation_parent, NavigationCursor):
                    subject.map_connection["OUT"] = subject.navigation_parent

                if first_node is None or (
                        subject.sideW < first_node.sideW or
                        (subject.sideW == first_node.sideW and subject.sideA < first_node.sideA)
                ):
                    first_node = subject

                search_nodes = [node for node in section_children if node is not subject]

                if not search_nodes:
                    continue

                subject.map_connection["W"] = find_min_to_side_xy(subject, search_nodes, "Y", "L")
                subject.map_connection["S"] = find_min_to_side_xy(subject, search_nodes, "Y", "R")
                subject.map_connection["A"] = find_min_to_side_xy(subject, search_nodes, "X", "L")
                subject.map_connection["D"] = find_min_to_side_xy(subject, search_nodes, "X", "R")

            if first_node is not None and isinstance(first_node.navigation_parent, NavigationCursor):
                first_node.navigation_parent.map_connection["IN"] = first_node

        sections: dict[
            NavigationCursor | QWidget | None,
            list[NavigationCursor],
        ] = {}

        for node in cls.active_instance_of_class:
            # Geometry
            if isinstance(node, QWidget):
                node.sideA = node.x()
                node.sideD = node.x() + node.width()

                node.sideW = node.y()
                node.sideS = node.y() + node.height()

            #  Reset existing connections
            node.map_connection.update({
                "W": None,
                "S": None,
                "A": None,
                "D": None,
                "IN": None,
                "OUT": None,
            })
            # Divide nodes into sections by navigation parent
            sections.setdefault( node.navigation_parent, []).append(node)

        # Generate connections inside every section
        for parent, children in sections.items():
            create_connection_of_all_objects_in_section(parent, children)

        cls.FLAG_is_connection_generate = True

    @classmethod
    def set_cursor(cls, object: 'NavigationCursor') -> None:
        """
            Move the active selection cursor to a target navigation node.

            :param object: Widget node receiving active focus.
        """
        prev = cls.movement_cursor

        cls.movement_cursor = object
        cls.movement_cursor.FLAG_is_object_selected = True

        if isinstance(cls.movement_cursor, QWidget):
            # graphic update
            cls.movement_cursor.update()

        if isinstance(prev, NavigationCursor):
            prev.FLAG_is_object_selected = False
            if isinstance(prev, QWidget):
                # graphic update
                prev.update()

    def move_cursor_to_next_positon(self, moveTag: str) -> None:
        """
            Trigger navigation jump toward a designated direction tag.

            :param moveTag: Direction key identifying the navigation jump ('W', 'S', 'A', 'D', 'IN', 'OUT').
        """
        Logs.print(f"<< Jump >> {moveTag} {self}")

        if moveTag in self.map_connection:
            target = self.map_connection[moveTag]

            # if moveTag == "IN" and callable(target):
            #     # activate interactive object
            #     target()
            #     return

            # change position of navigation cursor to target
            if isinstance(target, NavigationCursor):
                NavigationCursor.set_cursor(target)