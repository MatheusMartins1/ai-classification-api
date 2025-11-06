"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

from typing import Dict, Any, Optional, TypedDict, Union
from System.Drawing import Point, Rectangle  # type: ignore


class PointDict(TypedDict):
    x: int
    y: int


class RectangleDict(TypedDict):
    x: int
    y: int
    width: int
    height: int


def point_to_dict(point: Point) -> PointDict:
    """
    Convert a System.Drawing.Point to a Python dictionary.

    Args:
        point: System.Drawing.Point object

    Returns:
        Dictionary containing x,y coordinates
    """
    return {"x": point.X, "y": point.Y}


def dict_to_point(data: Dict[str, int]) -> Point:
    """
    Convert a dictionary to System.Drawing.Point.

    Args:
        data: Dictionary containing x,y coordinates

    Returns:
        System.Drawing.Point object
    """
    return Point(data.get("x", 0), data.get("y", 0))


def rectangle_to_dict(rect: Rectangle) -> RectangleDict:
    """
    Convert a System.Drawing.Rectangle to a Python dictionary.

    Args:
        rect: System.Drawing.Rectangle object

    Returns:
        Dictionary containing x,y,width,height values
    """
    return {"x": rect.X, "y": rect.Y, "width": rect.Width, "height": rect.Height}


def dict_to_rectangle(data: Dict[str, int]) -> Rectangle:
    """
    Convert a dictionary to System.Drawing.Rectangle.

    Args:
        data: Dictionary containing x,y,width,height values

    Returns:
        System.Drawing.Rectangle object
    """
    return Rectangle(
        data.get("x", 0), data.get("y", 0), data.get("width", 0), data.get("height", 0)
    )


def geometry_to_dict(obj: Union[Point, Rectangle]) -> Union[PointDict, RectangleDict]:
    """
    Convert a geometry object to a Python dictionary.

    Args:
        obj: System.Drawing.Point or System.Drawing.Rectangle object

    Returns:
        Dictionary representation of the geometry object

    Raises:
        ValueError: If object type is not supported
    """
    if isinstance(obj, Point):
        return point_to_dict(obj)
    elif isinstance(obj, Rectangle):
        return rectangle_to_dict(obj)
    else:
        raise ValueError(f"Unsupported geometry type: {type(obj)}")


def dict_to_geometry(
    data: Dict[str, Any], geometry_type: str
) -> Union[Point, Rectangle]:
    """
    Convert a dictionary to a geometry object.

    Args:
        data: Dictionary containing geometry data
        geometry_type: Type of geometry object to create ('point' or 'rectangle')

    Returns:
        Geometry object (Point or Rectangle)

    Raises:
        ValueError: If geometry_type is not supported
    """
    if geometry_type.lower() == "point":
        return dict_to_point(data)
    elif geometry_type.lower() == "rectangle":
        return dict_to_rectangle(data)
    else:
        raise ValueError(f"Unsupported geometry type: {geometry_type}")
